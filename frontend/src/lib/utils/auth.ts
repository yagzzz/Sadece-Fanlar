import { get } from 'svelte/store';
import { authStore } from '$lib/stores/auth';

/** Auth store hazır olana kadar bekle (sayfa değişiminde erken login yönlendirmesini önler). */
export function waitForAuth(): Promise<void> {
	return new Promise((resolve) => {
		const state = get(authStore);
		if (state.initialized) {
			resolve();
			return;
		}

		const unsub = authStore.subscribe((s) => {
			if (s.initialized) {
				unsub();
				resolve();
			}
		});
	});
}

/** Yalnızca admin. */
export function isAdmin(user: { role?: string } | null | undefined): boolean {
	return user?.role === 'admin';
}

/** Admin veya moderatör (yönetim paneli erişimi). */
export function isStaff(user: { role?: string } | null | undefined): boolean {
	return user?.role === 'admin' || user?.role === 'moderator';
}
