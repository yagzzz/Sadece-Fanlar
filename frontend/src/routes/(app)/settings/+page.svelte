<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth';
	import { api, adminApi } from '$lib/api';
	import { Avatar, Button, Card, Input, Switch, Tabs, Textarea } from '$lib/components/ui';
	import { waitForAuth, isAdmin } from '$lib/utils/auth';

	let loading = false;
	let activeTab = 'profile';

	// Site settings (admin)
	let siteName = '';
	let siteDescription = '';
	let platformFee = '';
	let withdrawalFee = '';
	let minWithdrawal = '';
	let minSubPrice = '';
	let maxSubPrice = '';
	let referralBonus = '';
	let maxUploadMb = '';
	let maintenanceMode = false;
	let registrationEnabled = true;
	let creatorVerificationRequired = false;
	let moneroEnabled = true;
	let btcpayEnabled = true;

	$: adminUser = isAdmin($authStore.user);
	$: if ($page.url.searchParams.get('tab') === 'site' && adminUser) {
		activeTab = 'site';
	}

	const tabs = [
		{ id: 'profile', label: 'Profil' },
		{ id: 'subscription', label: 'Abonelik' },
		{ id: 'privacy', label: 'Gizlilik' },
		{ id: 'notifications', label: 'Bildirimler' },
		{ id: 'security', label: 'Güvenlik' },
	];
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

	async function loadSiteSettings() {
		if (!adminUser) return;
		try {
			const s: any = await adminApi.getSiteSettings();
			siteName = s.site_name || '';
			siteDescription = s.site_description || '';
			platformFee = String(s.platform_fee_percent ?? '');
			withdrawalFee = String(s.withdrawal_fee_percent ?? '');
			minWithdrawal = String(s.min_withdrawal_amount ?? '');
			minSubPrice = String(s.min_subscription_price ?? '');
			maxSubPrice = String(s.max_subscription_price ?? '');
			referralBonus = String(s.referral_bonus_percent ?? '');
			maxUploadMb = String(s.max_upload_size_mb ?? '');
			maintenanceMode = !!s.maintenance_mode;
			registrationEnabled = s.registration_enabled !== false;
			creatorVerificationRequired = !!s.creator_verification_required;
			moneroEnabled = s.monero_enabled !== false;
			btcpayEnabled = s.btcpay_enabled !== false;
		} catch (err) {
			console.error('Site ayarları yüklenemedi:', err);
		}
	}

	async function saveSiteSettings() {
		loading = true;
		try {
			await adminApi.updateSiteSettings({
				site_name: siteName,
				site_description: siteDescription,
				platform_fee_percent: parseFloat(platformFee) || 0,
				withdrawal_fee_percent: parseFloat(withdrawalFee) || 0,
				min_withdrawal_amount: parseFloat(minWithdrawal) || 0,
				min_subscription_price: parseFloat(minSubPrice) || 0,
				max_subscription_price: parseFloat(maxSubPrice) || 0,
				referral_bonus_percent: parseFloat(referralBonus) || 0,
				max_upload_size_mb: parseInt(maxUploadMb) || 100,
				maintenance_mode: maintenanceMode,
				registration_enabled: registrationEnabled,
				creator_verification_required: creatorVerificationRequired,
				monero_enabled: moneroEnabled,
				btcpay_enabled: btcpayEnabled,
			});
			alert('Site ayarları kaydedildi');
		} catch (err: any) {
			alert(err.message || 'Kaydedilemedi');
		} finally {
			loading = false;
		}
	}

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

	onMount(async () => {
		await waitForAuth();
		if (!$authStore.user) {
			goto('/login');
			return;
		}
		await loadSettings();
		if (adminUser) await loadSiteSettings();
	});
</script>

<svelte:head>
	<title>Ayarlar | SadeceFanlar</title>
</svelte:head>

<div>
	<h1 class="text-xl font-semibold mb-6">Ayarlar</h1>

	<Tabs tabs={adminUser ? [...tabs, { id: 'site', label: 'Site Ayarları' }] : tabs} bind:activeTab>
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
						label="Aylık Abonelik Fiyatı (₺)"
						bind:value={subscriptionPrice}
						placeholder="Ücretsiz için 0"
					/>
					<p class="text-xs text-neutral-500 -mt-4">
						Ücretsiz abonelik için 0 yazın. Platform %5 komisyon alır.
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
		{:else if activeTab === 'site' && adminUser}
			<div class="space-y-4">
				<Card class="p-6">
					<h3 class="font-medium mb-4">Genel</h3>
					<form on:submit|preventDefault={saveSiteSettings} class="space-y-4">
						<Input label="Site adı" bind:value={siteName} />
						<Textarea label="Site açıklaması" bind:value={siteDescription} rows={3} />
						<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
							<Input label="Platform komisyonu (%)" type="number" bind:value={platformFee} />
							<Input label="Çekim ücreti (%)" type="number" bind:value={withdrawalFee} />
							<Input label="Min. çekim (₺)" type="number" bind:value={minWithdrawal} />
							<Input label="Min. abonelik (₺)" type="number" bind:value={minSubPrice} />
							<Input label="Max. abonelik (₺)" type="number" bind:value={maxSubPrice} />
							<Input label="Referans bonusu (%)" type="number" bind:value={referralBonus} />
							<Input label="Max. yükleme (MB)" type="number" bind:value={maxUploadMb} />
						</div>
						<div class="space-y-3 pt-2">
							<Switch label="Bakım modu" bind:checked={maintenanceMode} />
							<Switch label="Kayıt açık" bind:checked={registrationEnabled} />
							<Switch label="Üretici onayı zorunlu" bind:checked={creatorVerificationRequired} />
							<Switch label="Monero ödemeleri" bind:checked={moneroEnabled} />
							<Switch label="Bitcoin (BTCPay) ödemeleri" bind:checked={btcpayEnabled} />
						</div>
						<Button type="submit" disabled={loading}>Kaydet</Button>
					</form>
				</Card>
			</div>
		{/if}
	</Tabs>
</div>
