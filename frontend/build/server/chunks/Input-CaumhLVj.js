import { c as create_ssr_component, l as compute_rest_props, d as add_attribute, f as escape, p as spread, q as escape_attribute_value, t as escape_object } from './ssr-CAqK4lyn.js';
import { c as cn } from './index2-O1tI1Vis.js';

const Input = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let $$restProps = compute_rest_props($$props, ["type", "value", "placeholder", "disabled", "error", "label", "class"]);
  let { type = "text" } = $$props;
  let { value = "" } = $$props;
  let { placeholder = "" } = $$props;
  let { disabled = false } = $$props;
  let { error = "" } = $$props;
  let { label = "" } = $$props;
  let { class: className = "" } = $$props;
  const inputId = `input-${Math.random().toString(36).slice(2, 10)}`;
  if ($$props.type === void 0 && $$bindings.type && type !== void 0) $$bindings.type(type);
  if ($$props.value === void 0 && $$bindings.value && value !== void 0) $$bindings.value(value);
  if ($$props.placeholder === void 0 && $$bindings.placeholder && placeholder !== void 0) $$bindings.placeholder(placeholder);
  if ($$props.disabled === void 0 && $$bindings.disabled && disabled !== void 0) $$bindings.disabled(disabled);
  if ($$props.error === void 0 && $$bindings.error && error !== void 0) $$bindings.error(error);
  if ($$props.label === void 0 && $$bindings.label && label !== void 0) $$bindings.label(label);
  if ($$props.class === void 0 && $$bindings.class && className !== void 0) $$bindings.class(className);
  return `<div class="w-full">${label ? `<label${add_attribute("for", inputId, 0)} class="mb-1.5 block text-sm font-medium text-foreground">${escape(label)}</label>` : ``} <input${spread(
    [
      { id: escape_attribute_value(inputId) },
      { type: escape_attribute_value(type) },
      { value: escape_attribute_value(value) },
      {
        placeholder: escape_attribute_value(placeholder)
      },
      { disabled: disabled || null },
      {
        class: escape_attribute_value(cn("flex h-10 w-full rounded-lg border bg-background px-3 py-2 text-sm", "ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium", "placeholder:text-muted-foreground", "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring", "disabled:cursor-not-allowed disabled:opacity-50", error ? "border-destructive" : "border-input", className))
      },
      escape_object($$restProps)
    ],
    {}
  )}> ${error ? `<p class="mt-1 text-sm text-destructive">${escape(error)}</p>` : ``}</div>`;
});

export { Input as I };
//# sourceMappingURL=Input-CaumhLVj.js.map
