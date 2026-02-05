<script lang="ts">
	import { goto } from '$app/navigation';
	import { login } from '$lib/stores/auth';
	import { Button, Card, Input } from '$lib/components/ui';

	let identifier = '';
	let password = '';
	let loading = false;
	let error = '';

	async function handleSubmit() {
		loading = true;
		error = '';

		try {
			const result = await login({ username: identifier, password });
			if (result?.error) {
				throw new Error(result.error);
			}
			goto('/');
		} catch (err: any) {
			error = err.message || 'Login failed. Please try again.';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Giriş Yap | SadeceFanlar</title>
</svelte:head>

<Card class="p-8">
	<div class="text-center mb-8">
		<a href="/" class="text-3xl font-bold text-primary">SadeceFanlar</a>
		<p class="text-neutral-500 mt-2">Tekrar hoş geldiniz</p>
	</div>

	<form on:submit|preventDefault={handleSubmit} class="space-y-4">
		{#if error}
			<div class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400 text-sm">
				{error}
			</div>
		{/if}

		<Input
			label="Kullanıcı adı veya e-posta"
			placeholder="kullaniciadi"
			bind:value={identifier}
			required
		/>

		<Input
			type="password"
			label="Şifre"
			placeholder="••••••••"
			bind:value={password}
			required
		/>

		<div class="flex items-center justify-between text-sm">
			<label class="flex items-center gap-2">
				<input type="checkbox" class="rounded border-neutral-300" />
				<span class="text-neutral-600 dark:text-neutral-400">Beni hatırla</span>
			</label>
			<a href="/forgot-password" class="text-primary hover:underline">
				Şifremi unuttum?
			</a>
		</div>

		<Button type="submit" class="w-full" disabled={loading}>
			{loading ? 'Giriş yapılıyor...' : 'Giriş Yap'}
		</Button>
	</form>

	<p class="text-center text-sm text-neutral-500 mt-6">
		Hesabınız yok mu?
		<a href="/register" class="text-primary hover:underline">Kayıt ol</a>
	</p>

	<div class="mt-6 rounded-lg border border-neutral-200 dark:border-neutral-700 p-4">
		<p class="text-sm font-semibold text-neutral-800 dark:text-neutral-200">
			İçerik Üreticisi Başvurusu
		</p>
		<p class="mt-1 text-xs text-neutral-500">
			Başvuru formu kayıt sayfasında. İsim, doğum tarihi, yüz fotoğrafları ve kategori seçimleri istenir.
		</p>
		<a
			href="/register?creator=1"
			class="mt-3 inline-flex w-full items-center justify-center rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white"
		>
			Başvuruya Başla
		</a>
	</div>

	<div class="mt-8 pt-6 border-t border-neutral-200 dark:border-neutral-700">
		<p class="text-xs text-neutral-400 text-center">
			🔒 Gizliliğiniz korunmaktadır. Kişisel verilerinizi takip etmiyor veya saklamıyoruz.
		</p>
	</div>
</Card>
