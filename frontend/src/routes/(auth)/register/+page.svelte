<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { register } from '$lib/stores/auth';
	import { api } from '$lib/api';
	import { Button, Card, Input } from '$lib/components/ui';
	import { isValidEmail, isValidUsername, isStrongPassword } from '$lib/utils';

	let email = '';
	let username = '';
	let password = '';
	let confirmPassword = '';
	let displayName = '';
	let agreedToTerms = false;
	let ageConfirmed = false;
	let loading = false;
	let error = '';
	let step = 1;

	// Gizlilik öncelikli içerik üretici onboarding (kimlik/yüz fotoğrafı YOK)
	let wantCreator = false;
	let bio = '';
	let subscriptionPrice = 10;
	let selectedCategories: string[] = [];

	const categoryOptions = [
		'Günlük Hayat',
		'Fotoğraf-Video',
		'Poz',
		'Ayak',
		'ASMR',
		'Canlı içerik',
		'Özel İstek',
		'Özel Mesaj',
		'Genel',
		'Diğer',
	];

	$: emailError = email && !isValidEmail(email) ? 'Geçersiz e-posta adresi' : '';
	$: usernameError =
		username && !isValidUsername(username)
			? 'Kullanıcı adı 3-20 karakter olmalı; sadece harf, rakam ve alt çizgi'
			: '';
	$: passwordError =
		password && !isStrongPassword(password)
			? 'Şifre en az 8 karakter olmalı; büyük harf, küçük harf ve rakam içermeli'
			: '';
	$: confirmError =
		confirmPassword && password !== confirmPassword ? 'Şifreler eşleşmiyor' : '';
	$: if ($page.url.searchParams.get('creator') === '1') wantCreator = true;

	function handleCategoryToggle(category: string) {
		selectedCategories = selectedCategories.includes(category)
			? selectedCategories.filter((c) => c !== category)
			: [...selectedCategories, category];
	}

	async function handleSubmit() {
		if (step === 1) {
			if (emailError || usernameError || !username) return;
			step = 2;
			return;
		}

		if (passwordError || confirmError || !agreedToTerms || !ageConfirmed) return;

		loading = true;
		error = '';

		try {
			const result = await register({
				username,
				email,
				password,
				display_name: displayName || username,
			});

			if ((result as any)?.error) {
				error = (result as any).error;
				return;
			}

			// Otomatik giriş yapıldıysa ve üretici olmak istendiyse başvuruyu gönder.
			if (wantCreator) {
				try {
					await api.users.applyCreator({
						display_name: displayName || username,
						bio: bio || 'Merhaba!',
						subscription_price: Number(subscriptionPrice) || 0,
						categories: selectedCategories,
						age_confirmed: true,
					});
				} catch (e) {
					// Üretici başvurusu başarısız olsa bile kayıt tamamlandı; sessiz geç.
				}
			}

			goto('/');
		} catch (err: any) {
			error = err.message || 'Kayıt başarısız. Lütfen tekrar deneyin.';
		} finally {
			loading = false;
		}
	}

	function goBack() {
		step = 1;
	}
</script>

<svelte:head>
	<title>Kayıt Ol | SadeceFanlar</title>
</svelte:head>

