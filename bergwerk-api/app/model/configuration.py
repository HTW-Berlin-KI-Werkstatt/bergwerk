from pydantic import BaseModel

class ConfigItem(BaseModel):
    key: str
    value: str | list