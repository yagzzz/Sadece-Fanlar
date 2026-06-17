import { o as onMount } from './ssr2-CJcMdXvQ.js';

const is_legacy = onMount.toString().includes("$$") || /function \w+\(\) \{\}/.test(onMount.toString());
if (is_legacy) {
  ({
    url: new URL("https://example.com")
  });
}
//# sourceMappingURL=state.svelte-DYGtfCg5.js.map
