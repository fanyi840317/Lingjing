<script lang="ts">
	import { goto } from '$app/navigation';

	// Feature cards data
	const features = [
		{
			id: 'research',
			title: '神秘事件研究',
			description: '深度分析神秘事件，运用AI技术进行多维度调查研究',
			icon: '🔍',
			color: 'from-blue-500 to-indigo-600',
			href: '/research',
			stats: { label: '研究案例', value: '156+' }
		},
		{
			id: 'chat',
			title: '智能对话助手',
			description: '与AI助手对话，获取专业的研究建议和分析支持',
			icon: '💬',
			color: 'from-green-500 to-emerald-600',
			href: '/chat',
			stats: { label: '对话次数', value: '2.3K+' }
		},
		{
			id: 'reports',
			title: '研究报告',
			description: '查看详细的研究报告，包含数据分析和结论总结',
			icon: '📊',
			color: 'from-purple-500 to-pink-600',
			href: '/reports',
			stats: { label: '生成报告', value: '89' }
		},
		{
			id: 'timeline',
			title: '事件时间线',
			description: '可视化展示事件发展脉络，理清时间关系',
			icon: '📅',
			color: 'from-orange-500 to-red-600',
			href: '/timeline',
			stats: { label: '时间节点', value: '1.2K+' }
		},
		{
			id: 'graph',
			title: '关联图谱',
			description: '探索事件、人物、地点之间的复杂关联关系',
			icon: '🕸️',
			color: 'from-teal-500 to-cyan-600',
			href: '/graph',
			stats: { label: '关联节点', value: '3.4K+' }
		},
		{
			id: 'config',
			title: '系统配置',
			description: '自定义研究参数，优化AI分析模型设置',
			icon: '⚙️',
			color: 'from-gray-500 to-slate-600',
			href: '/config',
			stats: { label: '配置项', value: '25+' }
		}
	];

	// Recent activities
	const recentActivities = [
		{
			id: 1,
			type: 'research',
			title: '新研究案例：神秘失踪事件分析',
			time: '2小时前',
			status: 'completed'
		},
		{
			id: 2,
			type: 'report',
			title: '生成综合分析报告',
			time: '4小时前',
			status: 'completed'
		},
		{
			id: 3,
			type: 'chat',
			title: 'AI助手对话：证据可信度评估',
			time: '6小时前',
			status: 'completed'
		},
		{
			id: 4,
			type: 'timeline',
			title: '更新事件时间线',
			time: '1天前',
			status: 'completed'
		}
	];

	function navigateToFeature(href: string) {
		goto(href);
	}

	function getStatusColor(status: string) {
		switch (status) {
			case 'completed':
				return 'text-green-600 bg-green-100';
			case 'processing':
				return 'text-yellow-600 bg-yellow-100';
			case 'pending':
				return 'text-gray-600 bg-gray-100';
			default:
				return 'text-gray-600 bg-gray-100';
		}
	}
</script>

<svelte:head>
	<title>灵境研究 - 神秘事件智能分析系统</title>
	<meta name="description" content="专业的神秘事件研究平台，运用AI技术进行深度分析" />
</svelte:head>

