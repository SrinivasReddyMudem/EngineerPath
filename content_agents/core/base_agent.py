"""
Base agent — Groq-backed, strict JSON schema enforcement, retry-with-feedback.
Ported from the automotive-lifecycle-agents pattern: same reliability model,
applied to content generation instead of technical analysis.
"""

import os
import json
from groq import Groq, BadRequestError, RateLimitError
from pydantic import BaseModel, ValidationError
from typing import Literal
from .logger import get_logger

MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"  # confirmed working with Groq's strict json_schema mode on this account
MAX_RETRIES = 2  # each retry re-sends the full prompt + accumulated feedback — keep this low for latency; rely on the best-effort fallback below instead of chasing more attempts


def _load_api_keys() -> list[str]:
    """
    GROQ_API_KEY is required; GROQ_API_KEY_2, GROQ_API_KEY_3, ... are
    optional fallbacks tried in order whenever the current key hits its
    daily rate limit — each Groq account has its own separate 500k TPD
    quota, so a second account's key genuinely gives more headroom.
    """
    keys = []
    primary = os.getenv("GROQ_API_KEY")
    if primary:
        keys.append(primary)
    i = 2
    while True:
        k = os.getenv(f"GROQ_API_KEY_{i}")
        if not k:
            break
        keys.append(k)
        i += 1
    return keys


class AgentError(BaseModel):
    agent: str
    error_type: Literal["api_error", "validation_error", "quality_check_failed", "rate_limit_exceeded"]
    message: str
    raw_response: str | None = None


class BestEffortWarning(BaseModel):
    """Attached (not raised) when content is returned despite a failed quality gate on the final attempt."""
    unresolved_issue: str


class QualityCheckError(Exception):
    """Raised by an agent's validators.py when a quality-gate check fails."""
    pass


