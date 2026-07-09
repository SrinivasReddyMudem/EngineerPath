"""
The Reel Production Package — the ONLY thing the user should ever need
to see for `purpose="reel"`. Everything that goes into it (hook choice,
analogy, technical accuracy, mistake framing, CTA style, story arc) is
generated and validated internally (content_agents/video/reel_script/)
but never surfaces here as its own labeled section — it's compiled into
plain voice script + scene-by-scene visual script, ready to paste into
an AI voice tool and an AI video tool respectively.
"""

from pydantic import BaseModel, Field
from typing import Literal

PassFail = Literal["PASS", "FAIL"]
Overall = Literal["READY", "NEEDS_IMPROVEMENT"]


class ReelMetadata(BaseModel):
    topic: str
    content_type: str = Field(description="e.g. 'Concept Explanation', 'Comparison', 'Interview Preparation'")
    audience: str
    duration: str = Field(description="e.g. '60 seconds'")
    learning_objective: str
    core_message: str = Field(description="The one thing the viewer should remember")


class VisualScene(BaseModel):
    scene_number: int
    time_range: str
    visual: str
    animation: str
    on_screen_text: str
    purpose: str


class SyncEntry(BaseModel):
    time_range: str
    voice: str
    visual: str


class QualityReport(BaseModel):
    technical_accuracy: PassFail
    teaching_quality: PassFail
    hook_quality: PassFail
    analogy_quality: PassFail
    voice_ready: PassFail
    video_generation_ready: PassFail
    overall: Overall
    notes: list[str] = Field(default_factory=list, description="Any unresolved issues from generation, if the best-effort fallback was used")


class ProductionPackage(BaseModel):
    reel_metadata: ReelMetadata
    voice_script: str = Field(description="Plain spoken text, no markdown, no bullet points, ready to paste into an AI voice tool")
    visual_script: list[VisualScene]
    sync_timeline: list[SyncEntry]
    quality_report: QualityReport
