const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set([]),
	mimeTypes: {},
	_: {
		client: {start:"_app/immutable/entry/start.DqoR6w3n.js",app:"_app/immutable/entry/app.Ccz_lTdV.js",imports:["_app/immutable/entry/start.DqoR6w3n.js","_app/immutable/chunks/DGZe7SjK.js","_app/immutable/chunks/DEfcOWBe.js","_app/immutable/chunks/BPoDya3x.js","_app/immutable/entry/app.Ccz_lTdV.js","_app/immutable/chunks/DEfcOWBe.js","_app/immutable/chunks/BH3wXgZ4.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./chunks/0-kSHKpR5w.js')),
			__memo(() => import('./chunks/1-DiSnTGyK.js')),
			__memo(() => import('./chunks/2-BR65HzSR.js')),
			__memo(() => import('./chunks/3-C7_jehBt.js')),
			__memo(() => import('./chunks/4-Bg5J7kEF.js')),
			__memo(() => import('./chunks/5-O6ra8CoK.js')),
			__memo(() => import('./chunks/6-Oqvl-yWt.js')),
			__memo(() => import('./chunks/7-CZxzpnJx.js')),
			__memo(() => import('./chunks/8-CVLPS8Ey.js')),
			__memo(() => import('./chunks/9-B2ahd-EH.js')),
			__memo(() => import('./chunks/10-VctePTBp.js')),
			__memo(() => import('./chunks/11-t6dpQMru.js')),
			__memo(() => import('./chunks/12-ulWUJe47.js')),
			__memo(() => import('./chunks/13-BpM9lx8K.js')),
			__memo(() => import('./chunks/14-z8BqYMxz.js')),
			__memo(() => import('./chunks/15-43R_q9D0.js')),
			__memo(() => import('./chunks/16-C8IDWLqH.js')),
			__memo(() => import('./chunks/17-sf9OH-1b.js')),
			__memo(() => import('./chunks/18-BKxOeUZH.js'))
		],
		remotes: {
			
		},
		routes: [
			{
				id: "/(app)",
				pattern: /^\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 4 },
				endpoint: null
			},
			{
				id: "/(app)/explore",
				pattern: /^\/explore\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 6 },
				endpoint: null
			},
			{
				id: "/(auth)/login",
				pattern: /^\/login\/?$/,
				params: [],
				page: { layouts: [0,3,], errors: [1,,], leaf: 16 },
				endpoint: null
			},
			{
				id: "/(app)/messages",
				pattern: /^\/messages\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 7 },
				endpoint: null
			},
			{
				id: "/(app)/new-post",
				pattern: /^\/new-post\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 8 },
				endpoint: null
			},
			{
				id: "/(app)/notifications",
				pattern: /^\/notifications\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 9 },
				endpoint: null
			},
			{
				id: "/(app)/post/[id]",
				pattern: /^\/post\/([^/]+?)\/?$/,
				params: [{"name":"id","optional":false,"rest":false,"chained":false}],
				page: { layouts: [0,2,], errors: [1,,], leaf: 10 },
				endpoint: null
			},
			{
				id: "/(app)/privacy",
				pattern: /^\/privacy\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 11 },
				endpoint: null
			},
			{
				id: "/(auth)/register",
				pattern: /^\/register\/?$/,
				params: [],
				page: { layouts: [0,3,], errors: [1,,], leaf: 17 },
				endpoint: null
			},
			{
				id: "/(app)/settings",
				pattern: /^\/settings\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 12 },
				endpoint: null
			},
			{
				id: "/(app)/support",
				pattern: /^\/support\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 13 },
				endpoint: null
			},
			{
				id: "/suspended",
				pattern: /^\/suspended\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 18 },
				endpoint: null
			},
			{
				id: "/(app)/terms",
				pattern: /^\/terms\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 14 },
				endpoint: null
			},
			{
				id: "/(app)/wallet",
				pattern: /^\/wallet\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 15 },
				endpoint: null
			},
			{
				id: "/(app)/[username]",
				pattern: /^\/([^/]+?)\/?$/,
				params: [{"name":"username","optional":false,"rest":false,"chained":false}],
				page: { layouts: [0,2,], errors: [1,,], leaf: 5 },
				endpoint: null
			}
		],
		prerendered_routes: new Set([]),
		matchers: async () => {
			
			return {  };
		},
		server_assets: {}
	}
}
})();

const prerendered = new Set([]);

export { manifest, prerendered };
//# sourceMappingURL=manifest.js.map
