<script lang="ts">
	import { onMount } from 'svelte';

	// Type definitions
	interface Message {
		id: number;
		type: 'user' | 'assistant' | 'error';
		content: string;
		timestamp: string;
		model?: string;
	}

	// Chat state
	let messages = $state<Message[]>([]);
	let isLoading = $state(false);
	let inputMessage = $state('');
	let chatContainer = $state<HTMLDivElement | null>(null);
	let messageInput = $state<HTMLTextAreaElement | null>(null);

	// Chat configuration
	let selectedModel = $state('gpt-4');
	let temperature = $state(0.7);
	let maxTokens = $state(2000);
	let systemPrompt = $state('你是一个专业的神秘事件研究助手，擅长分析各种超自然现象、未解之谜和神秘事件。请提供专业、客观的分析和建议。');

	// Available models
	const models = [
		{ id: 'gpt-4', name: 'GPT-4', description: '最强大的通用模型' },
		{ id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', description: '快速响应模型' },
		{ id: 'claude-3', name: 'Claude-3', description: '擅长分析推理' },
		{ id: 'gemini-pro', name: 'Gemini Pro', description: '多模态理解' }
	];

	// Quick prompts
	const quickPrompts = [
		{ id: 1, text: '分析这个神秘事件的可能原因' },
		{ id: 2, text: '评估证据的可信度' },
		{ id: 3, text: '寻找相关的历史案例' },
		{ id: 4, text: '制定调查计划' },
		{ id: 5, text: '分析时间线的逻辑性' },
		{ id: 6, text: '识别关键线索' }
	];

	onMount(() => {
		// Load chat history from localStorage
		const savedMessages = localStorage.getItem('chat-messages');
		if (savedMessages) {
			messages = JSON.parse(savedMessages);
		}

		// Add welcome message if no history
		if (messages.length === 0) {
			messages = [{
				id: Date.now(),
				type: 'assistant',
				content: '你好！我是灵境研究系统的AI助手。我可以帮助你分析神秘事件、评估证据可信度、制定调查计划等。请告诉我你想要研究什么？',
				timestamp: new Date().toISOString()
			}];
		}
	});

	// Save messages to localStorage
	$effect(() => {
		if (messages.length > 0) {
			localStorage.setItem('chat-messages', JSON.stringify(messages));
		}
	});

	// Auto-scroll to bottom
	$effect(() => {
		if (chatContainer && messages.length > 0) {
			setTimeout(() => {
				if (chatContainer) {
					chatContainer.scrollTop = chatContainer.scrollHeight;
				}
			}, 100);
		}
	});

	async function sendMessage() {
		if (!inputMessage.trim() || isLoading) return;

		const userMessage: Message = {
			id: Date.now(),
			type: 'user',
			content: inputMessage.trim(),
			timestamp: new Date().toISOString()
		};

		messages = [...messages, userMessage];
		const currentInput = inputMessage;
		inputMessage = '';
		isLoading = true;

		try {
			// Call API
			const response = await fetch('/api/chat', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					message: currentInput,
					model: selectedModel,
					temperature,
					maxTokens,
					systemPrompt,
					history: messages.slice(-10) // Send last 10 messages for context
				})
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();

			const assistantMessage: Message = {
				id: Date.now() + 1,
				type: 'assistant',
				content: data.response,
				timestamp: new Date().toISOString(),
				model: selectedModel
			};

			messages = [...messages, assistantMessage];
		} catch (error) {
			console.error('Error sending message:', error);
			const errorMessage: Message = {
				id: Date.now() + 1,
				type: 'error',
				content: '抱歉，发送消息时出现错误。请检查网络连接或稍后重试。',
				timestamp: new Date().toISOString()
			};
			messages = [...messages, errorMessage];
		} finally {
			isLoading = false;
		}
	}

	function useQuickPrompt(prompt: string) {
		inputMessage = prompt;
		messageInput?.focus();
	}

	function clearChat() {
		if (confirm('确定要清空聊天记录吗？')) {
			messages = [];
			localStorage.removeItem('chat-messages');
		}
	}

	function exportChat() {
		const chatData = {
			exportTime: new Date().toISOString(),
			messages: messages
		};
		const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = `chat-export-${new Date().toISOString().split('T')[0]}.json`;
		a.click();
		URL.revokeObjectURL(url);
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			sendMessage();
		}
	}

	function formatTime(timestamp: string | number): string {
		return new Date(timestamp).toLocaleTimeString('zh-CN', {
			hour: '2-digit',
			minute: '2-digit'
		});
	}
