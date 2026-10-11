# ai-marketplace
Centralizing AI tools across teams

## Design

[Four-page design document (PDF)](docs/design.pdf) · [Editable source](docs/design.md) · [HTML version](docs/design.html)

The proposal covers team contributions, managed execution, manifest policy, release approval and revocation, and engineering value. Its working-piece scope is a small local manifest validator; production integrations remain architectural proposals.

To regenerate the HTML, run `python3 scripts/render_design.py`. Print `docs/design.html` to PDF with A4 paper, 100% scale, and browser headers/footers disabled. Page layout is defined in the document's print stylesheet.

## Try the manifest validator

Requires Python 3.10+ and Pydantic v2. From the repository root, create a virtual environment and install the dependency:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

If you use `uv`, the equivalent setup is:

```sh
uv venv .venv --python python3
uv pip install --python .venv/bin/python -r requirements.txt
source .venv/bin/activate
```

On Debian/Ubuntu, if `python3 -m venv` reports that `ensurepip` is unavailable, install the OS package `python3-venv` first or use the `uv` setup above. Dependency installation needs package-registry access; validation itself needs no network access or credentials.

With the environment activated, run:

```sh
python3 -m manifest_validator examples/jira-agent.json
python3 -m manifest_validator examples/security-skill.json
python3 -m manifest_validator examples/evaluation-pack.json
python3 -m manifest_validator examples/unsafe-jira-agent.json
```

The first three examples pass. The unsafe example requests wildcard Jira access and is rejected:

```text
REJECTED
$["permissions"][0]["resources"][0] [resource_scope]: Use an explicitly configured scope for this capability
```

Validate your own file with `python3 -m manifest_validator path/to/manifest.json`. Exit codes are **0** for a static validation pass, **1** for structural/policy rejection, and **2** for input failure (including malformed/duplicate JSON or an unreadable file). Errors include JSON field paths and stable codes on stderr, so Jenkins can fail a gate on any nonzero exit. Success explicitly says production approval is still required.

### Manifest and pilot policy

The examples show the complete contract: all fields are required, including empty `permissions` and `secret_refs` arrays when unused. Unknown fields are rejected at every object level, including embedded credential or approval fields. Schema version is the string `"1"`; release versions use semantic versioning such as `"1.0.0"`.

Validation has three steps: strict JSON parsing rejects malformed input and duplicate keys; [Pydantic models](manifest_validator/models.py) check required fields, types, and formats without coercion; [pilot checks](manifest_validator/validator.py) apply the trusted allowlists and cross-field rules to the typed manifest. Structural errors are reported first; policy checks run once the structure passes. CLI errors omit rejected values and preserve field paths and error codes.

Trusted configuration lives separately in [manifest_validator/policy.py](manifest_validator/policy.py). Publishers supply only a manifest; they cannot override policy through its fields or CLI flags. The illustrative policy is:

| Declaration | Permitted values |
| --- | --- |
| Kind → managed profile | `agent` → `managed-agent`; `skill` → `managed-skill`; `mcp_server` → `managed-mcp`; `evaluation_pack` → `managed-evaluation` |
| Artifact URI | `https://artifactory.example.internal/ai-assets/<id>/<version>/<filename>`, plus a 64-character hexadecimal SHA-256 digest |
| `jira.issues.read` resources | `project:ENG`, `project:FW` |
| `security.findings.read` resources | `project:platform`, `project:firmware` |
| Data classification | `public`, `internal` |
| Model route | `enterprise-default` permits public/internal; `enterprise-public` permits public only; JSON `null` declares no model use |
| Secret references | `jira-reader`, `security-reader` (logical names only) |

Every permission needs a nonempty list of explicitly configured resources. Wildcards, write capabilities, arbitrary model endpoints, and unrecognized credential references fail. Lab control and simulation submission capabilities remain outside the pilot, even for an MCP manifest. Empty `permissions` means no resource access.

The Artifactory host, contacts, and digests in the examples are placeholders. The validator never fetches artifacts, follows URLs, resolves credentials, or executes submissions. It checks the declared versioned location and digest **format**, not actual immutability or artifact contents. A pass does not verify truthful declarations, corporate ownership, user access, scans, evaluations, or hidden secrets inside otherwise allowed strings. Promotion and runtime checks in the design still supply those controls.

### Run the tests

```sh
python3 -m unittest discover -s tests -v
```

Tests cover all valid examples, required fields and types, unknown fields, malformed/duplicate JSON, wildcard and unsupported access, execution profiles, artifact locations/digests, prohibited data/model combinations, embedded credentials, and CLI exit codes.
