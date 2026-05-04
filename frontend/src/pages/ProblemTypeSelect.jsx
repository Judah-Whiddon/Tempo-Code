import { createSignal, For, Show } from "solid-js";
import { useNavigate } from "@solidjs/router";
import { getProblems } from "../api";

const TYPES = [
  {
    type: "FLOW_IMPL",
    title: "Flow + Implementation",
    blurb: "Arrange the flow, then write the code. The classic two-phase practice loop.",
  },
  {
    type: "DEBUGGING",
    title: "Debugging",
    blurb: "Broken code in. Working code out. Bring your gotcha radar.",
  },
  {
    type: "MOCK_INTERVIEW",
    title: "Mock Interview",
    blurb: "Read code, explain it, get graded. AI on the other side of the table.",
  },
];

function ProblemTypeSelect() {
  const navigate = useNavigate();
  const [loading, setLoading] = createSignal(null); // type currently being fetched
  const [error, setError] = createSignal("");

  async function pickType(type) {
    setError("");
    setLoading(type);
    try {
      const problems = await getProblems(type);
      if (!problems.length) {
        setError(`No ${type} problems available yet.`);
        return;
      }
      // For MVP: pick the first one. Later: random / next-in-progression.
      navigate(`/problem/${problems[0].id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(null);
    }
  }

  return (
    <main class="container">
      <header class="hero">
        <h1>TempoCode</h1>
        <p class="tagline">Practice programming fluency. Pick a mode.</p>
      </header>

      <section class="card-grid">
        <For each={TYPES}>
          {(t) => (
            <button
              class="type-card"
              onClick={() => pickType(t.type)}
              disabled={loading() !== null}
            >
              <h2>{t.title}</h2>
              <p>{t.blurb}</p>
              <Show when={loading() === t.type}>
                <span class="loading">loading…</span>
              </Show>
            </button>
          )}
        </For>
      </section>

      <Show when={error()}>
        <p class="error">{error()}</p>
      </Show>
    </main>
  );
}

export default ProblemTypeSelect;
