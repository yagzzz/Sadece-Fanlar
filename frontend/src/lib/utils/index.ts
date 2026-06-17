/**
 * Utility Functions
 */
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Tailwind class merger
export function cn(...inputs: ClassValue[]) {
	return twMerge(clsx(inputs));
}

// Format currency
export function formatCurrency(amount: number, currency = 'USD'): string {
	return new Intl.NumberFormat('tr-TR', {
		style: 'currency',
		currency,
		minimumFractionDigits: 2,
	}).format(amount);
}

// Format crypto amount
export function formatCrypto(amount: number, currency: string): string {
	const decimals = currency === 'BTC' ? 8 : 12; // XMR has 12 decimals
	return `${amount.toFixed(decimals)} ${currency}`;
}

// Format number with K/M suffix
export function formatNumber(num: number): string {
	if (num >= 1000000) {
		return (num / 1000000).toFixed(1) + 'M';
	}
	if (num >= 1000) {
		return (num / 1000).toFixed(1) + 'K';
	}
	return num.toString();
}

// Relative time formatting
export function timeAgo(dateString: string): string {
	const date = new Date(dateString);
	const now = new Date();
	const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

	const intervals = [
		{ label: 'yıl', seconds: 31536000 },
		{ label: 'ay', seconds: 2592000 },
		{ label: 'hafta', seconds: 604800 },
		{ label: 'gün', seconds: 86400 },
		{ label: 'saat', seconds: 3600 },
		{ label: 'dakika', seconds: 60 },
	];

	for (const interval of intervals) {
		const count = Math.floor(seconds / interval.seconds);
		if (count >= 1) {
			return `${count} ${interval.label} önce`;
		}
	}

	return 'az önce';
}

// Format full date
export function formatDate(dateString: string): string {
	const date = new Date(dateString);
	return new Intl.DateTimeFormat('tr-TR', {
		year: 'numeric',
		month: 'long',
		day: 'numeric',
		hour: '2-digit',
		minute: '2-digit',
	}).format(date);
}

// Format short date
export function formatDateShort(dateString: string): string {
	const date = new Date(dateString);
	return new Intl.DateTimeFormat('tr-TR', {
		month: 'short',
		day: 'numeric',
	}).format(date);
}

// Truncate text
export function truncate(text: string, length: number): string {
	if (text.length <= length) return text;
	return text.slice(0, length) + '...';
}

// Validate email
export function isValidEmail(email: string): boolean {
	const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
	return emailRegex.test(email);
}

// Validate username
export function isValidUsername(username: string): boolean {
	const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
	return usernameRegex.test(username);
}

// Validate password strength
export function validatePassword(password: string): { valid: boolean; errors: string[] } {
	const errors: string[] = [];

	if (password.length < 8) {
		errors.push('En az 8 karakter olmalı');
	}
	if (!/[A-Z]/.test(password)) {
		errors.push('En az bir büyük harf içermeli');
	}
	if (!/[a-z]/.test(password)) {
		errors.push('En az bir küçük harf içermeli');
	}
	if (!/[0-9]/.test(password)) {
		errors.push('En az bir rakam içermeli');
	}

	return {
		valid: errors.length === 0,
		errors,
	};
}

// Copy to clipboard
export async function copyToClipboard(text: string): Promise<boolean> {
	try {
		await navigator.clipboard.writeText(text);
		return true;
	} catch {
		return false;
	}
}

// Generate random string
export function randomString(length: number): string {
	const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
	let result = '';
	for (let i = 0; i < length; i++) {
		result += chars.charAt(Math.floor(Math.random() * chars.length));
	}
	return result;
}

// Debounce function
export function debounce<T extends (...args: any[]) => any>(
	func: T,
	wait: number
): (...args: Parameters<T>) => void {
	let timeout: ReturnType<typeof setTimeout> | null = null;

	return function (...args: Parameters<T>) {
		if (timeout) clearTimeout(timeout);
		timeout = setTimeout(() => func(...args), wait);
	};
}

// Get file extension
export function getFileExtension(filename: string): string {
	return filename.slice(((filename.lastIndexOf('.') - 1) >>> 0) + 2);
}

// Get file type from extension
export function getFileType(filename: string): 'image' | 'video' | 'audio' | 'file' {
	const ext = getFileExtension(filename).toLowerCase();
	
	const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'avif', 'svg'];
	const videoExts = ['mp4', 'webm', 'mov', 'avi', 'mkv'];
	const audioExts = ['mp3', 'wav', 'ogg', 'flac', 'm4a'];
	
	if (imageExts.includes(ext)) return 'image';
	if (videoExts.includes(ext)) return 'video';
	if (audioExts.includes(ext)) return 'audio';
	return 'file';
}

// Format file size
export function formatFileSize(bytes: number): string {
	if (bytes === 0) return '0 Bytes';
	const k = 1024;
	const sizes = ['Bytes', 'KB', 'MB', 'GB'];
	const i = Math.floor(Math.log(bytes) / Math.log(k));
	return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Format duration in seconds to HH:MM:SS
export function formatDuration(seconds: number): string {
	const hours = Math.floor(seconds / 3600);
	const minutes = Math.floor((seconds % 3600) / 60);
	const secs = Math.floor(seconds % 60);

	if (hours > 0) {
		return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
	}
	return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

// Check if password is strong
// Not: Backend kuralıyla aynı (büyük/küçük harf + rakam). Özel karakter
// zorunlu değildir; aksi halde backend'in kabul ettiği şifreler UI'da reddedilirdi.
export function isStrongPassword(password: string): boolean {
	if (password.length < 8) return false;
	if (!/[A-Z]/.test(password)) return false;
	if (!/[a-z]/.test(password)) return false;
	if (!/[0-9]/.test(password)) return false;
	return true;
}

// Click outside action for Svelte
export function clickOutside(node: HTMLElement, callback: () => void) {
	const handleClick = (event: MouseEvent) => {
		if (!node.contains(event.target as Node)) {
			callback();
		}
	};

	document.addEventListener('click', handleClick, true);

	return {
		destroy() {
			document.removeEventListener('click', handleClick, true);
		},
	};
}
