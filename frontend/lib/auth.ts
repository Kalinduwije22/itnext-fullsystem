const KEY = "itnext_token";

export const auth = {
  get: () => (typeof window === "undefined" ? null : localStorage.getItem(KEY)),
  set: (t: string) => localStorage.setItem(KEY, t),
  clear: () => localStorage.removeItem(KEY),
  isLoggedIn: () => typeof window !== "undefined" && !!localStorage.getItem(KEY),
};
