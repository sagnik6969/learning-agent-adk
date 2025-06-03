from pydantic import BaseModel,Field

class LearningCheckpoint(BaseModel):
    """Structure for a single checkpoint"""
    description: str = Field(..., description="Main checkpoint description")
    criteria: list[str] = Field(..., description="List of success criteria")
    verification: str = Field(..., description="How to verify this checkpoint")

class Checkpoints(BaseModel):
    """Main checkpoints container with index tracking"""
    checkpoints: list[LearningCheckpoint] = Field(
        ..., 
        description="List of checkpoints covering foundation, application, and mastery levels"
    )