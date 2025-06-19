<script lang="ts">
	import { onMount } from 'svelte';

	// Type definitions
	interface TimelineEvent {
		id: string;
		title: string;
		description: string;
		timestamp: string;
		category: string;
		status: 'completed' | 'running' | 'failed' | 'pending';
		duration?: number;
		metadata?: Record<string, string | number | boolean>;
		details?: Record<string, string | number | boolean>;
	}

	interface Category {
		id: string;
		label: string;
		color: string;
	}

	type ViewMode = 'timeline' | 'calendar';
	type TimeRange = 'all' | 'week' | 'month' | 'year';
	type SortOrder = 'asc' | 'desc';

	// Timeline state
	let events: TimelineEvent[] = $state([]);
	let filteredEvents: TimelineEvent[] = $state([]);
	let isLoading: boolean = $state(true);
	let selectedEvent: TimelineEvent | null = $state(null);
	let showEventModal: boolean = $state(false);
	let viewMode: ViewMode = $state('timeline');
	let timeRange: TimeRange = $state('all');
	let searchQuery: string = $state('');
	let selectedCategories: string[] = $state([]);
	let sortOrder: SortOrder = $state('desc');

	// Filter options
	const categories: Category[] = [
		{ id: 'research', label: '研究任务', color: 'bg-blue-500' },
		{ id: 'discovery', label: '重要发现', color: 'bg-green-500' },
		{ id: 'analysis', label: '分析结果', color: 'bg-purple-500' },
		{ id: 'report', label: '报告生成', color: 'bg-orange-500' },
		{ id: 'system', label: '系统事件', color: 'bg-gray-500' },
		{ id: 'mystery', label: '神秘事件', color: 'bg-red-500' }
	];

	const timeRanges: Record<TimeRange, string> = {
		all: '全部时间',
		week: '最近一周',
		month: '最近一月',
		year: '最近一年'
	};

	onMount(async () => {
		await loadEvents();
	});

	// Reactive filtering
	$effect(() => {
		filterEvents();
	});

	async function loadEvents(): Promise<void> {
		isLoading = true;
		try {
			const response = await fetch('/api/timeline/events');
			if (response.ok) {
				events = await response.json();
			} else {
				// Mock data for development
				events = generateMockEvents();
			}
		} catch (error) {
			console.error('Failed to load events:', error);
			// Use mock data as fallback
			events = generateMockEvents();
		} finally {
			isLoading = false;
		}
	}

	function generateMockEvents(): TimelineEvent[] {
		const now = new Date();
		return [
			{
				id: '1',
				title: '开始调查神秘失踪案',
				description: '接收到关于某地区连续失踪案件的报告，开始初步调查',
				category: 'mystery',
				timestamp: new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString(),
				duration: 120,
				status: 'completed',
				details: {
					location: '某市区',
					involvedPersons: 5,
					evidenceCount: 12,
					credibility: 0.85
				}
			},
			{
				id: '2',
				title: '发现关键线索',
				description: '在调查过程中发现了重要的物理证据和目击者证词',
				category: 'discovery',
				timestamp: new Date(now.getTime() - 5 * 24 * 60 * 60 * 1000).toISOString(),
				duration: 45,
				status: 'completed',
				details: {
					evidenceType: '物理证据',
					witnessCount: 3,
					credibility: 0.92
				}
			},
			{
				id: '3',
				title: '数据关联分析',
				description: '使用AI算法分析收集到的数据，寻找隐藏的关联模式',
				category: 'analysis',
				timestamp: new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000).toISOString(),
				duration: 180,
				status: 'completed',
				details: {
					algorithm: 'Deep Learning',
					accuracy: 0.89,
					patterns: 7
				}
			},
			{
				id: '4',
				title: '生成调查报告',
				description: '基于所有收集的证据和分析结果生成综合调查报告',
				category: 'report',
				timestamp: new Date(now.getTime() - 1 * 24 * 60 * 60 * 1000).toISOString(),
				duration: 60,
				status: 'completed',
				details: {
					wordCount: 5420,
					sections: 8,
					confidenceLevel: 0.87
				}
			},
			{
				id: '5',
				title: '持续监控异常活动',
			description: '设置自动监控系统，追踪相关区域的异常活动',
			category: 'system',
			timestamp: new Date().toISOString(),
			duration: undefined,
			status: 'running',
				details: {
					monitoringPoints: 15,
					alertThreshold: 0.7,
					updateFrequency: '每小时'
				}
			}
		];
	}

	function filterEvents(): void {
		let filtered = [...events];

		// Filter by search query
		if (searchQuery.trim()) {
			const query = searchQuery.toLowerCase();
			filtered = filtered.filter(event => 
				event.title.toLowerCase().includes(query) ||
				event.description.toLowerCase().includes(query)
			);
		}

		// Filter by categories
		if (selectedCategories.length > 0) {
			filtered = filtered.filter(event => 
				selectedCategories.includes(event.category)
			);
		}

		// Filter by time range
		if (timeRange !== 'all') {
			const now = new Date();
			let cutoffDate: Date;
			
			switch (timeRange) {
				case 'week':
					cutoffDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
					break;
				case 'month':
					cutoffDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
					break;
				case 'year':
					cutoffDate = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000);
					break;
			}
			
			filtered = filtered.filter(event => 
				new Date(event.timestamp) >= cutoffDate!
			);
		}

		// Sort by timestamp
		filtered.sort((a, b) => {
			const dateA = new Date(a.timestamp);
			const dateB = new Date(b.timestamp);
			return sortOrder === 'desc' ? dateB.getTime() - dateA.getTime() : dateA.getTime() - dateB.getTime();
		});

		filteredEvents = filtered;
	}

	function toggleCategory(categoryId: string): void {
		if (selectedCategories.includes(categoryId)) {
			selectedCategories = selectedCategories.filter(id => id !== categoryId);
		} else {
			selectedCategories = [...selectedCategories, categoryId];
		}
	}

	function showEventDetails(event: TimelineEvent): void {
		selectedEvent = event;
		showEventModal = true;
	}

	function formatDate(dateString: string): string {
		return new Date(dateString).toLocaleString('zh-CN');
	}

	function formatDuration(minutes: number | null | undefined): string {
		if (!minutes) return '进行中';
		if (minutes < 60) return `${minutes}分钟`;
		const hours = Math.floor(minutes / 60);
		const remainingMinutes = minutes % 60;
		return remainingMinutes > 0 ? `${hours}小时${remainingMinutes}分钟` : `${hours}小时`;
	}

	function getCategoryInfo(categoryId: string): Category {
		return categories.find(cat => cat.id === categoryId) || { id: 'unknown', label: '未知', color: 'bg-gray-500' };
	}

	function getStatusColor(status: string): string {
		switch (status) {
			case 'completed': return 'text-green-600 dark:text-green-400';
			case 'running': return 'text-blue-600 dark:text-blue-400';
			case 'failed': return 'text-red-600 dark:text-red-400';
			case 'pending': return 'text-yellow-600 dark:text-yellow-400';
			default: return 'text-gray-600 dark:text-gray-400';
		}
	}

	function getStatusText(status: string): string {
		switch (status) {
			case 'completed': return '已完成';
			case 'running': return '进行中';
			case 'failed': return '失败';
			case 'pending': return '等待中';
			default: return '未知';
		}
	}

	async function exportTimeline(): Promise<void> {
		try {
			const response = await fetch('/api/timeline/export', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					events: filteredEvents,
					filters: {
						searchQuery,
						selectedCategories,
						timeRange
					}
				})
			});

			if (response.ok) {
				const blob = await response.blob();
				const url = window.URL.createObjectURL(blob);
				const a = document.createElement('a');
				a.href = url;
				a.download = `timeline-${new Date().toISOString().split('T')[0]}.pdf`;
				document.body.appendChild(a);
				a.click();
				window.URL.revokeObjectURL(url);
				document.body.removeChild(a);
			}
		} catch (error) {
			console.error('Failed to export timeline:', error);
			alert('导出时间线失败');
		}
	}
