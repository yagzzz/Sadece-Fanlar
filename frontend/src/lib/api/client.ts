/**
 * API Client for Sadece Fanlar
 */

import { PUBLIC_API_URL, PUBLIC_WS_URL } from '$env/static/public';

const API_BASE = PUBLIC_API_URL ? `${PUBLIC_API_URL}/api/v1` : '/api/v1';

/**
 * WebSocket URL üretir. Tarayıcıda her zaman sayfanın servis edildiği host
 * üzerinden (nginx) bağlanır; böylece domain değişse bile (IP -> alan adı)
 * doğru çalışır ve sabit "localhost" hatası oluşmaz.
 */
export function wsUrl(path: string): string {
	const p = path.startsWith('/') ? path : `/${path}`;
	if (typeof window !== 'undefined') {
		const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
		return `${proto}//${window.location.host}${p}`;
	}
	return `${PUBLIC_WS_URL || ''}${p}`;
}

interface ApiResponse<T> {
	data?: T;
	error?: string;
	status: number;
}

function parseApiError(data: unknown): string {
	if (!data || typeof data !== 'object') return 'Bir hata oluştu';
	const detail = (data as { detail?: unknown }).detail;
	if (typeof detail === 'string') return detail;
	if (Array.isArray(detail)) {
		return detail
			.map((item) => {
				if (typeof item === 'string') return item;
				if (item && typeof item === 'object' && 'msg' in item) return String((item as { msg: string }).msg);
				return 'Geçersiz istek';
			})
			.join(', ');
	}
	return 'Bir hata oluştu';
}

class ApiClient {
	private token: string | null = null;
	users?: any;
	posts?: any;
	messages?: any;
	notifications?: any;
	wallet?: any;
	auth?: any;
	subscriptions?: any;
	payments?: any;
	streams?: any;

	setToken(token: string | null) {
		this.token = token;
		if (token) {
			localStorage.setItem('access_token', token);
		} else {
			localStorage.removeItem('access_token');
		}
	}

	getToken(): string | null {
		if (this.token) return this.token;
		if (typeof window !== 'undefined') {
			const stored = localStorage.getItem('access_token');
			if (stored) this.token = stored;
			return stored;
		}
		return null;
	}

	private async refreshAccessToken(): Promise<boolean> {
		if (typeof window === 'undefined') return false;
		const refreshToken = localStorage.getItem('refresh_token');
		if (!refreshToken) return false;

		try {
			const response = await fetch(`${API_BASE}/auth/refresh`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ refresh_token: refreshToken }),
			});
			const data = await response.json().catch(() => null);
			if (!response.ok || !data?.access_token) return false;
			this.setToken(data.access_token);
			if (data.refresh_token) {
				localStorage.setItem('refresh_token', data.refresh_token);
			}
			return true;
		} catch {
			return false;
		}
	}

	private async request<T>(
		endpoint: string,
		options: RequestInit = {},
		retry = true
	): Promise<ApiResponse<T>> {
		const token = this.getToken();
		const headers: HeadersInit = {
			'Content-Type': 'application/json',
			...(options.headers || {}),
		};

		if (token) {
			(headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
		}

		try {
			const response = await fetch(`${API_BASE}${endpoint}`, {
				...options,
				headers,
			});

			const data = await response.json().catch(() => null);

			if (response.status === 401 && retry && endpoint !== '/auth/refresh') {
				const refreshed = await this.refreshAccessToken();
				if (refreshed) {
					return this.request<T>(endpoint, options, false);
				}
				this.setToken(null);
				localStorage.removeItem('refresh_token');
			}

			if (!response.ok) {
				return {
					error: parseApiError(data),
					status: response.status,
				};
			}

			return { data, status: response.status };
		} catch {
			return {
				error: 'Sunucuya bağlanılamadı',
				status: 0,
			};
		}
	}

	// GET request
	async get<T>(endpoint: string): Promise<ApiResponse<T>> {
		return this.request<T>(endpoint, { method: 'GET' });
	}

	// POST request
	async post<T>(endpoint: string, body?: unknown): Promise<ApiResponse<T>> {
		return this.request<T>(endpoint, {
			method: 'POST',
			body: body ? JSON.stringify(body) : undefined,
		});
	}

	// PUT request
	async put<T>(endpoint: string, body?: unknown): Promise<ApiResponse<T>> {
		return this.request<T>(endpoint, {
			method: 'PUT',
			body: body ? JSON.stringify(body) : undefined,
		});
	}

	// PATCH request
	async patch<T>(endpoint: string, body?: unknown): Promise<ApiResponse<T>> {
		return this.request<T>(endpoint, {
			method: 'PATCH',
			body: body ? JSON.stringify(body) : undefined,
		});
	}

	// DELETE request
	async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
		return this.request<T>(endpoint, { method: 'DELETE' });
	}

	// File upload
	async upload<T>(endpoint: string, formData: FormData): Promise<ApiResponse<T>> {
		const token = this.getToken();
		const headers: HeadersInit = {};

		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}

		try {
			const response = await fetch(`${API_BASE}${endpoint}`, {
				method: 'POST',
				headers,
				body: formData,
			});

			const data = await response.json().catch(() => null);

			if (!response.ok) {
				return {
					error: data?.detail || 'Yükleme başarısız',
					status: response.status,
				};
			}

			return { data, status: response.status };
		} catch (error) {
			return {
				error: 'Sunucuya bağlanılamadı',
				status: 0,
			};
		}
	}
}

