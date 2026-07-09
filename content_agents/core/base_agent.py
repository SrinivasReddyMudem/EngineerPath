"""
Base agent — Groq-backed, strict JSON schema enforcement, retry-with-feedback.
Ported from the automotive-lifecycle-agents pattern: same reliability model,
applied to content generation instead of technical analysis.
"""

import os
import json
from groq import Groq, BadRequestError
from pydantic import BaseModel, ValidationError
from typing import Literal
from .logger import get_logger

MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"  # confirmed working with Groq's strict json_schema mode on this account
MAX_RETRIES = 3  # bumped from 2: richer multi-section schemas (e.g. reel-script) have more gates that can each fail per attempt


class AgentError(BaseModel):
    agent: str
    error_type: Literal["api_error", "validation_error", "quality_check_failed"]
    message: str
    raw_response: str | None = None


class QualityCheckError(Exception):
    """Raised by an agent's validators.py when a quality-gate check fails."""
    pass


class BaseAgent:
    AGENT_NAME = "base"

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GROQ_API_KEY not set.\n"
                "Get a free key (no credit card) at console.groq.com\n"
                "Then add it to .env as: GROQ_API_KEY=your-key"
            )
        self.client = Groq(api_key=api_key)
        self.logger = get_logger(self.AGENT_NAME)

    def run(self, user_message: str) -> BaseModel | AgentError:
        """Always returns a Pydantic model or AgentError — never raises."""
        raw = None
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

        for attempt in range(MAX_RETRIES + 1):
            try:
                raw = self._call_api(user_message, feedback=_feedback())
                parsed = self._parse(raw)
                self._validate_quality(parsed)
                return parsed

            except ValidationError as e:
                self.logger.error(f"Schema validation failed (attempt {attempt + 1}): {e}")
                if attempt == MAX_RETRIES:
                    return AgentError(agent=self.AGENT_NAME, error_type="validation_error", message=str(e), raw_response=raw)
                seen_issues.append(f"Schema validation error: {e}")

            except QualityCheckError as e:
                self.logger.warning(f"Quality gate failed (attempt {attempt + 1}): {e}")
                if attempt == MAX_RETRIES:
                    return AgentError(agent=self.AGENT_NAME, error_type="quality_check_failed", message=str(e))
                seen_issues.append(str(e))

            except BadRequestError as e:
                self.logger.warning(f"API schema rejection (attempt {attempt + 1}): {e}")
                if attempt == MAX_RETRIES:
                    return AgentError(agent=self.AGENT_NAME, error_type="api_error", message=str(e))
                seen_issues.append(f"API schema rejection (check field types match the schema exactly, e.g. whole numbers not decimals): {e}")

            except Exception as e:
                self.logger.error(f"Unexpected error (attempt {attempt + 1}): {e}")
                if attempt == MAX_RETRIES:
                    return AgentError(agent=self.AGENT_NAME, error_type="api_error", message=str(e))

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
