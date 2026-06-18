import { writable } from 'svelte/store';
import { browser } from '$app/environment';

type Theme = 'light' | 'dark';

function createTheme() {
	const initial: Theme = browser
		? ((localStorage.getItem('theme') as Theme) || 'dark')
		: 'dark';
	const { subscribe, set } = writable<Theme>(initial);

	function apply(value: Theme) {
		if (browser) {
			document.documentElement.classList.toggle('dark', value === 'dark');
			localStorage.setItem('theme', value);
		}
		set(value);
	}

	return {
		subscribe,
		set: apply,
		toggle: () => {
			if (!browser) return;
			const next: Theme = document.documentElement.classList.contains('dark') ? 'light' : 'dark';
			apply(next);
		},
	};
}

export const theme = createTheme();
