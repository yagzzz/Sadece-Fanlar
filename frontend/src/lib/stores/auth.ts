/**
 * Auth Store
 */
import { writable, derived } from 'svelte/store';
import { api, authApi, userApi } from '$lib/api';
import type { User } from '$lib/types';

interface AuthState {
	user: User | null;
	loading: boolean;
	initialized: boolean;
}

function createAuthStore() {
	const { subscribe, set, update } = writable<AuthState>({
		user: null,
		loading: true,
		initialized: false,
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
					set({ user: response.data as User, loading: false, initialized: true });
				} else {
					api.setToken(null);
					set({ user: null, loading: false, initialized: true });
				}
			} catch {
				api.setToken(null);
				set({ user: null, loading: false, initialized: true });
			}
		},

		async login(
			identifier: string | { username?: string; email?: string; password: string },
			password?: string,
			twoFactorCode?: string
		) {
			update((s) => ({ ...s, loading: true }));

			const username =
				typeof identifier === 'string'
					? identifier
					: identifier.username || identifier.email || '';
			const finalPassword = typeof identifier === 'string' ? password || '' : identifier.password;

			const response = await authApi.login({
				username,
				password: finalPassword,
				two_factor_code: twoFactorCode || undefined
			});
			
			if (response.error) {
				update((s) => ({ ...s, loading: false }));
				return { error: response.error };
			}

			// 2FA gerekiyorsa boş token gelir; token saklama, 2FA iste.
			if ((response.data as any)?.requires_2fa || !response.data!.access_token) {
				update((s) => ({ ...s, loading: false }));
				return { requires2fa: true };
			}

			api.setToken(response.data!.access_token);
			
			// Store refresh token separately
			if (response.data!.refresh_token) {
				localStorage.setItem('refresh_token', response.data!.refresh_token);
			}

			const userResponse = await userApi.getMe();
			if (userResponse.data) {
				set({ user: userResponse.data as User, loading: false, initialized: true });
				return { success: true };
			}

			return { error: 'Kullanıcı bilgileri alınamadı' };
		},

		async register(
			username: string | { username: string; email: string; password: string; display_name?: string },
			email?: string,
			password?: string
		) {
			update((s) => ({ ...s, loading: true }));

			const payload =
				typeof username === 'string'
					? { username, email: email || '', password: password || '' }
					: username;

			const response = await authApi.register({
				username: payload.username,
				email: payload.email,
				password: payload.password,
				display_name: payload.display_name,
			});
			
			if (response.error) {
				update((s) => ({ ...s, loading: false }));
				return { error: response.error };
			}

			// Otomatik giriş: kayıt token döndürür, kullanıcıyı oturum açmış say.
			if (response.data?.access_token) {
				api.setToken(response.data.access_token);
				if (response.data.refresh_token) {
					localStorage.setItem('refresh_token', response.data.refresh_token);
				}
				const userResponse = await userApi.getMe();
				if (userResponse.data) {
					set({ user: userResponse.data as User, loading: false, initialized: true });
					return { success: true, message: 'Kayıt başarılı!' };
				}
			}

			update((s) => ({ ...s, loading: false }));
			return { success: true, message: 'Kayıt başarılı! Giriş yapabilirsiniz.' };
		},

		async logout() {
			try {
				await authApi.logout();
			} catch {
				// Ignore errors
			}
			
			api.setToken(null);
			localStorage.removeItem('refresh_token');
			set({ user: null, loading: false, initialized: true });
		},

		updateUser(userData: Partial<User>) {
			update((s) => ({
				...s,
				user: s.user ? { ...s.user, ...userData } : null,
			}));
		},

		async refreshUser() {
			const response = await userApi.getMe();
			if (response.data) {
				update((s) => ({ ...s, user: response.data as User }));
			}
		},
	};
}

export const auth = createAuthStore();

// Export individual functions for convenience
export const login = auth.login.bind(auth);
export const register = auth.register.bind(auth);
export const logout = auth.logout.bind(auth);
export const checkAuth = auth.init.bind(auth);

// Alias for backwards compatibility
export const authStore = auth;

// Derived stores
export const isAuthenticated = derived(auth, ($auth) => !!$auth.user);
export const isCreator = derived(auth, ($auth) => $auth.user?.is_creator ?? false);
export const isVerified = derived(
	auth,
	($auth) => $auth.user?.is_verified_creator ?? $auth.user?.is_verified ?? false
);
