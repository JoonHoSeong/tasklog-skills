import { spawn } from "node:child_process";

const python = "__TASKLOG_PYTHON__";
const script = "__TASKLOG_SCRIPT__";

export default function tasklog(pi) {
  let recording = false;

  function run(ctx, event) {
    return new Promise((resolve, reject) => {
      const child = spawn(python, [script, "--root", ctx.cwd, "hook", "--agent", "pi"],
        { stdio: ["pipe", "pipe", "pipe"] });
      let output = "";
      child.stdout.on("data", chunk => { output += chunk; });
      child.stderr.resume();
      child.on("error", reject);
      child.stdin.on("error", () => {});
      child.on("close", code => code === 0 ? resolve(output.trim()) : reject(new Error("tasklog hook failed")));
      child.stdin.end(JSON.stringify({ cwd: ctx.cwd, session_id: ctx.sessionManager.getSessionId(), hook_event_name: event }));
    });
  }

  pi.on("session_start", () => { recording = false; });
  pi.on("agent_before_settle", async (event, ctx) => {
    if (recording) {
      recording = false;
      return;
    }
    try {
      const prompt = await run(ctx, "Stop");
      if (prompt) {
        recording = true;
        return {
          entries: [...event.entries, {
            type: "custom_message", customType: "tasklog-auto", content: prompt, display: true,
          }],
          continue: true,
        };
      }
    } catch {
      recording = false;
      ctx.ui.notify("Tasklog: automatic recording unavailable; use notion-log-work manually.", "warning");
    }
  });
  pi.on("session_shutdown", async (_event, ctx) => {
    try { await run(ctx, "session_shutdown"); }
    catch { /* Shutdown must not prevent Pi from closing. */ }
  });
}
