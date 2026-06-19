<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { api } from '$lib/api';
	import { Icon } from '$lib/components/ui';

	export let src: string;
	export let poster: string | undefined = undefined;
	/** Bedava içerik mi? true ise videodan önce atlanabilir pre-roll reklam gösterilir. */
	export let freeContent: boolean = false;

	let videoEl: HTMLVideoElement;
	let adEl: HTMLVideoElement;
	let container: HTMLDivElement;

	// Faz: reklam mı ana video mu
	let phase: 'idle' | 'ad' | 'main' = 'idle';
	let ad: any = null;
	let adChecked = false;

	// Oynatma durumu
	let playing = false;
	let current = 0;
	let duration = 0;
	let buffered = 0;
	let volume = 1;
	let muted = false;
	let speed = 1;
	let isFs = false;
	let controlsVisible = true;
	let hideTimer: any;
	let loadingMain = false;

	// Reklam atlama
	let skipIn = 0;
	let skipReady = false;
	let adInterval: any;

	const speeds = [0.5, 1, 1.25, 1.5, 2];

	onMount(async () => {
		if (freeContent) {
			try {
				ad = await (api as any).ads.preroll();
			} catch {
				ad = null;
			}
		}
		adChecked = true;
	});

	onDestroy(() => {
		clearInterval(adInterval);
		clearTimeout(hideTimer);
	});

	function fmt(t: number): string {
		if (!isFinite(t) || t < 0) t = 0;
		const m = Math.floor(t / 60);
		const s = Math.floor(t % 60);
		return `${m}:${s.toString().padStart(2, '0')}`;
	}

	// ----- Başlat -----
	function start() {
		if (ad && ad.media_url) {
			phase = 'ad';
			skipIn = ad.skip_after ?? 3;
			skipReady = skipIn <= 0;
			setTimeout(() => {
				adEl?.play().catch(() => {});
				adInterval = setInterval(() => {
					skipIn = Math.max(0, skipIn - 1);
					if (skipIn <= 0) { skipReady = true; clearInterval(adInterval); }
				}, 1000);
			}, 0);
		} else {
			beginMain();
		}
	}

	function beginMain() {
		clearInterval(adInterval);
		phase = 'main';
		loadingMain = true;
		setTimeout(() => {
			videoEl?.play().then(() => { playing = true; }).catch(() => {});
		}, 0);
	}

	function skipAd() {
		if (!skipReady) return;
		beginMain();
	}

	function adClick() {
		if (!ad) return;
		(api as any).ads.click(ad.id).then((r: any) => {
			if (r?.url) window.open(r.url, '_blank', 'noopener');
		}).catch(() => {});
	}

	// ----- Ana video kontrolleri -----
	function togglePlay() {
		if (phase === 'idle') { start(); return; }
		if (phase !== 'main') return;
		if (videoEl.paused) { videoEl.play(); playing = true; }
		else { videoEl.pause(); playing = false; }
		flashControls();
	}

	function onTime() {
		current = videoEl.currentTime;
		if (videoEl.buffered.length) buffered = videoEl.buffered.end(videoEl.buffered.length - 1);
	}
	function onLoaded() { duration = videoEl.duration; loadingMain = false; }
	function seek(e: MouseEvent) {
		const bar = e.currentTarget as HTMLElement;
		const rect = bar.getBoundingClientRect();
		const pct = (e.clientX - rect.left) / rect.width;
		videoEl.currentTime = pct * duration;
		current = videoEl.currentTime;
	}
	function setVolume(v: number) { volume = v; videoEl.volume = v; muted = v === 0; }
	function toggleMute() { muted = !muted; videoEl.muted = muted; }
	function setSpeed(s: number) { speed = s; videoEl.playbackRate = s; }
	function toggleFs() {
		if (!document.fullscreenElement) container.requestFullscreen?.().then(() => (isFs = true)).catch(() => {});
		else document.exitFullscreen?.().then(() => (isFs = false)).catch(() => {});
	}
	function flashControls() {
		controlsVisible = true;
		clearTimeout(hideTimer);
		if (playing) hideTimer = setTimeout(() => (controlsVisible = false), 2800);
	}
	function onKey(e: KeyboardEvent) {
		if (phase !== 'main') return;
		if (e.key === ' ' || e.key === 'k') { e.preventDefault(); togglePlay(); }
		else if (e.key === 'ArrowRight') videoEl.currentTime = Math.min(duration, videoEl.currentTime + 5);
		else if (e.key === 'ArrowLeft') videoEl.currentTime = Math.max(0, videoEl.currentTime - 5);
		else if (e.key === 'f') toggleFs();
		else if (e.key === 'm') toggleMute();
	}

	$: progress = duration ? (current / duration) * 100 : 0;
	$: bufPct = duration ? (buffered / duration) * 100 : 0;
