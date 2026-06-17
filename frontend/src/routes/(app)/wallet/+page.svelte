<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';
	import { waitForAuth } from '$lib/utils/auth';
	import { api } from '$lib/api';
	import { PaymentModal } from '$lib/components/features';
	import { Button, Card, Input, Spinner, Tabs } from '$lib/components/ui';
	import { cn, formatCurrency, formatCrypto, timeAgo } from '$lib/utils';
	import type { Wallet, Transaction } from '$lib/types';

	let wallet: Wallet | null = null;
	let transactions: Transaction[] = [];
	let loading = true;
	let activeTab = 'overview';
	let showDepositModal = false;
	let depositAmount = 0;
	let withdrawAmount = '';
	let withdrawAddress = '';
	let withdrawCurrency: 'xmr' | 'btc' = 'xmr';
	let withdrawing = false;

	const tabs = [
		{ id: 'overview', label: 'Genel' },
		{ id: 'deposit', label: 'Yatır' },
		{ id: 'withdraw', label: 'Çek' },
		{ id: 'history', label: 'Geçmiş' },
	];

	async function loadWallet() {
		loading = true;
		try {
			wallet = await api.wallet.get();
			const response = await api.wallet.getTransactions();
			transactions = response.items;
		} catch (err) {
			console.error('Failed to load wallet:', err);
		} finally {
			loading = false;
		}
	}

	async function handleWithdraw() {
		if (!withdrawAmount || !withdrawAddress || withdrawing) return;
		
		withdrawing = true;
		try {
			await api.wallet.withdraw({
				amount: parseFloat(withdrawAmount),
				currency: withdrawCurrency,
				address: withdrawAddress,
			});
			
			// Refresh wallet
			await loadWallet();
			
			// Reset form
			withdrawAmount = '';
			withdrawAddress = '';
			
			alert('Withdrawal request submitted!');
		} catch (err: any) {
			alert(err.message || 'Withdrawal failed');
		} finally {
			withdrawing = false;
		}
	}

	function getTransactionIcon(type: string): string {
		switch (type) {
			case 'deposit':
				return '💰';
			case 'withdrawal':
				return '📤';
			case 'subscription':
				return '⭐';
			case 'tip':
				return '🎁';
			case 'unlock':
				return '🔓';
			case 'referral':
				return '👥';
			default:
				return '💵';
		}
	}

	onMount(async () => {
		await waitForAuth();
		if (!$authStore.user) {
			goto('/login');
			return;
		}
		loadWallet();
	});
</script>

<svelte:head>
	<title>Cüzdan | SadeceFanlar</title>
</svelte:head>