</script>

<svelte:head>
	<title>智能对话 - 灵境研究</title>
	<meta name="description" content="与AI助手对话，获取专业的神秘事件研究建议" />
</svelte:head>

<div class="h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
	<!-- Header -->
	<div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
		<div class="flex items-center justify-between">
			<div class="flex items-center space-x-4">
				<h1 class="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
					💬 智能对话助手
				</h1>
				<div class="flex items-center space-x-2">
					<select
						bind:value={selectedModel}
						class="text-sm border border-gray-300 dark:border-gray-600 rounded-md px-3 py-1 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
					>
						{#each models as model (model.id)}
									<option value={model.id}>{model.name}</option>
						{/each}
					</select>
					<span class="text-sm text-gray-500 dark:text-gray-400">
						{models.find(m => m.id === selectedModel)?.description}
					</span>
				</div>
			</div>
			<div class="flex items-center space-x-2">
				<button
					onclick={exportChat}
					class="px-3 py-1 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
				>
					导出
				</button>
				<button
					onclick={clearChat}
					class="px-3 py-1 text-sm bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
				>
					清空
				</button>
			</div>
		</div>
	</div>

	<!-- Chat Container -->
	<div class="flex-1 flex overflow-hidden">
		<!-- Main Chat Area -->
		<div class="flex-1 flex flex-col">
			<!-- Messages -->
			<div
				bind:this={chatContainer}
				class="flex-1 overflow-y-auto p-6 space-y-4"
			>
				{#each messages as message (message.id)}
						<div class="flex {message.type === 'user' ? 'justify-end' : 'justify-start'}">
						<div class="max-w-3xl {message.type === 'user' ? 'order-2' : 'order-1'}">
							<div class="flex items-end space-x-2 {message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}">
								<!-- Avatar -->
								<div class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0
									{message.type === 'user' 
										? 'bg-indigo-600 text-white' 
										: message.type === 'error'
											? 'bg-red-600 text-white'
											: 'bg-gray-600 text-white'}"
								>
									{#if message.type === 'user'}
										👤
									{:else if message.type === 'error'}
										❌
									{:else}
										🤖
									{/if}
								</div>

								<!-- Message Content -->
								<div class="flex flex-col space-y-1">
									<div class="px-4 py-3 rounded-lg
										{message.type === 'user'
											? 'bg-indigo-600 text-white'
											: message.type === 'error'
												? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
												: 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700'}"
									>
										<div class="whitespace-pre-wrap">{message.content}</div>
									</div>
									<div class="text-xs text-gray-500 dark:text-gray-400 {message.type === 'user' ? 'text-right' : 'text-left'}">
										{formatTime(message.timestamp)}
										{#if message.model}
											• {models.find(m => m.id === message.model)?.name}
										{/if}
									</div>
								</div>
							</div>
						</div>
					</div>
				{/each}

				<!-- Loading indicator -->
				{#if isLoading}
					<div class="flex justify-start">
						<div class="max-w-3xl">
							<div class="flex items-end space-x-2">
								<div class="w-8 h-8 rounded-full bg-gray-600 text-white flex items-center justify-center flex-shrink-0">
									🤖
								</div>
								<div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg px-4 py-3">
									<div class="flex space-x-1">
										<div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
										<div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
										<div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
									</div>
								</div>
							</div>
						</div>
					</div>
				{/if}
			</div>

			<!-- Input Area -->
			<div class="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6">
				<!-- Quick Prompts -->
				{#if messages.length <= 1}
					<div class="mb-4">
						<p class="text-sm text-gray-600 dark:text-gray-400 mb-2">快速开始：</p>
						<div class="flex flex-wrap gap-2">
							{#each quickPrompts as prompt (prompt.id)}
				<button
						class="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
						onclick={() => useQuickPrompt(prompt.text)}
					>
						{prompt.text}
					</button>
							{/each}
						</div>
					</div>
				{/if}

				<!-- Message Input -->
				<div class="flex space-x-4">
					<div class="flex-1">
						<textarea
							bind:this={messageInput}
							bind:value={inputMessage}
							onkeydown={handleKeydown}
							placeholder="输入你的问题... (Shift+Enter 换行，Enter 发送)"
							class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
							rows="3"
							disabled={isLoading}
						></textarea>
					</div>
					<button
						onclick={sendMessage}
						disabled={!inputMessage.trim() || isLoading}
						class="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
					>
						{#if isLoading}
							<div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
						{:else}
							<span>发送</span>
							<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
							</svg>
						{/if}
					</button>
				</div>
			</div>
		</div>

		<!-- Settings Sidebar -->
		<div class="w-80 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 p-6 overflow-y-auto">
			<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">对话设置</h3>
			
			<div class="space-y-6">
				<!-- Model Selection -->
				<div>
					<label for="model-select" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						AI 模型
					</label>
					<select
						id="model-select"
						bind:value={selectedModel}
						class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
					>
						{#each models as model (model.id)}
										<option value={model.id}>{model.name} - {model.description}</option>
						{/each}
					</select>
				</div>

				<!-- Temperature -->
				<div>
					<label for="temperature-range" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						创造性 (Temperature): {temperature}
					</label>
					<input
						id="temperature-range"
						type="range"
						min="0"
						max="1"
						step="0.1"
						bind:value={temperature}
						class="w-full"
					/>
					<div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
						<span>保守</span>
						<span>创新</span>
					</div>
				</div>

				<!-- Max Tokens -->
				<div>
					<label for="max-tokens-range" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						最大回复长度: {maxTokens}
					</label>
					<input
						id="max-tokens-range"
						type="range"
						min="500"
						max="4000"
						step="100"
						bind:value={maxTokens}
						class="w-full"
					/>
				</div>

				<!-- System Prompt -->
				<div>
					<label for="system-prompt" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						系统提示词
					</label>
					<textarea
						id="system-prompt"
						bind:value={systemPrompt}
						class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
						rows="4"
						placeholder="定义AI助手的角色和行为..."
					></textarea>
				</div>

				<!-- Chat Stats -->
				<div class="border-t border-gray-200 dark:border-gray-700 pt-4">
					<h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">对话统计</h4>
					<div class="space-y-2 text-sm text-gray-600 dark:text-gray-400">
						<div class="flex justify-between">
							<span>消息数量:</span>
							<span>{messages.length}</span>
						</div>
						<div class="flex justify-between">
							<span>用户消息:</span>
							<span>{messages.filter(m => m.type === 'user').length}</span>
						</div>
						<div class="flex justify-between">
							<span>AI回复:</span>
							<span>{messages.filter(m => m.type === 'assistant').length}</span>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	/* Custom scrollbar */
	:global(.overflow-y-auto::-webkit-scrollbar) {
		width: 6px;
	}

	:global(.overflow-y-auto::-webkit-scrollbar-track) {
		background: transparent;
	}

	:global(.overflow-y-auto::-webkit-scrollbar-thumb) {
		background: #d1d5db;
		border-radius: 3px;
	}

	:global(.dark .overflow-y-auto::-webkit-scrollbar-thumb) {
		background: #4b5563;
	}

	/* Animation for loading dots */
	@keyframes bounce {
		0%, 80%, 100% {
			transform: scale(0);
		}
		40% {
			transform: scale(1);
		}
	}
</style>