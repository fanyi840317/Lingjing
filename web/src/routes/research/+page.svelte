<script lang="ts">
	import { onMount } from 'svelte';

	// Research result interface
	interface ResearchResult {
		id?: string;
		title: string;
		summary: string;
		credibility: number;
		source?: string;
	}

	// Research log interface
	interface ResearchLog {
		id?: string;
		timestamp: string;
		level: 'info' | 'warning' | 'error';
		message: string;
	}

	// Research task interface
	interface ResearchTask {
		id: string;
		title: string;
		description: string;
		keywords: string[];
		maxDepth: number;
		enableAcademicSearch: boolean;
		credibilityThreshold: number;
		enableGraphStorage: boolean;
		priority: 'low' | 'medium' | 'high' | 'urgent';
		tags: string[];
		status: 'pending' | 'running' | 'completed' | 'failed' | 'paused';
		createdAt: string;
		updatedAt: string;
		startedAt?: string;
		completedAt?: string;
		duration?: number;
		progress?: number;
		currentStep?: string;
		results?: ResearchResult[];
		logs?: ResearchLog[];
	}

	// Research state
	let researchTasks = $state<ResearchTask[]>([]);
	let activeTask = $state<ResearchTask | null>(null);
	let isCreating = $state(false);
	let isLoading = $state(false);
	let searchQuery = $state('');
	let filterStatus = $state('all');

	// New task form interface
	interface NewTaskForm {
		title: string;
		description: string;
		keywords: string[];
		maxDepth: number;
		enableAcademicSearch: boolean;
		credibilityThreshold: number;
		enableGraphStorage: boolean;
		priority: 'low' | 'medium' | 'high' | 'urgent';
		tags: string[];
	}

	// New task form
	let newTask = $state<NewTaskForm>({
		title: '',
		description: '',
		keywords: [],
		maxDepth: 3,
		enableAcademicSearch: true,
		credibilityThreshold: 0.7,
		enableGraphStorage: true,
		priority: 'medium',
		tags: []
	});

	let keywordInput = $state('');
	let tagInput = $state('');

	// Task statistics interface
	interface TaskStats {
		total: number;
		running: number;
		completed: number;
		failed: number;
		pending: number;
	}

	// Task statistics
	let stats = $state<TaskStats>({
		total: 0,
		running: 0,
		completed: 0,
		failed: 0,
		pending: 0
	});

	const statusColors = {
		pending: 'bg-yellow-100 text-yellow-800',
		running: 'bg-blue-100 text-blue-800',
		completed: 'bg-green-100 text-green-800',
		failed: 'bg-red-100 text-red-800',
		paused: 'bg-gray-100 text-gray-800'
	};

	const priorityColors = {
		low: 'bg-gray-100 text-gray-800',
		medium: 'bg-blue-100 text-blue-800',
		high: 'bg-orange-100 text-orange-800',
		urgent: 'bg-red-100 text-red-800'
	};

	onMount(async () => {
		await loadResearchTasks();
		await loadStats();
		// Set up real-time updates
		setInterval(loadStats, 30000); // Update stats every 30 seconds
	});

	async function loadResearchTasks() {
		isLoading = true;
		try {
			const response = await fetch('/api/research/tasks');
			if (response.ok) {
				researchTasks = await response.json();
			}
		} catch (error) {
			console.error('Failed to load research tasks:', error);
		} finally {
			isLoading = false;
		}
	}

	async function loadStats() {
		try {
			const response = await fetch('/api/research/stats');
			if (response.ok) {
				stats = await response.json();
			}
		} catch (error) {
			console.error('Failed to load stats:', error);
		}
	}

	async function createResearchTask(event: Event) {
		event.preventDefault();
		if (!newTask.title.trim()) {
			alert('请输入研究标题');
			return;
		}

		isCreating = true;
		try {
			const response = await fetch('/api/research/tasks', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(newTask)
			});

			if (response.ok) {
				const task = await response.json();
				researchTasks = [task, ...researchTasks];
				resetNewTaskForm();
				await loadStats();
			} else {
				throw new Error('创建任务失败');
			}
		} catch (error) {
			console.error('Failed to create task:', error);
			alert('创建任务失败，请重试');
		} finally {
			isCreating = false;
		}
	}

	async function deleteTask(taskId: string) {
		if (!confirm('确定要删除这个研究任务吗？')) return;

		try {
			const response = await fetch(`/api/research/tasks/${taskId}`, {
				method: 'DELETE'
			});

			if (response.ok) {
				researchTasks = researchTasks.filter(task => task.id !== taskId);
				if (activeTask?.id === taskId) {
					activeTask = null;
				}
				await loadStats();
			}
		} catch (error) {
			console.error('Failed to delete task:', error);
			alert('删除任务失败');
		}
	}

	async function pauseTask(taskId: string) {
		try {
			const response = await fetch(`/api/research/tasks/${taskId}/pause`, {
				method: 'POST'
			});

			if (response.ok) {
				await loadResearchTasks();
				await loadStats();
			}
		} catch (error) {
			console.error('Failed to pause task:', error);
		}
	}

	async function resumeTask(taskId: string) {
		try {
			const response = await fetch(`/api/research/tasks/${taskId}/resume`, {
				method: 'POST'
			});

			if (response.ok) {
				await loadResearchTasks();
				await loadStats();
			}
		} catch (error) {
			console.error('Failed to resume task:', error);
		}
	}

	function resetNewTaskForm() {
		newTask = {
			title: '',
			description: '',
			keywords: [],
			maxDepth: 3,
			enableAcademicSearch: true,
			credibilityThreshold: 0.7,
			enableGraphStorage: true,
			priority: 'medium',
			tags: []
		};
		keywordInput = '';
		tagInput = '';
	}

	function addKeyword() {
		if (keywordInput.trim() && !newTask.keywords.includes(keywordInput.trim())) {
			newTask.keywords = [...newTask.keywords, keywordInput.trim()];
			keywordInput = '';
		}
	}

	function removeKeyword(keyword: string) {
		newTask.keywords = newTask.keywords.filter(k => k !== keyword);
	}

	function addTag() {
		if (tagInput.trim() && !newTask.tags.includes(tagInput.trim())) {
			newTask.tags = [...newTask.tags, tagInput.trim()];
			tagInput = '';
		}
	}

	function removeTag(tag: string) {
		newTask.tags = newTask.tags.filter(t => t !== tag);
	}

	function handleKeywordKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter') {
			event.preventDefault();
			addKeyword();
		}
	}

	function handleTagKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter') {
			event.preventDefault();
			addTag();
		}
	}

	function formatDate(dateString: string) {
		return new Date(dateString).toLocaleString('zh-CN');
	}

	function formatDuration(seconds: number) {
		if (seconds < 60) return `${seconds}秒`;
		if (seconds < 3600) return `${Math.floor(seconds / 60)}分钟`;
		return `${Math.floor(seconds / 3600)}小时${Math.floor((seconds % 3600) / 60)}分钟`;
	}

	// Computed properties
	const filteredTasks = $derived(researchTasks.filter(task => {
		const matchesSearch = !searchQuery || 
			task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
			task.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
			task.keywords.some(k => k.toLowerCase().includes(searchQuery.toLowerCase()));
		
		const matchesStatus = filterStatus === 'all' || task.status === filterStatus;
		
		return matchesSearch && matchesStatus;
	}));