</script>

<svelte:document on:fullscreenchange={() => (isFs = !!document.fullscreenElement)} />

<div
	bind:this={container}
	class="relative w-full h-full bg-black select-none group"
	on:mousemove={flashControls}
	on:keydown={onKey}
	role="application"
	tabindex="0"
>
	{#if phase === 'ad' && ad}
		<!-- Pre-roll reklam -->
		<video
			bind:this={adEl}
			src={ad.media_url}
			class="w-full h-full object-contain bg-black cursor-pointer"
			autoplay
			playsinline
			on:ended={beginMain}
			on:click={adClick}
		></video>
		<span class="absolute top-3 left-3 px-2 py-0.5 text-[10px] font-bold uppercase rounded bg-yellow-400 text-black">Reklam</span>
		<button
			class="absolute bottom-4 right-4 px-3 py-2 text-sm rounded-md bg-black/70 text-white border border-white/20 hover:bg-black/90 disabled:opacity-70"
			on:click={skipAd}
			disabled={!skipReady}
		>
			{skipReady ? 'Reklamı geç ▸' : `Geç (${skipIn})`}
		</button>
	{:else if phase === 'main'}
		<!-- Ana video -->
		<video
			bind:this={videoEl}
			{src}
			{poster}
			class="w-full h-full object-contain bg-black"
			playsinline
			on:timeupdate={onTime}
			on:loadedmetadata={onLoaded}
			on:progress={onTime}
			on:click={togglePlay}
			on:play={() => (playing = true)}
			on:pause={() => (playing = false)}
			on:ended={() => (playing = false)}
		>
			<track kind="captions" />
		</video>

		{#if loadingMain}
			<div class="absolute inset-0 grid place-items-center pointer-events-none">
				<div class="w-10 h-10 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
			</div>
		{/if}

		{#if !playing}
			<button class="absolute inset-0 grid place-items-center" on:click={togglePlay} aria-label="Oynat">
				<span class="grid place-items-center w-16 h-16 rounded-full bg-black/60 text-white">
					<Icon name="zap" size={28} />
				</span>
			</button>
		{/if}

		<!-- Kontrol çubuğu -->
		<div
			class="absolute bottom-0 inset-x-0 px-3 pb-2 pt-8 bg-gradient-to-t from-black/80 to-transparent transition-opacity {controlsVisible || !playing ? 'opacity-100' : 'opacity-0'}"
		>
			<!-- İlerleme çubuğu -->
			<div class="relative h-1.5 bg-white/25 rounded-full cursor-pointer mb-2 group/bar" on:click={seek} role="slider" aria-valuenow={progress} tabindex="0">
				<div class="absolute inset-y-0 left-0 bg-white/40 rounded-full" style="width:{bufPct}%"></div>
				<div class="absolute inset-y-0 left-0 bg-primary rounded-full" style="width:{progress}%"></div>
				<div class="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-primary shadow" style="left:calc({progress}% - 6px)"></div>
			</div>

			<div class="flex items-center gap-3 text-white text-sm">
				<button on:click={togglePlay} aria-label="Oynat/Duraklat">
					<Icon name={playing ? 'clock' : 'zap'} size={18} />
				</button>
				<div class="flex items-center gap-1.5">
					<button on:click={toggleMute} aria-label="Ses">
						<Icon name={muted || volume === 0 ? 'x' : 'bell'} size={16} />
					</button>
					<input type="range" min="0" max="1" step="0.05" value={muted ? 0 : volume} on:input={(e) => setVolume(parseFloat(e.currentTarget.value))} class="w-16 accent-primary" />
				</div>
				<span class="tabular-nums text-xs">{fmt(current)} / {fmt(duration)}</span>
				<div class="ml-auto flex items-center gap-3">
					<select class="bg-transparent text-xs border border-white/20 rounded px-1 py-0.5" value={speed} on:change={(e) => setSpeed(parseFloat(e.currentTarget.value))}>
						{#each speeds as s}<option class="text-black" value={s}>{s}x</option>{/each}
					</select>
					<button on:click={toggleFs} aria-label="Tam ekran"><Icon name="image" size={16} /></button>
				</div>
			</div>
		</div>
	{:else}
		<!-- Başlangıç (poster + büyük oynat) -->
		{#if poster}<img src={poster} alt="" class="absolute inset-0 w-full h-full object-cover" />{/if}
		<button class="absolute inset-0 grid place-items-center bg-black/30" on:click={start} aria-label="Oynat" disabled={!adChecked}>
			<span class="grid place-items-center w-16 h-16 rounded-full bg-primary text-white shadow-glow">
				<Icon name="zap" size={28} />
			</span>
		</button>
	{/if}
</div>
