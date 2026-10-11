"""Trusted demo policy, maintained by the platform rather than publishers.

These names are illustrative local configuration, not live integrations.
"""

SCHEMA_VERSION = "1"
EXECUTION_PROFILES = {
    "agent": "managed-agent",
    "skill": "managed-skill",
    "mcp_server": "managed-mcp",
    "evaluation_pack": "managed-evaluation",
}
ARTIFACT_BASE = "https://artifactory.example.internal/ai-assets/"
CAPABILITY_SCOPES = {
    "jira.issues.read": frozenset({"project:ENG", "project:FW"}),
    "security.findings.read": frozenset({"project:platform", "project:firmware"}),
}
CLASSIFICATIONS = frozenset({"public", "internal"})
MODEL_ROUTES = {
    "enterprise-default": frozenset({"public", "internal"}),
    "enterprise-public": frozenset({"public"}),
}
SECRET_REFS = frozenset({"jira-reader", "security-reader"})
