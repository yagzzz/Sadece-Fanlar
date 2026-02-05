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
	let loading = false;
	let error = '';
	let step = 1;

	// Creator application
	let showCreatorApplication = false;
	let fullName = '';
	let birthDate = '';
	let gender = '';
	let facePhotos: File[] = [];
	let submittingApplication = false;
	let applicationMessage = '';
	let selectedCategories: string[] = [];

	const categoryOptions = [
		'Rule34',
		'Günlük Hayat',
		'Ayak',
		'Nude',
		'Poz',
		'Fotoğraf-Video',
		'Özel İstek',
		'Özel Mesaj',
		'Canlı içerik',
		'ASMR',
		'Rastgele (Genel)',
		'Diğer',
	];

	const genderOptions = [
		'Erkek',
		'Kadın',
		'Non-binary',
		'Belirtmek istemiyorum',
		'Diğer',
	];

	$: emailError = email && !isValidEmail(email) ? 'Geçersiz e-posta adresi' : '';
	$: usernameError = username && !isValidUsername(username) ? 'Kullanıcı adı 3-20 karakter olmalı, sadece harf, rakam ve alt çizgi içerebilir' : '';
	$: passwordError = password && !isStrongPassword(password) ? 'Şifre en az 8 karakter olmalı, büyük harf, küçük harf, rakam ve özel karakter içermeli' : '';
	$: confirmError = confirmPassword && password !== confirmPassword ? 'Şifreler eşleşmiyor' : '';
	$: if ($page.url.searchParams.get('creator') === '1') showCreatorApplication = true;

	async function handleSubmit() {
		if (step === 1) {
			if (emailError || usernameError) return;
			step = 2;
			return;
		}

		if (passwordError || confirmError || !agreedToTerms) return;

		loading = true;
		error = '';

		try {
			await register({
				email,
				username,
				password,
				display_name: displayName || username,
			});
			goto('/');
		} catch (err: any) {
			error = err.message || 'Registration failed. Please try again.';
		} finally {
			loading = false;
		}
	}

	function handleCategoryToggle(category: string) {
		selectedCategories = selectedCategories.includes(category)
			? selectedCategories.filter((c) => c !== category)
			: [...selectedCategories, category];
	}

	function handlePhotoSelect(event: Event) {
		const target = event.target as HTMLInputElement;
		if (target.files) {
			facePhotos = Array.from(target.files);
		}
	}

	async function submitCreatorApplication() {
		applicationMessage = '';
		if (!fullName || !username || !birthDate || !gender) {
			applicationMessage = 'Lütfen tüm zorunlu alanları doldurun.';
			return;
		}
		if (facePhotos.length < 3) {
			applicationMessage = 'En az 3 yüz fotoğrafı yükleyin.';
			return;
		}
		if (selectedCategories.length === 0) {
			applicationMessage = 'En az bir kategori seçin.';
			return;
		}
		submittingApplication = true;
		try {
			const formData = new FormData();
			formData.append('full_name', fullName);
			formData.append('username', username);
			formData.append('birth_date', birthDate);
			formData.append('gender', gender);
			selectedCategories.forEach((c) => formData.append('categories', c));
			facePhotos.forEach((file) => formData.append('face_photos', file));
			await api.users.submitCreatorApplication(formData);
			applicationMessage = 'Başvurunuz alındı.';
		} catch (err: any) {
			applicationMessage = err.message || 'Başvuru gönderilemedi.';
		} finally {
			submittingApplication = false;
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
		<p class="text-neutral-500 mt-2">Hesabınızı oluşturun</p>
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
				type="email"
				label="E-posta"
				placeholder="siz@ornek.com"
				bind:value={email}
				error={emailError}
				required
			/>

			<Input
				label="Kullanıcı Adı"
				placeholder="kullaniciadiniz"
				bind:value={username}
				error={usernameError}
				required
			/>

			<Input
				label="Görünen Ad (isteğe bağlı)"
				placeholder="Adınız"
				bind:value={displayName}
			/>

			<Button type="submit" class="w-full" disabled={!email || !username || !!emailError || !!usernameError}>
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
				<input
					type="checkbox"
					bind:checked={agreedToTerms}
					class="mt-1 rounded border-neutral-300"
				/>
				<span class="text-sm text-neutral-600 dark:text-neutral-400">
					<a href="/terms" class="text-primary hover:underline">Kullanım Koşulları</a>'nı
					ve
					<a href="/privacy" class="text-primary hover:underline">Gizlilik Politikası</a>'nı kabul ediyorum
				</span>
			</label>

			<div class="flex gap-2">
				<Button type="button" variant="outline" class="flex-1" on:click={goBack}>
					Geri
				</Button>
				<Button
					type="submit"
					class="flex-1"
					disabled={loading || !password || !confirmPassword || !!passwordError || !!confirmError || !agreedToTerms}
				>
					{loading ? 'Oluşturuluyor...' : 'Hesap Oluştur'}
				</Button>
			</div>
		{/if}
	</form>

	<div class="mt-8 border-t border-neutral-200 dark:border-neutral-700 pt-6">
		<button
			type="button"
			class="w-full text-left flex items-center justify-between text-sm font-semibold text-neutral-700 dark:text-neutral-300"
			on:click={() => (showCreatorApplication = !showCreatorApplication)}
		>
			<span>İçerik Üreticisi Başvurusu</span>
			<span>{showCreatorApplication ? '−' : '+'}</span>
		</button>

		{#if showCreatorApplication}
			<div class="mt-4 space-y-4">
				{#if applicationMessage}
					<div class="p-3 rounded-lg text-sm bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-200">
						{applicationMessage}
					</div>
				{/if}
				<Input
					label="İsim Soyisim"
					placeholder="Ad Soyad"
					bind:value={fullName}
					required
				/>
				<Input
					label="Kullanıcı Adı"
					placeholder="kullaniciadi"
					bind:value={username}
					required
				/>
				<Input
					label="Doğum Tarihi"
					type="date"
					bind:value={birthDate}
					required
				/>
				<div>
					<label class="mb-2 block text-sm font-medium text-neutral-700 dark:text-neutral-300">
						Cinsiyet
					</label>
					<select
						class="w-full rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-900 px-3 py-2 text-sm"
						bind:value={gender}
					>
						<option value="" disabled>Seçiniz</option>
						{#each genderOptions as option}
							<option value={option}>{option}</option>
						{/each}
					</select>
				</div>
				<div>
					<label class="mb-2 block text-sm font-medium text-neutral-700 dark:text-neutral-300">
						Paylaşım Kategorileri (birden fazla seçilebilir)
					</label>
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
				<div>
					<label class="mb-2 block text-sm font-medium text-neutral-700 dark:text-neutral-300">
						Yüz Fotoğrafları (en az 3 açıdan, aydınlık)
					</label>
					<input type="file" accept="image/*" multiple on:change={handlePhotoSelect} />
					{#if facePhotos.length > 0}
						<p class="mt-2 text-xs text-neutral-500">Seçilen: {facePhotos.length} dosya</p>
					{/if}
				</div>
				<Button
					type="button"
					class="w-full"
					disabled={submittingApplication}
					on:click={submitCreatorApplication}
				>
					{submittingApplication ? 'Gönderiliyor...' : 'Başvuru Gönder'}
				</Button>
			</div>
		{/if}
	</div>

	<p class="text-center text-sm text-neutral-500 mt-6">
		Zaten hesabınız var mı?
		<a href="/login" class="text-primary hover:underline">Giriş yap</a>
	</p>

	<div class="mt-8 pt-6 border-t border-neutral-200 dark:border-neutral-700">
		<p class="text-xs text-neutral-400 text-center">
			🔒 Anonim kayıt desteklenir. Kripto ile ödeyin, kişisel veri gerekmez.
		</p>
	</div>
</Card>
