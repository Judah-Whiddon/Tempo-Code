import { Router, Route } from "@solidjs/router";
import ProblemTypeSelect from "./pages/ProblemTypeSelect";
import ProblemPage from "./pages/ProblemPage";

function App() {
  return (
    <Router>
      <Route path="/" component={ProblemTypeSelect} />
      <Route path="/problem/:id" component={ProblemPage} />
    </Router>
  );
}

export default App;