<Card class="p-8">
	<div class="text-center mb-8">
		<a href="/" class="text-3xl font-bold text-primary">SadeceFanlar</a>
		<p class="text-neutral-500 mt-2">Anonim hesabını oluştur</p>
	</div>

	<!-- Progress -->
	<div class="flex items-center justify-center gap-2 mb-8">
		<div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium bg-primary text-white">
			1
		</div>
		<div class="w-12 h-1 rounded bg-neutral-200 dark:bg-neutral-700">
			<div class="h-full bg-primary rounded transition-all" style:width={step === 2 ? '100%' : '0%'} />
		</div>
		<div
			class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors"
			class:bg-primary={step === 2}
			class:text-white={step === 2}
			class:bg-neutral-200={step === 1}
			class:dark:bg-neutral-700={step === 1}
			class:text-neutral-500={step === 1}
		>
			2
		</div>
	</div>

	<form on:submit|preventDefault={handleSubmit} class="space-y-4">
		{#if error}
			<div class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400 text-sm">
				{error}
			</div>
		{/if}

		{#if step === 1}
			<Input
				label="Kullanıcı Adı"
				placeholder="kullaniciadiniz"
				bind:value={username}
				error={usernameError}
				required
			/>

			<Input
				type="email"
				label="E-posta (isteğe bağlı)"
				placeholder="anonim kalmak için boş bırakın"
				bind:value={email}
				error={emailError}
			/>

			<Input
				label="Görünen Ad (isteğe bağlı)"
				placeholder="Takma adınız"
				bind:value={displayName}
			/>

			<Button type="submit" class="w-full" disabled={!username || !!emailError || !!usernameError}>
				Devam Et
			</Button>
		{:else}
			<Input
				type="password"
				label="Şifre"
				placeholder="••••••••"
				bind:value={password}
				error={passwordError}
				required
			/>

			<Input
				type="password"
				label="Şifre Tekrar"
				placeholder="••••••••"
				bind:value={confirmPassword}
				error={confirmError}
				required
			/>

			<label class="flex items-start gap-3">
				<input type="checkbox" bind:checked={ageConfirmed} class="mt-1 rounded border-neutral-300" />
				<span class="text-sm text-neutral-600 dark:text-neutral-400">
					🔞 18 yaşından büyük olduğumu onaylıyorum
				</span>
			</label>

			<label class="flex items-start gap-3">
				<input type="checkbox" bind:checked={agreedToTerms} class="mt-1 rounded border-neutral-300" />
				<span class="text-sm text-neutral-600 dark:text-neutral-400">
					<a href="/terms" class="text-primary hover:underline">Kullanım Koşulları</a>'nı ve
					<a href="/privacy" class="text-primary hover:underline">Gizlilik Politikası</a>'nı kabul ediyorum
				</span>
			</label>

			<label class="flex items-start gap-3 rounded-lg border border-neutral-200 dark:border-neutral-700 p-3">
				<input type="checkbox" bind:checked={wantCreator} class="mt-1 rounded border-neutral-300" />
				<span class="text-sm text-neutral-700 dark:text-neutral-300">
					İçerik üreticisi olmak istiyorum
					<span class="block text-xs text-neutral-500 mt-0.5">
						Gerçek isim, kimlik veya yüz fotoğrafı istenmez — takma adınla kazan.
					</span>
				</span>
			</label>

			{#if wantCreator}
				<div class="space-y-3 rounded-lg bg-neutral-50 dark:bg-neutral-800/50 p-3">
					<Input
						label="Aylık abonelik fiyatı (USD)"
						type="number"
						bind:value={subscriptionPrice}
					/>
					<div>
						<label for="creator-bio" class="mb-1 block text-sm font-medium text-neutral-700 dark:text-neutral-300">
							Kısa tanıtım
						</label>
						<textarea
							id="creator-bio"
							bind:value={bio}
							rows="2"
							maxlength="1000"
							placeholder="Profilinde görünecek kısa bir tanıtım"
							class="w-full rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-900 px-3 py-2 text-sm"
						/>
					</div>
					<div>
						<span class="mb-2 block text-sm font-medium text-neutral-700 dark:text-neutral-300">
							Kategoriler (isteğe bağlı)
						</span>
						<div class="grid grid-cols-2 gap-2">
							{#each categoryOptions as category}
								<label class="flex items-center gap-2 rounded-lg border border-neutral-200 dark:border-neutral-700 px-3 py-2 text-sm">
									<input
										type="checkbox"
										checked={selectedCategories.includes(category)}
										on:change={() => handleCategoryToggle(category)}
									/>
									<span>{category}</span>
								</label>
							{/each}
						</div>
					</div>
				</div>
			{/if}

			<div class="flex gap-2">
				<Button type="button" variant="outline" class="flex-1" on:click={goBack}>
					Geri
				</Button>
				<Button
					type="submit"
					class="flex-1"
					disabled={loading || !password || !confirmPassword || !!passwordError || !!confirmError || !agreedToTerms || !ageConfirmed}
				>
					{loading ? 'Oluşturuluyor...' : 'Hesap Oluştur'}
				</Button>
			</div>
		{/if}
	</form>

	<p class="text-center text-sm text-neutral-500 mt-6">
		Zaten hesabınız var mı?
		<a href="/login" class="text-primary hover:underline">Giriş yap</a>
	</p>

	<div class="mt-8 pt-6 border-t border-neutral-200 dark:border-neutral-700">
		<p class="text-xs text-neutral-400 text-center">
			🔒 Anonim kayıt. Kripto ile ödeyin, kişisel veri gerekmez. E-posta isteğe bağlıdır.
		</p>
	</div>
</Card>