<div class="min-h-screen">
	<!-- Hero Section -->
	<section class="relative bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 text-white">
		<div class="absolute inset-0 bg-black opacity-50"></div>
		<div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
			<div class="text-center">
				<h1 class="text-4xl md:text-6xl font-bold mb-6">
					<span class="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
						灵境研究系统
					</span>
				</h1>
				<p class="text-xl md:text-2xl mb-8 text-gray-300 max-w-3xl mx-auto">
					运用先进AI技术，深度分析神秘事件，揭示隐藏真相
				</p>
				<div class="flex flex-col sm:flex-row gap-4 justify-center">
					<button
						class="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-8 rounded-lg transition-colors duration-200 shadow-lg"
						onclick={() => navigateToFeature('/research')}
					>
						🔍 开始研究
					</button>
					<button
						class="bg-transparent border-2 border-white text-white hover:bg-white hover:text-gray-900 font-semibold py-3 px-8 rounded-lg transition-colors duration-200"
						onclick={() => navigateToFeature('/chat')}
					>
						💬 智能对话
					</button>
				</div>
			</div>
		</div>
	</section>

	<!-- Features Grid -->
	<section class="py-16 bg-white dark:bg-gray-900">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="text-center mb-12">
				<h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">核心功能</h2>
				<p class="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
					集成多种AI工具，提供全方位的神秘事件研究解决方案
				</p>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
				{#each features as feature (feature.title)}
						<div
						class="group relative bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden cursor-pointer transform hover:-translate-y-1"
						role="button"
						tabindex="0"
						onclick={() => navigateToFeature(feature.href)}
						onkeydown={(e) => {
							if (e.key === 'Enter' || e.key === ' ') {
								e.preventDefault();
								navigateToFeature(feature.href);
							}
						}}
					>
						<!-- Gradient Background -->
						<div class="absolute inset-0 bg-gradient-to-br {feature.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300"></div>
						
						<div class="relative p-6">
							<!-- Icon and Stats -->
							<div class="flex justify-between items-start mb-4">
								<div class="text-4xl">{feature.icon}</div>
								<div class="text-right">
									<div class="text-2xl font-bold text-gray-900 dark:text-white">{feature.stats.value}</div>
									<div class="text-sm text-gray-500 dark:text-gray-400">{feature.stats.label}</div>
								</div>
							</div>

							<!-- Content -->
							<h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
								{feature.title}
							</h3>
							<p class="text-gray-600 dark:text-gray-300 mb-4">
								{feature.description}
							</p>

							<!-- Action Button -->
							<div class="flex justify-end">
								<span class="text-indigo-600 dark:text-indigo-400 font-medium group-hover:text-indigo-700 dark:group-hover:text-indigo-300 transition-colors">
									立即使用 →
								</span>
							</div>
						</div>
					</div>
				{/each}
			</div>
		</div>
	</section>

	<!-- Recent Activities -->
	<section class="py-16 bg-gray-50 dark:bg-gray-800">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between items-center mb-8">
				<h2 class="text-3xl font-bold text-gray-900 dark:text-white">最近活动</h2>
				<a href="/reports" class="text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 font-medium">
					查看全部 →
				</a>
			</div>

			<div class="bg-white dark:bg-gray-900 rounded-lg shadow-lg overflow-hidden">
				<div class="divide-y divide-gray-200 dark:divide-gray-700">
					{#each recentActivities as activity (activity.id)}
							<div class="p-6 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
							<div class="flex items-center justify-between">
								<div class="flex items-center space-x-4">
									<div class="flex-shrink-0">
										{#if activity.type === 'research'}
											<div class="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
												<span class="text-blue-600 dark:text-blue-400">🔍</span>
											</div>
										{:else if activity.type === 'report'}
											<div class="w-10 h-10 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center">
												<span class="text-purple-600 dark:text-purple-400">📊</span>
											</div>
										{:else if activity.type === 'chat'}
											<div class="w-10 h-10 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
												<span class="text-green-600 dark:text-green-400">💬</span>
											</div>
										{:else}
											<div class="w-10 h-10 bg-orange-100 dark:bg-orange-900 rounded-full flex items-center justify-center">
												<span class="text-orange-600 dark:text-orange-400">📅</span>
											</div>
										{/if}
									</div>
									<div>
										<h3 class="text-sm font-medium text-gray-900 dark:text-white">
											{activity.title}
										</h3>
										<p class="text-sm text-gray-500 dark:text-gray-400">
											{activity.time}
										</p>
									</div>
								</div>
								<div>
									<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getStatusColor(activity.status)}">
										已完成
									</span>
								</div>
							</div>
						</div>
					{/each}
				</div>
			</div>
		</div>
	</section>

	<!-- Quick Stats -->
	<section class="py-16 bg-white dark:bg-gray-900">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="grid grid-cols-2 md:grid-cols-4 gap-8">
				<div class="text-center">
					<div class="text-3xl font-bold text-indigo-600 dark:text-indigo-400 mb-2">156+</div>
					<div class="text-sm text-gray-600 dark:text-gray-400">研究案例</div>
				</div>
				<div class="text-center">
					<div class="text-3xl font-bold text-green-600 dark:text-green-400 mb-2">2.3K+</div>
					<div class="text-sm text-gray-600 dark:text-gray-400">AI对话</div>
				</div>
				<div class="text-center">
					<div class="text-3xl font-bold text-purple-600 dark:text-purple-400 mb-2">89</div>
					<div class="text-sm text-gray-600 dark:text-gray-400">分析报告</div>
				</div>
				<div class="text-center">
					<div class="text-3xl font-bold text-orange-600 dark:text-orange-400 mb-2">98.5%</div>
					<div class="text-sm text-gray-600 dark:text-gray-400">准确率</div>
				</div>
			</div>
		</div>
	</section>
</div>

<style>
	/* Custom animations */
	@keyframes fadeInUp {
		from {
			opacity: 0;
			transform: translateY(30px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.animate-fade-in-up {
		animation: fadeInUp 0.6s ease-out;
	}
</style>
