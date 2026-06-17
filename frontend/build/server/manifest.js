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
		client: {start:"_app/immutable/entry/start.D1VCNiPN.js",app:"_app/immutable/entry/app.C6DnxyCC.js",imports:["_app/immutable/entry/start.D1VCNiPN.js","_app/immutable/chunks/B-IATXUi.js","_app/immutable/chunks/BPSwtOIW.js","_app/immutable/chunks/CH-g6pII.js","_app/immutable/entry/app.C6DnxyCC.js","_app/immutable/chunks/BPSwtOIW.js","_app/immutable/chunks/ju52Lj3h.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./chunks/0-9Wr8H5vO.js')),
			__memo(() => import('./chunks/1-CNrYTuEO.js')),
			__memo(() => import('./chunks/2-CsZ8y1J4.js')),
			__memo(() => import('./chunks/3-8jNuaVD1.js')),
			__memo(() => import('./chunks/4-IQRA_4Vb.js')),
			__memo(() => import('./chunks/5-DSySx3Z-.js')),
			__memo(() => import('./chunks/6-CT0X3iv5.js')),
			__memo(() => import('./chunks/7-DJOGRWeW.js')),
			__memo(() => import('./chunks/8-BFQTRc6A.js')),
			__memo(() => import('./chunks/9-BODWMOBy.js')),
			__memo(() => import('./chunks/10-lgARpbxO.js')),
			__memo(() => import('./chunks/11-BWsGquA6.js')),
			__memo(() => import('./chunks/12-aX-Xausy.js')),
			__memo(() => import('./chunks/13-CQtvHR8M.js')),
			__memo(() => import('./chunks/14-CHh5xrgD.js')),
			__memo(() => import('./chunks/15-CApNe_xV.js'))
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
				page: { layouts: [0,3,], errors: [1,,], leaf: 14 },
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
				id: "/(app)/privacy",
				pattern: /^\/privacy\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 10 },
				endpoint: null
			},
			{
				id: "/(auth)/register",
				pattern: /^\/register\/?$/,
				params: [],
				page: { layouts: [0,3,], errors: [1,,], leaf: 15 },
				endpoint: null
			},
			{
				id: "/(app)/settings",
				pattern: /^\/settings\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 11 },
				endpoint: null
			},
			{
				id: "/(app)/terms",
				pattern: /^\/terms\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 12 },
				endpoint: null
			},
			{
				id: "/(app)/wallet",
				pattern: /^\/wallet\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 13 },
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
