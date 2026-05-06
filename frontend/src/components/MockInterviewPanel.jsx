import { createSignal, createMemo, Show } from "solid-js";
import { submitAnswer } from "../api";

function MockInterviewPanel(props) {
  const [response, setResponse] = createSignal("");
  const [verdict, setVerdict] = createSignal(null); // null | "pass" | "fail"
  const [explanation, setExplanation] = createSignal("");
  const [submitting, setSubmitting] = createSignal(false);
  const [error, setError] = createSignal("");

  const locked = createMemo(() => verdict() === "pass" || submitting());

  function onResponseInput(e) {
    setResponse(e.currentTarget.value);
    if (verdict() === "fail") {
      setVerdict(null);
      setExplanation("");
    }
  }

  async function submit() {
    if (locked()) return;
    if (!response().trim()) {
      setError("Write your answer before submitting.");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      const res = await submitAnswer({
        problem_id: props.problem.id,
        phase: "MOCK_INTERVIEW",
        content: { response: response() },
      });
      setVerdict(res.feedback?.verdict ?? "fail");
      setExplanation(res.feedback?.ai_response ?? "");
    } catch (e) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section class="mock-panel">
      <header class="phase-header">
        <h2>Mock interview</h2>
        <p class="hint">
          Read the code, explain what it does and why. The AI is the interviewer.
        </p>
      </header>

      <pre class="code-block">{props.problem.starter_code}</pre>

      <textarea
        class="response-area"
        value={response()}
        onInput={onResponseInput}
        placeholder="Walk through the code as if you were on the call…"
        spellcheck={true}
        disabled={verdict() === "pass"}
        rows={8}
      />

      <div class="actions">
        <button
          type="button"
          class="primary"
          onClick={submit}
          disabled={locked()}
        >
          {verdict() === "pass"
            ? "Passed ✓"
            : submitting()
            ? "Grading…"
            : "Submit answer"}
        </button>
      </div>

      <Show when={verdict() === "pass"}>
        <p class="success">Interviewer says: pass.</p>
      </Show>
      <Show when={verdict() === "fail" && explanation()}>
        <p class="feedback-line"><strong>Verdict:</strong> fail</p>
      </Show>
      <Show when={explanation()}>
        <div class="ai-explanation">
          <h3>Interviewer notes</h3>
          <p>{explanation()}</p>
        </div>
      </Show>
      <Show when={error()}>
        <p class="error">{error()}</p>
      </Show>
    </section>
  );
}

export default MockInterviewPanel;
