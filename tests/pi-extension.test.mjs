import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const script = resolve("notion-log-work/scripts/tasklog.py");

test("pi extension requests one recording continuation and preserves manual recovery", async () => {
  const root = mkdtempSync(join(tmpdir(), "tasklog-pi-"));
  try {
    const git = (...args) => execFileSync("git", ["-C", root, ...args], { stdio: "pipe" });
    git("init", "-q");
    git("config", "user.email", "test@example.invalid");
    git("config", "user.name", "Tasklog Test");
    writeFileSync(join(root, ".gitignore"), ".tasklog/\n.tasklog.json\n.pi/\n");
    writeFileSync(join(root, "app.txt"), "initial");
    git("add", ".");
    git("commit", "-qm", "initial");
    writeFileSync(join(root, ".tasklog.json"), JSON.stringify({ auto_record: { enabled: true } }));
    execFileSync("python3", [script, "--root", root, "install", "--agent", "pi"]);
    const source = readFileSync(join(root, ".pi/extensions/tasklog.js"), "utf8");
    const extension = await import(`data:text/javascript;base64,${Buffer.from(source).toString("base64")}`);
    const handlers = new Map();
    extension.default({ on: (name, callback) => handlers.set(name, callback) });
    const notifications = [];
    const ctx = { cwd: root, sessionManager: { getSessionId: () => "test-pi" },
      ui: { notify: (...args) => notifications.push(args) } };
    const event = { entries: [] };
    const stop = handlers.get("agent_before_settle");
    assert.equal(await stop(event, ctx), undefined);
    writeFileSync(join(root, "app.txt"), "changed");
    const request = await stop(event, ctx);
    assert.equal(request.continue, true);
    assert.match(request.entries[0].content, /\[tasklog-auto\]/);
    assert.equal(await stop(event, ctx), undefined);
    assert.equal(await stop(event, ctx), undefined);
    await handlers.get("session_shutdown")({}, ctx);
    const pending = execFileSync("python3", [script, "--root", root, "pending"], { encoding: "utf8" });
    assert.equal(JSON.parse(pending).status, "pending");
    writeFileSync(join(root, ".tasklog.json"), "invalid");
    assert.equal(await stop(event, ctx), undefined);
    assert.equal(notifications.length, 1);
    assert.match(notifications[0][0], /manually/);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
