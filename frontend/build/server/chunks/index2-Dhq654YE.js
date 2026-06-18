import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}
function formatCurrency(amount, currency = "TRY") {
  return new Intl.NumberFormat("tr-TR", {
    style: "currency",
    currency,
    minimumFractionDigits: 2
  }).format(amount || 0);
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

export { isValidUsername as a, cn as c, formatCurrency as f, isValidEmail as i, timeAgo as t };
//# sourceMappingURL=index2-Dhq654YE.js.map
