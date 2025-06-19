<script lang="ts">
	import { onMount } from 'svelte';

	// Type definitions
	interface Node {
		id: string;
		label: string;
		type: string;
		properties?: Record<string, string | number | boolean | number[] | undefined>;
		x?: number;
		y?: number;
	}

	interface Link {
		id: string;
		source: string;
		target: string;
		type: string;
		label?: string;
	}

	interface GraphData {
		nodes: Node[];
		links: Link[];
	}

	// Graph state
	let graphData = $state<GraphData>({ nodes: [], links: [] });
	let isLoading = $state(true);
	let selectedNode = $state<Node | null>(null);
	let showNodeModal = $state(false);
	let searchQuery = $state('');
	let filterType = $state('all');
	let layoutType = $state('force'); // 'force', 'circular', 'hierarchical'
	let showLegend = $state(true);
	let graphContainer = $state<HTMLDivElement | null>(null);

	// Graph configuration
	let graphConfig = $state({
		width: 800,
		height: 600,
		nodeSize: 8,
		linkDistance: 100,
		charge: -300,
		showLabels: true,
		animationSpeed: 1000
	});

	// Node types and colors
	const nodeTypes = {
		event: { label: '事件', color: '#3b82f6', icon: '🔍' },
		person: { label: '人物', color: '#10b981', icon: '👤' },
		location: { label: '地点', color: '#f59e0b', icon: '📍' },
		organization: { label: '组织', color: '#8b5cf6', icon: '🏢' },
		evidence: { label: '证据', color: '#ef4444', icon: '📄' },
		concept: { label: '概念', color: '#6b7280', icon: '💡' },
		mystery: { label: '神秘事件', color: '#dc2626', icon: '❓' }
	};

	// Link types
	const linkTypes = {
		related: { label: '相关', color: '#9ca3af', width: 2 },
		caused: { label: '导致', color: '#ef4444', width: 3 },
		located: { label: '位于', color: '#f59e0b', width: 2 },
		involved: { label: '涉及', color: '#10b981', width: 2 },
		supports: { label: '支持', color: '#3b82f6', width: 2 },
		contradicts: { label: '矛盾', color: '#dc2626', width: 3 }
	};

	onMount(async () => {
		await loadGraphData();
		initializeGraph();
	});

	async function loadGraphData() {
		isLoading = true;
		try {
			const response = await fetch('/api/graph/data');
			if (response.ok) {
				graphData = await response.json();
			} else {
				// Mock data for development
				graphData = generateMockGraphData();
			}
		} catch (error) {
			console.error('Failed to load graph data:', error);
			graphData = generateMockGraphData();
		} finally {
			isLoading = false;
		}
	}

	function generateMockGraphData() {
		return {
			nodes: [
				{ id: '1', label: 'UFO目击事件', type: 'mystery', properties: { date: '2024-01-15', location: '某市', credibility: 0.75 } },
				{ id: '2', label: '张三', type: 'person', properties: { role: '目击者', age: 35, occupation: '工程师' } },
				{ id: '3', label: '李四', type: 'person', properties: { role: '目击者', age: 42, occupation: '教师' } },
				{ id: '4', label: '某市公园', type: 'location', properties: { coordinates: [116.4074, 39.9042], area: '城市公园' } },
				{ id: '5', label: '照片证据', type: 'evidence', properties: { type: '图像', quality: 'high', verified: true } },
				{ id: '6', label: '雷达数据', type: 'evidence', properties: { type: '技术数据', source: '空管局', verified: true } },
				{ id: '7', label: '不明飞行物', type: 'concept', properties: { category: '现象', description: '未识别空中物体' } },
				{ id: '8', label: '气象异常', type: 'event', properties: { date: '2024-01-15', type: '大气现象' } },
				{ id: '9', label: '当地媒体', type: 'organization', properties: { type: '新闻机构', credibility: 0.8 } },
				{ id: '10', label: '研究机构', type: 'organization', properties: { type: '科研单位', specialization: 'UFO研究' } }
			],
			links: [
				{ id: 'l1', source: '1', target: '2', type: 'involved' },
				{ id: 'l2', source: '1', target: '3', type: 'involved' },
				{ id: 'l3', source: '1', target: '4', type: 'located' },
				{ id: 'l4', source: '1', target: '5', type: 'supports' },
				{ id: 'l5', source: '1', target: '6', type: 'supports' },
				{ id: 'l6', source: '1', target: '7', type: 'related' },
				{ id: 'l7', source: '1', target: '8', type: 'related' },
				{ id: 'l8', source: '2', target: '3', type: 'related' },
				{ id: 'l9', source: '5', target: '2', type: 'related' },
				{ id: 'l10', source: '9', target: '1', type: 'related' },
				{ id: 'l11', source: '10', target: '1', type: 'related' }
			]
		};
	}

	function initializeGraph() {
		// This would initialize D3.js or other graph visualization library
		// For now, we'll use a simplified representation
		console.log('Initializing graph with data:', graphData);
	}

	function filterNodes() {
		let filtered = graphData.nodes;
		
		if (searchQuery.trim()) {
			const query = searchQuery.toLowerCase();
			filtered = filtered.filter(node => 
				node.label.toLowerCase().includes(query) ||
				node.type.toLowerCase().includes(query)
			);
		}
		
		if (filterType !== 'all') {
			filtered = filtered.filter(node => node.type === filterType);
		}
		
		return filtered;
	}

	function getNodeTypeInfo(type: string): { label: string; color: string; icon: string } {
		return nodeTypes[type as keyof typeof nodeTypes] || { label: '未知', color: '#6b7280', icon: '❓' };
	}

	function getLinkTypeInfo(type: string) {
		return linkTypes[type as keyof typeof linkTypes] || { label: '未知', color: '#9ca3af', width: 1 };
	}

	function showNodeDetails(node: Node) {
		selectedNode = node;
		showNodeModal = true;
	}

	function updateGraphLayout() {
		// Update graph layout based on layoutType
		console.log('Updating layout to:', layoutType);
		// This would trigger D3.js layout update
	}

	function exportGraph() {
		// Export graph data
		const dataStr = JSON.stringify(graphData, null, 2);
		const dataBlob = new Blob([dataStr], { type: 'application/json' });
		const url = URL.createObjectURL(dataBlob);
		const link = document.createElement('a');
		link.href = url;
		link.download = `graph-data-${new Date().toISOString().split('T')[0]}.json`;
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
		URL.revokeObjectURL(url);
	}

	async function saveGraphLayout() {
		try {
			const response = await fetch('/api/graph/layout', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					layout: layoutType,
					config: graphConfig
				})
			});
			
			if (response.ok) {
				alert('图谱布局已保存');
			}
		} catch (error) {
			console.error('Failed to save layout:', error);
			alert('保存布局失败');
		}
	}

	// Reactive filtering
	$effect(() => {
		filterNodes();
	});
