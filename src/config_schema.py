from enum import Enum
from pathlib import Path

import yaml
from pydantic import BaseModel, SecretStr


class Environment(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    STAGING = "staging"


class Settings(BaseModel):
    environment: Environment = Environment.DEVELOPMENT
    bot_token: SecretStr
    api_url: str
    redis_url: SecretStr | None = None

    @classmethod
    def from_yaml(cls, path: Path) -> "Settings":
        with open(path, "r", encoding="utf-8") as f:
            yaml_config: dict = yaml.safe_load(f)
            yaml_config.pop("$schema", None)

        return cls.model_validate(yaml_config)

    @classmethod
    def save_schema(cls, path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            schema = {"$schema": "http://json-schema.org/draft-07/schema#", **cls.model_json_schema()}
            schema["properties"]["$schema"] = {
                "description": "Path to the schema file",
                "title": "Schema",
                "type": "string",
            }
            yaml.dump(schema, f, sort_keys=False)
