<script lang="ts">
	import { onMount } from 'svelte';

	// Configuration state
	let config = $state({
		// Research Configuration
		research: {
			maxDepth: 3,
			enableAcademicSearch: true,
			credibilityThreshold: 0.7,
			enableGraphStorage: true,
			maxConcurrentTasks: 5,
			timeoutSeconds: 300
		},
		// AI Models Configuration
		models: {
			defaultModel: 'gpt-4',
			temperature: 0.7,
			maxTokens: 2000,
			topP: 0.9,
			frequencyPenalty: 0.0,
			presencePenalty: 0.0
		},
		// Crawlers Configuration
		crawlers: {
			userAgent: 'LingjingResearch/1.0',
			requestDelay: 1000,
			maxRetries: 3,
			timeout: 30000,
			enableJavaScript: false,
			maxPages: 100
		},
		// Database Configuration
		database: {
			neo4jUri: 'bolt://localhost:7687',
			neo4jUser: 'neo4j',
			neo4jPassword: '',
			elasticsearchHost: 'localhost:9200',
			elasticsearchIndex: 'lingjing_research'
		},
		// Report Configuration
		reports: {
			defaultFormat: 'markdown',
			includeTimeline: true,
			includeCredibilityAnalysis: true,
			includeSourceLinks: true,
			maxReportLength: 10000
		},
		// API Configuration
		api: {
			rateLimit: 100,
			enableCors: true,
			apiKey: '',
			logLevel: 'info'
		}
	});

	let isSaving = $state(false);
	let saveMessage = $state('');
	let activeTab = $state('research');

	// Available options
	const modelOptions = [
		{ value: 'gpt-4', label: 'GPT-4' },
		{ value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
		{ value: 'claude-3', label: 'Claude-3' },
		{ value: 'gemini-pro', label: 'Gemini Pro' }
	];

	const reportFormats = [
		{ value: 'markdown', label: 'Markdown' },
		{ value: 'html', label: 'HTML' },
		{ value: 'pdf', label: 'PDF' },
		{ value: 'json', label: 'JSON' }
	];

	const logLevels = [
		{ value: 'debug', label: 'Debug' },
		{ value: 'info', label: 'Info' },
		{ value: 'warning', label: 'Warning' },
		{ value: 'error', label: 'Error' }
	];

	const tabs = [
		{ id: 'research', label: '研究配置', icon: '🔍' },
		{ id: 'models', label: 'AI模型', icon: '🤖' },
		{ id: 'crawlers', label: '爬虫设置', icon: '🕷️' },
		{ id: 'database', label: '数据库', icon: '🗄️' },
		{ id: 'reports', label: '报告设置', icon: '📊' },
		{ id: 'api', label: 'API配置', icon: '🔌' }
	];

	onMount(async () => {
		// Load configuration from server
		try {
			const response = await fetch('/api/config');
			if (response.ok) {
				const serverConfig = await response.json();
				config = { ...config, ...serverConfig };
			}
		} catch (error) {
			console.error('Failed to load configuration:', error);
		}
	});

	async function saveConfiguration() {
		isSaving = true;
		saveMessage = '';

		try {
			const response = await fetch('/api/config', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(config)
			});

			if (response.ok) {
				saveMessage = '配置保存成功！';
				setTimeout(() => saveMessage = '', 3000);
			} else {
				throw new Error('保存失败');
			}
		} catch (error) {
			console.error('Failed to save configuration:', error);
			saveMessage = '保存失败，请重试';
			setTimeout(() => saveMessage = '', 3000);
		} finally {
			isSaving = false;
		}
	}

	async function resetToDefaults() {
		if (confirm('确定要重置为默认配置吗？这将覆盖所有当前设置。')) {
			try {
				const response = await fetch('/api/config/reset', {
					method: 'POST'
				});

				if (response.ok) {
					const defaultConfig = await response.json();
					config = defaultConfig;
					saveMessage = '已重置为默认配置';
					setTimeout(() => saveMessage = '', 3000);
				}
			} catch (error) {
				console.error('Failed to reset configuration:', error);
				saveMessage = '重置失败，请重试';
				setTimeout(() => saveMessage = '', 3000);
			}
		}
	}

	async function testConnection(type: string) {
		try {
			const response = await fetch(`/api/config/test/${type}`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(config[type as keyof typeof config] || config.database)
			});

			const result = await response.json();
			alert(result.success ? '连接测试成功！' : `连接测试失败：${result.error}`);
		} catch (error) {
			alert(`连接测试失败：${error instanceof Error ? error.message : String(error)}`);
		}
	}

	function exportConfig() {
		const configData = {
			exportTime: new Date().toISOString(),
			config: config
		};
		const blob = new Blob([JSON.stringify(configData, null, 2)], { type: 'application/json' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = `lingjing-config-${new Date().toISOString().split('T')[0]}.json`;
		a.click();
		URL.revokeObjectURL(url);
	}

	function importConfig(event: Event) {
		const target = event.target as HTMLInputElement;
		const file = target?.files?.[0];
		if (!file) return;

		const reader = new FileReader();
		reader.onload = (e) => {
			try {
				const result = e.target?.result;
				if (typeof result === 'string') {
					const importedData = JSON.parse(result);
					if (importedData.config) {
						config = { ...config, ...importedData.config };
						saveMessage = '配置导入成功！';
						setTimeout(() => saveMessage = '', 3000);
					} else {
						throw new Error('无效的配置文件格式');
					}
				}
			} catch (error) {
				alert(`导入失败：${error instanceof Error ? error.message : String(error)}`);
			}
		};
		reader.readAsText(file);
	}
</script>

<svelte:head>
	<title>项目配置 - 灵境研究</title>
	<meta name="description" content="配置灵境研究系统的各项参数和设置" />
</svelte:head>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	<!-- Header -->
	<div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
			<div class="flex items-center justify-between">
				<div>
					<h1 class="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
						⚙️ 项目配置
					</h1>
					<p class="mt-2 text-gray-600 dark:text-gray-400">
						自定义研究参数，优化系统性能
					</p>
				</div>
				<div class="flex items-center space-x-4">
					{#if saveMessage}
						<div class="px-4 py-2 rounded-md text-sm font-medium
							{saveMessage.includes('成功') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
							{saveMessage}
						</div>
					{/if}
					<input
						type="file"
						accept=".json"
						onchange={importConfig}
						class="hidden"
						id="import-config"
					/>
					<label
						for="import-config"
						class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors cursor-pointer"
					>
						导入配置
					</label>
					<button
						onclick={exportConfig}
						class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
					>
						导出配置
					</button>
					<button
						onclick={resetToDefaults}
						class="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 transition-colors"
					>
						重置默认
					</button>
					<button
						onclick={saveConfiguration}
						disabled={isSaving}
						class="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 transition-colors flex items-center space-x-2"
					>
						{#if isSaving}
							<div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
						{/if}
						<span>保存配置</span>
					</button>
				</div>
			</div>
		</div>
	</div>

	<!-- Main Content -->
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<div class="flex space-x-8">
			<!-- Sidebar Navigation -->
			<div class="w-64 flex-shrink-0">
				<nav class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
					<ul class="space-y-2">
						{#each tabs as tab (tab.id)}
						<li>
							<button
									onclick={() => activeTab = tab.id}
									class="w-full text-left px-4 py-3 rounded-md transition-colors flex items-center space-x-3
										{activeTab === tab.id
											? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300'
											: 'text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'}"
								>
									<span class="text-lg">{tab.icon}</span>
									<span class="font-medium">{tab.label}</span>
								</button>
							</li>
						{/each}
					</ul>
				</nav>
			</div>

			<!-- Configuration Content -->
			<div class="flex-1">
				<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
					<!-- Research Configuration -->
					{#if activeTab === 'research'}
						<div class="space-y-6">
							<h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">🔍 研究配置</h2>
							
							<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
								<div>
						<label for="maxDepth" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							最大研究深度
						</label>
						<input
							id="maxDepth"
							type="number"
							min="1"
							max="10"
							bind:value={config.research.maxDepth}
							class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
						/>
						<p class="text-xs text-gray-500 dark:text-gray-400 mt-1">控制研究的深度层级</p>
					</div>

								<div>
						<label for="credibilityThreshold" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							可信度阈值
						</label>
						<input
							id="credibilityThreshold"
							type="number"
							min="0"
							max="1"
							step="0.1"
							bind:value={config.research.credibilityThreshold}
							class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
						/>
						<p class="text-xs text-gray-500 dark:text-gray-400 mt-1">过滤低可信度信息</p>
					</div>

								<div>
						<label for="maxConcurrentTasks" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							最大并发任务数
						</label>
						<input
							id="maxConcurrentTasks"
							type="number"
							min="1"
							max="20"
							bind:value={config.research.maxConcurrentTasks}
							class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
						/>
						<p class="text-xs text-gray-500 dark:text-gray-400 mt-1">控制系统负载</p>
					</div>

								<div>
						<label for="timeoutSeconds" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							超时时间 (秒)
						</label>
						<input
							id="timeoutSeconds"
							type="number"
							min="30"
							max="3600"
							bind:value={config.research.timeoutSeconds}
							class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
						/>
						<p class="text-xs text-gray-500 dark:text-gray-400 mt-1">任务执行超时限制</p>
					</div>
							</div>

							<div class="space-y-4">
								<div class="flex items-center">
									<input
										id="enable-academic"
										type="checkbox"
										bind:checked={config.research.enableAcademicSearch}
										class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
									/>
									<label for="enable-academic" class="ml-2 block text-sm text-gray-900 dark:text-white">
										启用学术搜索
									</label>
								</div>

								<div class="flex items-center">
									<input
										id="enable-graph"
										type="checkbox"
										bind:checked={config.research.enableGraphStorage}
										class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
									/>
									<label for="enable-graph" class="ml-2 block text-sm text-gray-900 dark:text-white">
										启用图数据库存储
									</label>
								</div>
							</div>
						</div>

					<!-- AI Models Configuration -->
					{:else if activeTab === 'models'}
						<div class="space-y-6">
							<h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">🤖 AI模型配置</h2>
							
							<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
								<div>
						<label for="defaultModel" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							默认模型
						</label>
						<select
							id="defaultModel"
							bind:value={config.models.defaultModel}
							class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
						>
							{#each modelOptions as option (option.value)}
					<option value={option.value}>{option.label}</option>
							{/each}
						</select>
					</div>

								<div>
						<label for="maxTokens" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							最大Token数
						</label>
						<input
							id="maxTokens"
							type="number"
										min="1000"
										max="50000"
										bind:value={config.reports.maxReportLength}
										class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
									/>
								</div>
							</div>

							<div class="space-y-4">
								<div class="flex items-center">
									<input
										id="include-timeline"
										type="checkbox"
										bind:checked={config.reports.includeTimeline}
										class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
									/>
									<label for="include-timeline" class="ml-2 block text-sm text-gray-900 dark:text-white">
										包含时间线分析
									</label>
								</div>

								<div class="flex items-center">
									<input
										id="include-credibility"
										type="checkbox"
										bind:checked={config.reports.includeCredibilityAnalysis}
										class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
									/>
									<label for="include-credibility" class="ml-2 block text-sm text-gray-900 dark:text-white">
										包含可信度分析
									</label>
								</div>

								<div class="flex items-center">
									<input
										id="include-sources"
										type="checkbox"
										bind:checked={config.reports.includeSourceLinks}
										class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
									/>
									<label for="include-sources" class="ml-2 block text-sm text-gray-900 dark:text-white">
										包含源链接
									</label>
								</div>
							</div>
						</div>

					<!-- API Configuration -->
					{:else if activeTab === 'api'}
						<div class="space-y-6">
							<h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">🔌 API配置</h2>
							
							<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
								<div>
						<label for="rateLimit" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							速率限制 (请求/分钟)
						</label>
						<input
							id="rateLimit"
							type="number"
							min="1"
							max="1000"
							bind:value={config.api.rateLimit}
										class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
									/>
								</div>

								<div>
									<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										日志级别
									</label>
									<select
										bind:value={config.api.logLevel}
										class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
									>
										{#each logLevels as level (level.value)}
								<option value={level.value}>{level.label}</option>
										{/each}
									</select>
								</div>

								<div class="md:col-span-2">
									<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										API密钥
									</label>
									<input
										type="password"
										bind:value={config.api.apiKey}
										placeholder="输入API密钥"
										class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
									/>
								</div>
							</div>

							<div class="flex items-center">
								<input
									id="enable-cors"
									type="checkbox"
									bind:checked={config.api.enableCors}
									class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
								/>
								<label for="enable-cors" class="ml-2 block text-sm text-gray-900 dark:text-white">
									启用CORS跨域支持
								</label>
							</div>
						</div>

			<!-- Crawlers Configuration -->
			{:else if activeTab === 'crawlers'}
				<div class="space-y-6">
					<h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">🕷️ 爬虫配置</h2>
					
					<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
						<div>
							<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
								User Agent
							</label>
							<input
								type="text"
								bind:value={config.crawlers.userAgent}
								class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
							/>
						</div>
					</div>
				</div>

			<!-- Database Configuration -->
			{:else if activeTab === 'database'}
				<div class="space-y-6">
							<h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">🗄️ 数据库配置</h2>
							
							<div class="space-y-8">
								<!-- Neo4j Configuration -->
								<div class="border border-gray-200 dark:border-gray-700 rounded-lg p-6">
									<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Neo4j 图数据库</h3>
									<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
										<div>
											<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
												连接URI
											</label>
											<input
												type="text"
												bind:value={config.database.neo4jUri}
												class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
											/>
										</div>
										<div>
											<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
												用户名
											</label>
											<input
												type="text"
												bind:value={config.database.neo4jUser}
												class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
											/>
										</div>
										<div class="md:col-span-2">
											<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
												密码
											</label>
											<input
												type="password"
												bind:value={config.database.neo4jPassword}
												class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
											/>
										</div>
									</div>
									<button
										onclick={() => testConnection('neo4j')}
										class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
									>
										测试Neo4j连接
									</button>
								</div>

								<!-- Elasticsearch Configuration -->
								<div class="border border-gray-200 dark:border-gray-700 rounded-lg p-6">
									<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Elasticsearch 搜索引擎</h3>
									<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
										<div>
											<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
												主机地址
											</label>
											<input
												type="text"
												bind:value={config.database.elasticsearchHost}
												class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
											/>
										</div>
										<div>
											<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
												索引名称
											</label>
											<input
												type="text"
												bind:value={config.database.elasticsearchIndex}
												class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
											/>
										</div>
									</div>
									<button
										onclick={() => testConnection('elasticsearch')}
										class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
									>
										测试Elasticsearch连接
									</button>
								</div>
							</div>
						</div>

					<!-- Reports Configuration -->
					{:else if activeTab === 'reports'}
						<div class="space-y-6">
							<h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">📊 报告配置</h2>
							
							<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
								<div>
									<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
										默认格式
									</label>
									<select
										bind:value={config.reports.defaultFormat}
										class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
									>
										{#each reportFormats as format (format.value)}
									<option value={format.value}>{format.label}</option>
								{/each}
								</select>
							</div>

							<div>
								<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
									最大报告长度
								</label>
								<input
									type="number"
									bind:value={config.reports.maxReportLength}
									class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
								/>
							</div>
						</div>
					</div>
				{/if}
			</div>
	</div>
	</div>
</div>
</div>

<style>
	/* Custom scrollbar for better UX */
	:global(html) {
		scroll-behavior: smooth;
	}

	/* Dark mode transitions */
	:global(.dark *) {
		transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
	}

	/* Custom range slider styling */
	input[type="range"] {
		-webkit-appearance: none;
		appearance: none;
		height: 6px;
		background: #e5e7eb;
		border-radius: 3px;
		outline: none;
	}

	input[type="range"]::-webkit-slider-thumb {
		-webkit-appearance: none;
		appearance: none;
		width: 20px;
		height: 20px;
		background: #4f46e5;
		border-radius: 50%;
		cursor: pointer;
	}

	input[type="range"]::-moz-range-thumb {
		width: 20px;
		height: 20px;
		background: #4f46e5;
		border-radius: 50%;
		cursor: pointer;
		border: none;
	}

	:global(.dark) input[type="range"] {
		background: #374151;
	}
</style>