export const api = new ApiClient();

const unwrap = async <T>(promise: Promise<ApiResponse<T>>): Promise<T> => {
	const response = await promise;
	if (response.error) {
		throw new Error(response.error);
	}
	return response.data as T;
};

const fileToFormData = (file: File) => {
	const formData = new FormData();
	formData.append('file', file);
	return formData;
};

// Auth API
export const authApi = {
	register: (data: { username: string; email?: string; password: string; display_name?: string; referral_code?: string }) => {
		// E-posta anonimlik için opsiyonel: boşsa hiç gönderme.
		const payload: Record<string, unknown> = {
			username: data.username,
			password: data.password,
		};
		if (data.email && data.email.trim()) payload.email = data.email.trim();
		if (data.display_name && data.display_name.trim()) payload.display_name = data.display_name.trim();
		if (data.referral_code && data.referral_code.trim()) payload.referral_code = data.referral_code.trim();
		return api.post<{ access_token: string; refresh_token: string }>('/auth/register', payload);
	},
	
	login: (data: { username: string; password: string; two_factor_code?: string }) =>
		api.post<{ access_token: string; refresh_token: string; requires_2fa?: boolean }>('/auth/login', data),
	
	logout: () => api.post('/auth/logout'),
	
	refreshToken: (refreshToken: string) =>
		api.post<{ access_token: string }>('/auth/refresh', { refresh_token: refreshToken }),
	
	requestPasswordReset: (email: string) =>
		api.post('/auth/password-reset/request', { email }),
	
	resetPassword: (token: string, password: string) =>
		api.post('/auth/password-reset', { token, new_password: password }),
	
	verifyEmail: (token: string) =>
		api.post('/auth/verify-email', { token }),
};

// User API
export const userApi = {
	getMe: () => api.get('/users/me'),
	updateProfile: (data: any) => api.patch('/users/me', data),
	getSettings: () => api.get('/users/me/settings'),
	updateSettings: (data: any) => api.patch('/users/me/settings', data),
	getUser: (username: string) => api.get(`/users/${username}`),
	follow: (username: string) => api.post(`/users/${username}/follow`),
	unfollow: (username: string) => api.delete(`/users/${username}/follow`),
	getFollowers: (username: string, page = 1) => api.get(`/users/${username}/followers?page=${page}`),
	getFollowing: (username: string, page = 1) => api.get(`/users/${username}/following?page=${page}`),
};

// Post API
export const postApi = {
	getFeed: (page = 1) => api.get(`/posts/feed?page=${page}`),
	getPost: (id: string) => api.get(`/posts/${id}`),
	createPost: (data: any) => api.post('/posts', data),
	updatePost: (id: string, data: any) => api.put(`/posts/${id}`, data),
	deletePost: (id: string) => api.delete(`/posts/${id}`),
	likePost: (id: string) => api.post(`/posts/${id}/like`),
	unlikePost: (id: string) => api.delete(`/posts/${id}/like`),
	bookmarkPost: (id: string) => api.post(`/posts/${id}/bookmark`),
	unbookmarkPost: (id: string) => api.delete(`/posts/${id}/bookmark`),
	getComments: (id: string, page = 1) => api.get(`/posts/${id}/comments?page=${page}`),
	addComment: (id: string, content: string) => api.post(`/posts/${id}/comments`, { content }),
	getUserPosts: (username: string, page = 1) => api.get(`/users/${username}/posts?page=${page}`),
};

