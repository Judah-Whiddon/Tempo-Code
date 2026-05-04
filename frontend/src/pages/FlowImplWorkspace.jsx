import { createSignal, Show } from "solid-js";
import FlowCanvas from "../components/FlowCanvas";
import ImplementationPanel from "../components/ImplementationPanel";

// Orchestrates the FLOW → IMPLEMENTATION transition for a FLOW_IMPL problem.
function FlowImplWorkspace(props) {
  const [phase, setPhase] = createSignal("FLOW"); // "FLOW" | "IMPLEMENTATION"
  const [flowOrder, setFlowOrder] = createSignal([]);

  function handleFlowPass(order) {
    setFlowOrder(order);
    setPhase("IMPLEMENTATION");
  }

  return (
    <>
      <Show when={phase() === "FLOW"}>
        <FlowCanvas problem={props.problem} onPass={handleFlowPass} />
      </Show>
      <Show when={phase() === "IMPLEMENTATION"}>
        <ImplementationPanel
          problem={props.problem}
          flowOrder={flowOrder()}
        />
      </Show>
    </>
  );
}

export default FlowImplWorkspace;
