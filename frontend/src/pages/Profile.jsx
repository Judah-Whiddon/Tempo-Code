import { createResource, For, Match, Show, Switch } from "solid-js";
import { A } from "@solidjs/router";

import * as api from "../api";
import { useAuth } from "../AuthContext";

const TYPE_LABELS = {
  FLOW_IMPL:      "Flow + Implementation",
  DEBUGGING:      "Debugging",
  MOCK_INTERVIEW: "Mock Interview",
};

function Profile() {
  const { currentUser } = useAuth();

  // Only fetch when there's an authed user. createResource runs whenever
  // its source signal changes — returning falsy skips the fetch entirely.
  const [profile] = createResource(
    () => (currentUser() ? currentUser().id : null),
    () => api.getProfile(),
  );

  return (
    <main class="container">
      <nav class="back">
        <A href="/">← back</A>
      </nav>

      <header class="hero">
        <h1>Profile</h1>
      </header>

      <Switch>
        <Match when={!currentUser()}>
          <section class="profile-stub">
            <p class="tagline">Sign in to track your practice progress.</p>
            <div class="auth-links" style="justify-content: center; margin-top: 1rem;">
              <A href="/login">Log in</A>
              <A href="/signup" class="primary-link">Sign up</A>
            </div>
          </section>
        </Match>

        <Match when={profile.loading}>
          <p class="loading">loading…</p>
        </Match>

        <Match when={profile.error}>
          <p class="error">{String(profile.error)}</p>
        </Match>

        <Match when={profile()}>
          <ProfileBody data={profile()} />
        </Match>
      </Switch>
    </main>
  );
}

function ProfileBody(props) {
  const data = () => props.data;
  const stats = () => data().per_problem_stats;
  const isEmpty = () => stats().length === 0;

  return (
    <>
      <p class="profile-greeting">
        Welcome back, <strong>{data().username}</strong>.
      </p>

      <section class="section">
        <h2>Problems completed</h2>
        <div class="completed-grid">
          <For each={Object.keys(TYPE_LABELS)}>
            {(key) => (
              <div class="completed-card">
                <span class="completed-count">
                  {data().problems_completed_by_type[key] ?? 0}
                </span>
                <span class="completed-label">{TYPE_LABELS[key]}</span>
              </div>
            )}
          </For>
        </div>
      </section>

      <section class="section">
        <h2>Per problem</h2>
        <Show
          when={!isEmpty()}
          fallback={
            <p class="muted">
              No submissions yet — try a problem from the{" "}
              <A href="/">home page</A>.
            </p>
          }
        >
          <table class="profile-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Type</th>
                <th class="num">Attempts</th>
                <th class="num">Accuracy</th>
                <th>Completed</th>
              </tr>
            </thead>
            <tbody>
              <For each={stats()}>
                {(row) => (
                  <tr>
                    <td>{row.title}</td>
                    <td>
                      <span class="pill subtle">{TYPE_LABELS[row.type] ?? row.type}</span>
                    </td>
                    <td class="num">{row.attempts}</td>
                    <td class="num">{Math.round(row.accuracy * 100)}%</td>
                    <td>
                      <Show
                        when={row.completed}
                        fallback={<span class="badge muted">In progress</span>}
                      >
                        <span class="badge greened">Done</span>
                      </Show>
                    </td>
                  </tr>
                )}
              </For>
            </tbody>
          </table>
        </Show>
      </section>
    </>
  );
}

export default Profile;