// Legacy compatibility layer for existing UI code
(api as ApiClient & { users?: any; posts?: any }).users = {
	getByUsername: (username: string) => unwrap(userApi.getUser(username)),
	follow: (username: string) => unwrap(userApi.follow(username)),
	unfollow: (username: string) => unwrap(userApi.unfollow(username)),
	getSettings: async () => {
		try {
			return await unwrap(userApi.getSettings());
		} catch {
			const me = await userApi.getMe();
			return me.data ?? {};
		}
	},
	updateProfile: (data: any) => unwrap(userApi.updateProfile(data)),
	updateSettings: (data: any) => unwrap(userApi.updateSettings(data)),
	uploadAvatar: (file: File) => unwrap(api.upload('/users/me/avatar', fileToFormData(file))),
	uploadCover: (file: File) => unwrap(api.upload('/users/me/cover', fileToFormData(file))),
	// Gizlilik öncelikli içerik üretici başvurusu - kimlik/yüz fotoğrafı İSTENMEZ.
	applyCreator: (data: {
		display_name: string;
		bio: string;
		subscription_price?: number;
		categories?: string[];
		age_confirmed: boolean;
	}) => unwrap(api.post('/users/creator-application', data)),
	explore: async (params?: { sort?: string; search?: string; page?: number; limit?: number }) => {
		const sort = params?.sort || 'featured';
		const page = params?.page || 1;
		const limit = params?.limit || 20;
		const search = params?.search ? `&q=${encodeURIComponent(params.search)}` : '';
		const data: any = await unwrap(
			api.get(`/users/creators?sort=${sort}&page=${page}&limit=${limit}${search}`)
		);
		return { items: data?.items ?? [], total: data?.total ?? 0, hasMore: data?.has_more ?? false };
	},
	search: async (q: string) => {
		if (!q || q.length < 2) return { items: [] };
		const data: any = await unwrap(api.get(`/users/search?q=${encodeURIComponent(q)}`));
		return { items: Array.isArray(data) ? data : (data?.items ?? []) };
	},
};

(api as ApiClient & { users?: any; posts?: any }).posts = {
	getFeed: async (page = 1, perPage = 20) => {
		const data = await unwrap(postApi.getFeed(page));
		const items = (data as any)?.posts ?? [];
		return { items, page, perPage, total: (data as any)?.total ?? items.length, hasMore: (data as any)?.has_more ?? false };
	},
	getDiscover: async (page = 1, perPage = 20) => {
		const data = await unwrap(api.get(`/posts/feed?page=${page}&per_page=${perPage}&discover=true`));
		const items = (data as any)?.posts ?? [];
		return { items, page, perPage, total: (data as any)?.total ?? items.length, hasMore: (data as any)?.has_more ?? false };
	},
	like: (id: string) => unwrap(postApi.likePost(id)),
	bookmark: (id: string) => unwrap(postApi.bookmarkPost(id)),
	getByUser: async (username: string, options?: { page?: number }) => {
		try {
			const data = await unwrap(postApi.getUserPosts(username, options?.page ?? 1));
			const items = (data as any)?.posts ?? (data as any)?.items ?? [];
			return { items };
		} catch {
			return { items: [] };
		}
	},
	create: (data: any) => unwrap(postApi.createPost(data)),
	get: async (id: string) => unwrap(postApi.getPost(id)),
	getComments: async (id: string, page = 1) => {
		try {
			const data: any = await unwrap(postApi.getComments(id, page));
			return { items: Array.isArray(data) ? data : (data?.items ?? data?.comments ?? []) };
		} catch {
			return { items: [] };
		}
	},
	addComment: (id: string, content: string) => unwrap(postApi.addComment(id, content)),
	uploadMedia: async (file: File) => {
		const fd = new FormData();
		fd.append('file', file);
		return unwrap(api.upload('/posts/media', fd));
	},
};

// Messages compatibility
// Subscription API
export const subscriptionApi = {
	subscribe: (username: string, data: any) => api.post(`/subscriptions/subscribe/${username}`, data),
	unsubscribe: (username: string) => api.delete(`/subscriptions/unsubscribe/${username}`),
	checkSubscription: (username: string) => api.get(`/subscriptions/check/${username}`),
	getMySubscriptions: (page = 1) => api.get(`/subscriptions/my/subscriptions?page=${page}`),
	getMySubscribers: (page = 1) => api.get(`/subscriptions/my/subscribers?page=${page}`),
	getPlans: (username: string) => api.get(`/subscriptions/users/${username}/plans`),
	createPlan: (data: any) => api.post('/subscriptions/plans', data),
	updatePlan: (id: string, data: any) => api.put(`/subscriptions/plans/${id}`, data),
	deletePlan: (id: string) => api.delete(`/subscriptions/plans/${id}`),
};

