/**
 * TypeScript Types for Sadece Fanlar
 */

export interface User {
	id: string;
	username: string;
	email?: string;
	display_name?: string;
	bio?: string;
	avatar_url?: string;
	cover_url?: string;
	is_creator: boolean;
	is_verified?: boolean;
	is_verified_creator?: boolean;
	role?: string;
	is_email_verified: boolean;
	is_free_profile?: boolean;
	is_following?: boolean;
	is_subscribed?: boolean;
	is_blocked?: boolean;
	is_me?: boolean;
	subscription_price?: number;
	subscribers_count: number;
	subscriptions_count: number;
	posts_count: number;
	media_count?: number;
	likes_count: number;
	created_at: string;
	website?: string;
	website_url?: string;
	location?: string;
}

export interface Post {
	id: string;
	author_id?: string;
	author?: User;
	user_id?: string;
	user?: User;
	content?: string;
	text?: string;
	text_html?: string;
	is_ppv: boolean;
	ppv_price?: number;
	is_premium?: boolean;
	price?: number;
	is_pinned: boolean;
	visibility?: 'public' | 'subscribers' | 'ppv';
	likes_count: number;
	comments_count: number;
	tips_total: number;
	media: Media[];
	is_liked: boolean;
	is_bookmarked: boolean;
	is_unlocked: boolean;
	created_at: string;
	updated_at?: string;
}

export interface Media {
	id: string;
	type: 'image' | 'video' | 'audio' | 'file';
	url: string;
	thumbnail_url?: string;
	blur_url?: string;
	width?: number;
	height?: number;
	duration?: number;
	is_blurred: boolean;
}

export interface Comment {
	id: string;
	post_id: string;
	user_id: string;
	user?: User;
	content: string;
	likes_count: number;
	is_liked: boolean;
	created_at: string;
}

export interface Subscription {
	id: string;
	subscriber_id: string;
	creator_id: string;
	subscriber?: User;
	creator?: User;
	type: 'free' | 'paid' | 'trial';
	status: 'active' | 'cancelled' | 'expired';
	price: number;
	started_at: string;
	expires_at?: string;
	auto_renew: boolean;
}

export interface SubscriptionPlan {
	id: string;
	creator_id: string;
	name: string;
	description?: string;
	price: number;
	duration_months: number;
	features?: string[];
	trial_days?: number;
	discount_percent?: number;
	is_active: boolean;
	is_public: boolean;
}

export interface Conversation {
	id: string;
	other_user?: User;
	last_message?: string | Message;
	last_message_at?: string;
	unread_count: number;
	is_muted: boolean;
}

export interface Message {
	id: string;
	conversation_id: string;
	sender_id: string;
	sender?: User;
	content: string;
	is_ppv: boolean;
	ppv_price?: number;
	price?: number;
	is_unlocked: boolean;
	is_read?: boolean;
	read_at?: string;
	created_at: string;
	media?: Media[];
}

export interface Notification {
	id: string;
	type: string;
	title: string;
	message: string;
	body?: string;
	image_url?: string;
	reference_type?: string;
	reference_id?: string;
	actor?: User;
	data?: Record<string, any>;
	is_read?: boolean;
	read_at?: string;
	created_at: string;
}

export interface Wallet {
	balance: number;
	pending_balance: number;
	total_earned: number;
	total_earnings?: number;
	this_month_earnings?: number;
	total_withdrawn: number;
	total_spent: number;
}

export interface Transaction {
	id: string;
	user_id: string;
	recipient_id?: string;
	type: string;
	status: string;
	amount: number;
	fee: number;
	net_amount: number;
	payment_method: string;
	crypto_amount?: number;
	crypto_currency?: string;
	description?: string;
	created_at: string;
}

export interface Withdrawal {
	id: string;
	amount: number;
	fee: number;
	net_amount: number;
	crypto_amount?: number;
	crypto_currency?: string;
	exchange_rate?: number;
	payment_method: string;
	address: string;
	status: 'pending' | 'processing' | 'completed' | 'rejected' | 'cancelled';
	tx_hash?: string;
	rejection_reason?: string;
	created_at: string;
	processed_at?: string;
}

export interface LiveStream {
	id: string;
	creator_id: string;
	creator?: User;
	title: string;
	description?: string;
	access: 'free' | 'subscribers' | 'paid';
	status: 'pending' | 'scheduled' | 'live' | 'ended' | 'cancelled';
	price?: number;
	viewer_count: number;
	total_viewers: number;
	tips_total: number;
	duration?: number;
	started_at?: string;
	ended_at?: string;
	created_at: string;
	has_access: boolean;
	stream_url?: string;
	thumbnail_url?: string;
}

export interface PaymentRequest {
	id: string;
	type: string;
	status: string;
	amount_usd: number;
	amount_crypto?: number;
	crypto_currency: string;
	exchange_rate?: number;
	payment_method: string;
	monero_address?: string;
	monero_payment_id?: string;
	monero_integrated_address?: string;
	btcpay_checkout_url?: string;
	expires_at: string;
	confirmations: number;
	created_at: string;
}

export interface PaginatedResponse<T> {
	items: T[];
	total: number;
	page: number;
	pages: number;
	has_next: boolean;
	has_prev: boolean;
}

export interface EarningsStats {
	total: number;
	subscriptions: number;
	tips: number;
	post_unlocks: number;
	messages: number;
	referrals: number;
	transaction_count: number;
	platform_fees: number;
	period: string;
}
