import { c as create_ssr_component } from './ssr-DDQ8otPt.js';

const Layout = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { children } = $$props;
  if ($$props.children === void 0 && $$bindings.children && children !== void 0) $$bindings.children(children);
  return `<div class="min-h-screen flex items-center justify-center bg-neutral-50 dark:bg-neutral-950 py-12 px-4"><div class="w-full max-w-md">${slots.default ? slots.default({}) : ``}</div></div>`;
});

export { Layout as default };
//# sourceMappingURL=_layout.svelte-HUgeQLmD.js.map
