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
		client: {start:"_app/immutable/entry/start.TPaIXYzO.js",app:"_app/immutable/entry/app.BqflNRa4.js",imports:["_app/immutable/entry/start.TPaIXYzO.js","_app/immutable/chunks/J8pAhCgK.js","_app/immutable/chunks/BeCmXZKr.js","_app/immutable/chunks/BlVhov2R.js","_app/immutable/entry/app.BqflNRa4.js","_app/immutable/chunks/BeCmXZKr.js","_app/immutable/chunks/DhgJD4CZ.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./chunks/0-zmxTIO_D.js')),
			__memo(() => import('./chunks/1-BEbWJ3YV.js')),
			__memo(() => import('./chunks/2--JnlWfbQ.js')),
			__memo(() => import('./chunks/3-hQF3-diZ.js')),
			__memo(() => import('./chunks/4-wp-GxSjt.js')),
			__memo(() => import('./chunks/5-B6YVM5wE.js')),
			__memo(() => import('./chunks/6-Ciy1yGaB.js')),
			__memo(() => import('./chunks/7-B05_dOqg.js')),
			__memo(() => import('./chunks/8-DyvEcchJ.js')),
			__memo(() => import('./chunks/9-DH38AQj0.js')),
			__memo(() => import('./chunks/10-Bhv6CJl2.js')),
			__memo(() => import('./chunks/11-DVZgp-Fs.js')),
			__memo(() => import('./chunks/12-DT5Rjglq.js')),
			__memo(() => import('./chunks/13-DJv0IJzr.js')),
			__memo(() => import('./chunks/14-4xr_K9PN.js')),
			__memo(() => import('./chunks/15-U25vYsN8.js')),
			__memo(() => import('./chunks/16-eK4gbWK9.js'))
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
				page: { layouts: [0,3,], errors: [1,,], leaf: 15 },
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
				page: { layouts: [0,3,], errors: [1,,], leaf: 16 },
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
				id: "/(app)/terms",
				pattern: /^\/terms\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 13 },
				endpoint: null
			},
			{
				id: "/(app)/wallet",
				pattern: /^\/wallet\/?$/,
				params: [],
				page: { layouts: [0,2,], errors: [1,,], leaf: 14 },
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
