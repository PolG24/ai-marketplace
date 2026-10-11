import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from manifest_validator.validator import InputError, parse_manifest, validate_manifest


ROOT = Path(__file__).resolve().parents[1]


def load_example(name="jira-agent"):
    return parse_manifest((ROOT / "examples" / f"{name}.json").read_text())


class ValidatorTests(unittest.TestCase):
    def assert_issue(self, manifest, code, path=None):
        issues = validate_manifest(manifest)
        self.assertTrue(any(issue.code == code and (path is None or issue.path == path)
                            for issue in issues), issues)

    def test_valid_examples(self):
        for name in ("jira-agent", "security-skill", "evaluation-pack"):
            with self.subTest(name=name):
                self.assertEqual(validate_manifest(load_example(name)), [])

    def test_every_core_field_is_required(self):
        base = load_example()
        for key in base:
            with self.subTest(key=key):
                manifest = copy.deepcopy(base)
                del manifest[key]
                self.assert_issue(manifest, "required", f'$["{key}"]')

    def test_nested_fields_are_required(self):
        for parent in ("owner", "artifact", "execution", "data"):
            for key in load_example()[parent]:
                with self.subTest(parent=parent, key=key):
                    manifest = load_example()
                    del manifest[parent][key]
                    self.assert_issue(manifest, "required", f'$["{parent}"]["{key}"]')
        for key in ("capability", "resources"):
            manifest = load_example()
            del manifest["permissions"][0][key]
            self.assert_issue(manifest, "required", f'$["permissions"][0]["{key}"]')

    def test_wrong_root_and_core_types(self):
        for value in (None, True, 1, "manifest", []):
            with self.subTest(root=value):
                self.assert_issue(value, "wrong_type", "$")
        for key in load_example():
            for value in (None, True, 42):
                with self.subTest(key=key, value=value):
                    manifest = load_example()
                    manifest[key] = value
                    self.assert_issue(manifest, "wrong_type", f'$["{key}"]')

    def test_wrong_nested_types(self):
        for parent in ("owner", "artifact", "execution", "data"):
            for key in load_example()[parent]:
                manifest = load_example()
                manifest[parent][key] = []
                self.assert_issue(manifest, "wrong_type", f'$["{parent}"]["{key}"]')
        for permission in (None, "read", []):
            manifest = load_example()
            manifest["permissions"] = [permission]
            self.assert_issue(manifest, "wrong_type", '$["permissions"][0]')
        for key in ("capability", "resources"):
            manifest = load_example()
            manifest["permissions"][0][key] = 42
            self.assert_issue(manifest, "wrong_type", f'$["permissions"][0]["{key}"]')
        manifest = load_example()
        manifest["permissions"][0]["resources"] = [False]
        self.assert_issue(manifest, "wrong_type", '$["permissions"][0]["resources"][0]')
        manifest["secret_refs"] = [{"token": "embedded"}]
        self.assert_issue(manifest, "wrong_type", '$["secret_refs"][0]')

    def test_identifiers_schema_kind_and_version(self):
        cases = [("schema_version", "2", "unsupported_schema"),
                 ("id", "Bad ID", "invalid_id"), ("kind", "plugin", "unsupported_kind"),
                 ("version", "latest", "invalid_version"), ("version", "1.0", "invalid_version"),
                 ("version", "01.0.0", "invalid_version"),
                 ("version", "1.0.0-01", "invalid_version"),
                 ("id", " ", "invalid_value")]
        for key, value, code in cases:
            with self.subTest(key=key, value=value):
                manifest = load_example()
                manifest[key] = value
                self.assert_issue(manifest, code, f'$["{key}"]')

    def test_explicit_prerelease_version(self):
        manifest = load_example()
        manifest["version"] = "1.2.0-rc.1+build.7"
        manifest["artifact"]["uri"] = manifest["artifact"]["uri"].replace("1.0.0", manifest["version"])
        self.assertEqual(validate_manifest(manifest), [])

    def test_nonblank_owner(self):
        for key in ("team", "contact"):
            for value in ("", " ", " team ", "team\nsecret"):
                manifest = load_example()
                manifest["owner"][key] = value
                self.assert_issue(manifest, "invalid_value", f'$["owner"]["{key}"]')

    def test_unknown_fields_and_embedded_credentials(self):
        for parent in (None, "owner", "artifact", "execution", "data", "permission"):
            with self.subTest(parent=parent):
                manifest = load_example()
                target = (manifest if parent is None else manifest["permissions"][0]
                          if parent == "permission" else manifest[parent])
                target["api_key"] = "should-never-be-accepted"
                self.assert_issue(manifest, "unknown_field")
        for key in ("approved", "secret_values", "model_endpoint"):
            manifest = load_example()
            manifest[key] = True
            self.assert_issue(manifest, "unknown_field", f'$["{key}"]')

    def test_artifact_references(self):
        base = load_example()["artifact"]["uri"]
        uris = ["file:///tmp/asset", base.replace("https:", "http:"),
                base.replace("example.internal", "example.internal.evil"),
                base.replace("https://", "https://user:password@"),
                base.replace("/1.0.0/", "/latest/"),
                base.replace("jira-test-plan", "another-asset"),
                base.replace("agent.tar.gz", "../agent.tar.gz"),
                base.replace("agent.tar.gz", "%2e%2e/agent.tar.gz"),
                base.replace("agent.tar.gz", "subdir/agent.tar.gz"),
                base.replace("agent.tar.gz", "..\\agent.tar.gz"),
                base + "?token=secret", base + "#fragment", base.rsplit("/", 1)[0] + "/"]
        for uri in uris:
            with self.subTest(uri=uri):
                manifest = load_example()
                manifest["artifact"]["uri"] = uri
                self.assert_issue(manifest, "artifact_location", '$["artifact"]["uri"]')
        for digest in ("abc", "g" * 64, "sha256:" + "a" * 64):
            manifest = load_example()
            manifest["artifact"]["sha256"] = digest
            self.assert_issue(manifest, "invalid_digest")

    def test_managed_execution(self):
        for profile in ("local", "managed-skill", "https://runner.example"):
            manifest = load_example()
            manifest["execution"]["profile"] = profile
            self.assert_issue(manifest, "execution_profile")

    def test_broad_or_unsupported_access(self):
        for resource in ("*", "project:*", "project:OTHER"):
            manifest = load_example()
            manifest["permissions"][0]["resources"] = [resource]
            self.assert_issue(manifest, "resource_scope")
        manifest = load_example()
        manifest["permissions"][0]["resources"] = []
        self.assert_issue(manifest, "empty_scope")
        for capability in ("*", "jira.issues.write", "lab.instrument.control", "simulation.jobs.submit"):
            manifest = load_example()
            manifest["permissions"][0]["capability"] = capability
            self.assert_issue(manifest, "unsupported_capability")
        manifest = load_example()
        manifest["permissions"][0]["resources"] = ["project:platform"]
        self.assert_issue(manifest, "resource_scope")

    def test_mcp_kind_is_supported_but_future_permissions_are_rejected(self):
        manifest = load_example()
        manifest["kind"] = "mcp_server"
        manifest["execution"]["profile"] = "managed-mcp"
        self.assertEqual(validate_manifest(manifest), [])
        manifest["permissions"][0]["capability"] = "lab.instrument.control"
        self.assert_issue(manifest, "unsupported_capability")

    def test_data_model_and_secret_policy(self):
        for classification in ("restricted", "unknown", "confidential"):
            manifest = load_example()
            manifest["data"]["classification"] = classification
            self.assert_issue(manifest, "data_classification")
        for route in ("https://models.example/v1", "unregistered"):
            manifest = load_example()
            manifest["data"]["model_route"] = route
            self.assert_issue(manifest, "model_route")
        manifest = load_example()
        manifest["data"]["model_route"] = "enterprise-public"
        self.assert_issue(manifest, "model_data_mismatch")
        manifest["data"]["classification"] = "public"
        self.assertEqual(validate_manifest(manifest), [])
        manifest["data"]["model_route"] = None
        self.assertEqual(validate_manifest(manifest), [])
        for reference in ("vault://arbitrary/path", "raw-password", "*"):
            manifest = load_example()
            manifest["secret_refs"] = [reference]
            self.assert_issue(manifest, "secret_reference")


