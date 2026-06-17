import { c as create_ssr_component, a as subscribe, f as escape } from './ssr-CAqK4lyn.js';
import { p as page } from './stores-qOaUuLm-.js';
import './ssr2-CJcMdXvQ.js';
import './state.svelte-DYGtfCg5.js';

const Error = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let $page, $$unsubscribe_page;
  $$unsubscribe_page = subscribe(page, (value) => $page = value);
  $$unsubscribe_page();
  return `<h1>${escape($page.status)}</h1> <p>${escape($page.error?.message)}</p>`;
});

export { Error as default };
//# sourceMappingURL=error.svelte-BkZB-EYp.js.map
