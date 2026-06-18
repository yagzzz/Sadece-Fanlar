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
		client: {start:"_app/immutable/entry/start.T01BwsGF.js",app:"_app/immutable/entry/app.CxfenbzG.js",imports:["_app/immutable/entry/start.T01BwsGF.js","_app/immutable/chunks/1oxUfEqp.js","_app/immutable/chunks/BeCmXZKr.js","_app/immutable/chunks/BlVhov2R.js","_app/immutable/entry/app.CxfenbzG.js","_app/immutable/chunks/BeCmXZKr.js","_app/immutable/chunks/DhgJD4CZ.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./chunks/0-DbQyoKft.js')),
			__memo(() => import('./chunks/1-BQkg8dGL.js')),
			__memo(() => import('./chunks/2-Bz6hLAAx.js')),
			__memo(() => import('./chunks/3-hQF3-diZ.js')),
			__memo(() => import('./chunks/4-BSY7hnup.js')),
			__memo(() => import('./chunks/5-CJcWvsbl.js')),
			__memo(() => import('./chunks/6-CabQ6EQ0.js')),
			__memo(() => import('./chunks/7-CRMr7vrW.js')),
			__memo(() => import('./chunks/8-Cz79BEpc.js')),
			__memo(() => import('./chunks/9-BDepzV5M.js')),
			__memo(() => import('./chunks/10--SXLqZFd.js')),
			__memo(() => import('./chunks/11-DVZgp-Fs.js')),
			__memo(() => import('./chunks/12-BdugXrb3.js')),
			__memo(() => import('./chunks/13-DJv0IJzr.js')),
			__memo(() => import('./chunks/14-CeE5I3p1.js')),
			__memo(() => import('./chunks/15-LXt2JsX7.js')),
			__memo(() => import('./chunks/16-D8dnEOIw.js'))
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
