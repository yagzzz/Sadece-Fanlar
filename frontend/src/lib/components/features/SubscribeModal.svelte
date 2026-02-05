<script lang="ts">
	import { cn, formatCurrency } from '$lib/utils';
	import { Avatar, Badge, Button, Modal, Input, Spinner } from '$lib/components/ui';
	import type { User, SubscriptionPlan } from '$lib/types';
	import { createEventDispatcher } from 'svelte';
	import { api } from '$lib/api';

	export let open = false;
	export let user: User;
	let className = '';
	export { className as class };

	const dispatch = createEventDispatcher();

	let loading = true;
	let plans: SubscriptionPlan[] = [];
	let selectedPlan: SubscriptionPlan | null = null;
	let selectedBundle: { months: number; discount: number } | null = null;

	const bundles = [
		{ months: 1, discount: 0 },
		{ months: 3, discount: 10 },
		{ months: 6, discount: 15 },
		{ months: 12, discount: 20 },
	];

	async function loadPlans() {
		loading = true;
		try {
			plans = await api.subscriptions.getCreatorPlans(user.id);
			if (plans.length > 0) {
				selectedPlan = plans[0];
			}
		} catch (err) {
			console.error('Failed to load plans:', err);
		} finally {
			loading = false;
		}
	}

	function calculatePrice(basePrice: number, months: number, discount: number) {
		const total = basePrice * months;
		return total - (total * discount) / 100;
	}

	function handleSubscribe() {
		if (!selectedPlan) return;
		
		const months = selectedBundle?.months || 1;
		const price = calculatePrice(selectedPlan.price, months, selectedBundle?.discount || 0);
		
		dispatch('subscribe', {
			plan: selectedPlan,
			months,
			price,
			user,
		});
	}

	function handleClose() {
		open = false;
	}

	$: if (open && !plans.length && !loading) {
		loadPlans();
	}

	$: selectedBundle = selectedBundle || bundles[0];
</script>

<Modal {open} on:close={handleClose} title="{user.display_name} Aboneliği" class={className}>
	{#if loading}
		<div class="flex items-center justify-center py-12">
			<Spinner size="lg" />
		</div>
	{:else}
		<div class="space-y-6">
			<!-- Creator Info -->
			<div class="flex items-center gap-3 pb-4 border-b border-neutral-200 dark:border-neutral-700">
				<Avatar src={user.avatar_url} alt={user.display_name} size="lg" />
				<div>
					<div class="flex items-center gap-1">
						<h3 class="font-semibold text-neutral-900 dark:text-white">{user.display_name}</h3>
						{#if user.is_verified}
							<Badge variant="primary" class="text-xs">✓</Badge>
						{/if}
					</div>
					<p class="text-sm text-neutral-500">@{user.username}</p>
					<p class="text-sm text-neutral-500">
						{user.posts_count || 0} gönderi · {user.subscribers_count || 0} abone
					</p>
				</div>
			</div>

			<!-- Plans -->
			{#if plans.length > 1}
				<div>
					<h4 class="text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">Plan Seçin</h4>
					<div class="grid grid-cols-1 gap-2">
						{#each plans as plan}
							<button
								type="button"
								class={cn(
									'p-4 rounded-lg border-2 text-left transition-all',
									selectedPlan?.id === plan.id
										? 'border-primary bg-primary/5'
										: 'border-neutral-200 dark:border-neutral-700 hover:border-primary/50'
								)}
								on:click={() => (selectedPlan = plan)}
							>
								<div class="flex items-center justify-between">
									<div>
										<p class="font-medium text-neutral-900 dark:text-white">{plan.name}</p>
										{#if plan.description}
											<p class="text-sm text-neutral-500">{plan.description}</p>
										{/if}
									</div>
									<p class="font-bold text-primary">{formatCurrency(plan.price)}/mo</p>
								</div>
							</button>
						{/each}
					</div>
				</div>
			{/if}

			<!-- Bundles -->
			{#if selectedPlan}
				<div>
					<h4 class="text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
						Abonelik Süresi
					</h4>
					<div class="grid grid-cols-2 gap-2">
						{#each bundles as bundle}
							{@const price = calculatePrice(selectedPlan.price, bundle.months, bundle.discount)}
							<button
								type="button"
								class={cn(
									'p-3 rounded-lg border-2 text-center transition-all relative',
									selectedBundle?.months === bundle.months
										? 'border-primary bg-primary/5'
										: 'border-neutral-200 dark:border-neutral-700 hover:border-primary/50'
								)}
								on:click={() => (selectedBundle = bundle)}
							>
								{#if bundle.discount > 0}
									<Badge variant="success" class="absolute -top-2 -right-2 text-xs">
										-{bundle.discount}%
									</Badge>
								{/if}
								<p class="font-medium text-neutral-900 dark:text-white">
									{bundle.months} {bundle.months === 1 ? 'Ay' : 'Ay'}
								</p>
								<p class="text-sm text-primary font-bold">{formatCurrency(price)}</p>
								{#if bundle.months > 1}
									<p class="text-xs text-neutral-500">
										{formatCurrency(price / bundle.months)}/mo
									</p>
								{/if}
							</button>
						{/each}
					</div>
				</div>
			{/if}

			<!-- Total -->
			{#if selectedPlan && selectedBundle}
				{@const totalPrice = calculatePrice(selectedPlan.price, selectedBundle.months, selectedBundle.discount)}
				<div class="bg-neutral-50 dark:bg-neutral-800 rounded-lg p-4">
					<div class="flex items-center justify-between mb-2">
						<span class="text-neutral-600 dark:text-neutral-400">
							{selectedPlan.name} × {selectedBundle.months} ay
						</span>
						<span class="text-neutral-600 dark:text-neutral-400">
							{formatCurrency(selectedPlan.price * selectedBundle.months)}
						</span>
					</div>
					{#if selectedBundle.discount > 0}
						<div class="flex items-center justify-between mb-2 text-green-500">
							<span>İndirim ({selectedBundle.discount}%)</span>
							<span>-{formatCurrency((selectedPlan.price * selectedBundle.months * selectedBundle.discount) / 100)}</span>
						</div>
					{/if}
					<div class="flex items-center justify-between pt-2 border-t border-neutral-200 dark:border-neutral-700">
						<span class="font-semibold text-neutral-900 dark:text-white">Toplam</span>
						<span class="text-xl font-bold text-primary">{formatCurrency(totalPrice)}</span>
					</div>
				</div>
			{/if}

			<!-- Abone Ol Butonu -->
			<Button class="w-full" size="lg" on:click={handleSubscribe} disabled={!selectedPlan}>
				Abone Ol
			</Button>

			<p class="text-xs text-neutral-400 text-center">
				🔒 Monero veya Bitcoin ile anonim ödeme yapın. İstediğiniz zaman iptal edin.
			</p>
		</div>
	{/if}
</Modal>