class BaseAgent:
    AGENT_NAME = "base"

    def __init__(self):
        self._api_keys = _load_api_keys()
        if not self._api_keys:
            raise EnvironmentError(
                "GROQ_API_KEY not set.\n"
                "Get a free key (no credit card) at console.groq.com\n"
                "Then add it to .env as: GROQ_API_KEY=your-key"
            )
        self._key_index = 0
        self.client = Groq(api_key=self._api_keys[0])
        self.logger = get_logger(self.AGENT_NAME)

    def _switch_to_next_key(self) -> bool:
        """Returns True if a fallback key was available and swapped in, False if keys are exhausted."""
        if self._key_index + 1 >= len(self._api_keys):
            return False
        self._key_index += 1
        self.client = Groq(api_key=self._api_keys[self._key_index])
        self.logger.warning(f"Rate limit hit on key #{self._key_index} — switched to fallback key #{self._key_index + 1}.")
        return True

    def run(self, user_message: str) -> BaseModel | AgentError:
        """Always returns a Pydantic model or AgentError — never raises."""
        self.last_unresolved_issues: list[str] = []  # populated only if best-effort fallback triggers; callers that care (e.g. the production compiler) check this right after run()
        raw = None
        # Track the LAST schema-valid parse across ALL attempts, not just the
        # final one. A later attempt can fail at the Groq API level (strict
        # schema rejection) or fail Pydantic validation even though an
        # earlier attempt already produced perfectly usable, schema-valid
        # content — that earlier result shouldn't be thrown away just
        # because the last roll of the dice went worse.
        best_effort_parsed: BaseModel | None = None
        best_effort_issue: str | None = None

        # Accumulate every distinct issue seen across attempts (not just the
        # latest one). Each retry regenerates the whole response from scratch,
        # so fixing field X can silently reintroduce a bug in field Y that was
        # already correct — cumulative feedback keeps every past constraint
        # in view instead of trading one fix for a regression elsewhere.
        seen_issues: list[str] = []

        def _feedback() -> str | None:
            if not seen_issues:
                return None
            numbered = "\n".join(f"{i + 1}. {issue}" for i, issue in enumerate(seen_issues))
            return (
                f"Your response has failed on these {len(seen_issues)} issue(s) across attempts so far "
                f"— fix ALL of them simultaneously in your next response, don't just fix the most recent "
                f"one and accidentally reintroduce an earlier one:\n{numbered}\n"
                f"Return the complete corrected response matching the schema exactly."
            )

        def _return_best_effort_or_error(error_type: str, message: str) -> BaseModel | AgentError:
            if best_effort_parsed is not None:
                self.logger.warning(f"Returning best-effort result from an earlier attempt; final attempt failed with: {message}")
                self.last_unresolved_issues = [best_effort_issue or message]
                return best_effort_parsed
            return AgentError(agent=self.AGENT_NAME, error_type=error_type, message=message, raw_response=raw)

        for attempt in range(MAX_RETRIES + 1):
            try:
                raw = self._call_api(user_message, feedback=_feedback())
                parsed = self._parse(raw)
                best_effort_parsed = parsed  # schema-valid regardless of what the quality check below decides
                self._validate_quality(parsed)
                return parsed

            except ValidationError as e:
                self.logger.error(f"Schema validation failed (attempt {attempt + 1}): {e}")
                if attempt == MAX_RETRIES:
                    return _return_best_effort_or_error("validation_error", str(e))
                seen_issues.append(f"Schema validation error: {e}")

            except QualityCheckError as e:
                self.logger.warning(f"Quality gate failed (attempt {attempt + 1}): {e}")
                best_effort_issue = str(e)
                if attempt == MAX_RETRIES:
                    # `parsed` already passed strict schema validation — it just missed a
                    # quality bar. Returning it beats a hard failure after the full retry
                    # budget was already spent; log the gap for later review instead of
                    # discarding a mostly-good result.
                    return _return_best_effort_or_error("quality_check_failed", str(e))
                seen_issues.append(str(e))

            except BadRequestError as e:
                self.logger.warning(f"API schema rejection (attempt {attempt + 1}): {e}")
                if attempt == MAX_RETRIES:
                    return _return_best_effort_or_error("api_error", str(e))
                seen_issues.append(f"API schema rejection (check field types match the schema exactly, e.g. whole numbers not decimals): {e}")

            except RateLimitError as e:
                # Only reaches here if EVERY configured key (see _load_api_keys)
                # is also rate-limited — _call_api already tried every fallback.
                self.logger.error(f"All configured API keys are rate-limited (attempt {attempt + 1}): {e}")
                if attempt == MAX_RETRIES:
                    return _return_best_effort_or_error("rate_limit_exceeded", str(e))

            except Exception as e:
                self.logger.error(f"Unexpected error (attempt {attempt + 1}): {e}")
                if attempt == MAX_RETRIES:
                    return _return_best_effort_or_error("api_error", str(e))

    @staticmethod
    def _inline_schema(schema: dict) -> dict:
        """Inline $defs/$ref so the schema is flat — required by Groq's strict json_schema mode."""
        defs = schema.get("$defs", {})

        def resolve(obj):
            if isinstance(obj, dict):
                if "$ref" in obj:
                    ref_name = obj["$ref"].split("/")[-1]
                    return resolve(dict(defs[ref_name]))
                result = {}
                for k, v in obj.items():
                    if k in ("$defs", "title", "minItems", "maxItems"):
                        continue
                    result[k] = resolve(v)
                if result.get("type") == "object" and "additionalProperties" not in result:
                    result["additionalProperties"] = False
                if result.get("type") == "object" and "properties" in result:
                    all_props = list(result["properties"].keys())
                    existing = result.get("required", [])
                    result["required"] = list(dict.fromkeys(existing + all_props))
                return result
            if isinstance(obj, list):
                return [resolve(item) for item in obj]
            return obj

        return resolve(schema)

    def _call_api(self, user_message: str, feedback: str | None = None) -> str:
        schema = self._inline_schema(self.get_schema().model_json_schema())
        messages: list[dict] = [
            {"role": "system", "content": self.get_prompt()},
            {"role": "user", "content": user_message},
        ]
        if feedback:
            messages.append({"role": "user", "content": feedback})

        # Rate limits are an infrastructure problem, not a content problem —
        # swap to the next available key and retry the SAME call rather than
        # burning a quality-retry attempt or failing outright. Only raises
        # once every configured key has hit its limit.
        while True:
            try:
                response = self.client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {"name": self.AGENT_NAME.replace("-", "_"), "schema": schema, "strict": True},
                    },
                )
                raw = response.choices[0].message.content
                self.logger.debug(f"Raw response preview: {raw[:300]}")
                return raw
            except RateLimitError:
                if not self._switch_to_next_key():
                    raise

    def _parse(self, raw: str) -> BaseModel:
        try:
            decoded = json.loads(raw)
            if isinstance(decoded, list) and len(decoded) == 1:
                self.logger.warning("Model returned array instead of object — unwrapping.")
                raw = json.dumps(decoded[0])
        except Exception:
            pass
        return self.get_schema().model_validate_json(raw)

    def _validate_quality(self, parsed: BaseModel) -> None:
        """Override in subclass: call this agent's validators.validate(parsed)."""
        pass

    def get_schema(self) -> type[BaseModel]:
        raise NotImplementedError

    def get_prompt(self) -> str:
        raise NotImplementedError
