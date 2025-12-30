from pydantic import BaseModel, ConfigDict


class UserPreferenceBase(BaseModel):
    theme: str = "light"


class UserPreferenceCreate(UserPreferenceBase):
    pass


class UserPreferenceUpdate(UserPreferenceBase):
    pass


class UserPreferenceResponse(UserPreferenceBase):
    model_config = ConfigDict(from_attributes=True)
