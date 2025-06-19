<script>
	import '../app.css';
	import { page } from '$app/stores';

	let { children } = $props();

	// Navigation state
	let isMenuOpen = $state(false);

	// Navigation items
	const navItems = [
		{ href: '/', label: '首页', icon: '🏠' },
		{ href: '/research', label: '神秘研究', icon: '🔍' },
		{ href: '/chat', label: '智能对话', icon: '💬' },
		{ href: '/config', label: '项目配置', icon: '⚙️' },
		{ href: '/reports', label: '研究报告', icon: '📊' },
		{ href: '/timeline', label: '事件时间线', icon: '📅' },
		{ href: '/graph', label: '关联图谱', icon: '🕸️' }
	];

	function toggleMenu() {
		isMenuOpen = !isMenuOpen;
	}

	function closeMenu() {
		isMenuOpen = false;
	}
</script>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	<!-- Navigation Header -->
	<nav class="bg-white dark:bg-gray-800 shadow-lg border-b border-gray-200 dark:border-gray-700">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between h-16">
				<!-- Logo and Title -->
				<div class="flex items-center">
					<div class="flex-shrink-0 flex items-center">
						<span class="text-2xl font-bold text-indigo-600 dark:text-indigo-400">🔮</span>
						<span class="ml-2 text-xl font-semibold text-gray-900 dark:text-white">灵境研究</span>
					</div>
				</div>

				<!-- Desktop Navigation -->
				<div class="hidden md:flex items-center space-x-8">
					{#each navItems as item (item.href)}
						<a
							href={item.href}
							class="flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors
								{$page.url.pathname === item.href
									? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300'
									: 'text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'}"
							onclick={closeMenu}
						>
							<span class="mr-2">{item.icon}</span>
							{item.label}
						</a>
					{/each}
				</div>

				<!-- Mobile menu button -->
				<div class="md:hidden flex items-center">
					<button
						type="button"
						class="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
						onclick={toggleMenu}
					>
						<span class="sr-only">打开主菜单</span>
						{#if isMenuOpen}
							<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
							</svg>
						{:else}
							<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
							</svg>
						{/if}
					</button>
				</div>
			</div>
		</div>

		<!-- Mobile Navigation Menu -->
		{#if isMenuOpen}
			<div class="md:hidden">
				<div class="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
					{#each navItems as item (item.href)}
							<a
							href={item.href}
							class="flex items-center px-3 py-2 rounded-md text-base font-medium transition-colors
								{$page.url.pathname === item.href
									? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300'
									: 'text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'}"
							onclick={closeMenu}
						>
							<span class="mr-3">{item.icon}</span>
							{item.label}
						</a>
					{/each}
				</div>
			</div>
		{/if}
	</nav>

	<!-- Main Content -->
	<main class="flex-1">
		{@render children()}
	</main>

	<!-- Footer -->
	<footer class="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
		<div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between items-center">
				<div class="text-sm text-gray-500 dark:text-gray-400">
					© 2024 灵境研究系统. 探索未知，揭示真相.
				</div>
				<div class="flex space-x-4">
					<a href="/about" class="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300">关于我们</a>
					<a href="/privacy" class="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300">隐私政策</a>
					<a href="/contact" class="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300">联系我们</a>
				</div>
			</div>
		</div>
	</footer>
</div>

<style>
	/* Custom scrollbar for webkit browsers */
	:global(html) {
		scroll-behavior: smooth;
	}

	:global(::-webkit-scrollbar) {
		width: 8px;
	}

	:global(::-webkit-scrollbar-track) {
		background: #f1f1f1;
	}

	:global(::-webkit-scrollbar-thumb) {
		background: #c1c1c1;
		border-radius: 4px;
	}

	:global(::-webkit-scrollbar-thumb:hover) {
		background: #a1a1a1;
	}

	:global(.dark ::-webkit-scrollbar-track) {
		background: #374151;
	}

	:global(.dark ::-webkit-scrollbar-thumb) {
		background: #6b7280;
	}

	:global(.dark ::-webkit-scrollbar-thumb:hover) {
		background: #9ca3af;
	}
</style>
