import { Route, Router } from "@solidjs/router";

import { AuthProvider } from "./AuthContext";
import Login from "./pages/Login";
import ProblemPage from "./pages/ProblemPage";
import ProblemTypeSelect from "./pages/ProblemTypeSelect";
import Profile from "./pages/Profile";
import Signup from "./pages/Signup";

// Auth is opt-in. Every route is publicly reachable; signing up enables
// per-user progress tracking on the (upcoming) profile page.
function App() {
  return (
    <AuthProvider>
      <Router>
        <Route path="/" component={ProblemTypeSelect} />
        <Route path="/login" component={Login} />
        <Route path="/signup" component={Signup} />
        <Route path="/profile" component={Profile} />
        <Route path="/problem/:id" component={ProblemPage} />
      </Router>
    </AuthProvider>
  );
}

export default App;
