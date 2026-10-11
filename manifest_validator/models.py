"""The manifest's structure and formats; access policy lives in policy.py."""

from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field
from pydantic_core import PydanticCustomError


def nonblank(value: str) -> str:
    if not value.strip() or value != value.strip() or any(ord(c) < 32 for c in value):
        raise PydanticCustomError(
            "invalid_value",
            "Use nonblank text without surrounding whitespace or controls",
        )
    return value


NonblankString = Annotated[str, AfterValidator(nonblank)]
AssetId = Annotated[NonblankString, Field(pattern=r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")]
ReleaseVersion = Annotated[
    NonblankString,
    Field(pattern=(
        r"^(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
        r"(?:-(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
        r"(?:\.(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*)?"
        r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
    )),
]
Sha256 = Annotated[NonblankString, Field(pattern=r"^[0-9a-fA-F]{64}$")]


class StrictModel(BaseModel):
    # Inherited by every nested model: no coercion, extra fields, or input echoing.
    model_config = ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True)


class Owner(StrictModel):
    team: NonblankString
    contact: NonblankString


class Artifact(StrictModel):
    uri: NonblankString
    sha256: Sha256


class Execution(StrictModel):
    profile: NonblankString


class Permission(StrictModel):
    capability: NonblankString
    resources: Annotated[list[NonblankString], Field(min_length=1)]


class Data(StrictModel):
    classification: NonblankString
    model_route: NonblankString | None  # Required; null explicitly means no model use.


class Manifest(StrictModel):
    schema_version: NonblankString
    id: AssetId
    kind: NonblankString
    version: ReleaseVersion
    owner: Owner
    artifact: Artifact
    execution: Execution
    permissions: list[Permission]
    data: Data
    secret_refs: list[NonblankString]
