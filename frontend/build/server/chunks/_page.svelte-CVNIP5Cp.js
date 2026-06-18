import { c as create_ssr_component, v as validate_component, f as escape } from './ssr-DDQ8otPt.js';
import './ssr2-CJcMdXvQ.js';
import './state.svelte-DYGtfCg5.js';
import './auth-C_KGpDdi.js';
import { B as Button } from './Button-DeTt_asi.js';
import { C as Card } from './Card-BxCPRD7E.js';
import { I as Input } from './Input-DHAIDfxf.js';
import 'clsx';
import './index-BCAmX91C.js';
import './index2-DIqK_D2c.js';
import 'tailwind-merge';

const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let identifier = "";
  let password = "";
  let loading = false;
  let $$settled;
  let $$rendered;
  let previous_head = $$result.head;
  do {
    $$settled = true;
    $$result.head = previous_head;
    $$rendered = `${$$result.head += `<!-- HEAD_svelte-1x8k82r_START -->${$$result.title = `<title>Giriş Yap | SadeceFanlar</title>`, ""}<!-- HEAD_svelte-1x8k82r_END -->`, ""} ${validate_component(Card, "Card").$$render($$result, { class: "p-8" }, {}, {
      default: () => {
        return `<div class="text-center mb-8" data-svelte-h="svelte-ga2j87"><a href="/" class="text-3xl font-bold text-primary">SadeceFanlar</a> <p class="text-neutral-500 mt-2">Tekrar hoş geldiniz</p></div> <form class="space-y-4">${``} ${validate_component(Input, "Input").$$render(
          $$result,
          {
            label: "Kullanıcı adı veya e-posta",
            placeholder: "kullaniciadi",
            required: true,
            value: identifier
          },
          {
            value: ($$value) => {
              identifier = $$value;
              $$settled = false;
            }
          },
          {}
        )} ${validate_component(Input, "Input").$$render(
          $$result,
          {
            type: "password",
            label: "Şifre",
            placeholder: "••••••••",
            required: true,
            value: password
          },
          {
            value: ($$value) => {
              password = $$value;
              $$settled = false;
            }
          },
          {}
        )} <div class="flex items-center justify-between text-sm" data-svelte-h="svelte-1ydwnqe"><label class="flex items-center gap-2"><input type="checkbox" class="rounded border-neutral-300"> <span class="text-neutral-600 dark:text-neutral-400">Beni hatırla</span></label> <a href="/forgot-password" class="text-primary hover:underline">Şifremi unuttum?</a></div> ${validate_component(Button, "Button").$$render(
          $$result,
          {
            type: "submit",
            class: "w-full",
            disabled: loading
          },
          {},
          {
            default: () => {
              return `${escape("Giriş Yap")}`;
            }
          }
        )}</form> <p class="text-center text-sm text-neutral-500 mt-6" data-svelte-h="svelte-6wg5tg">Hesabınız yok mu?
		<a href="/register" class="text-primary hover:underline">Kayıt ol</a></p> <div class="mt-6 rounded-lg border border-neutral-200 dark:border-neutral-700 p-4" data-svelte-h="svelte-gy2dft"><p class="text-sm font-semibold text-neutral-800 dark:text-neutral-200">İçerik Üreticisi misin?</p> <p class="mt-1 text-xs text-neutral-500">Takma adınla saniyeler içinde başla. Gerçek isim, kimlik veya yüz fotoğrafı istenmez — yalnızca 18+ onayı.</p> <a href="/register?creator=1" class="mt-3 inline-flex w-full items-center justify-center rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white">Üretici olarak kayıt ol</a></div> <div class="mt-8 pt-6 border-t border-neutral-200 dark:border-neutral-700" data-svelte-h="svelte-15k4x6p"><p class="text-xs text-neutral-400 text-center">🔒 Gizliliğiniz korunmaktadır. IP adresinizi loglamıyor, kişisel verilerinizi saklamıyoruz.</p></div>`;
      }
    })}`;
  } while (!$$settled);
  return $$rendered;
});

export { Page as default };
//# sourceMappingURL=_page.svelte-CVNIP5Cp.js.map
