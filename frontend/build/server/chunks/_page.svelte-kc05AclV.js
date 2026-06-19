import { c as create_ssr_component, a as subscribe, v as validate_component, g as add_styles } from './ssr-CxJiF8w8.js';
import './ssr2-CJcMdXvQ.js';
import './state.svelte-DYGtfCg5.js';
import { p as page } from './stores-CQajP4Vw.js';
import './auth-BhyVnWr0.js';
import './client-CybrWH6X.js';
import { B as Button } from './Button-ClLhbrma.js';
import { C as Card } from './Card-CWZexsSp.js';
import { I as Input } from './Input-BgLM1v2T.js';
import { i as isValidEmail, a as isValidUsername } from './index2-Dhq654YE.js';
import './index-YI0dIwkT.js';
import 'clsx';
import 'tailwind-merge';

const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let emailError;
  let usernameError;
  let $page, $$unsubscribe_page;
  $$unsubscribe_page = subscribe(page, (value) => $page = value);
  let email = "";
  let username = "";
  let displayName = "";
  let $$settled;
  let $$rendered;
  let previous_head = $$result.head;
  do {
    $$settled = true;
    $$result.head = previous_head;
    emailError = email && !isValidEmail(email) ? "Geçersiz e-posta adresi" : "";
    usernameError = username && !isValidUsername(username) ? "Kullanıcı adı 3-20 karakter olmalı; sadece harf, rakam ve alt çizgi" : "";
    {
      if ($page.url.searchParams.get("creator") === "1") ;
    }
    $$rendered = `${$$result.head += `<!-- HEAD_svelte-1k19nv8_START -->${$$result.title = `<title>Kayıt Ol | SadeceFanlar</title>`, ""}<!-- HEAD_svelte-1k19nv8_END -->`, ""} ${validate_component(Card, "Card").$$render($$result, { class: "p-8" }, {}, {
      default: () => {
        return `<div class="text-center mb-8" data-svelte-h="svelte-69uffr"><a href="/" class="text-3xl font-bold text-primary">SadeceFanlar</a> <p class="text-neutral-500 mt-2">Anonim hesabını oluştur</p></div>  <div class="flex items-center justify-center gap-2 mb-8"><div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium bg-primary text-white" data-svelte-h="svelte-1qggk4e">1</div> <div class="w-12 h-1 rounded bg-neutral-200 dark:bg-neutral-700"><div class="h-full bg-primary rounded transition-all"${add_styles({ "width": "0%" })}></div></div> <div class="${[
          "w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors",
          "  bg-neutral-200 dark:bg-neutral-700 text-neutral-500"
        ].join(" ").trim()}" data-svelte-h="svelte-1cmfiaa">2</div></div> <form class="space-y-4">${``} ${`${validate_component(Input, "Input").$$render(
          $$result,
          {
            label: "Kullanıcı Adı",
            placeholder: "kullaniciadiniz",
            error: usernameError,
            required: true,
            value: username
          },
          {
            value: ($$value) => {
              username = $$value;
              $$settled = false;
            }
          },
          {}
        )} ${validate_component(Input, "Input").$$render(
          $$result,
          {
            type: "email",
            label: "E-posta (isteğe bağlı)",
            placeholder: "anonim kalmak için boş bırakın",
            error: emailError,
            value: email
          },
          {
            value: ($$value) => {
              email = $$value;
              $$settled = false;
            }
          },
          {}
        )} ${validate_component(Input, "Input").$$render(
          $$result,
          {
            label: "Görünen Ad (isteğe bağlı)",
            placeholder: "Takma adınız",
            value: displayName
          },
          {
            value: ($$value) => {
              displayName = $$value;
              $$settled = false;
            }
          },
          {}
        )} ${validate_component(Button, "Button").$$render(
          $$result,
          {
            type: "submit",
            class: "w-full",
            disabled: !username || !!emailError || !!usernameError
          },
          {},
          {
            default: () => {
              return `Devam Et`;
            }
          }
        )}`}</form> <p class="text-center text-sm text-neutral-500 mt-6" data-svelte-h="svelte-14bs9oj">Zaten hesabınız var mı?
		<a href="/login" class="text-primary hover:underline">Giriş yap</a></p> <div class="mt-8 pt-6 border-t border-neutral-200 dark:border-neutral-700" data-svelte-h="svelte-1frad3p"><p class="text-xs text-neutral-400 text-center">🔒 Anonim kayıt. Kripto ile ödeyin, kişisel veri gerekmez. E-posta isteğe bağlıdır.</p></div>`;
      }
    })}`;
  } while (!$$settled);
  $$unsubscribe_page();
  return $$rendered;
});

export { Page as default };
//# sourceMappingURL=_page.svelte-kc05AclV.js.map
