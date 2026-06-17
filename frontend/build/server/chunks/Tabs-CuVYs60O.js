import { c as create_ssr_component, b as createEventDispatcher, d as add_attribute, e as each, f as escape } from './ssr-DDQ8otPt.js';
import { c as cn } from './index2-CqlzXTMx.js';

const Tabs = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { tabs } = $$props;
  let { activeTab } = $$props;
  let { class: className = "" } = $$props;
  createEventDispatcher();
  if ($$props.tabs === void 0 && $$bindings.tabs && tabs !== void 0) $$bindings.tabs(tabs);
  if ($$props.activeTab === void 0 && $$bindings.activeTab && activeTab !== void 0) $$bindings.activeTab(activeTab);
  if ($$props.class === void 0 && $$bindings.class && className !== void 0) $$bindings.class(className);
  return `<div${add_attribute("class", cn("border-b border-neutral-200 dark:border-neutral-700", className), 0)}><nav class="-mb-px flex space-x-8" aria-label="Tabs">${each(tabs, (tab) => {
    return `<button type="button"${add_attribute(
      "class",
      cn(
        "whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors",
        activeTab === tab.id ? "border-primary text-primary" : "border-transparent text-neutral-500 hover:text-neutral-700 hover:border-neutral-300 dark:text-neutral-400 dark:hover:text-neutral-300",
        tab.disabled && "opacity-50 cursor-not-allowed"
      ),
      0
    )} ${tab.disabled ? "disabled" : ""}${add_attribute("aria-selected", activeTab === tab.id, 0)} role="tab">${tab.icon ? `<span class="mr-2">${escape(tab.icon)}</span>` : ``} ${escape(tab.label)} </button>`;
  })}</nav></div> <div class="mt-4">${slots.default ? slots.default({}) : ``}</div>`;
});

export { Tabs as T };
//# sourceMappingURL=Tabs-CuVYs60O.js.map
