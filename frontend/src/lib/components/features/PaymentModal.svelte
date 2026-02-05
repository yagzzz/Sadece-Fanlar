<script lang="ts">
	import { cn, formatCrypto, formatCurrency } from '$lib/utils';
	import { Button, Input, Modal, Spinner, Tabs } from '$lib/components/ui';
	import { paymentApi } from '$lib/api';
	import { createEventDispatcher, onDestroy } from 'svelte';

	export let open = false;
	export let amount: number;
	export let description = '';
	export let type: 'subscription' | 'tip' | 'unlock' | 'deposit' = 'tip';
	export let targetUserId: string | undefined = undefined;
	export let postId: string | undefined = undefined;
	let className = '';
	export { className as class };

	const dispatch = createEventDispatcher();

	let activeTab = 'monero';
	let loading = false;
	let paymentData: {
		request_id?: string;
		address?: string;
		payment_id?: string;
		amount_crypto?: number;
		invoice_url?: string;
		expires_at?: string;
	} | null = null;
	let error = '';
	let checkInterval: ReturnType<typeof setInterval>;

	const tabs = [
		{ id: 'monero', label: '🪙 Monero (XMR)' },
		{ id: 'btcpay', label: '₿ Bitcoin' },
	];

	async function initPayment() {
		loading = true;
		error = '';

		try {
			if (activeTab === 'monero') {
				const response = (await paymentApi.createDeposit(amount, 'monero')) as { data?: any };
				paymentData = {
					request_id: response.data?.id,
					address: response.data?.monero_integrated_address,
					payment_id: response.data?.monero_payment_id,
					amount_crypto: response.data?.amount_crypto,
					expires_at: response.data?.expires_at,
				};
			} else {
				const response = (await paymentApi.createDeposit(amount, 'btcpay')) as { data?: any };
				paymentData = {
					request_id: response.data?.id,
					invoice_url: response.data?.btcpay_checkout_url,
					expires_at: response.data?.expires_at,
				};
			}

			// Start checking for payment
			startPaymentCheck();
		} catch (err: any) {
			error = err.message || 'Failed to initialize payment';
		} finally {
			loading = false;
		}
	}

	function startPaymentCheck() {
		checkInterval = setInterval(async () => {
			try {
				// Check payment status
				if (paymentData?.request_id) {
					const status = (await paymentApi.checkPaymentStatus(paymentData.request_id)) as { data?: any };
					if (status.data?.status === 'confirmed' || status.data?.status === 'completed') {
						handlePaymentSuccess();
					}
				}
			} catch (err) {
				console.error('Payment check error:', err);
			}
		}, 5000); // Check every 5 seconds
	}

	function handlePaymentSuccess() {
		clearInterval(checkInterval);
		dispatch('success', { type, amount, targetUserId, postId });
		open = false;
	}

	function handleClose() {
		clearInterval(checkInterval);
		paymentData = null;
		error = '';
		open = false;
	}

	function copyToClipboard(text: string) {
		navigator.clipboard.writeText(text);
	}

	onDestroy(() => {
		if (checkInterval) clearInterval(checkInterval);
	});

	$: if (open && !paymentData && !loading) {
		initPayment();
	}
</script>

<Modal {open} on:close={handleClose} title="Ödemeyi Tamamla" class={className}>
	<div class="space-y-4">
		<div class="text-center pb-4 border-b border-neutral-200 dark:border-neutral-700">
			<p class="text-sm text-neutral-500 mb-1">{description || 'Ödeme'}</p>
			<p class="text-3xl font-bold text-neutral-900 dark:text-white">{formatCurrency(amount)}</p>
		</div>

		<Tabs {tabs} bind:activeTab on:change={() => { paymentData = null; initPayment(); }}>
			{#if loading}
				<div class="flex items-center justify-center py-12">
					<Spinner size="lg" />
				</div>
			{:else if error}
				<div class="text-center py-8">
					<p class="text-red-500 mb-4">{error}</p>
					<Button on:click={initPayment}>Tekrar Dene</Button>
				</div>
			{:else if paymentData}
				<div class="space-y-4">
					{#if activeTab === 'monero'}
						<!-- Monero Ödeme -->
						<div class="bg-neutral-50 dark:bg-neutral-800 rounded-lg p-4 text-center">
							<p class="text-sm text-neutral-500 mb-2">Tam olarak şu miktarı gönderin</p>
							<p class="text-2xl font-mono font-bold text-orange-500 mb-2">
								{formatCrypto(paymentData.amount_crypto || 0, 'XMR')}
							</p>
							<p class="text-sm text-neutral-500">bu adrese</p>
						</div>

						<div class="relative">
							<Input
								value={paymentData.address}
								readonly
								class="font-mono text-xs pr-16"
							/>
							<button
								type="button"
								class="absolute right-2 top-1/2 -translate-y-1/2 text-sm text-primary hover:text-primary/80"
								on:click={() => copyToClipboard(paymentData?.address || '')}
							>
								Kopyala
							</button>
						</div>

						{#if paymentData.payment_id}
							<div>
								<p class="text-xs text-neutral-500 mb-1">Ödeme ID'si (işleme dahil edin)</p>
								<div class="relative">
									<Input
										value={paymentData.payment_id}
										readonly
										class="font-mono text-xs pr-16"
									/>
									<button
										type="button"
										class="absolute right-2 top-1/2 -translate-y-1/2 text-sm text-primary hover:text-primary/80"
										on:click={() => copyToClipboard(paymentData?.payment_id || '')}
									>
										Kopyala
									</button>
								</div>
							</div>
						{/if}

						<div class="flex items-center justify-center gap-2 text-sm text-neutral-500">
							<Spinner size="sm" />
							<span>Ödeme onayı bekleniyor...</span>
						</div>
					{:else}
						<!-- BTCPay Fatura -->
						{#if paymentData.invoice_url}
							<div class="text-center">
								<p class="text-sm text-neutral-500 mb-4">
									Bitcoin ile ödemek için QR kodu tarayın veya butona tıklayın
								</p>
								<Button
									class="w-full"
									on:click={() => window.open(paymentData?.invoice_url, '_blank')}
								>
									Ödeme Sayfasını Aç
								</Button>
							</div>
						{/if}
					{/if}

					{#if paymentData.expires_at}
						<p class="text-center text-xs text-neutral-400">
							Expires: {new Date(paymentData.expires_at).toLocaleString()}
						</p>
					{/if}
				</div>
			{/if}
		</Tabs>

		<div class="pt-4 border-t border-neutral-200 dark:border-neutral-700">
			<p class="text-xs text-neutral-400 text-center">
				🔒 All payments are anonymous and secure. No personal information required.
			</p>
		</div>
	</div>
</Modal>
