import { c as create_ssr_component, a as subscribe, e as each, v as validate_component, b as createEventDispatcher, d as add_attribute, f as escape } from './ssr-DDQ8otPt.js';
import { a as authStore } from './auth-C_KGpDdi.js';
import 'clsx';
import { c as cn } from './index2-DIqK_D2c.js';
import { w as writable } from './index-BCAmX91C.js';
import 'tailwind-merge';

const Toast = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { title } = $$props;
  let { message } = $$props;
  let { type = "info" } = $$props;
  let { duration = 5e3 } = $$props;
  let { dismissible = true } = $$props;
  let { class: className = "" } = $$props;
  createEventDispatcher();
  const typeStyles = {
    success: {
      bg: "bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-800",
      icon: "✓",
      color: "text-green-600 dark:text-green-400"
    },
    error: {
      bg: "bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-800",
      icon: "✕",
      color: "text-red-600 dark:text-red-400"
    },
    warning: {
      bg: "bg-yellow-50 dark:bg-yellow-900/30 border-yellow-200 dark:border-yellow-800",
      icon: "⚠",
      color: "text-yellow-600 dark:text-yellow-400"
    },
    info: {
      bg: "bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-800",
      icon: "ℹ",
      color: "text-blue-600 dark:text-blue-400"
    }
  };
  if ($$props.title === void 0 && $$bindings.title && title !== void 0) $$bindings.title(title);
  if ($$props.message === void 0 && $$bindings.message && message !== void 0) $$bindings.message(message);
  if ($$props.type === void 0 && $$bindings.type && type !== void 0) $$bindings.type(type);
  if ($$props.duration === void 0 && $$bindings.duration && duration !== void 0) $$bindings.duration(duration);
  if ($$props.dismissible === void 0 && $$bindings.dismissible && dismissible !== void 0) $$bindings.dismissible(dismissible);
  if ($$props.class === void 0 && $$bindings.class && className !== void 0) $$bindings.class(className);
  return `<div${add_attribute("class", cn("pointer-events-auto w-full max-w-sm overflow-hidden rounded-lg border shadow-lg", typeStyles[type].bg, className), 0)} role="alert"><div class="p-4"><div class="flex items-start"><div${add_attribute("class", cn("flex-shrink-0 text-lg", typeStyles[type].color), 0)}>${escape(typeStyles[type].icon)}</div> <div class="ml-3 w-0 flex-1 pt-0.5"><p${add_attribute("class", cn("text-sm font-medium", typeStyles[type].color), 0)}>${escape(title)}</p> <p class="mt-1 text-sm text-neutral-600 dark:text-neutral-400">${escape(message)}</p></div> ${dismissible ? `<div class="ml-4 flex flex-shrink-0"><button type="button" class="inline-flex rounded-md text-neutral-400 hover:text-neutral-500 focus:outline-none focus:ring-2 focus:ring-primary" data-svelte-h="svelte-elt9h3"><span class="sr-only">Close</span> <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg></button></div>` : ``}</div></div></div>`;
});
const Layout = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let $authStore, $$unsubscribe_authStore;
  let $toasts, $$unsubscribe_toasts;
  $$unsubscribe_authStore = subscribe(authStore, (value) => $authStore = value);
  const toasts = writable([]);
  $$unsubscribe_toasts = subscribe(toasts, (value) => $toasts = value);
  if ($$props.toasts === void 0 && $$bindings.toasts && toasts !== void 0) $$bindings.toasts(toasts);
  $$unsubscribe_authStore();
  $$unsubscribe_toasts();
  return `${$$result.head += `<!-- HEAD_svelte-1l4zroh_START -->${$$result.title = `<title>SadeceFanlar</title>`, ""}<meta name="description" content="Anonim içerik üretici platformu"><!-- HEAD_svelte-1l4zroh_END -->`, ""} ${$authStore.initialized ? `${slots.default ? slots.default({}) : ``}` : `<div class="min-h-screen flex items-center justify-center bg-white dark:bg-neutral-950" data-svelte-h="svelte-glhiif"><div class="h-8 w-8 rounded-full border-2 border-neutral-300 border-t-neutral-800 animate-spin"></div></div>`}  <div class="fixed top-4 right-4 z-50 space-y-2 pointer-events-none">${each($toasts, (toast) => {
    return `${validate_component(Toast, "Toast").$$render(
      $$result,
      {
        title: toast.title,
        message: toast.message,
        type: toast.type
      },
      {},
      {}
    )}`;
  })}</div>`;
});

export { Layout as default };
//# sourceMappingURL=_layout.svelte-C6VonZuU.js.map
