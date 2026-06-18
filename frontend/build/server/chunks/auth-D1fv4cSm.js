import { d as derived, w as writable } from './index-BCAmX91C.js';
import { u as userApi, b as authApi, a as api } from './index2-BnafdvHM.js';

function createAuthStore() {
  const { subscribe, set, update } = writable({
    user: null,
    loading: true,
    initialized: false
  });
  return {
    subscribe,
    async init() {
      const token = api.getToken();
      if (!token) {
        set({ user: null, loading: false, initialized: true });
        return;
      }
      try {
        const response = await userApi.getMe();
        if (response.data) {
          set({ user: response.data, loading: false, initialized: true });
        } else {
          api.setToken(null);
          set({ user: null, loading: false, initialized: true });
        }
      } catch {
        api.setToken(null);
        set({ user: null, loading: false, initialized: true });
      }
    },
    async login(identifier, password) {
      update((s) => ({ ...s, loading: true }));
      const username = typeof identifier === "string" ? identifier : identifier.username || identifier.email || "";
      const finalPassword = typeof identifier === "string" ? password || "" : identifier.password;
      const response = await authApi.login({ username, password: finalPassword });
      if (response.error) {
        update((s) => ({ ...s, loading: false }));
        return { error: response.error };
      }
      if (response.data?.requires_2fa || !response.data.access_token) {
        update((s) => ({ ...s, loading: false }));
        return { requires2fa: true };
      }
      api.setToken(response.data.access_token);
      if (response.data.refresh_token) {
        localStorage.setItem("refresh_token", response.data.refresh_token);
      }
      const userResponse = await userApi.getMe();
      if (userResponse.data) {
        set({ user: userResponse.data, loading: false, initialized: true });
        return { success: true };
      }
      return { error: "Kullanıcı bilgileri alınamadı" };
    },
    async register(username, email, password) {
      update((s) => ({ ...s, loading: true }));
      const payload = typeof username === "string" ? { username, email: email || "", password: password || "" } : username;
      const response = await authApi.register({
        username: payload.username,
        email: payload.email,
        password: payload.password,
        display_name: payload.display_name
      });
      if (response.error) {
        update((s) => ({ ...s, loading: false }));
        return { error: response.error };
      }
      if (response.data?.access_token) {
        api.setToken(response.data.access_token);
        if (response.data.refresh_token) {
          localStorage.setItem("refresh_token", response.data.refresh_token);
        }
        const userResponse = await userApi.getMe();
        if (userResponse.data) {
          set({ user: userResponse.data, loading: false, initialized: true });
          return { success: true, message: "Kayıt başarılı!" };
        }
      }
      update((s) => ({ ...s, loading: false }));
      return { success: true, message: "Kayıt başarılı! Giriş yapabilirsiniz." };
    },
    async logout() {
      try {
        await authApi.logout();
      } catch {
      }
      api.setToken(null);
      localStorage.removeItem("refresh_token");
      set({ user: null, loading: false, initialized: true });
    },
    updateUser(userData) {
      update((s) => ({
        ...s,
        user: s.user ? { ...s.user, ...userData } : null
      }));
    },
    async refreshUser() {
      const response = await userApi.getMe();
      if (response.data) {
        update((s) => ({ ...s, user: response.data }));
      }
    }
  };
}
const auth = createAuthStore();
auth.login.bind(auth);
auth.register.bind(auth);
auth.logout.bind(auth);
auth.init.bind(auth);
const authStore = auth;
derived(auth, ($auth) => !!$auth.user);
derived(auth, ($auth) => $auth.user?.is_creator ?? false);
derived(
  auth,
  ($auth) => $auth.user?.is_verified_creator ?? $auth.user?.is_verified ?? false
);

export { authStore as a };
//# sourceMappingURL=auth-D1fv4cSm.js.map