// Payment API
export const paymentApi = {
	getWallet: () => api.get('/payments/wallet'),
	createDeposit: (amount: number, method: string) =>
		api.post('/payments/deposit', { amount, payment_method: method }),
	checkPaymentStatus: (id: string) => api.get(`/payments/request/${id}/status`),
	sendTip: (data: any) => api.post('/payments/tip', data),
	unlockPost: (postId: string, method: string) =>
		api.post(`/payments/posts/${postId}/unlock`, { payment_method: method }),
};

// Wallet API
export const walletApi = {
	getWallet: () => api.get('/wallet'),
	getTransactions: (page = 1, type?: string) => 
		api.get(`/wallet/transactions?page=${page}${type ? `&type_filter=${type}` : ''}`),
	getEarningsStats: (period = 'month') => api.get(`/wallet/earnings/stats?period=${period}`),
	requestWithdrawal: (data: any) => api.post('/wallet/withdraw', data),
	getWithdrawals: (page = 1) => api.get(`/wallet/withdrawals?page=${page}`),
	cancelWithdrawal: (id: string) => api.delete(`/wallet/withdrawals/${id}`),
	getPayoutInfo: () => api.get('/wallet/payout-info'),
};

// Message API
export const messageApi = {
	getConversations: (page = 1) => api.get(`/messages/conversations?page=${page}`),
	getConversation: (id: string) => api.get(`/messages/conversations/${id}`),
	getMessages: (conversationId: string, page = 1) =>
		api.get(`/messages/conversations/${conversationId}/messages?page=${page}`),
	sendMessage: (data: any) => api.post('/messages/send', data),
	sendToConversation: (conversationId: string, data: any) =>
		api.post(`/messages/conversations/${conversationId}/messages`, data),
	sendMassMessage: (data: any) => api.post('/messages/mass', data),
	deleteMessage: (id: string) => api.delete(`/messages/messages/${id}`),
};

// Notification API
export const notificationApi = {
	getNotifications: (page = 1, unreadOnly = false) =>
		api.get(`/notifications?page=${page}&unread_only=${unreadOnly}`),
	getUnreadCount: () => api.get('/notifications/unread-count'),
	markAsRead: (id: string) => api.post(`/notifications/mark-read/${id}`),
	markAllAsRead: () => api.post('/notifications/mark-all-read'),
	deleteNotification: (id: string) => api.delete(`/notifications/${id}`),
	clearAll: () => api.delete('/notifications'),
	getSettings: () => api.get('/notifications/settings'),
	updateSettings: (data: any) => api.put('/notifications/settings', data),
};

// Stream API
export const streamApi = {
	getLiveStreams: () => api.get('/streams/live'),
	getStream: (id: string) => api.get(`/streams/${id}`),
	startStream: (data: any) => api.post('/streams/start', data),
	endStream: (id: string) => api.post(`/streams/${id}/end`),
	getStreamKey: () => api.get('/streams/key'),
	regenerateStreamKey: () => api.post('/streams/key/regenerate'),
	joinStream: (id: string) => api.post(`/streams/${id}/join`),
	leaveStream: (id: string) => api.post(`/streams/${id}/leave`),
	getStreamMessages: (id: string, limit = 50) => api.get(`/streams/${id}/messages?limit=${limit}`),
	sendStreamMessage: (id: string, content: string) =>
		api.post(`/streams/${id}/messages`, { content }),
	sendStreamTip: (id: string, data: any) => api.post(`/streams/${id}/tip`, data),
	getScheduledStreams: () => api.get('/streams/scheduled'),
	scheduleStream: (data: any) => api.post('/streams/schedule', data),
};

// Messages compatibility
(api as ApiClient & { messages?: any }).messages = {
	getConversations: async () => {
		const data = await unwrap(messageApi.getConversations());
		return (data as any)?.items ?? [];
	},
	getMessages: async (conversationId: string, page = 1) => {
		const data = await unwrap(messageApi.getMessages(conversationId, page));
		return { items: (data as any)?.items ?? [] };
	},
	markAsRead: async (_conversationId: string) => true,
	send: async (conversationId: string, payload: any) =>
		unwrap(messageApi.sendToConversation(conversationId, payload)),
};

