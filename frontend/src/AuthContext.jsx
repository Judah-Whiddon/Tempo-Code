import { createContext, createSignal, onMount, useContext } from "solid-js";
import * as api from "./api";
import { clearToken, getToken, setToken } from "./auth";

// Solid context: not React. Lifecycle is onMount / createEffect, not useEffect.
// The provider hydrates currentUser from /auth/me on mount if a token exists.
// Source of truth for "who is the user" is always the server, not JWT claims.

const AuthContext = createContext();

export function AuthProvider(props) {
  const [currentUser, setCurrentUser] = createSignal(null);
  const [hydrating, setHydrating] = createSignal(true);

  onMount(async () => {
    if (!getToken()) {
      setHydrating(false);
      return;
    }
    try {
      const user = await api.me();
      setCurrentUser(user);
    } catch {
      // 401 path already cleared the token + redirects via api.js. Other errors
      // (network, server down) leave the token in place — user can retry.
      setCurrentUser(null);
    } finally {
      setHydrating(false);
    }
  });

  async function login(username, password) {
    const { user, access_token } = await api.login(username, password);
    setToken(access_token);
    setCurrentUser(user);
    return user;
  }

  async function signup(username, password) {
    const { user, access_token } = await api.signup(username, password);
    setToken(access_token);
    setCurrentUser(user);
    return user;
  }

  function logout() {
    clearToken();
    setCurrentUser(null);
  }

  const value = { currentUser, hydrating, login, signup, logout };
  return (
    <AuthContext.Provider value={value}>{props.children}</AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