</script>

<svelte:head>
	<title>关系图谱 - 灵境研究</title>
	<meta name="description" content="可视化展示研究数据的关联关系和网络结构" />
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	<!-- Header -->
	<div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
			<div class="flex items-center justify-between">
				<div>
					<h1 class="text-3xl font-bold text-gray-900 dark:text-white">关系图谱</h1>
					<p class="mt-2 text-gray-600 dark:text-gray-400">
						可视化展示研究数据的关联关系和网络结构
					</p>
				</div>
				<div class="flex items-center space-x-4">
					<button
						onclick={exportGraph}
						class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2"
					>
						<span>📥</span>
						<span>导出数据</span>
					</button>
					<button
						onclick={saveGraphLayout}
						class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center space-x-2"
					>
						<span>💾</span>
						<span>保存布局</span>
					</button>
					<button
						onclick={() => showLegend = !showLegend}
						class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center space-x-2"
					>
						<span>📖</span>
						<span>{showLegend ? '隐藏' : '显示'}图例</span>
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
					<p class="text-gray-600 dark:text-gray-400">加载图谱数据...</p>
				</div>
			</div>
		{:else}
			<div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
				<!-- Sidebar Controls -->
				<div class="lg:col-span-1">
					<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 space-y-6">
						<!-- Search -->
						<div>
							<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
								搜索节点
							</label>
							<input
								type="text"
								bind:value={searchQuery}
								placeholder="搜索节点名称或类型..."
								class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
							/>
						</div>

						<!-- Filter by Type -->
						<div>
							<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
								节点类型
							</label>
							<select
								bind:value={filterType}
								class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
							>
								<option value="all">全部类型</option>
								{#each Object.entries(nodeTypes) as [type, info] (type)}
								<option value={type}>{info.icon} {info.label}</option>
							{/each}
							</select>
						</div>

						<!-- Layout Type -->
						<div>
							<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
								布局类型
							</label>
							<select
								bind:value={layoutType}
								onchange={updateGraphLayout}
								class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
							>
								<option value="force">力导向布局</option>
								<option value="circular">环形布局</option>
								<option value="hierarchical">层次布局</option>
							</select>
						</div>

						<!-- Graph Configuration -->
						<div>
							<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">图谱配置</h3>
							<div class="space-y-4">
								<div>
									<label class="block text-sm text-gray-600 dark:text-gray-400 mb-1">
										节点大小: {graphConfig.nodeSize}
									</label>
									<input
										type="range"
										min="4"
										max="20"
										bind:value={graphConfig.nodeSize}
										class="w-full"
									/>
								</div>
								<div>
									<label class="block text-sm text-gray-600 dark:text-gray-400 mb-1">
										连接距离: {graphConfig.linkDistance}
									</label>
									<input
										type="range"
										min="50"
										max="200"
										bind:value={graphConfig.linkDistance}
										class="w-full"
									/>
								</div>
								<div class="flex items-center">
									<input
										type="checkbox"
										bind:checked={graphConfig.showLabels}
										id="showLabels"
										class="mr-2"
									/>
									<label for="showLabels" class="text-sm text-gray-600 dark:text-gray-400">
										显示标签
									</label>
								</div>
							</div>
						</div>

						<!-- Statistics -->
						<div>
							<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">图谱统计</h3>
							<div class="space-y-2 text-sm">
								<div class="flex justify-between">
									<span class="text-gray-600 dark:text-gray-400">节点数:</span>
									<span class="font-medium">{graphData.nodes.length}</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-600 dark:text-gray-400">连接数:</span>
									<span class="font-medium">{graphData.links.length}</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-600 dark:text-gray-400">显示节点:</span>
									<span class="font-medium">{filterNodes().length}</span>
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Main Graph Area -->
				<div class="lg:col-span-3">
					<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
						<!-- Graph Container -->
						<div 
							bind:this={graphContainer}
							class="w-full h-96 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg flex items-center justify-center bg-gray-50 dark:bg-gray-700"
						>
							{#if graphData.nodes.length === 0}
								<div class="text-center">
									<div class="text-6xl mb-4">🕸️</div>
									<h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">暂无图谱数据</h3>
									<p class="text-gray-600 dark:text-gray-400">请先进行研究以生成关系图谱</p>
								</div>
							{:else}
								<!-- Simplified Graph Representation -->
								<div class="w-full h-full relative overflow-hidden">
									<svg class="w-full h-full">
										<!-- Links -->
							{#each graphData.links as link, i (link.id || `${link.source}-${link.target}`)}
							{@const linkInfo = getLinkTypeInfo(link.type)}
							<line
									x1={100 + (i % 5) * 120}
									y1={100 + Math.floor(i / 5) * 80}
									x2={200 + (i % 5) * 120}
									y2={150 + Math.floor(i / 5) * 80}
									stroke={linkInfo.color}
									stroke-width={linkInfo.width}
									opacity="0.6"
								/>
							{/each}
							
							<!-- Nodes -->
							{#each filterNodes() as node, i (node.id)}
							{@const nodeInfo = getNodeTypeInfo(node.type)}
							<g transform="translate({100 + (i % 5) * 120}, {100 + Math.floor(i / 5) * 80})">
												<circle
													r={graphConfig.nodeSize}
													fill={nodeInfo.color}
													stroke="white"
													stroke-width="2"
													class="cursor-pointer hover:opacity-80 transition-opacity"
													onclick={() => showNodeDetails(node)}
												/>
												{#if graphConfig.showLabels}
													<text
														x="0"
														y={graphConfig.nodeSize + 15}
														text-anchor="middle"
														class="text-xs fill-gray-700 dark:fill-gray-300"
													>
														{node.label.length > 10 ? node.label.substring(0, 10) + '...' : node.label}
													</text>
												{/if}
											</g>
										{/each}
									</svg>
									
									<!-- Graph Info Overlay -->
									<div class="absolute top-4 left-4 bg-white dark:bg-gray-800 rounded-lg p-3 shadow-lg border border-gray-200 dark:border-gray-600">
										<p class="text-sm text-gray-600 dark:text-gray-400">
											💡 这是简化的图谱预览，完整的交互式图谱正在开发中
										</p>
									</div>
								</div>
							{/if}
						</div>

						<!-- Node List -->
						<div class="mt-6">
							<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">节点列表</h3>
							<div class="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-64 overflow-y-auto">
								{#each filterNodes() as node (node.id)}
								{@const nodeInfo = getNodeTypeInfo(node.type)}
								<div 
										class="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer transition-colors"
										onclick={() => showNodeDetails(node)}
									>
										<div 
											class="w-4 h-4 rounded-full flex-shrink-0"
											style="background-color: {nodeInfo.color}"
										></div>
										<div class="flex-1 min-w-0">
											<p class="text-sm font-medium text-gray-900 dark:text-white truncate">
												{nodeInfo.icon} {node.label}
											</p>
											<p class="text-xs text-gray-500 dark:text-gray-400">
												{nodeInfo.label}
											</p>
										</div>
									</div>
								{/each}
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Legend -->
			{#if showLegend}
				<div class="mt-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
					<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">图例说明</h3>
					<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
						<!-- Node Types -->
						<div>
							<h4 class="text-md font-medium text-gray-900 dark:text-white mb-3">节点类型</h4>
							<div class="space-y-2">
								{#each Object.entries(nodeTypes) as [type, info] (type)}
								<div class="flex items-center space-x-3">
										<div 
											class="w-4 h-4 rounded-full"
											style="background-color: {info.color}"
										></div>
										<span class="text-sm text-gray-700 dark:text-gray-300">
											{info.icon} {info.label}
										</span>
									</div>
								{/each}
							</div>
						</div>

						<!-- Link Types -->
						<div>
							<h4 class="text-md font-medium text-gray-900 dark:text-white mb-3">连接类型</h4>
							<div class="space-y-2">
								{#each Object.entries(linkTypes) as [type, info] (type)}
								<div class="flex items-center space-x-3">
										<div class="flex items-center">
											<div 
												class="w-6 h-0.5"
												style="background-color: {info.color}; height: {info.width}px"
											></div>
										</div>
										<span class="text-sm text-gray-700 dark:text-gray-300">
											{info.label}
										</span>
									</div>
								{/each}
							</div>
						</div>
					</div>
				</div>
			{/if}
		{/if}
	</div>
</div>

<!-- Node Details Modal -->
{#if showNodeModal && selectedNode}
{@const nodeInfo = getNodeTypeInfo(selectedNode.type)}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
		<div class="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
			<div class="p-6">
				
				<div class="flex items-start justify-between mb-6">
				<div class="flex items-center space-x-3">
					<div 
							class="w-6 h-6 rounded-full flex-shrink-0"
							style="background-color: {nodeInfo.color}"
						></div>
						<div>
							<h2 class="text-2xl font-bold text-gray-900 dark:text-white">
								{nodeInfo.icon} {selectedNode.label}
							</h2>
							<p class="text-gray-600 dark:text-gray-400">
								{nodeInfo.label}
							</p>
						</div>
					</div>
					<button
						onclick={() => showNodeModal = false}
						class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
					>
						✕
					</button>
				</div>

				{#if selectedNode.properties}
					<div class="space-y-4">
						<h3 class="text-lg font-semibold text-gray-900 dark:text-white">属性信息</h3>
						<div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
							<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
								{#each Object.entries(selectedNode.properties) as [key, value] (key)}
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

				<!-- Related Connections -->
				<div class="mt-6">
					<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">相关连接</h3>
					<div class="space-y-2">
						{#each graphData.links.filter(link => selectedNode && (link.source === selectedNode.id || link.target === selectedNode.id)) as link (link.id || `${link.source}-${link.target}`)}
					{@const linkInfo = getLinkTypeInfo(link.type)}
					{@const otherNodeId = selectedNode && link.source === selectedNode.id ? link.target : link.source}
							{@const otherNode = graphData.nodes.find(n => n.id === otherNodeId)}
							{#if otherNode}
								<div class="flex items-center space-x-3 p-2 bg-gray-50 dark:bg-gray-700 rounded">
									<div 
										class="w-3 h-3 rounded-full"
										style="background-color: {getNodeTypeInfo(otherNode.type).color}"
									></div>
									<span class="text-sm text-gray-700 dark:text-gray-300">
										{otherNode.label}
									</span>
									<span class="text-xs text-gray-500 dark:text-gray-400">
										({linkInfo.label})
									</span>
								</div>
							{/if}
						{/each}
					</div>
				</div>

				<div class="flex justify-end mt-8">
					<button
						onclick={() => showNodeModal = false}
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
	/* Custom scrollbar */
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

	/* SVG text styling */
	.fill-gray-700 {
		fill: #374151;
	}
	
	.dark .fill-gray-300 {
		fill: #d1d5db;
	}
</style>