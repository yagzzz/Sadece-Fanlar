/// <reference types="@sveltejs/kit" />

// See https://kit.svelte.dev/docs/types#app
declare global {
	namespace App {
		interface Error {
			message: string;
			code?: string;
		}
		interface Locals {
			user: import('$lib/types').User | null;
		}
		interface PageData {}
		interface Platform {}
	}
}

export {};