// Notifications compatibility
(api as ApiClient & { notifications?: any }).notifications = {
	list: async (params?: { page?: number; unreadOnly?: boolean }) => {
		const data = await unwrap(notificationApi.getNotifications(params?.page ?? 1, params?.unreadOnly ?? false));
		return {
			items: (data as any)?.items ?? [],
			total: (data as any)?.total ?? 0,
		};
	},
	markAsRead: (id: string) => unwrap(notificationApi.markAsRead(id)),
	markAllAsRead: () => unwrap(notificationApi.markAllAsRead()),
};

// Payments compatibility (cüzdan ile anında işlem)
(api as ApiClient & { payments?: any }).payments = {
	tip: (recipientId: string, amount: number, opts?: { postId?: string; message?: string }) =>
		unwrap(
			api.post('/payments/tip', {
				recipient_id: recipientId,
				amount,
				post_id: opts?.postId,
				message: opts?.message,
				payment_method: 'wallet',
			})
		),
	unlockPost: (postId: string) =>
		unwrap(api.post(`/payments/posts/${postId}/unlock`, { payment_method: 'wallet' })),
	createDeposit: (amount: number, method = 'monero') =>
		unwrap(api.post('/payments/deposit', { amount, payment_method: method })),
	checkStatus: (id: string) => unwrap(api.get(`/payments/request/${id}/status`)),
};

// Subscriptions compatibility
(api as ApiClient & { subscriptions?: any }).subscriptions = {
	getCreatorPlans: async (username: string) => {
		try {
			const data: any = await unwrap(subscriptionApi.getPlans(username));
			return Array.isArray(data) ? data : (data?.items ?? data?.plans ?? []);
		} catch {
			return [];
		}
	},
	subscribe: async (
		creatorId: string,
		username: string,
		opts?: { months?: number; paymentMethod?: string }
	) =>
		unwrap(
			subscriptionApi.subscribe(username, {
				creator_id: creatorId,
				months: opts?.months ?? 1,
				payment_method: opts?.paymentMethod ?? 'wallet',
			})
		),
	unsubscribe: (username: string) => unwrap(subscriptionApi.unsubscribe(username)),
};

// Wallet compatibility
(api as ApiClient & { wallet?: any }).wallet = {
	get: async () => {
		const data = await unwrap(walletApi.getWallet());
		return (data as any)?.wallet ?? data;
	},
	getTransactions: async (page = 1) => {
		const data = await unwrap(walletApi.getTransactions(page));
		return { items: (data as any)?.items ?? (data as any)?.transactions ?? [] };
	},
	withdraw: (payload: any) => unwrap(walletApi.requestWithdrawal(payload)),
};

// Auth compatibility for settings page
(api as ApiClient & { auth?: any }).auth = {
	changePassword: (data: { current_password: string; new_password: string }) =>
		unwrap(api.post('/auth/change-password', data)),
	setup2FA: () => unwrap(api.post('/auth/2fa/setup')),
	verify2FA: (code: string) => unwrap(api.post('/auth/2fa/verify', { code })),
	disable2FA: (code: string) => unwrap(api.post('/auth/2fa/disable', { code })),
};

export const adminApi = {
	getSiteSettings: () => unwrap(api.get('/admin/settings')),
	updateSiteSettings: (data: Record<string, unknown>) => unwrap(api.put('/admin/settings', data)),
	getStats: () => unwrap(api.get('/admin/stats')),
	credit: (username: string, amount: number, note?: string) =>
		unwrap(api.post('/admin/credit', { username, amount, note })),
	setBalance: (userId: string, balance: number) => unwrap(api.put(`/admin/users/${userId}/balance`, { balance })),
	creditAll: (amount: number, opts?: { set?: boolean; note?: string }) =>
		unwrap(api.post('/admin/credit-all', { amount, set: opts?.set ?? false, note: opts?.note })),
	setRole: (userId: string, role: string) => unwrap(api.put(`/admin/users/${userId}/role`, { role })),
	listUsers: async (params?: { page?: number; search?: string }) => {
		const q = new URLSearchParams();
		q.set('page', String(params?.page ?? 1));
		if (params?.search) q.set('search', params.search);
		return unwrap(api.get(`/admin/users?${q.toString()}`));
	},
	banUser: (userId: string, reason: string) => unwrap(api.post(`/admin/users/${userId}/ban`, { reason })),
	unbanUser: (userId: string) => unwrap(api.post(`/admin/users/${userId}/unban`)),
	listWithdrawals: async (statusFilter?: string) => {
		const d: any = await unwrap(api.get(`/admin/withdrawals${statusFilter ? `?status_filter=${statusFilter}` : ''}`));
		return d?.items ?? [];
	},
	approveWithdrawal: (id: string) => unwrap(api.post(`/admin/withdrawals/${id}/approve`)),
	rejectWithdrawal: (id: string, reason: string) =>
		unwrap(api.post(`/admin/withdrawals/${id}/reject?reason=${encodeURIComponent(reason)}`)),
};