class JSONTests(unittest.TestCase):
    def test_malformed_json(self):
        for text in ("", "{", '{"id": 1,}', "NaN", "Infinity", "-Infinity", "{} {}"):
            with self.subTest(text=text), self.assertRaises(InputError) as caught:
                parse_manifest(text)
            self.assertEqual(caught.exception.issue.code, "malformed_json")

    def test_duplicate_keys_at_root_in_objects_and_in_arrays(self):
        cases = [('{"id":"safe","id":"unsafe"}', '$["id"]'),
                 ('{"owner":{"team":"a","team":"b"}}', '$["owner"]["team"]'),
                 ('{"permissions":[{"resources":[],"resources":["*"]}]}',
                  '$["permissions"][0]["resources"]')]
        for text, path in cases:
            with self.subTest(path=path), self.assertRaises(InputError) as caught:
                parse_manifest(text)
            self.assertEqual(caught.exception.issue.code, "duplicate_key")
            self.assertEqual(caught.exception.issue.path, path)


class CLITests(unittest.TestCase):
    def run_cli(self, path):
        return subprocess.run([sys.executable, "-m", "manifest_validator", str(path)],
                              cwd=ROOT, capture_output=True, text=True, timeout=10)

    def test_success_and_policy_rejection_exit_codes(self):
        valid = self.run_cli(ROOT / "examples/jira-agent.json")
        self.assertEqual(valid.returncode, 0, valid.stderr)
        self.assertIn("production approval is still required", valid.stdout)
        invalid = self.run_cli(ROOT / "examples/unsafe-jira-agent.json")
        self.assertEqual(invalid.returncode, 1)
        self.assertIn('$["permissions"][0]["resources"][0] [resource_scope]', invalid.stderr)

    def test_input_failures_exit_two_without_tracebacks(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            for content, code in ((b"{", "malformed_json"),
                                  (b'{"id":1,"id":2}', "duplicate_key"),
                                  (b"\xff", "input_error")):
                path.write_bytes(content)
                result = self.run_cli(path)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn(code, result.stderr)
                self.assertNotIn("Traceback", result.stderr)
            missing = self.run_cli(Path(directory) / "missing.json")
            self.assertEqual(missing.returncode, 2)
            self.assertIn("input_error", missing.stderr)

    def test_embedded_credential_values_are_not_echoed(self):
        secret = "sensitive-demo-value!"
        cases = []
        manifest = load_example()
        manifest["token"] = secret
        cases.append((manifest, "unknown_field"))
        manifest = load_example()
        manifest["id"] = secret
        cases.append((manifest, "invalid_id"))
        manifest = load_example()
        manifest["owner"]["contact"] = {"password": secret}
        cases.append((manifest, "wrong_type"))
        for manifest, code in cases:
            with self.subTest(code=code), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "manifest.json"
                path.write_text(json.dumps(manifest))
                result = self.run_cli(path)
            self.assertEqual(result.returncode, 1)
            self.assertIn(code, result.stderr)
            self.assertNotIn(secret, result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
