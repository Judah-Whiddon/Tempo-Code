import { createSignal, Show } from "solid-js";
import { A, useNavigate } from "@solidjs/router";
import { useAuth } from "../AuthContext";

function Signup() {
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
      await auth.signup(username(), password());
      navigate("/");
    } catch (err) {
      if (err.status === 409) setError("That username is already taken.");
      else setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main class="container auth-container">
      <header class="hero">
        <h1>Sign up</h1>
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
            autocomplete="new-password"
            value={password()}
            onInput={(e) => setPassword(e.currentTarget.value)}
            required
          />
        </label>

        <Show when={error()}>
          <p class="error">{error()}</p>
        </Show>

        <button type="submit" class="primary" disabled={submitting()}>
          {submitting() ? "Creating account…" : "Sign up"}
        </button>
      </form>

      <p class="auth-switch">
        Already have an account? <A href="/login">Log in</A>
      </p>
    </main>
  );
}

export default Signup;
