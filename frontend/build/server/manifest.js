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
		client: {start:"_app/immutable/entry/start.DEm--If0.js",app:"_app/immutable/entry/app.fbWURknA.js",imports:["_app/immutable/entry/start.DEm--If0.js","_app/immutable/chunks/k2PWlTdl.js","_app/immutable/chunks/XXpMwIwE.js","_app/immutable/chunks/DTW7u3Rm.js","_app/immutable/entry/app.fbWURknA.js","_app/immutable/chunks/XXpMwIwE.js","_app/immutable/chunks/3UVa4XIC.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./chunks/0-Bsf5q4aM.js')),
			__memo(() => import('./chunks/1-CMZLPyNF.js')),
			__memo(() => import('./chunks/2-BSAdVmld.js')),
			__memo(() => import('./chunks/3-BeQSoe2F.js')),
			__memo(() => import('./chunks/4-o8q6fygP.js')),
			__memo(() => import('./chunks/5-CpU9kyny.js')),
			__memo(() => import('./chunks/6-1v3oi0g2.js')),
			__memo(() => import('./chunks/7-BF-HK83d.js')),
			__memo(() => import('./chunks/8-CZbvVf-H.js')),
			__memo(() => import('./chunks/9-DAOrtn2L.js')),
			__memo(() => import('./chunks/10-BwdI5VMi.js')),
			__memo(() => import('./chunks/11-bRidAMt2.js')),
			__memo(() => import('./chunks/12-DSQSx62G.js')),
			__memo(() => import('./chunks/13-CAzk36Lr.js')),
			__memo(() => import('./chunks/14-DQtA2p0g.js')),
			__memo(() => import('./chunks/15-Da_lZCM9.js'))
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
