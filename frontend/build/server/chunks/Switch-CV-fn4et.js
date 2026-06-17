import { c as create_ssr_component, d as add_attribute, f as escape } from './ssr-DDQ8otPt.js';
import { c as cn } from './index2-CqlzXTMx.js';

const Textarea = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { value = "" } = $$props;
  let { placeholder = "" } = $$props;
  let { label = "" } = $$props;
  let { error = "" } = $$props;
  let { disabled = false } = $$props;
  let { rows = 4 } = $$props;
  let { maxLength = void 0 } = $$props;
  let { class: className = "" } = $$props;
  let showCount = !!maxLength;
  const textareaId = `textarea-${Math.random().toString(36).slice(2, 10)}`;
  if ($$props.value === void 0 && $$bindings.value && value !== void 0) $$bindings.value(value);
  if ($$props.placeholder === void 0 && $$bindings.placeholder && placeholder !== void 0) $$bindings.placeholder(placeholder);
  if ($$props.label === void 0 && $$bindings.label && label !== void 0) $$bindings.label(label);
  if ($$props.error === void 0 && $$bindings.error && error !== void 0) $$bindings.error(error);
  if ($$props.disabled === void 0 && $$bindings.disabled && disabled !== void 0) $$bindings.disabled(disabled);
  if ($$props.rows === void 0 && $$bindings.rows && rows !== void 0) $$bindings.rows(rows);
  if ($$props.maxLength === void 0 && $$bindings.maxLength && maxLength !== void 0) $$bindings.maxLength(maxLength);
  if ($$props.class === void 0 && $$bindings.class && className !== void 0) $$bindings.class(className);
  return `<div${add_attribute("class", cn("w-full", className), 0)}>${label ? `<label${add_attribute("for", textareaId, 0)} class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">${escape(label)}</label>` : ``} <div class="relative"><textarea${add_attribute("id", textareaId, 0)}${add_attribute("placeholder", placeholder, 0)} ${disabled ? "disabled" : ""}${add_attribute("rows", rows, 0)}${add_attribute("maxlength", maxLength, 0)}${add_attribute(
    "class",
    cn(
      "block w-full rounded-lg border px-3 py-2 text-sm transition-colors resize-none",
      "bg-white dark:bg-neutral-900",
      "placeholder:text-neutral-400 dark:placeholder:text-neutral-500",
      "focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent",
      error ? "border-red-500 focus:ring-red-500" : "border-neutral-300 dark:border-neutral-600",
      disabled && "opacity-50 cursor-not-allowed bg-neutral-100 dark:bg-neutral-800"
    ),
    0
  )}>${escape(value || "")}</textarea> ${showCount ? `<div class="absolute bottom-2 right-2 text-xs text-neutral-400">${escape(value.length)}${escape(maxLength ? `/${maxLength}` : "")}</div>` : ``}</div> ${error ? `<p class="mt-1 text-sm text-red-500">${escape(error)}</p>` : ``}</div>`;
});
const Switch = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { checked = false } = $$props;
  let { label = "" } = $$props;
  let { disabled = false } = $$props;
  let { class: className = "" } = $$props;
  if ($$props.checked === void 0 && $$bindings.checked && checked !== void 0) $$bindings.checked(checked);
  if ($$props.label === void 0 && $$bindings.label && label !== void 0) $$bindings.label(label);
  if ($$props.disabled === void 0 && $$bindings.disabled && disabled !== void 0) $$bindings.disabled(disabled);
  if ($$props.class === void 0 && $$bindings.class && className !== void 0) $$bindings.class(className);
  return `<label${add_attribute("class", cn("inline-flex items-center cursor-pointer", disabled && "cursor-not-allowed opacity-50", className), 0)}><button type="button" role="switch"${add_attribute("aria-checked", checked, 0)} ${disabled ? "disabled" : ""}${add_attribute(
    "class",
    cn("relative inline-flex h-6 w-11 flex-shrink-0 rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 dark:focus:ring-offset-neutral-900", checked ? "bg-primary" : "bg-neutral-200 dark:bg-neutral-700"),
    0
  )}><span${add_attribute("class", cn("pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out", checked ? "translate-x-5" : "translate-x-0"), 0)}></span></button> ${label ? `<span class="ml-3 text-sm font-medium text-neutral-700 dark:text-neutral-300">${escape(label)}</span>` : ``}</label>`;
});

export { Switch as S, Textarea as T };
//# sourceMappingURL=Switch-CV-fn4et.js.map
