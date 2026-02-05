<script lang="ts">
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';
	import { api } from '$lib/api';
	import { Button, Card, Input, Switch, Textarea } from '$lib/components/ui';
	import { cn, formatCurrency } from '$lib/utils';
	import { onMount } from 'svelte';

	let content = '';
	let price = '';
	let isPremium = false;
	let scheduledAt = '';
	let mediaFiles: File[] = [];
	let mediaPreviews: string[] = [];
	let loading = false;
	let uploading = false;
	let uploadProgress = 0;

	function handleFileSelect(e: Event) {
		const target = e.target as HTMLInputElement;
		if (target.files) {
			const files = Array.from(target.files);
			mediaFiles = [...mediaFiles, ...files];

			// Generate previews
			files.forEach((file) => {
				const reader = new FileReader();
				reader.onload = (e) => {
					mediaPreviews = [...mediaPreviews, e.target?.result as string];
				};
				reader.readAsDataURL(file);
			});
		}
	}

	function removeMedia(index: number) {
		mediaFiles = mediaFiles.filter((_, i) => i !== index);
		mediaPreviews = mediaPreviews.filter((_, i) => i !== index);
	}

	async function handleSubmit() {
		if (!content && mediaFiles.length === 0) return;

		loading = true;

		try {
			// Upload media files first
			const mediaIds: string[] = [];
			
			if (mediaFiles.length > 0) {
				uploading = true;
				for (let i = 0; i < mediaFiles.length; i++) {
					const file = mediaFiles[i];
					try {
						const response = await api.posts.uploadMedia(file);
						if (response?.id) {
							mediaIds.push(response.id);
						}
					} catch {
						// Skip failed upload
					}
					uploadProgress = ((i + 1) / mediaFiles.length) * 100;
				}
				uploading = false;
			}

			// Create post
			const post = await api.posts.create({
				content,
				media_ids: mediaIds.length > 0 ? mediaIds : undefined,
				is_premium: isPremium,
				price: isPremium ? parseFloat(price) || 0 : undefined,
				scheduled_at: scheduledAt || undefined,
			});

			goto(`/post/${post.id}`);
		} catch (err: any) {
			alert(err.message || 'Failed to create post');
		} finally {
			loading = false;
			uploading = false;
		}
	}

	onMount(() => {
		if (!$authStore.user) {
			goto('/login');
		}
	});
</script>

<svelte:head>
	<title>Yeni Gönderi | SadeceFanlar</title>
</svelte:head>

<div class="p-4 max-w-2xl mx-auto">
	<div class="flex items-center justify-between mb-6">
		<h1 class="text-2xl font-bold text-neutral-900 dark:text-white">Gönderi Oluştur</h1>
		<Button variant="ghost" href="/">İptal</Button>
	</div>

	<Card class="p-6">
		<form on:submit|preventDefault={handleSubmit} class="space-y-6">
			<Textarea
				placeholder="Aklınızdan ne geçiyor?"
				bind:value={content}
				rows={6}
				maxLength={5000}
			/>

			<!-- Media Upload -->
			<div>
				<label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
					Medya (isteğe bağlı)
				</label>

				{#if mediaPreviews.length > 0}
					<div class="grid grid-cols-3 gap-2 mb-4">
						{#each mediaPreviews as preview, i}
							<div class="relative aspect-square rounded-lg overflow-hidden bg-neutral-100 dark:bg-neutral-800">
								{#if mediaFiles[i]?.type.startsWith('video/')}
									<video src={preview} class="w-full h-full object-cover">
										<track kind="captions" />
									</video>
								{:else}
									<img src={preview} alt="Preview" class="w-full h-full object-cover" />
								{/if}
								<button
									type="button"
									class="absolute top-1 right-1 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-sm hover:bg-red-600 transition-colors"
									on:click={() => removeMedia(i)}
								>
									×
								</button>
							</div>
						{/each}
					</div>
				{/if}

				<label
					class="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-neutral-300 dark:border-neutral-600 rounded-lg cursor-pointer hover:border-primary transition-colors"
				>
					<div class="flex flex-col items-center justify-center pt-5 pb-6">
						<span class="text-3xl mb-2">📷</span>
						<p class="text-sm text-neutral-500">
							Fotoğraf veya video yüklemek için tıklayın
						</p>
						<p class="text-xs text-neutral-400">
							PNG, JPG, GIF, MP4 maksimum 100MB
						</p>
					</div>
					<input
						type="file"
						accept="image/*,video/*"
						multiple
						class="hidden"
						on:change={handleFileSelect}
					/>
				</label>
			</div>

			<!-- Premium Content -->
			<div class="space-y-4 p-4 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
				<Switch label="Premium İçerik (İzle başına öde)" bind:checked={isPremium} />

				{#if isPremium}
					<Input
						type="number"
						label="Fiyat ($)"
						placeholder="0.00"
						bind:value={price}
						min="0"
						step="0.01"
					/>
					<p class="text-xs text-neutral-500">
						Sadece aboneler veya ödeme yapan kullanıcılar bu içeriği görebilir.
						Abone olmayanlar bulanık bir önizleme görür.
					</p>
				{/if}
			</div>

			<!-- Schedule -->
			<div>
				<Input
					type="datetime-local"
					label="Gönderiyi Zamanla (isteğe bağlı)"
					bind:value={scheduledAt}
				/>
			</div>

			<!-- Upload Progress -->
			{#if uploading}
				<div class="space-y-2">
					<div class="flex justify-between text-sm text-neutral-500">
						<span>Medya yükleniyor...</span>
						<span>{Math.round(uploadProgress)}%</span>
					</div>
					<div class="w-full h-2 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
						<div
							class="h-full bg-primary transition-all"
							style:width="{uploadProgress}%"
						/>
					</div>
				</div>
			{/if}

			<!-- Submit -->
			<div class="flex gap-2">
				<Button
					type="submit"
					class="flex-1"
					disabled={loading || (!content && mediaFiles.length === 0)}
				>
					{loading ? 'Gönderiliyor...' : scheduledAt ? 'Gönderiyi Zamanla' : 'Şimdi Paylaş'}
				</Button>
			</div>
		</form>
	</Card>
</div>
