import { createSignal, createMemo, For, Show } from "solid-js";
import { submitAnswer } from "../api";

// Returns a new array with elements at i and j swapped.
function swap(arr, i, j) {
  const next = arr.slice();
  [next[i], next[j]] = [next[j], next[i]];
  return next;
}

// Fisher-Yates. If the result happens to match the expected order, swap the
// last two so the user always has at least one move to make.
function shuffle(arr, expected) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  if (expected && a.length >= 2 && a.every((x, i) => x === expected[i])) {
    [a[a.length - 2], a[a.length - 1]] = [a[a.length - 1], a[a.length - 2]];
  }
  return a;
}

function FlowCanvas(props) {
  const labels = props.problem.flow_steps.map((s) => s.label);
  const expected = props.problem.expected_flow ?? null;

  const [order, setOrder] = createSignal(shuffle(labels, expected));
  const [verdict, setVerdict] = createSignal(null); // null | "pass" | "fail"
  const [greened, setGreened] = createSignal([]); // labels greened from last submission
  const [hint, setHint] = createSignal("");
  const [submitting, setSubmitting] = createSignal(false);
  const [error, setError] = createSignal("");

  const locked = createMemo(() => verdict() === "pass" || submitting());

  function clearVerdict() {
    if (verdict() !== "pass") {
      setVerdict(null);
      setGreened([]);
      setHint("");
    }
  }

  function moveUp(i) {
    if (locked() || i <= 0) return;
    setOrder(swap(order(), i, i - 1));
    clearVerdict();
  }

  function moveDown(i) {
    if (locked() || i >= order().length - 1) return;
    setOrder(swap(order(), i, i + 1));
    clearVerdict();
  }

  function reshuffle() {
    if (locked()) return;
    setOrder(shuffle(labels, expected));
    clearVerdict();
    setError("");
  }

  async function submit() {
    if (locked()) return;
    setSubmitting(true);
    setError("");
    try {
      const res = await submitAnswer({
        problem_id: props.problem.id,
        phase: "FLOW",
        content: order(),
      });
      const v = res.feedback?.verdict ?? "fail";
      setVerdict(v);
      setGreened(res.feedback?.greened_steps ?? []);
      setHint(res.feedback?.hint ?? "");
      if (v === "pass") {
        // Brief celebration before handing off to Implementation phase.
        setTimeout(() => props.onPass?.(order()), 900);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  function cardClass(label, i) {
    const v = verdict();
    const isGreened =
      v === "pass" || (v === "fail" && greened().includes(label) && order()[i] === label);
    return `flow-card${isGreened ? " greened" : ""}${v === "fail" && !isGreened ? " missed" : ""}`;
  }

  return (
    <section class="flow-canvas">
      <header class="phase-header">
        <h2>Flow phase</h2>
        <p class="hint">
          Arrange the steps in the order they should be implemented. Use ↑ / ↓ to reorder.
        </p>
      </header>

      <ol class="flow-list">
        <For each={order()}>
          {(label, i) => (
            <li class={cardClass(label, i())}>
              <span class="step-index">{i() + 1}</span>
              <span class="step-label">{label}</span>
              <div class="step-controls">
                <button
                  type="button"
                  aria-label="Move up"
                  onClick={() => moveUp(i())}
                  disabled={locked() || i() === 0}
                >
                  ↑
                </button>
                <button
                  type="button"
                  aria-label="Move down"
                  onClick={() => moveDown(i())}
                  disabled={locked() || i() === order().length - 1}
                >
                  ↓
                </button>
              </div>
            </li>
          )}
        </For>
      </ol>

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
            ? "Checking…"
            : "Submit flow"}
        </button>
        <button
          type="button"
          class="ghost"
          onClick={reshuffle}
          disabled={locked()}
        >
          Shuffle again
        </button>
      </div>

      <Show when={verdict() === "fail" && hint()}>
        <p class="feedback-line">{hint()}</p>
      </Show>
      <Show when={error()}>
        <p class="error">{error()}</p>
      </Show>
    </section>
  );
}

export default FlowCanvas;
