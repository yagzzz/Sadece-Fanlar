/**
 * API Client for Sadece Fanlar
 */

import { PUBLIC_API_URL } from '$env/static/public';

const API_BASE = PUBLIC_API_URL ? `${PUBLIC_API_URL}/api/v1` : '/api/v1';

interface ApiResponse<T> {
	data?: T;
	error?: string;
	status: number;
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
			return localStorage.getItem('access_token');
		}
		return null;
	}

	private async request<T>(
		endpoint: string,
		options: RequestInit = {}
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

			if (!response.ok) {
				return {
					error: data?.detail || 'Bir hata oluştu',
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
	register: (data: { username: string; email: string; password: string }) =>
		api.post('/auth/register', data),
	
	login: (data: { username: string; password: string }) =>
		api.post<{ access_token: string; refresh_token: string }>('/auth/login', data),
	
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
	updateProfile: (data: any) => api.put('/users/me', data),
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
		const me = await userApi.getMe();
		return me.data ?? {};
	},
	updateProfile: (data: any) => unwrap(userApi.updateProfile(data)),
	updateSettings: (data: any) => unwrap(userApi.updateProfile(data)),
	uploadAvatar: (file: File) => unwrap(api.upload('/users/me/avatar', fileToFormData(file))),
	uploadCover: (file: File) => unwrap(api.upload('/users/me/cover', fileToFormData(file))),
	submitCreatorApplication: (formData: FormData) =>
		unwrap(api.upload('/users/creator-application', formData)),
	explore: async (params: { q?: string }) => {
		const q = params?.q ? encodeURIComponent(params.q) : '';
		return unwrap(api.get(`/users/search?q=${q}`));
	},
};

(api as ApiClient & { users?: any; posts?: any }).posts = {
	getFeed: async (page = 1, perPage = 20) => {
		const data = await unwrap(postApi.getFeed(page));
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
	uploadMedia: async (_file: File) => {
		throw new Error('Medya yükleme servisi yapılandırılmadı.');
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
	disable2FA: (data?: { code?: string }) => unwrap(api.post('/auth/2fa/disable', data ?? {})),
};
