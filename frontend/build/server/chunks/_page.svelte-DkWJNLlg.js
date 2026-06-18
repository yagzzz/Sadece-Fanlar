import { c as create_ssr_component, a as subscribe, v as validate_component } from './ssr-CxJiF8w8.js';
import { p as page } from './stores-CQajP4Vw.js';
import './ssr2-CJcMdXvQ.js';
import './state.svelte-DYGtfCg5.js';
import './client-DAdgJWpw.js';
import { a as authStore } from './auth-1cButIF9.js';
import 'clsx';
import { S as Spinner } from './Spinner-DnO2KtYq.js';
import './index-YI0dIwkT.js';
import './index2-Dhq654YE.js';
import 'tailwind-merge';

const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let $page, $$unsubscribe_page;
  let $$unsubscribe_authStore;
  $$unsubscribe_page = subscribe(page, (value) => $page = value);
  $$unsubscribe_authStore = subscribe(authStore, (value) => value);
  $page.params.id;
  $$unsubscribe_page();
  $$unsubscribe_authStore();
  return `${$$result.head += `<!-- HEAD_svelte-2dcj55_START -->${$$result.title = `<title>Gönderi | SadeceFanlar</title>`, ""}<meta name="robots" content="noindex, nofollow"><!-- HEAD_svelte-2dcj55_END -->`, ""} <div class="py-2"><button class="text-sm text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-300 mb-4" data-svelte-h="svelte-145vsv5">← Geri</button> ${`<div class="flex justify-center py-16">${validate_component(Spinner, "Spinner").$$render($$result, { size: "lg" }, {}, {})}</div>`}</div>`;
});

export { Page as default };
//# sourceMappingURL=_page.svelte-DkWJNLlg.js.map
