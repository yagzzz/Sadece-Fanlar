import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

const PUBLIC_API_URL = "http://localhost:8000";
const API_BASE = `${PUBLIC_API_URL}/api/v1`;
function parseApiError(data) {
  if (!data || typeof data !== "object") return "Bir hata oluştu";
  const detail = data.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => {
      if (typeof item === "string") return item;
      if (item && typeof item === "object" && "msg" in item) return String(item.msg);
      return "Geçersiz istek";
    }).join(", ");
  }
  return "Bir hata oluştu";
}
class ApiClient {
  token = null;
  users;
  posts;
  messages;
  notifications;
  wallet;
  auth;
  subscriptions;
  payments;
  streams;
  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem("access_token", token);
    } else {
      localStorage.removeItem("access_token");
    }
  }
  getToken() {
    if (this.token) return this.token;
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("access_token");
      if (stored) this.token = stored;
      return stored;
    }
    return null;
  }
  async refreshAccessToken() {
    if (typeof window === "undefined") return false;
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) return false;
    try {
      const response = await fetch(`${API_BASE}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken })
      });
      const data = await response.json().catch(() => null);
      if (!response.ok || !data?.access_token) return false;
      this.setToken(data.access_token);
      if (data.refresh_token) {
        localStorage.setItem("refresh_token", data.refresh_token);
      }
      return true;
    } catch {
      return false;
    }
  }
  async request(endpoint, options = {}, retry = true) {
    const token = this.getToken();
    const headers = {
      "Content-Type": "application/json",
      ...options.headers || {}
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
      });
      const data = await response.json().catch(() => null);
      if (response.status === 401 && retry && endpoint !== "/auth/refresh") {
        const refreshed = await this.refreshAccessToken();
        if (refreshed) {
          return this.request(endpoint, options, false);
        }
        this.setToken(null);
        localStorage.removeItem("refresh_token");
      }
      if (!response.ok) {
        return {
          error: parseApiError(data),
          status: response.status
        };
      }
      return { data, status: response.status };
    } catch {
      return {
        error: "Sunucuya bağlanılamadı",
        status: 0
      };
    }
  }
  // GET request
  async get(endpoint) {
    return this.request(endpoint, { method: "GET" });
  }
  // POST request
  async post(endpoint, body) {
    return this.request(endpoint, {
      method: "POST",
      body: body ? JSON.stringify(body) : void 0
    });
  }
  // PUT request
  async put(endpoint, body) {
    return this.request(endpoint, {
      method: "PUT",
      body: body ? JSON.stringify(body) : void 0
    });
  }
  // DELETE request
  async delete(endpoint) {
    return this.request(endpoint, { method: "DELETE" });
  }
  // File upload
  async upload(endpoint, formData) {
    const token = this.getToken();
    const headers = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers,
        body: formData
      });
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        return {
          error: data?.detail || "Yükleme başarısız",
          status: response.status
        };
      }
      return { data, status: response.status };
    } catch (error) {
      return {
        error: "Sunucuya bağlanılamadı",
        status: 0
      };
    }
  }
}
const api = new ApiClient();
const unwrap = async (promise) => {
  const response = await promise;
  if (response.error) {
    throw new Error(response.error);
  }
  return response.data;
};
const fileToFormData = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return formData;
};
const authApi = {
  register: (data) => {
    const payload = {
      username: data.username,
      password: data.password
    };
    if (data.email && data.email.trim()) payload.email = data.email.trim();
    if (data.display_name && data.display_name.trim()) payload.display_name = data.display_name.trim();
    if (data.referral_code && data.referral_code.trim()) payload.referral_code = data.referral_code.trim();
    return api.post("/auth/register", payload);
  },
  login: (data) => api.post("/auth/login", data),
  logout: () => api.post("/auth/logout"),
  refreshToken: (refreshToken) => api.post("/auth/refresh", { refresh_token: refreshToken }),
  requestPasswordReset: (email) => api.post("/auth/password-reset/request", { email }),
  resetPassword: (token, password) => api.post("/auth/password-reset", { token, new_password: password }),
  verifyEmail: (token) => api.post("/auth/verify-email", { token })
};
const userApi = {
  getMe: () => api.get("/users/me"),
  updateProfile: (data) => api.put("/users/me", data),
  getUser: (username) => api.get(`/users/${username}`),
  follow: (username) => api.post(`/users/${username}/follow`),
  unfollow: (username) => api.delete(`/users/${username}/follow`),
  getFollowers: (username, page = 1) => api.get(`/users/${username}/followers?page=${page}`),
  getFollowing: (username, page = 1) => api.get(`/users/${username}/following?page=${page}`)
};
const postApi = {
  getFeed: (page = 1) => api.get(`/posts/feed?page=${page}`),
  getPost: (id) => api.get(`/posts/${id}`),
  createPost: (data) => api.post("/posts", data),
  updatePost: (id, data) => api.put(`/posts/${id}`, data),
  deletePost: (id) => api.delete(`/posts/${id}`),
  likePost: (id) => api.post(`/posts/${id}/like`),
  unlikePost: (id) => api.delete(`/posts/${id}/like`),
  bookmarkPost: (id) => api.post(`/posts/${id}/bookmark`),
  unbookmarkPost: (id) => api.delete(`/posts/${id}/bookmark`),
  getComments: (id, page = 1) => api.get(`/posts/${id}/comments?page=${page}`),
  addComment: (id, content) => api.post(`/posts/${id}/comments`, { content }),
  getUserPosts: (username, page = 1) => api.get(`/users/${username}/posts?page=${page}`)
};
api.users = {
  getByUsername: (username) => unwrap(userApi.getUser(username)),
  follow: (username) => unwrap(userApi.follow(username)),
  unfollow: (username) => unwrap(userApi.unfollow(username)),
  getSettings: async () => {
    const me = await userApi.getMe();
    return me.data ?? {};
  },
  updateProfile: (data) => unwrap(userApi.updateProfile(data)),
  updateSettings: (data) => unwrap(userApi.updateProfile(data)),
  uploadAvatar: (file) => unwrap(api.upload("/users/me/avatar", fileToFormData(file))),
  uploadCover: (file) => unwrap(api.upload("/users/me/cover", fileToFormData(file))),
  // Gizlilik öncelikli içerik üretici başvurusu - kimlik/yüz fotoğrafı İSTENMEZ.
  applyCreator: (data) => unwrap(api.post("/users/creator-application", data)),
  explore: async (params) => {
    const q = params?.q ? encodeURIComponent(params.q) : "";
    return unwrap(api.get(`/users/search?q=${q}`));
  }
};
api.posts = {
  getFeed: async (page = 1, perPage = 20) => {
    const data = await unwrap(postApi.getFeed(page));
    const items = data?.posts ?? [];
    return { items, page, perPage, total: data?.total ?? items.length, hasMore: data?.has_more ?? false };
  },
  like: (id) => unwrap(postApi.likePost(id)),
  bookmark: (id) => unwrap(postApi.bookmarkPost(id)),
  getByUser: async (username, options) => {
    try {
      const data = await unwrap(postApi.getUserPosts(username, options?.page ?? 1));
      const items = data?.posts ?? data?.items ?? [];
      return { items };
    } catch {
      return { items: [] };
    }
  },
  create: (data) => unwrap(postApi.createPost(data)),
  uploadMedia: async (_file) => {
    throw new Error("Medya yükleme servisi yapılandırılmadı.");
  }
};
const walletApi = {
  getWallet: () => api.get("/wallet"),
  getTransactions: (page = 1, type) => api.get(`/wallet/transactions?page=${page}${type ? `&type_filter=${type}` : ""}`),
  getEarningsStats: (period = "month") => api.get(`/wallet/earnings/stats?period=${period}`),
  requestWithdrawal: (data) => api.post("/wallet/withdraw", data),
  getWithdrawals: (page = 1) => api.get(`/wallet/withdrawals?page=${page}`),
  cancelWithdrawal: (id) => api.delete(`/wallet/withdrawals/${id}`),
  getPayoutInfo: () => api.get("/wallet/payout-info")
};
const messageApi = {
  getConversations: (page = 1) => api.get(`/messages/conversations?page=${page}`),
  getConversation: (id) => api.get(`/messages/conversations/${id}`),
  getMessages: (conversationId, page = 1) => api.get(`/messages/conversations/${conversationId}/messages?page=${page}`),
  sendMessage: (data) => api.post("/messages/send", data),
  sendToConversation: (conversationId, data) => api.post(`/messages/conversations/${conversationId}/messages`, data),
  sendMassMessage: (data) => api.post("/messages/mass", data),
  deleteMessage: (id) => api.delete(`/messages/messages/${id}`)
};
const notificationApi = {
  getNotifications: (page = 1, unreadOnly = false) => api.get(`/notifications?page=${page}&unread_only=${unreadOnly}`),
  getUnreadCount: () => api.get("/notifications/unread-count"),
  markAsRead: (id) => api.post(`/notifications/mark-read/${id}`),
  markAllAsRead: () => api.post("/notifications/mark-all-read"),
  deleteNotification: (id) => api.delete(`/notifications/${id}`),
  clearAll: () => api.delete("/notifications"),
  getSettings: () => api.get("/notifications/settings"),
  updateSettings: (data) => api.put("/notifications/settings", data)
};
api.messages = {
  getConversations: async () => {
    const data = await unwrap(messageApi.getConversations());
    return data?.items ?? [];
  },
  getMessages: async (conversationId, page = 1) => {
    const data = await unwrap(messageApi.getMessages(conversationId, page));
    return { items: data?.items ?? [] };
  },
  markAsRead: async (_conversationId) => true,
  send: async (conversationId, payload) => unwrap(messageApi.sendToConversation(conversationId, payload))
};
api.notifications = {
  list: async (params) => {
    const data = await unwrap(notificationApi.getNotifications(params?.page ?? 1, params?.unreadOnly ?? false));
    return {
      items: data?.items ?? [],
      total: data?.total ?? 0
    };
  },
  markAsRead: (id) => unwrap(notificationApi.markAsRead(id)),
  markAllAsRead: () => unwrap(notificationApi.markAllAsRead())
};
api.wallet = {
  get: async () => {
    const data = await unwrap(walletApi.getWallet());
    return data?.wallet ?? data;
  },
  getTransactions: async (page = 1) => {
    const data = await unwrap(walletApi.getTransactions(page));
    return { items: data?.items ?? data?.transactions ?? [] };
  },
  withdraw: (payload) => unwrap(walletApi.requestWithdrawal(payload))
};
api.auth = {
  changePassword: (data) => unwrap(api.post("/auth/change-password", data)),
  setup2FA: () => unwrap(api.post("/auth/2fa/setup")),
  disable2FA: (data) => unwrap(api.post("/auth/2fa/disable", data ?? {}))
};
function cn(...inputs) {
  return twMerge(clsx(inputs));
}
function formatCurrency(amount, currency = "USD") {
  return new Intl.NumberFormat("tr-TR", {
    style: "currency",
    currency,
    minimumFractionDigits: 2
  }).format(amount);
}
function timeAgo(dateString) {
  const date = new Date(dateString);
  const now = /* @__PURE__ */ new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1e3);
  const intervals = [
    { label: "yıl", seconds: 31536e3 },
    { label: "ay", seconds: 2592e3 },
    { label: "hafta", seconds: 604800 },
    { label: "gün", seconds: 86400 },
    { label: "saat", seconds: 3600 },
    { label: "dakika", seconds: 60 }
  ];
  for (const interval of intervals) {
    const count = Math.floor(seconds / interval.seconds);
    if (count >= 1) {
      return `${count} ${interval.label} önce`;
    }
  }
  return "az önce";
}
function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}
function isValidUsername(username) {
  const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
  return usernameRegex.test(username);
}

export { api as a, authApi as b, cn as c, isValidUsername as d, formatCurrency as f, isValidEmail as i, timeAgo as t, userApi as u };
//# sourceMappingURL=index2-CqlzXTMx.js.map
