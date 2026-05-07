import { createSignal, Show } from "solid-js";
import { A, useNavigate } from "@solidjs/router";
import { useAuth } from "../AuthContext";

function Login() {
  const navigate = useNavigate();
  const auth = useAuth();
  const [username, setUsername] = createSignal("");
  const [password, setPassword] = createSignal("");
  const [error, setError] = createSignal("");
  const [submitting, setSubmitting] = createSignal(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await auth.login(username(), password());
      navigate("/");
    } catch (err) {
      setError(err.status === 401 ? "Invalid username or password." : err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main class="container auth-container">
      <header class="hero">
        <h1>Log in</h1>
      </header>

      <form class="auth-form" onSubmit={handleSubmit}>
        <label>
          <span>Username</span>
          <input
            type="text"
            autocomplete="username"
            value={username()}
            onInput={(e) => setUsername(e.currentTarget.value)}
            required
          />
        </label>

        <label>
          <span>Password</span>
          <input
            type="password"
            autocomplete="current-password"
            value={password()}
            onInput={(e) => setPassword(e.currentTarget.value)}
            required
          />
        </label>

        <Show when={error()}>
          <p class="error">{error()}</p>
        </Show>

        <button type="submit" class="primary" disabled={submitting()}>
          {submitting() ? "Logging in…" : "Log in"}
        </button>
      </form>

      <p class="auth-switch">
        New here? <A href="/signup">Create an account</A>
      </p>
    </main>
  );
}

export default Login;
