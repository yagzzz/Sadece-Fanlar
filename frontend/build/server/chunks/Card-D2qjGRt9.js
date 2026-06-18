import { c as create_ssr_component, k as compute_rest_props, l as spread, p as escape_attribute_value, q as escape_object } from './ssr-DDQ8otPt.js';
import { c as cn } from './index2-BnafdvHM.js';

const Card = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let $$restProps = compute_rest_props($$props, ["class"]);
  let { class: className = "" } = $$props;
  if ($$props.class === void 0 && $$bindings.class && className !== void 0) $$bindings.class(className);
  return `<div${spread(
    [
      {
        class: escape_attribute_value(cn("rounded-xl border bg-card text-card-foreground shadow", className))
      },
      escape_object($$restProps)
    ],
    {}
  )}>${slots.default ? slots.default({}) : ``}</div>`;
});

export { Card as C };
//# sourceMappingURL=Card-D2qjGRt9.js.map
