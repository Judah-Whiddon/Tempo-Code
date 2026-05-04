import { createResource, Show } from "solid-js";
import { useParams, A } from "@solidjs/router";
import { getProblem } from "../api";
import FlowImplWorkspace from "./FlowImplWorkspace";
import ImplementationPanel from "../components/ImplementationPanel";

function ProblemPage() {
  const params = useParams();
  const [problem] = createResource(() => params.id, getProblem);

  return (
    <main class="container">
      <nav class="back">
        <A href="/">← back</A>
      </nav>

      <Show
        when={!problem.loading && !problem.error}
        fallback={
          <Show when={problem.error} fallback={<p class="loading">loading…</p>}>
            <p class="error">{String(problem.error)}</p>
          </Show>
        }
      >
        <header class="problem-header">
          <h1>{problem().title}</h1>
          <div class="meta">
            <span class="pill">{problem().type}</span>
            <span class="pill">{problem().difficulty}</span>
            <Show when={problem().topic}>
              <span class="pill subtle">{problem().topic}</span>
            </Show>
          </div>
          <p class="prompt">{problem().prompt}</p>
        </header>

        <Show when={problem().type === "FLOW_IMPL"}>
          <FlowImplWorkspace problem={problem()} />
        </Show>
        <Show when={problem().type === "DEBUGGING"}>
          <ImplementationPanel problem={problem()} phase="DEBUGGING" />
        </Show>
        <Show when={problem().type === "MOCK_INTERVIEW"}>
          <p class="footnote">Mock Interview UI is deferred from MVP.</p>
        </Show>
      </Show>
    </main>
  );
}

export default ProblemPage;
