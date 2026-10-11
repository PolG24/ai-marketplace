"""Strict JSON decoding and structural/pilot-policy checks; no network or execution."""

import json
import re
from dataclasses import dataclass

from pydantic import ValidationError

from . import policy
from .models import Manifest


@dataclass(frozen=True)
class Issue:
    path: str
    code: str
    message: str


class InputError(ValueError):
    def __init__(self, issue):
        super().__init__(issue.message)
        self.issue = issue


class _ObjectPairs(list):
    """Keep object pairs until we can report duplicate keys at their full path."""


def _path(parent, key):
    return f"{parent}[{json.dumps(key)}]"


def parse_manifest(text):
    def reject_constant(_value):
        raise ValueError("Nonstandard JSON constant")

    try:
        raw = json.loads(text, object_pairs_hook=_ObjectPairs,
                         parse_constant=reject_constant)
    except (ValueError, RecursionError) as exc:
        location = ""
        if isinstance(exc, json.JSONDecodeError):
            location = f" (line {exc.lineno}, column {exc.colno})"
        raise InputError(Issue("$", "malformed_json", "Invalid JSON" + location)) from exc

    def unpack(value, path):
        if isinstance(value, _ObjectPairs):
            result = {}
            for key, child in value:
                child_path = _path(path, key)
                if key in result:
                    raise InputError(Issue(child_path, "duplicate_key", "Duplicate JSON key"))
                result[key] = unpack(child, child_path)
            return result
        if isinstance(value, list):
            return [unpack(child, f"{path}[{i}]") for i, child in enumerate(value)]
        return value

    try:
        return unpack(raw, "$")
    except RecursionError as exc:
        raise InputError(Issue("$", "malformed_json", "JSON nesting is too deep")) from exc


_FILENAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


def _structural_issue(error):
    """Keep CLI codes stable and omit rejected values from Pydantic errors."""
    path = "$"
    for part in error["loc"]:
        path = f"{path}[{part}]" if isinstance(part, int) else _path(path, part)
    code = error["type"]
    if code == "missing":
        code, message = "required", "Required field is missing"
    elif code == "extra_forbidden":
        code, message = "unknown_field", "Field is not allowed"
    elif code in {"model_type", "string_type", "list_type"}:
        expected = {"model_type": "an object", "string_type": "a string", "list_type": "an array"}
        message, code = f"Expected {expected[code]}", "wrong_type"
    elif code == "too_short":
        code, message = "empty_scope", "Declare at least one explicit resource scope"
    elif code == "string_pattern_mismatch":
        formats = {
            "id": ("invalid_id", "Use a lowercase ID such as 'jira-test-plan'"),
            "version": ("invalid_version", "Use an explicit semantic version such as '1.0.0'"),
            "sha256": ("invalid_digest", "Expected 64 hexadecimal SHA-256 characters"),
        }
        code, message = formats[error["loc"][-1]]
    else:
        # Custom validators use fixed messages; never stringify the full exception.
        message = error["msg"]
    return Issue(path, code, message)


def validate_manifest(value):
    """Check structure first, then trusted policy; return actionable field issues."""
    try:
        manifest = Manifest.model_validate(value)
    except ValidationError as exc:
        return [_structural_issue(error) for error in
                exc.errors(include_input=False, include_context=False, include_url=False)]
    return _check_policy(manifest)


def _check_policy(manifest: Manifest):
    """Pydantic has checked types and formats, so only pilot rules remain here."""
    issues = []

    def fail(path, code, message):
        issues.append(Issue(path, code, message))

    if manifest.schema_version != policy.SCHEMA_VERSION:
        fail('$["schema_version"]', "unsupported_schema", "Supported schema_version is '1'")

    expected = policy.EXECUTION_PROFILES.get(manifest.kind)
    if expected is None:
        fail('$["kind"]', "unsupported_kind", "Use agent, skill, mcp_server, or evaluation_pack")
    elif manifest.execution.profile != expected:
        fail('$["execution"]["profile"]', "execution_profile", f"This kind requires '{expected}'")

    # Exact prefix plus one plain filename rejects alternate hosts, credentials,
    # queries, fragments, encoded paths, traversal, and mutable release aliases.
    prefix = f"{policy.ARTIFACT_BASE}{manifest.id}/{manifest.version}/"
    uri = manifest.artifact.uri
    if not uri.startswith(prefix) or not _FILENAME.fullmatch(uri[len(prefix):]):
        fail('$["artifact"]["uri"]', "artifact_location",
             "Use the approved Artifactory base with /<id>/<version>/<filename>")

    for i, permission in enumerate(manifest.permissions):
        path = f'$["permissions"][{i}]'
        scopes = policy.CAPABILITY_SCOPES.get(permission.capability)
        if scopes is None:
            fail(_path(path, "capability"), "unsupported_capability", "Only pilot read-only capabilities are allowed")
        for j, resource in enumerate(permission.resources):
            if "*" in resource or (scopes is not None and resource not in scopes):
                fail(f'{_path(path, "resources")}[{j}]', "resource_scope",
                     "Use an explicitly configured scope for this capability")

    classification = manifest.data.classification
    if classification not in policy.CLASSIFICATIONS:
        fail('$["data"]["classification"]', "data_classification", "Pilot permits only public or internal data")
    route = manifest.data.model_route
    if route is not None:
        supported = policy.MODEL_ROUTES.get(route)
        if supported is None:
            fail('$["data"]["model_route"]', "model_route", "Use an approved model-route alias or null for no model use")
        elif classification in policy.CLASSIFICATIONS and classification not in supported:
            fail('$["data"]["model_route"]', "model_data_mismatch", "Model route does not permit the declared data classification")

    for i, reference in enumerate(manifest.secret_refs):
        if reference not in policy.SECRET_REFS:
            fail(f'$["secret_refs"][{i}]', "secret_reference",
                 "Use a configured logical credential reference; never embed a secret value")

    return issues