</script>

<svelte:head>
	<title>时间线 - 灵境研究</title>
	<meta name="description" content="查看研究事件的时间线和关联分析" />
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	<!-- Header -->
	<div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
			<div class="flex items-center justify-between">
				<div>
					<h1 class="text-3xl font-bold text-gray-900 dark:text-white">事件时间线</h1>
					<p class="mt-2 text-gray-600 dark:text-gray-400">
						追踪和分析研究事件的时间序列
					</p>
				</div>
				<div class="flex items-center space-x-4">
					<button
						onclick={exportTimeline}
						class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2"
					>
						<span>📥</span>
						<span>导出时间线</span>
					</button>
					<button
						onclick={() => viewMode = viewMode === 'timeline' ? 'calendar' : 'timeline'}
						class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center space-x-2"
					>
						<span>{viewMode === 'timeline' ? '📅' : '📊'}</span>
						<span>{viewMode === 'timeline' ? '日历视图' : '时间线视图'}</span>
					</button>
				</div>
			</div>
		</div>
	</div>

	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		{#if isLoading}
			<div class="flex items-center justify-center py-12">
				<div class="text-center">
					<div class="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
					<p class="text-gray-600 dark:text-gray-400">加载时间线数据...</p>
				</div>
			</div>
		{:else}
			<!-- Filters -->
			<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
				<div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
					<!-- Search -->
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							搜索事件
						</label>
						<input
							type="text"
							bind:value={searchQuery}
							placeholder="搜索标题或描述..."
							class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
						/>
					</div>

					<!-- Time Range -->
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							时间范围
						</label>
						<select
							bind:value={timeRange}
							class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
						>
							{#each Object.entries(timeRanges) as [value, label] (value)}
								<option value={value}>{label}</option>
							{/each}
						</select>
					</div>

					<!-- Sort Order -->
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							排序方式
						</label>
						<select
							bind:value={sortOrder}
							class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
						>
							<option value="desc">最新优先</option>
							<option value="asc">最早优先</option>
						</select>
					</div>

					<!-- Results Count -->
					<div class="flex items-end">
						<div class="text-sm text-gray-600 dark:text-gray-400">
							显示 {filteredEvents.length} / {events.length} 个事件
						</div>
					</div>
				</div>

				<!-- Category Filters -->
				<div class="mt-6">
					<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
						事件类型
					</label>
					<div class="flex flex-wrap gap-2">
						{#each categories as category (category.id)}
							<button
								onclick={() => toggleCategory(category.id)}
								class="px-3 py-1 rounded-full text-sm font-medium transition-all {selectedCategories.includes(category.id) ? `${category.color} text-white` : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'}"
							>
								{category.label}
							</button>
						{/each}
					</div>
				</div>
			</div>

			<!-- Timeline View -->
			{#if viewMode === 'timeline'}
				<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
					{#if filteredEvents.length === 0}
						<div class="text-center py-12">
							<div class="text-6xl mb-4">📅</div>
							<h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">暂无事件</h3>
							<p class="text-gray-600 dark:text-gray-400">当前筛选条件下没有找到相关事件</p>
						</div>
					{:else}
						<div class="relative">
							<!-- Timeline Line -->
							<div class="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-300 dark:bg-gray-600"></div>
							
							<!-- Events -->
							<div class="space-y-8">
								{#each filteredEvents as event (event.id)}
								{@const categoryInfo = getCategoryInfo(event.category)}
									<div class="relative flex items-start space-x-6">
										<!-- Timeline Dot -->
										<div class="flex-shrink-0 relative">
											<div class="w-4 h-4 {categoryInfo.color} rounded-full border-4 border-white dark:border-gray-800 relative z-10"></div>
										</div>
										
										<!-- Event Content -->
										<div class="flex-1 min-w-0">
											<div 
											class="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer" 
											role="button"
											tabindex="0"
											onclick={() => showEventDetails(event)}
											onkeydown={(e) => {
												if (e.key === 'Enter' || e.key === ' ') {
													e.preventDefault();
													showEventDetails(event);
												}
											}}
										>
												<div class="flex items-start justify-between mb-3">
													<div class="flex-1">
														<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">
															{event.title}
														</h3>
														<p class="text-sm text-gray-600 dark:text-gray-400">
															{formatDate(event.timestamp)}
														</p>
													</div>
													<div class="flex items-center space-x-2">
														<span class="px-2 py-1 {categoryInfo.color} text-white rounded-full text-xs font-medium">
															{categoryInfo.label}
														</span>
														<span class="px-2 py-1 rounded-full text-xs font-medium {getStatusColor(event.status)} bg-gray-100 dark:bg-gray-600">
															{getStatusText(event.status)}
														</span>
													</div>
												</div>
												
												<p class="text-gray-700 dark:text-gray-300 mb-3">
													{event.description}
												</p>
												
												<div class="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
													<span>持续时间: {formatDuration(event.duration)}</span>
													<span class="text-indigo-600 dark:text-indigo-400 hover:underline">
														查看详情 →
													</span>
												</div>
											</div>
										</div>
									</div>
								{/each}
							</div>
						</div>
					{/if}
				</div>
			{:else}
				<!-- Calendar View (Placeholder) -->
				<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
					<div class="text-center py-12">
						<div class="text-6xl mb-4">📅</div>
						<h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">日历视图</h3>
						<p class="text-gray-600 dark:text-gray-400">日历视图功能正在开发中...</p>
					</div>
				</div>
			{/if}
		{/if}
	</div>
</div>

<!-- Event Details Modal -->
{#if showEventModal && selectedEvent}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
		<div class="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
			<div class="p-6">
				<div class="flex items-start justify-between mb-6">
					<div class="flex-1">
						<h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
							{selectedEvent.title}
						</h2>
						<p class="text-gray-600 dark:text-gray-400">
							{formatDate(selectedEvent.timestamp)}
						</p>
					</div>
					<button
						onclick={() => showEventModal = false}
						class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
					>
						✕
					</button>
				</div>

				<div class="space-y-6">
					<!-- Basic Info -->
					<div>
						<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">基本信息</h3>
						<div class="grid grid-cols-2 gap-4">
							<div>
								<span class="text-sm text-gray-600 dark:text-gray-400">类型:</span>
								<span class="ml-2 px-2 py-1 {getCategoryInfo(selectedEvent.category).color} text-white rounded-full text-xs">
									{getCategoryInfo(selectedEvent.category).label}
								</span>
							</div>
							<div>
								<span class="text-sm text-gray-600 dark:text-gray-400">状态:</span>
								<span class="ml-2 {getStatusColor(selectedEvent.status)} font-medium">
									{getStatusText(selectedEvent.status)}
								</span>
							</div>
							<div class="col-span-2">
								<span class="text-sm text-gray-600 dark:text-gray-400">持续时间:</span>
								<span class="ml-2 text-gray-900 dark:text-white">
									{formatDuration(selectedEvent.duration)}
								</span>
							</div>
						</div>
					</div>

					<!-- Description -->
					<div>
						<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">详细描述</h3>
						<p class="text-gray-700 dark:text-gray-300 leading-relaxed">
							{selectedEvent.description}
						</p>
					</div>

					<!-- Details -->
					{#if selectedEvent.details}
						<div>
							<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">详细数据</h3>
							<div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
								<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
									{#each Object.entries(selectedEvent.details) as [key, value] (key)}
										<div class="flex justify-between">
											<span class="text-sm text-gray-600 dark:text-gray-400 capitalize">
												{key.replace(/([A-Z])/g, ' $1').toLowerCase()}:
											</span>
											<span class="text-sm font-medium text-gray-900 dark:text-white">
												{typeof value === 'number' && value < 1 && value > 0 ? (value * 100).toFixed(1) + '%' : value}
											</span>
										</div>
									{/each}
								</div>
							</div>
						</div>
					{/if}
				</div>

				<div class="flex justify-end mt-8">
					<button
						onclick={() => showEventModal = false}
						class="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
					>
						关闭
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}

<style>
	/* Custom scrollbar for modal */
	.overflow-y-auto::-webkit-scrollbar {
		width: 6px;
	}
	
	.overflow-y-auto::-webkit-scrollbar-track {
		background: #f1f1f1;
		border-radius: 3px;
	}
	
	.overflow-y-auto::-webkit-scrollbar-thumb {
		background: #c1c1c1;
		border-radius: 3px;
	}
	
	.overflow-y-auto::-webkit-scrollbar-thumb:hover {
		background: #a8a8a8;
	}
	
	@media (prefers-color-scheme: dark) {
		.overflow-y-auto::-webkit-scrollbar-track {
			background: #374151;
		}
		
		.overflow-y-auto::-webkit-scrollbar-thumb {
			background: #6b7280;
		}
		
		.overflow-y-auto::-webkit-scrollbar-thumb:hover {
			background: #9ca3af;
		}
	}
</style>