// Reports
(api as any).reports = {
	create: (data: { reported_type: string; reported_id: string; type?: string; description?: string; reported_user_id?: string }) =>
		unwrap(api.post('/reports', { type: 'other', description: '', ...data })),
	queue: (statusFilter?: string) => unwrap(api.get(`/reports/queue${statusFilter ? `?status_filter=${statusFilter}` : ''}`)),
	resolve: (id: string, data: { status?: string; resolution_note?: string; action_taken?: string }) =>
		unwrap(api.post(`/reports/${id}/resolve`, data)),
};

// Ads
(api as any).ads = {
	list: async (placement: string) => {
		try {
			const data: any = await unwrap(api.get(`/ads?placement=${placement}`));
			return data?.items ?? [];
		} catch {
			return [];
		}
	},
	preroll: async () => {
		try {
			const data: any = await unwrap(api.get('/ads/preroll'));
			return data?.ad ?? null;
		} catch {
			return null;
		}
	},
	impression: (id: string) => unwrap(api.post(`/ads/${id}/impression`)).catch(() => {}),
	click: (id: string) => unwrap(api.post(`/ads/${id}/click`)),
	all: async () => { const d: any = await unwrap(api.get('/ads/all')); return d?.items ?? d ?? []; },
	create: (data: any) => unwrap(api.post('/ads', data)),
	update: (id: string, data: any) => unwrap(api.put(`/ads/${id}`, data)),
	remove: (id: string) => unwrap(api.delete(`/ads/${id}`)),
};

// Tickets
(api as any).tickets = {
	create: (data: { subject: string; category?: string; message: string }) => unwrap(api.post('/tickets', data)),
	mine: async () => { const d: any = await unwrap(api.get('/tickets')); return d?.items ?? []; },
	get: (id: string) => unwrap(api.get(`/tickets/${id}`)),
	reply: (id: string, text: string) => unwrap(api.post(`/tickets/${id}/reply`, { text })),
	close: (id: string) => unwrap(api.post(`/tickets/${id}/close`)),
	queue: async (statusFilter?: string) => { const d: any = await unwrap(api.get(`/tickets/queue${statusFilter ? `?status_filter=${statusFilter}` : ''}`)); return d?.items ?? []; },
};

// Escrow
(api as any).escrow = {
	create: (data: { creator_username: string; title: string; description: string; amount: number }) =>
		unwrap(api.post('/escrow', data)),
	mine: async (role = 'all') => { const d: any = await unwrap(api.get(`/escrow?role=${role}`)); return d?.items ?? []; },
	deliver: (id: string, data: { note?: string; url?: string }) => unwrap(api.post(`/escrow/${id}/deliver`, data)),
	approve: (id: string) => unwrap(api.post(`/escrow/${id}/approve`)),
	cancel: (id: string) => unwrap(api.post(`/escrow/${id}/cancel`)),
	dispute: (id: string, reason: string) => unwrap(api.post(`/escrow/${id}/dispute`, { reason })),
	resolve: (id: string, action: string) => unwrap(api.post(`/escrow/${id}/resolve?action=${action}`)),
	disputes: async () => { const d: any = await unwrap(api.get('/escrow/disputes')); return d?.items ?? []; },
};

// Stories (şipşak)
(api as any).stories = {
	feed: async () => { const d: any = await unwrap(api.get('/stories')); return d?.items ?? []; },
	create: (data: { media_url: string; media_type?: string; caption?: string; single_view?: boolean; subscribers_only?: boolean; duration_hours?: number }) =>
		unwrap(api.post('/stories', data)),
	view: (id: string) => unwrap(api.post(`/stories/${id}/view`)),
	remove: (id: string) => unwrap(api.delete(`/stories/${id}`))
};

// Screenshot flag
(api as any).flagScreenshot = () => unwrap(api.post('/users/me/flag-screenshot'));
