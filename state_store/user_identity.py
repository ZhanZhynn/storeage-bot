from pydantic import BaseModel, ConfigDict


class UserIdentity(BaseModel):
    """User identity and preference state."""

    user_id: str = ""
    provider: str = ""
    model: str = ""

    model_config = ConfigDict(extra="forbid")