<script lang="ts">
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';
	import { api } from '$lib/api';
	import { Avatar, Button, Card, Input, Switch, Tabs, Textarea } from '$lib/components/ui';
	import { onMount } from 'svelte';

	let loading = false;
	let activeTab = 'profile';

	// Profile form
	let displayName = '';
	let username = '';
	let bio = '';
	let location = '';
	let website = '';
	let avatarFile: File | null = null;
	let coverFile: File | null = null;

	// Subscription settings
	let subscriptionPrice = '';
	let showSubscribersCount = true;
	let allowMessages = true;
	let welcomeMessage = '';

	// Privacy settings
	let showActivityStatus = true;
	let showOnlineStatus = true;
	let allowComments = true;

	// Notification settings
	let emailNotifications = true;
	let pushNotifications = true;
	let newSubscriberNotify = true;
	let newTipNotify = true;
	let newCommentNotify = true;
	let newMessageNotify = true;

	// Security
	let currentPassword = '';
	let newPassword = '';
	let confirmPassword = '';
	let twoFactorEnabled = false;

	const tabs = [
		{ id: 'profile', label: '👤 Profil' },
		{ id: 'subscription', label: '💰 Abonelik' },
		{ id: 'privacy', label: '🔒 Gizlilik' },
		{ id: 'notifications', label: '🔔 Bildirimler' },
		{ id: 'security', label: '🛡️ Güvenlik' },
	];

	async function loadSettings() {
		if (!$authStore.user) return;

		displayName = $authStore.user.display_name || '';
		username = $authStore.user.username || '';
		bio = $authStore.user.bio || '';
		location = $authStore.user.location || '';
		website = $authStore.user.website || '';
		subscriptionPrice = ($authStore.user.subscription_price || 0).toString();

		// Load additional settings from API
		try {
			const settings = await api.users.getSettings();
			showSubscribersCount = settings.show_subscribers_count ?? true;
			allowMessages = settings.allow_messages ?? true;
			welcomeMessage = settings.welcome_message || '';
			showActivityStatus = settings.show_activity_status ?? true;
			showOnlineStatus = settings.show_online_status ?? true;
			allowComments = settings.allow_comments ?? true;
			emailNotifications = settings.email_notifications ?? true;
			pushNotifications = settings.push_notifications ?? true;
			newSubscriberNotify = settings.new_subscriber_notify ?? true;
			newTipNotify = settings.new_tip_notify ?? true;
			newCommentNotify = settings.new_comment_notify ?? true;
			newMessageNotify = settings.new_message_notify ?? true;
			twoFactorEnabled = settings.two_factor_enabled ?? false;
		} catch (err) {
			console.error('Failed to load settings:', err);
		}
	}

	async function saveProfile() {
		loading = true;
		try {
			await api.users.updateProfile({
				display_name: displayName,
				bio,
				location,
				website,
			});

			// Upload avatar if changed
			if (avatarFile) {
				await api.users.uploadAvatar(avatarFile);
			}

			// Upload cover if changed
			if (coverFile) {
				await api.users.uploadCover(coverFile);
			}

			alert('Profile updated successfully!');
		} catch (err: any) {
			alert(err.message || 'Failed to update profile');
		} finally {
			loading = false;
		}
	}

	async function saveSubscriptionSettings() {
		loading = true;
		try {
			await api.users.updateSettings({
				subscription_price: parseFloat(subscriptionPrice) || 0,
				show_subscribers_count: showSubscribersCount,
				allow_messages: allowMessages,
				welcome_message: welcomeMessage,
			});
			alert('Settings saved!');
		} catch (err: any) {
			alert(err.message || 'Failed to save settings');
		} finally {
			loading = false;
		}
	}

	async function savePrivacySettings() {
		loading = true;
		try {
			await api.users.updateSettings({
				show_activity_status: showActivityStatus,
				show_online_status: showOnlineStatus,
				allow_comments: allowComments,
			});
			alert('Settings saved!');
		} catch (err: any) {
			alert(err.message || 'Failed to save settings');
		} finally {
			loading = false;
		}
	}

	async function saveNotificationSettings() {
		loading = true;
		try {
			await api.users.updateSettings({
				email_notifications: emailNotifications,
				push_notifications: pushNotifications,
				new_subscriber_notify: newSubscriberNotify,
				new_tip_notify: newTipNotify,
				new_comment_notify: newCommentNotify,
				new_message_notify: newMessageNotify,
			});
			alert('Settings saved!');
		} catch (err: any) {
			alert(err.message || 'Failed to save settings');
		} finally {
			loading = false;
		}
	}

	async function changePassword() {
		if (newPassword !== confirmPassword) {
			alert('Passwords do not match');
			return;
		}

		loading = true;
		try {
			await api.auth.changePassword({
				current_password: currentPassword,
				new_password: newPassword,
			});
			alert('Password changed successfully!');
			currentPassword = '';
			newPassword = '';
			confirmPassword = '';
		} catch (err: any) {
			alert(err.message || 'Failed to change password');
		} finally {
			loading = false;
		}
	}

	async function toggle2FA() {
		loading = true;
		try {
			if (twoFactorEnabled) {
				await api.auth.disable2FA();
				twoFactorEnabled = false;
				alert('2FA disabled');
			} else {
				const response = await api.auth.setup2FA();
				// Show QR code modal
				alert('2FA setup initiated. Check your authenticator app.');
				twoFactorEnabled = true;
			}
		} catch (err: any) {
			alert(err.message || 'Failed to toggle 2FA');
		} finally {
			loading = false;
		}
	}

	function handleAvatarChange(e: Event) {
		const target = e.target as HTMLInputElement;
		if (target.files && target.files[0]) {
			avatarFile = target.files[0];
		}
	}

	function handleCoverChange(e: Event) {
		const target = e.target as HTMLInputElement;
		if (target.files && target.files[0]) {
			coverFile = target.files[0];
		}
	}

	onMount(() => {
		if (!$authStore.user) {
			goto('/login');
			return;
		}
		loadSettings();
	});