</script>

<svelte:head>
	<title>研究管理 - 灵境研究</title>
	<meta name="description" content="管理和监控神秘事件研究任务" />
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	<!-- Header -->
	<div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
			<div class="flex items-center justify-between">
				<div>
					<h1 class="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
						🔍 研究管理
					</h1>
					<p class="mt-2 text-gray-600 dark:text-gray-400">
						创建、管理和监控神秘事件研究任务
					</p>
				</div>
				<button
					onclick={() => isCreating = !isCreating}
					class="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center space-x-2"
				>
					<span>➕</span>
					<span>新建研究</span>
				</button>
			</div>
		</div>
	</div>

	<!-- Stats Dashboard -->
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
		<div class="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
			<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
				<div class="flex items-center">
					<div class="flex-shrink-0">
						<div class="w-8 h-8 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center">
							📊
						</div>
					</div>
					<div class="ml-4">
						<p class="text-sm font-medium text-gray-500 dark:text-gray-400">总任务数</p>
						<p class="text-2xl font-bold text-gray-900 dark:text-white">{stats.total}</p>
					</div>
				</div>
			</div>

			<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
				<div class="flex items-center">
					<div class="flex-shrink-0">
						<div class="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
							🔄
						</div>
					</div>
					<div class="ml-4">
						<p class="text-sm font-medium text-gray-500 dark:text-gray-400">运行中</p>
						<p class="text-2xl font-bold text-blue-600 dark:text-blue-400">{stats.running}</p>
					</div>
				</div>
			</div>

			<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
				<div class="flex items-center">
					<div class="flex-shrink-0">
						<div class="w-8 h-8 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
							✅
						</div>
					</div>
					<div class="ml-4">
						<p class="text-sm font-medium text-gray-500 dark:text-gray-400">已完成</p>
						<p class="text-2xl font-bold text-green-600 dark:text-green-400">{stats.completed}</p>
					</div>
				</div>
			</div>

			<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
				<div class="flex items-center">
					<div class="flex-shrink-0">
						<div class="w-8 h-8 bg-yellow-100 dark:bg-yellow-900 rounded-full flex items-center justify-center">
							⏳
						</div>
					</div>
					<div class="ml-4">
						<p class="text-sm font-medium text-gray-500 dark:text-gray-400">等待中</p>
						<p class="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{stats.pending}</p>
					</div>
				</div>
			</div>

			<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
				<div class="flex items-center">
					<div class="flex-shrink-0">
						<div class="w-8 h-8 bg-red-100 dark:bg-red-900 rounded-full flex items-center justify-center">
							❌
						</div>
					</div>
					<div class="ml-4">
						<p class="text-sm font-medium text-gray-500 dark:text-gray-400">失败</p>
						<p class="text-2xl font-bold text-red-600 dark:text-red-400">{stats.failed}</p>
					</div>
				</div>
			</div>
		</div>

		<!-- Create New Task Form -->
		{#if isCreating}
			<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 mb-8">
				<div class="flex items-center justify-between mb-6">
					<h2 class="text-2xl font-bold text-gray-900 dark:text-white">创建新研究任务</h2>
					<button
						onclick={() => isCreating = false}
						class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
					>
						✕
					</button>
				</div>

				<form onsubmit={createResearchTask} class="space-y-6">
					<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
						<div class="md:col-span-2">
							<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
								研究标题 *
							</label>
							<input
								type="text"
								bind:value={newTask.title}
								placeholder="输入研究主题或事件名称"
								class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
								required
							/>
						</div>

						<div class="md:col-span-2">
							<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
								详细描述
							</label>
							<textarea
								bind:value={newTask.description}
								placeholder="描述研究目标、背景信息和期望结果"
								rows="4"
								class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
							></textarea>
						</div>

						<div>
							<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
								关键词
							</label>
							<div class="flex space-x-2 mb-2">
								<input
									type="text"
									bind:value={keywordInput}
									onkeydown={handleKeywordKeydown}
									placeholder="输入关键词后按回车"
									class="flex-1 border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
								/>
								<button
									type="button"
									onclick={addKeyword}
									class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
								>
									添加
								</button>
							</div>
							<div class="flex flex-wrap gap-2">
								{#each newTask.keywords as keyword (keyword)}
											<span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200">
										{keyword}
										<button
											type="button"
											onclick={() => removeKeyword(keyword)}
											class="ml-2 text-indigo-600 hover:text-indigo-800 dark:text-indigo-300 dark:hover:text-indigo-100"
										>
											×
										</button>
									</span>
								{/each}
							</div>
						</div>

						<div>
							<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
								标签
							</label>
							<div class="flex space-x-2 mb-2">
								<input
									type="text"
									bind:value={tagInput}
									onkeydown={handleTagKeydown}
									placeholder="输入标签后按回车"
									class="flex-1 border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
								/>
								<button
									type="button"
									onclick={addTag}
									class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
								>
									添加
								</button>
							</div>
							<div class="flex flex-wrap gap-2">
								{#each newTask.tags as tag (tag)}
											<span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
										{tag}
										<button
											type="button"
											onclick={() => removeTag(tag)}
											class="ml-2 text-green-600 hover:text-green-800 dark:text-green-300 dark:hover:text-green-100"
										>
											×
										</button>
									</span>
								{/each}
							</div>
						</div>

						<div>
							<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
								研究深度: {newTask.maxDepth}
							</label>
							<input
								type="range"
								min="1"
								max="10"
								bind:value={newTask.maxDepth}
								class="w-full"
							/>
						</div>

						<div>
							<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
								可信度阈值: {newTask.credibilityThreshold}
							</label>
							<input
								type="range"
								min="0"
								max="1"
								step="0.1"
								bind:value={newTask.credibilityThreshold}
								class="w-full"
							/>
						</div>

						<div>
							<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
								优先级
							</label>
							<select
								bind:value={newTask.priority}
								class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
							>
								<option value="low">低</option>
								<option value="medium">中</option>
								<option value="high">高</option>
								<option value="urgent">紧急</option>
							</select>
						</div>

						<div class="md:col-span-2">
							<div class="space-y-4">
								<div class="flex items-center">
									<input
										id="enable-academic"
										type="checkbox"
										bind:checked={newTask.enableAcademicSearch}
										class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
									/>
									<label for="enable-academic" class="ml-2 block text-sm text-gray-900 dark:text-white">
										启用学术搜索
									</label>
								</div>

								<div class="flex items-center">
									<input
										id="enable-graph-storage"
										type="checkbox"
										bind:checked={newTask.enableGraphStorage}
										class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
									/>
									<label for="enable-graph-storage" class="ml-2 block text-sm text-gray-900 dark:text-white">
										启用图数据库存储
									</label>
								</div>
							</div>
						</div>
					</div>

					<div class="flex justify-end space-x-4">
						<button
							type="button"
							onclick={() => isCreating = false}
							class="px-6 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
						>
							取消
						</button>
						<button
							type="submit"
							disabled={isCreating}
							class="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 transition-colors flex items-center space-x-2"
						>
							{#if isCreating}
								<div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
							{/if}
							<span>创建任务</span>
						</button>
					</div>
				</form>
			</div>
		{/if}

		<!-- Search and Filter -->
		<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
			<div class="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
				<div class="flex-1 max-w-lg">
					<input
						type="text"
						bind:value={searchQuery}
						placeholder="搜索任务标题、描述或关键词..."
						class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-4 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
					/>
				</div>
				<div class="flex items-center space-x-4">
					<select
						bind:value={filterStatus}
						class="border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
					>
						<option value="all">全部状态</option>
						<option value="pending">等待中</option>
						<option value="running">运行中</option>
						<option value="completed">已完成</option>
						<option value="failed">失败</option>
						<option value="paused">已暂停</option>
					</select>
					<button
						onclick={loadResearchTasks}
						class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors flex items-center space-x-2"
					>
						<span>🔄</span>
						<span>刷新</span>
					</button>
				</div>
			</div>
		</div>

		<!-- Tasks List -->
		<div class="space-y-6">
			{#if isLoading}
				<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 text-center">
					<div class="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
					<p class="text-gray-600 dark:text-gray-400">加载研究任务中...</p>
				</div>
			{:else if filteredTasks.length === 0}
				<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 text-center">
					<div class="text-6xl mb-4">🔍</div>
					<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
						{searchQuery || filterStatus !== 'all' ? '未找到匹配的任务' : '暂无研究任务'}
					</h3>
					<p class="text-gray-600 dark:text-gray-400">
						{searchQuery || filterStatus !== 'all' ? '尝试调整搜索条件或筛选器' : '点击上方按钮创建第一个研究任务'}
					</p>
				</div>
			{:else}
				{#each filteredTasks as task (task.id)}
					<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
						<div class="flex items-start justify-between">
							<div class="flex-1">
								<div class="flex items-center space-x-3 mb-3">
									<h3 class="text-xl font-semibold text-gray-900 dark:text-white">
										{task.title}
									</h3>
									<span class="px-2 py-1 rounded-full text-xs font-medium {statusColors[task.status]}">
										{task.status === 'pending' ? '等待中' : 
										 task.status === 'running' ? '运行中' :
										 task.status === 'completed' ? '已完成' :
										 task.status === 'failed' ? '失败' : '已暂停'}
									</span>
									<span class="px-2 py-1 rounded-full text-xs font-medium {priorityColors[task.priority]}">
										{task.priority === 'low' ? '低优先级' :
										 task.priority === 'medium' ? '中优先级' :
										 task.priority === 'high' ? '高优先级' : '紧急'}
									</span>
								</div>

								{#if task.description}
									<p class="text-gray-600 dark:text-gray-400 mb-3">{task.description}</p>
								{/if}

								<div class="flex flex-wrap gap-2 mb-3">
									{#each task.keywords as keyword (keyword)}
													<span class="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded text-sm">
											{keyword}
										</span>
									{/each}
									{#each task.tags as tag (tag)}
													<span class="px-2 py-1 bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded text-sm">
											#{tag}
										</span>
									{/each}
								</div>

								<div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 dark:text-gray-400">
									<div>
										<span class="font-medium">创建时间:</span>
										<br>{formatDate(task.createdAt)}
									</div>
									{#if task.startedAt}
										<div>
											<span class="font-medium">开始时间:</span>
											<br>{formatDate(task.startedAt)}
										</div>
									{/if}
									{#if task.completedAt}
										<div>
											<span class="font-medium">完成时间:</span>
											<br>{formatDate(task.completedAt)}
										</div>
									{/if}
									{#if task.duration}
										<div>
											<span class="font-medium">耗时:</span>
											<br>{formatDuration(task.duration)}
										</div>
									{/if}
								</div>

								{#if task.progress}
									<div class="mt-4">
										<div class="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-1">
											<span>进度</span>
											<span>{task.progress}%</span>
										</div>
										<div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
											<div 
												class="bg-indigo-600 h-2 rounded-full transition-all duration-300" 
												style="width: {task.progress}%"
											></div>
										</div>
									</div>
								{/if}
							</div>

							<div class="flex flex-col space-y-2">
								<button
									onclick={() => activeTask = task}
									class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors text-sm"
								>
									查看详情
								</button>

								{#if task.status === 'running'}
									<button
										onclick={() => pauseTask(task.id)}
										class="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 transition-colors text-sm"
									>
										暂停
									</button>
								{:else if task.status === 'paused'}
									<button
										onclick={() => resumeTask(task.id)}
										class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors text-sm"
									>
										继续
									</button>
								{/if}

								{#if task.status === 'completed'}
									<a
										href="/reports/{task.id}"
										class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm text-center"
									>
										查看报告
									</a>
								{/if}

								<button
									onclick={() => deleteTask(task.id)}
									class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors text-sm"
								>
									删除
								</button>
							</div>
						</div>
					</div>
				{/each}
			{/if}
		</div>
	</div>
</div>

<!-- Task Detail Modal -->
{#if activeTask}
	<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
		<div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
			<div class="p-6">
				<div class="flex items-center justify-between mb-6">
					<h2 class="text-2xl font-bold text-gray-900 dark:text-white">{activeTask.title}</h2>
					<button
						onclick={() => activeTask = null}
						class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 text-2xl"
					>
						×
					</button>
				</div>

				<div class="space-y-6">
					<div>
						<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">任务详情</h3>
						<div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
							<p class="text-gray-700 dark:text-gray-300">{activeTask.description || '暂无描述'}</p>
						</div>
					</div>

					<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
						<div>
							<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">配置参数</h3>
							<div class="space-y-2 text-sm">
								<div class="flex justify-between">
									<span class="text-gray-600 dark:text-gray-400">研究深度:</span>
									<span class="font-medium">{activeTask.maxDepth}</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-600 dark:text-gray-400">可信度阈值:</span>
									<span class="font-medium">{activeTask.credibilityThreshold}</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-600 dark:text-gray-400">学术搜索:</span>
									<span class="font-medium">{activeTask.enableAcademicSearch ? '启用' : '禁用'}</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-600 dark:text-gray-400">图存储:</span>
									<span class="font-medium">{activeTask.enableGraphStorage ? '启用' : '禁用'}</span>
								</div>
							</div>
						</div>

						<div>
							<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">执行状态</h3>
							<div class="space-y-2 text-sm">
								<div class="flex justify-between">
									<span class="text-gray-600 dark:text-gray-400">当前状态:</span>
									<span class="px-2 py-1 rounded-full text-xs font-medium {statusColors[activeTask.status]}">
										{activeTask.status === 'pending' ? '等待中' : 
										 activeTask.status === 'running' ? '运行中' :
										 activeTask.status === 'completed' ? '已完成' :
										 activeTask.status === 'failed' ? '失败' : '已暂停'}
									</span>
								</div>
								{#if activeTask.progress}
									<div>
										<div class="flex justify-between mb-1">
											<span class="text-gray-600 dark:text-gray-400">进度:</span>
											<span class="font-medium">{activeTask.progress}%</span>
										</div>
										<div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
											<div 
												class="bg-indigo-600 h-2 rounded-full transition-all duration-300" 
												style="width: {activeTask.progress}%"
											></div>
										</div>
									</div>
								{/if}
								{#if activeTask.currentStep}
									<div class="flex justify-between">
										<span class="text-gray-600 dark:text-gray-400">当前步骤:</span>
										<span class="font-medium">{activeTask.currentStep}</span>
									</div>
								{/if}
							</div>
						</div>
					</div>

					{#if activeTask.keywords.length > 0}
						<div>
							<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">关键词</h3>
							<div class="flex flex-wrap gap-2">
								{#each activeTask.keywords as keyword (keyword)}
												<span class="px-3 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded-full text-sm">
										{keyword}
									</span>
								{/each}
							</div>
						</div>
					{/if}

					{#if activeTask.tags.length > 0}
						<div>
							<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">标签</h3>
							<div class="flex flex-wrap gap-2">
								{#each activeTask.tags as tag (tag)}
												<span class="px-3 py-1 bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded-full text-sm">
										#{tag}
									</span>
								{/each}
							</div>
						</div>
					{/if}

					{#if activeTask.logs && activeTask.logs.length > 0}
						<div>
							<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">执行日志</h3>
							<div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 max-h-64 overflow-y-auto">
								<div class="space-y-2 text-sm font-mono">
									{#each activeTask.logs as log (log.id || log.timestamp)}
											<div class="flex items-start space-x-2">
											<span class="text-gray-500 dark:text-gray-400 whitespace-nowrap">
												{formatDate(log.timestamp)}
											</span>
											<span class="px-2 py-1 rounded text-xs {log.level === 'error' ? 'bg-red-100 text-red-800' : log.level === 'warning' ? 'bg-yellow-100 text-yellow-800' : 'bg-blue-100 text-blue-800'}">
												{log.level.toUpperCase()}
											</span>
											<span class="text-gray-700 dark:text-gray-300">{log.message}</span>
										</div>
									{/each}
								</div>
							</div>
						</div>
					{/if}

					{#if activeTask.results && activeTask.results.length > 0}
						<div>
							<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">研究结果</h3>
							<div class="space-y-3">
								{#each activeTask.results as result (result.id || result.title)}
											<div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
										<div class="flex items-center justify-between mb-2">
											<h4 class="font-medium text-gray-900 dark:text-white">{result.title}</h4>
											<span class="text-sm text-gray-500 dark:text-gray-400">
												可信度: {(result.credibility * 100).toFixed(1)}%
											</span>
										</div>
										<p class="text-gray-700 dark:text-gray-300 text-sm">{result.summary}</p>
										{#if result.source}
											<a href="{result.source}" target="_blank" class="text-indigo-600 dark:text-indigo-400 hover:underline text-sm">
												查看来源
											</a>
										{/if}
									</div>
								{/each}
							</div>
						</div>
					{/if}
				</div>

				<div class="flex justify-end space-x-4 mt-6 pt-6 border-t border-gray-200 dark:border-gray-600">
					{#if activeTask.status === 'completed'}
						<a
							href="/reports/{activeTask.id}"
							class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
						>
							查看完整报告
						</a>
					{/if}
					<button
						onclick={() => activeTask = null}
						class="px-6 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
					>
						关闭
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}

<style>
	/* Custom scrollbar for logs */
	.overflow-y-auto::-webkit-scrollbar {
		width: 6px;
	}

	.overflow-y-auto::-webkit-scrollbar-track {
		background: #f1f5f9;
		border-radius: 3px;
	}

	.overflow-y-auto::-webkit-scrollbar-thumb {
		background: #cbd5e1;
		border-radius: 3px;
	}

	.overflow-y-auto::-webkit-scrollbar-thumb:hover {
		background: #94a3b8;
	}

	:global(.dark) .overflow-y-auto::-webkit-scrollbar-track {
		background: #374151;
	}

	:global(.dark) .overflow-y-auto::-webkit-scrollbar-thumb {
		background: #6b7280;
	}

	:global(.dark) .overflow-y-auto::-webkit-scrollbar-thumb:hover {
		background: #9ca3af;
	}
</style>