<div>
	<h1 class="text-xl font-semibold mb-6">Cüzdan</h1>

	{#if loading}
		<div class="flex items-center justify-center py-12">
			<Spinner size="lg" />
		</div>
	{:else if wallet}
		<!-- Balance Cards -->
		<div class="grid grid-cols-2 gap-4 mb-6">
			<Card class="p-4">
				<p class="text-sm text-neutral-500 mb-1">Kullanılabilir Bakiye</p>
				<p class="text-2xl font-bold text-neutral-900 dark:text-white">
					{formatCurrency(wallet.balance)}
				</p>
			</Card>
			<Card class="p-4">
				<p class="text-sm text-neutral-500 mb-1">Bekleyen</p>
				<p class="text-2xl font-bold text-yellow-500">
					{formatCurrency(wallet.pending_balance || 0)}
				</p>
			</Card>
		</div>

		<!-- Earnings Stats -->
		<Card class="p-4 mb-6">
			<h3 class="font-semibold text-neutral-900 dark:text-white mb-4">Kazanç Özeti</h3>
			<div class="grid grid-cols-3 gap-4 text-center">
				<div>
					<p class="text-xl font-bold text-green-500">
						{formatCurrency(wallet.total_earnings || 0)}
					</p>
					<p class="text-xs text-neutral-500">Toplam Kazanç</p>
				</div>
				<div>
					<p class="text-xl font-bold text-neutral-900 dark:text-white">
						{formatCurrency(wallet.this_month_earnings || 0)}
					</p>
					<p class="text-xs text-neutral-500">Bu Ay</p>
				</div>
				<div>
					<p class="text-xl font-bold text-neutral-900 dark:text-white">
						{formatCurrency(wallet.total_withdrawn || 0)}
					</p>
					<p class="text-xs text-neutral-500">Çekilen</p>
				</div>
			</div>
		</Card>

		<Tabs {tabs} bind:activeTab>
			{#if activeTab === 'overview'}
				<!-- Recent Transactions -->
				<div class="space-y-4">
					<h3 class="font-semibold text-neutral-900 dark:text-white">Son Aktivite</h3>
					{#if transactions.length === 0}
						<p class="text-neutral-500 text-center py-8">Henüz işlem yok</p>
					{:else}
						{#each transactions.slice(0, 5) as tx}
							<div class="flex items-center gap-3 p-3 bg-white dark:bg-neutral-900 rounded-lg">
								<span class="text-2xl">{getTransactionIcon(tx.type)}</span>
								<div class="flex-1">
									<p class="font-medium text-neutral-900 dark:text-white capitalize">
										{tx.type}
									</p>
									<p class="text-xs text-neutral-500">{timeAgo(tx.created_at)}</p>
								</div>
								<p
									class="font-semibold"
									class:text-green-500={tx.amount > 0}
									class:text-red-500={tx.amount < 0}
								>
									{tx.amount > 0 ? '+' : ''}{formatCurrency(tx.amount)}
								</p>
							</div>
						{/each}
					{/if}
				</div>
			{:else if activeTab === 'deposit'}
				<Card class="p-6">
					<h3 class="font-semibold text-neutral-900 dark:text-white mb-4">Para Yatır</h3>
					<p class="text-sm text-neutral-500 mb-6">
						Kripto para kullanarak cüzdanınıza para yatırın. Tüm ödemeler anonimdir.
					</p>

					<div class="grid grid-cols-2 gap-4 mb-6">
						{#each [10, 25, 50, 100] as amount}
							<button
								type="button"
									class={cn(
											'p-4 border-2 rounded-lg text-center transition-colors hover:border-primary',
											depositAmount === amount && 'bg-primary/5'
										)}
								class:border-primary={depositAmount === amount}
								class:border-neutral-200={depositAmount !== amount}
								class:dark:border-neutral-700={depositAmount !== amount}
								on:click={() => (depositAmount = amount)}
							>
								<p class="text-xl font-bold text-neutral-900 dark:text-white">
									{formatCurrency(amount)}
								</p>
							</button>
						{/each}
					</div>

					<Input
						type="number"
						label="Özel Miktar"
						placeholder="Miktar girin..."
						bind:value={depositAmount}
					/>

					<Button
						class="w-full mt-4"
						disabled={!depositAmount || depositAmount <= 0}
						on:click={() => (showDepositModal = true)}
					>
						Ödemeye Devam Et
					</Button>
				</Card>
			{:else if activeTab === 'withdraw'}
				<Card class="p-6">
					<h3 class="font-semibold text-neutral-900 dark:text-white mb-4">Para Çek</h3>
					<p class="text-sm text-neutral-500 mb-6">
						Kazançlarınızı kripto cüzdanınıza çekin. Minimum çekim: $10
					</p>

					<div class="space-y-4">
						<div>
							<label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
								Kripto Para
							</label>
							<div class="grid grid-cols-2 gap-2">
								<button
									type="button"
									class="p-3 border-2 rounded-lg text-center transition-colors {withdrawCurrency === 'xmr' ? 'border-primary bg-primary/5' : 'border-neutral-200 dark:border-neutral-700'}"
									on:click={() => (withdrawCurrency = 'xmr')}
								>
									🪙 Monero (XMR)
								</button>
								<button
									type="button"
									class="p-3 border-2 rounded-lg text-center transition-colors {withdrawCurrency === 'btc' ? 'border-primary bg-primary/5' : 'border-neutral-200 dark:border-neutral-700'}"
									on:click={() => (withdrawCurrency = 'btc')}
								>
									₿ Bitcoin (BTC)
								</button>
							</div>
						</div>

						<Input
							type="number"
							label="Miktar (USD)"
							placeholder="Miktar girin..."
							bind:value={withdrawAmount}
						/>

						<Input
							label={withdrawCurrency === 'xmr' ? 'Monero Adresi' : 'Bitcoin Adresi'}
							placeholder={withdrawCurrency === 'xmr' ? '4...' : 'bc1...'}
							bind:value={withdrawAddress}
						/>

						<div class="bg-neutral-50 dark:bg-neutral-800 rounded-lg p-4">
							<div class="flex justify-between text-sm">
								<span class="text-neutral-500">Kullanılabilir</span>
								<span class="text-neutral-900 dark:text-white">
									{formatCurrency(wallet.balance)}
								</span>
							</div>
							<div class="flex justify-between text-sm mt-2">
								<span class="text-neutral-500">Komisyon (%5)</span>
								<span class="text-neutral-900 dark:text-white">
									{formatCurrency(parseFloat(withdrawAmount || '0') * 0.05)}
								</span>
							</div>
							<div class="flex justify-between font-semibold mt-2 pt-2 border-t border-neutral-200 dark:border-neutral-700">
								<span>Alacağınız</span>
								<span class="text-green-500">
									{formatCurrency(parseFloat(withdrawAmount || '0') * 0.95)}
								</span>
							</div>
						</div>

						<Button
							class="w-full"
							disabled={!withdrawAmount || !withdrawAddress || parseFloat(withdrawAmount) < 10 || parseFloat(withdrawAmount) > wallet.balance || withdrawing}
							on:click={handleWithdraw}
						>
							{withdrawing ? 'İşleniyor...' : 'Çekim Talebi Oluştur'}
						</Button>

						<p class="text-xs text-neutral-400 text-center">
							Çekim talepleri yönetici onayından sonra 24-48 saat içinde işlenir.
						</p>
					</div>
				</Card>
			{:else if activeTab === 'history'}
				<div class="space-y-2">
					{#if transactions.length === 0}
						<p class="text-neutral-500 text-center py-8">Henüz işlem yok</p>
					{:else}
						{#each transactions as tx}
							<div class="flex items-center gap-3 p-4 bg-white dark:bg-neutral-900 rounded-lg">
								<span class="text-2xl">{getTransactionIcon(tx.type)}</span>
								<div class="flex-1">
									<p class="font-medium text-neutral-900 dark:text-white capitalize">
										{tx.type}
										{#if tx.description}
											<span class="text-sm text-neutral-500 font-normal">
												- {tx.description}
											</span>
										{/if}
									</p>
									<p class="text-xs text-neutral-500">{timeAgo(tx.created_at)}</p>
								</div>
								<div class="text-right">
									<p
										class="font-semibold"
										class:text-green-500={tx.amount > 0}
										class:text-red-500={tx.amount < 0}
									>
										{tx.amount > 0 ? '+' : ''}{formatCurrency(tx.amount)}
									</p>
									<p class="text-xs text-neutral-400 capitalize">{tx.status}</p>
								</div>
							</div>
						{/each}
					{/if}
				</div>
			{/if}
		</Tabs>

		<!-- Deposit Modal -->
		<PaymentModal
			bind:open={showDepositModal}
			amount={depositAmount}
			description="Wallet Deposit"
			type="deposit"
			on:success={() => {
				showDepositModal = false;
				loadWallet();
			}}
		/>
	{/if}
</div>