</script>

<svelte:head>
	<title>Ayarlar | SadeceFanlar</title>
</svelte:head>

<div class="p-4">
	<h1 class="text-2xl font-bold text-neutral-900 dark:text-white mb-6">Ayarlar</h1>

	<Tabs {tabs} bind:activeTab>
		{#if activeTab === 'profile'}
			<Card class="p-6">
				<form on:submit|preventDefault={saveProfile} class="space-y-6">
					<!-- Avatar & Cover -->
					<div class="space-y-4">
						<div>
							<label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
							Profil Fotoğrafı
						</label>
						<div class="flex items-center gap-4">
							<Avatar
								src={avatarFile ? URL.createObjectURL(avatarFile) : $authStore.user?.avatar_url}
								alt={displayName}
								size="lg"
							/>
							<label class="cursor-pointer">
								<span class="text-sm text-primary hover:underline">Fotoğrafı değiştir</span>
									<input
										type="file"
										accept="image/*"
										class="hidden"
										on:change={handleAvatarChange}
									/>
								</label>
							</div>
						</div>

						<div>
							<label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
								Kapak Görseli
							</label>
							<div
								class="relative h-32 bg-neutral-100 dark:bg-neutral-800 rounded-lg overflow-hidden"
							>
								{#if coverFile || $authStore.user?.cover_url}
									<img
										src={coverFile ? URL.createObjectURL(coverFile) : $authStore.user?.cover_url}
										alt="Cover"
										class="w-full h-full object-cover"
									/>
								{/if}
								<label
									class="absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 hover:opacity-100 transition-opacity cursor-pointer"
								>
									<span class="text-white">Kapağı değiştir</span>
									<input
										type="file"
										accept="image/*"
										class="hidden"
										on:change={handleCoverChange}
									/>
								</label>
							</div>
						</div>
					</div>

					<Input label="Görünen Ad" bind:value={displayName} required />
					<Input label="Kullanıcı Adı" value={username} disabled />
					<Textarea label="Biyografi" bind:value={bio} maxLength={500} rows={4} />
					<Input label="Konum" bind:value={location} placeholder="Şehir, Ülke" />
					<Input label="Web Sitesi" type="url" bind:value={website} placeholder="https://" />

					<Button type="submit" disabled={loading}>
						{loading ? 'Kaydediliyor...' : 'Değişiklikleri Kaydet'}
					</Button>
				</form>
			</Card>
		{:else if activeTab === 'subscription'}
			<Card class="p-6">
				<form on:submit|preventDefault={saveSubscriptionSettings} class="space-y-6">
					<Input
						type="number"
						label="Aylık Abonelik Fiyatı ($)"
						bind:value={subscriptionPrice}
						placeholder="Ücretsiz için 0"
					/>
					<p class="text-xs text-neutral-500 -mt-4">
						Ücretsiz abonelik için 0 yazın. Platform %20 komisyon alır.
					</p>

					<Textarea
						label="Karşılama Mesajı"
						bind:value={welcomeMessage}
						placeholder="Yeni abonelere gönderilen mesaj..."
						rows={3}
					/>

					<div class="space-y-4">
						<Switch label="Profilde abone sayısını göster" bind:checked={showSubscribersCount} />
						<Switch label="Abonelerin mesaj göndermesine izin ver" bind:checked={allowMessages} />
					</div>

					<Button type="submit" disabled={loading}>
						{loading ? 'Kaydediliyor...' : 'Ayarları Kaydet'}
					</Button>
				</form>
			</Card>
		{:else if activeTab === 'privacy'}
			<Card class="p-6">
				<form on:submit|preventDefault={savePrivacySettings} class="space-y-6">
					<div class="space-y-4">
						<Switch label="Aktivite durumunu göster" bind:checked={showActivityStatus} />
						<Switch label="Çevrimiçi durumunu göster" bind:checked={showOnlineStatus} />
						<Switch label="Gönderilere yorum yapılmasına izin ver" bind:checked={allowComments} />
					</div>

					<Button type="submit" disabled={loading}>
						{loading ? 'Kaydediliyor...' : 'Ayarları Kaydet'}
					</Button>
				</form>
			</Card>
		{:else if activeTab === 'notifications'}
			<Card class="p-6">
				<form on:submit|preventDefault={saveNotificationSettings} class="space-y-6">
					<div class="space-y-4">
						<h3 class="font-medium text-neutral-900 dark:text-white">Kanallar</h3>
						<Switch label="E-posta bildirimleri" bind:checked={emailNotifications} />
						<Switch label="Anlık bildirimler" bind:checked={pushNotifications} />
					</div>

					<div class="space-y-4 pt-4 border-t border-neutral-200 dark:border-neutral-700">
						<h3 class="font-medium text-neutral-900 dark:text-white">Olaylar</h3>
						<Switch label="Yeni abone" bind:checked={newSubscriberNotify} />
						<Switch label="Yeni bahşiş alındı" bind:checked={newTipNotify} />
						<Switch label="Yeni yorum" bind:checked={newCommentNotify} />
						<Switch label="Yeni mesaj" bind:checked={newMessageNotify} />
					</div>

					<Button type="submit" disabled={loading}>
						{loading ? 'Kaydediliyor...' : 'Ayarları Kaydet'}
					</Button>
				</form>
			</Card>
		{:else if activeTab === 'security'}
			<div class="space-y-6">
				<Card class="p-6">
					<h3 class="font-medium text-neutral-900 dark:text-white mb-4">Şifre Değiştir</h3>
					<form on:submit|preventDefault={changePassword} class="space-y-4">
						<Input
							type="password"
							label="Mevcut Şifre"
							bind:value={currentPassword}
							required
						/>
						<Input
							type="password"
							label="Yeni Şifre"
							bind:value={newPassword}
							required
						/>
						<Input
							type="password"
							label="Yeni Şifre Tekrar"
							bind:value={confirmPassword}
							required
						/>
						<Button type="submit" disabled={loading}>
							{loading ? 'Değiştiriliyor...' : 'Şifreyi Değiştir'}
						</Button>
					</form>
				</Card>

				<Card class="p-6">
					<h3 class="font-medium text-neutral-900 dark:text-white mb-4">İki Faktörlü Doğrulama</h3>
					<p class="text-sm text-neutral-500 mb-4">
						Doğrulama uygulaması kullanarak hesabınıza ekstra güvenlik katın.
					</p>
					<div class="flex items-center justify-between">
						<div>
							<p class="font-medium text-neutral-900 dark:text-white">
								{twoFactorEnabled ? '2FA Aktif' : '2FA Kapalı'}
							</p>
							<p class="text-sm text-neutral-500">
								{twoFactorEnabled ? 'Hesabınız korunuyor' : 'Daha iyi güvenlik için etkinleştirin'}
							</p>
						</div>
						<Button
							variant={twoFactorEnabled ? 'outline' : 'default'}
							on:click={toggle2FA}
							disabled={loading}
						>
							{twoFactorEnabled ? 'Devre Dışı Bırak' : 'Etkinleştir'}
						</Button>
					</div>
				</Card>

				<Card class="p-6 border-red-200 dark:border-red-800">
					<h3 class="font-medium text-red-600 mb-4">Tehlikeli Bölge</h3>
					<p class="text-sm text-neutral-500 mb-4">
						Hesabınızı sildiğinizde geri dönüş yoktur. Lütfen emin olun.
					</p>
					<Button variant="danger">Hesabı Sil</Button>
				</Card>
			</div>
		{/if}
	</Tabs>
</div>
