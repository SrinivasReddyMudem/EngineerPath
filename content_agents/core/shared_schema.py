"""Schema pieces shared across every content agent's output schema."""

from pydantic import BaseModel, Field
from typing import Literal


class SelfEvaluationLine(BaseModel):
    item: str = Field(description="The specific quality rule being checked, e.g. 'analogy has why_it_fits'")
    result: Literal["PASS", "FAIL"]
    evidence: str = Field(description="Quote or specific detail proving the result — never left empty on a PASS")
