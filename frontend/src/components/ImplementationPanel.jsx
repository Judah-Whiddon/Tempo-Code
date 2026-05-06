import { createSignal, createMemo, For, Show } from "solid-js";
import { submitAnswer, gradeSteps } from "../api";

const DEFAULT_STARTER = "def solve():\n    pass\n";

function ImplementationPanel(props) {
  const phase = props.phase ?? "IMPLEMENTATION";
  const [code, setCode] = createSignal(props.problem.starter_code ?? DEFAULT_STARTER);
  const [verdict, setVerdict] = createSignal(null); // null | "pass" | "fail"
  const [hint, setHint] = createSignal("");
  const [submitting, setSubmitting] = createSignal(false);
  const [error, setError] = createSignal("");
  // Set of step labels the AI has classified as completed by the current code.
  // Additive — once a step greens, it stays green for the session.
  const [greenedSteps, setGreenedSteps] = createSignal(new Set());

  const locked = createMemo(() => verdict() === "pass" || submitting());

  function onCodeInput(e) {
    setCode(e.currentTarget.value);
    if (verdict() === "fail") {
      setVerdict(null);
      setHint("");
    }
  }

  async function submit() {
    if (locked()) return;
    setSubmitting(true);
    setError("");

    // Fire AI step detection in parallel with the rule-based test runner.
    // Step detection is best-effort: a 503 or network failure must not block
    // the verdict path, so we swallow its errors.
    const stepsPromise = gradeSteps(props.problem.id, code()).catch(() => null);

    try {
      const [res, stepsRes] = await Promise.all([
        submitAnswer({
          problem_id: props.problem.id,
          phase,
          content: { code: code() },
        }),
        stepsPromise,
      ]);
      const v = res.feedback?.verdict ?? "fail";
      setVerdict(v);
      setHint(res.feedback?.hint ?? "");

      if (stepsRes?.completed_steps?.length) {
        setGreenedSteps((prev) => {
          const next = new Set(prev);
          for (const label of stepsRes.completed_steps) next.add(label);
          return next;
        });
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  const editorClass = createMemo(() => {
    const v = verdict();
    return `code-editor${v === "pass" ? " greened" : ""}${v === "fail" ? " missed" : ""}`;
  });

  return (
    <section class="impl-panel">
      <header class="phase-header">
        <h2>{phase === "DEBUGGING" ? "Fix the code" : "Implementation phase"}</h2>
        <p class="hint">
          {phase === "DEBUGGING"
            ? "Find and fix the bug. Tests will tell you when it's right."
            : "Implement solve(...) so all test cases pass."}
        </p>
      </header>

      <Show when={props.flowOrder?.length}>
        <aside class="flow-summary">
          <h3>Flow steps</h3>
          <ol>
            <For each={props.flowOrder}>
              {(label) => (
                <li class={greenedSteps().has(label) ? "greened" : ""}>
                  {label}
                </li>
              )}
            </For>
          </ol>
        </aside>
      </Show>

      <textarea
        class={editorClass()}
        value={code()}
        onInput={onCodeInput}
        spellcheck={false}
        autocapitalize="off"
        autocomplete="off"
        autocorrect="off"
        disabled={verdict() === "pass"}
        rows={14}
      />

      <div class="actions">
        <button
          type="button"
          class="primary"
          onClick={submit}
          disabled={locked()}
        >
          {verdict() === "pass"
            ? "Greened ✓"
            : submitting()
            ? "Running tests…"
            : "Submit code"}
        </button>
      </div>

      <Show when={verdict() === "pass"}>
        <p class="success">All test cases passed.</p>
      </Show>
      <Show when={verdict() === "fail" && hint()}>
        <p class="feedback-line">{hint()}</p>
      </Show>
      <Show when={error()}>
        <p class="error">{error()}</p>
      </Show>
    </section>
  );
}

export default ImplementationPanel;
