import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "notion-log-work/scripts/tasklog.py"
spec = importlib.util.spec_from_file_location("tasklog", SCRIPT)
tasklog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tasklog)


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Tasklog Test")
        (self.root / ".gitignore").write_text(".tasklog/\n.tasklog.json\n")
        (self.root / "app.txt").write_text("original\n")
        self.git("add", ".")
        self.git("commit", "-qm", "initial")
        tasklog.save_json(self.root / ".tasklog.json", {"project": "test", "auto_record": {"enabled": True}})

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, check=True)

    def cli(self, *args, payload=None, check=True):
        return subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root), *args],
                              input=json.dumps(payload) if payload is not None else None,
                              capture_output=True, text=True, check=check)

    def changed(self):
        (self.root / "app.txt").write_text("changed\n")

    def test_disabled_and_clean_projects_do_not_record(self):
        self.assertIsNone(tasklog.checkpoint(self.root, "codex", "session"))
        tasklog.save_json(self.root / ".tasklog.json", {})
        self.changed()
        self.assertIsNone(tasklog.checkpoint(self.root, "codex", "session"))
        self.assertFalse((self.root / ".tasklog").exists() and list((self.root / ".tasklog").glob("*.json")))

    def test_checkpoint_dedup_ack_and_new_changes(self):
        self.changed()
        record = tasklog.checkpoint(self.root, "codex", "session", request=True)
        self.assertIsNone(tasklog.checkpoint(self.root, "codex", "session", request=True))
        self.cli("ack", record["id"], "--page-url", "https://www.notion.so/test-page")
        self.assertEqual(self.cli("pending").stdout, "")
        (self.root / "app.txt").write_text("another change\n")
        updated = tasklog.checkpoint(self.root, "codex", "session", request=True)
        self.assertEqual(updated["id"], record["id"])
        self.assertEqual(updated["page_url"], "https://www.notion.so/test-page")
        self.assertEqual(updated["status"], "pending")

    def test_queue_changes_do_not_trigger_new_record(self):
        self.changed()
        record = tasklog.checkpoint(self.root, "pi", "s", request=True)
        path = self.root / ".tasklog" / f"{record['id']}.json"
        value = tasklog.read_json(path)
        value["draft"] = "Why: investigated locally"
        tasklog.save_json(path, value)
        self.assertIsNone(tasklog.checkpoint(self.root, "pi", "s", request=True))

    def test_untracked_content_changes_are_detected_without_storing_content(self):
        file = self.root / "new.txt"
        file.write_text("sensitive-value-123")
        one = tasklog.checkpoint(self.root, "pi", "s", request=True)
        file.write_text("different-sensitive-value")
        two = tasklog.checkpoint(self.root, "pi", "s", request=True)
        self.assertNotEqual(one["fingerprint"], two["fingerprint"])
        self.assertNotIn("sensitive-value", json.dumps(two))

    def test_stop_protocols_and_recursion_guards(self):
        self.changed()
        for agent in ("codex", "claude-code", "kiro", "agy", "pi"):
            with self.subTest(agent=agent):
                payload = {"cwd": str(self.root), "session_id": agent, "hook_event_name": "Stop"}
                text = self.cli("hook", "--agent", agent, payload=payload).stdout
                if agent in ("codex", "claude-code", "kiro", "agy"):
                    output = json.loads(text)
                    self.assertEqual(output["decision"], "continue" if agent == "agy" else "block")
                    self.assertIn("[tasklog-auto]", output["reason"])
                else:
                    self.assertIn("[tasklog-auto]", text)
                self.assertEqual(self.cli("hook", "--agent", agent, payload=payload).stdout, "")
                payload.update(session_id="other", stop_hook_active=True)
                self.assertEqual(self.cli("hook", "--agent", agent, payload=payload).stdout, "")

    def test_agy_payload_and_background_guard(self):
        self.changed()
        payload = {"workspacePaths": [str(self.root)], "conversationId": "agy-session", "fullyIdle": False}
        self.assertEqual(self.cli("hook", "--agent", "agy", payload=payload).stdout, "")
        payload["fullyIdle"] = True
        self.assertEqual(json.loads(self.cli("hook", "--agent", "agy", payload=payload).stdout)["decision"], "continue")

    def test_shutdown_is_local_only_and_can_be_processed_later(self):
        self.changed()
        payload = {"cwd": str(self.root), "session_id": "s", "hook_event_name": "SessionEnd"}
        self.assertEqual(self.cli("hook", "--agent", "codex", payload=payload).stdout, "")
        self.assertEqual(json.loads(self.cli("pending").stdout)["status"], "pending")
        payload["hook_event_name"] = "Stop"
        self.assertIn("[tasklog-auto]", self.cli("hook", "--agent", "codex", payload=payload).stdout)

    def test_manual_fallback_without_git_or_mcp(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            draft = "### Why\nVerified manual draft"
            record = tasklog.checkpoint(root, "manual", "offline", force=True, note=draft)
            self.assertEqual(record["draft"], draft)
            self.assertEqual(record["status"], "pending")

    def test_install_preserves_existing_hooks_and_is_idempotent(self):
        target = self.root / ".claude/settings.json"
        original = {"permissions": {"allow": []}, "hooks": {"Stop": [{"hooks": [{"type": "command", "command": "echo existing"}]}]}}
        tasklog.save_json(target, original)
        for agent in tasklog.AGENTS:
            self.cli("install", "--agent", agent)
            before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file() and ".git" not in p.parts}
            self.cli("install", "--agent", agent)
            for p, data in before.items():
                self.assertEqual(p.read_bytes(), data)
        value = tasklog.read_json(target)
        self.assertEqual(value["permissions"], original["permissions"])
        self.assertEqual(len(value["hooks"]["Stop"]), 2)
        self.assertEqual(tasklog.read_json(target.with_name(target.name + ".pre-tasklog")), original)
        self.assertTrue(tasklog.read_json(self.root / ".tasklog.json")["auto_record"]["enabled"])

    def test_invalid_config_and_missing_session_leave_no_record(self):
        self.changed()
        result = self.cli("hook", "--agent", "pi", payload={"cwd": str(self.root)}, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("manual", result.stderr)
        (self.root / ".tasklog.json").write_text("invalid")
        self.assertNotEqual(self.cli("doctor", check=False).returncode, 0)

    def test_installed_kiro_command_consumes_real_session_payload(self):
        self.changed()
        self.cli("install", "--agent", "kiro")
        config = tasklog.read_json(self.root / ".kiro/hooks/tasklog.json")
        command = config["hooks"][0]["action"]["command"]
        payload = {"cwd": str(self.root), "session_id": "session-from-kiro", "hook_event_name": "Stop"}
        result = subprocess.run(command, shell=True, cwd=self.root, input=json.dumps(payload),
                                capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)["decision"], "block")
        self.assertTrue(json.loads(self.cli("pending").stdout)["requested_fingerprint"])


if __name__ == "__main__":
    unittest.main()
