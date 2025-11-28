<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { Promotion } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const messages = ref<any[]>([])
const inputMessage = ref('')
const ws = ref<WebSocket | null>(null)
const messagesContainer = ref<HTMLElement | null>(null)
const isConnected = ref(false)

// Contrast Color Helper
const getContrastColor = (hexcolor: string) => {
  if (!hexcolor) return 'black'
  // Remove # if present
  hexcolor = hexcolor.replace('#', '')
  const r = parseInt(hexcolor.substr(0, 2), 16)
  const g = parseInt(hexcolor.substr(2, 2), 16)
  const b = parseInt(hexcolor.substr(4, 2), 16)
  const yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000
  return yiq >= 128 ? 'black' : 'white'
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const connectWebSocket = () => {
  if (!authStore.token) return

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//localhost:8000/api/v1/chat/ws/${authStore.token}`
  
  ws.value = new WebSocket(wsUrl)
  
  ws.value.onopen = () => {
    isConnected.value = true
    console.log('Connected to chat')
  }
  
  ws.value.onmessage = (event) => {
    const message = JSON.parse(event.data)
    messages.value.push(message)
    scrollToBottom()
  }
  
  ws.value.onclose = () => {
    isConnected.value = false
    console.log('Disconnected from chat')
    // Reconnect logic could be added here
  }
}

const sendMessage = () => {
  if (!inputMessage.value.trim() || !ws.value || ws.value.readyState !== WebSocket.OPEN) return
  
  ws.value.send(inputMessage.value)
  inputMessage.value = ''
}

const fetchHistory = async () => {
  try {
    const res = await fetch('http://localhost:8000/api/v1/chat/history', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    const data = await res.json()
    if (Array.isArray(data)) {
      messages.value = data
      scrollToBottom()
    }
  } catch (error) {
    console.error('Failed to fetch history', error)
  }
}

onMounted(() => {
  fetchHistory()
  connectWebSocket()
})

onUnmounted(() => {
  if (ws.value) {
    ws.value.close()
  }
})
</script>

<template>
  <div class="h-[calc(100vh-100px)] flex flex-col bg-gray-50 dark:bg-gray-900 rounded-xl overflow-hidden shadow-lg border border-gray-200 dark:border-gray-700">
    <!-- Chat Header -->
    <div class="p-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center shadow-sm z-10">
      <h2 class="text-lg font-bold text-gray-800 dark:text-white flex items-center">
        <span class="w-2 h-2 rounded-full mr-2" :class="isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'"></span>
        大厅聊天
      </h2>
      <span class="text-xs text-gray-500">{{ isConnected ? '在线' : '离线' }}</span>
    </div>

    <!-- Messages Area -->
    <div 
      ref="messagesContainer" 
      class="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar bg-gray-100 dark:bg-gray-900"
    >
      <TransitionGroup name="message">
        <div 
          v-for="msg in messages" 
          :key="msg.id" 
          class="flex w-full"
          :class="msg.user_id === authStore.user?.id ? 'justify-end' : 'justify-start'"
        >
          <!-- Other User Avatar -->
          <el-avatar 
            v-if="msg.user_id !== authStore.user?.id" 
            :size="36" 
            :src="msg.sender?.avatar ? `http://localhost:8000${msg.sender.avatar}` : ''"
            class="mr-2 flex-shrink-0"
          >
            {{ msg.sender?.nickname?.charAt(0) || msg.sender?.username?.charAt(0) }}
          </el-avatar>

          <div class="flex flex-col max-w-[70%]" :class="msg.user_id === authStore.user?.id ? 'items-end' : 'items-start'">
            <div class="text-xs text-gray-500 mb-1 px-1" v-if="msg.user_id !== authStore.user?.id">
              {{ msg.sender?.nickname || msg.sender?.username }}
            </div>
            
            <div 
              class="p-3 rounded-2xl shadow-sm text-sm break-words relative transition-all duration-300 transform"
              :style="{ 
                backgroundColor: msg.sender?.chat_color || '#3b82f6',
                color: getContrastColor(msg.sender?.chat_color || '#3b82f6')
              }"
              :class="msg.user_id === authStore.user?.id ? 'rounded-tr-sm' : 'rounded-tl-sm'"
            >
              {{ msg.content }}
            </div>
            
            <div class="text-[10px] text-gray-400 mt-1 px-1">
              {{ new Date(msg.created_at).toLocaleTimeString() }}
            </div>
          </div>

          <!-- Current User Avatar (Optional, usually don't show own avatar in chat right side, but consistent style) -->
          <!-- We can omit own avatar to look like modern chat apps -->
        </div>
      </TransitionGroup>
    </div>

    <!-- Input Area -->
    <div class="p-4 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
      <div class="flex items-end space-x-2 bg-gray-50 dark:bg-gray-700 rounded-xl p-2 border border-gray-200 dark:border-gray-600 focus-within:ring-2 ring-blue-500/50 transition-all">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :autosize="{ minRows: 1, maxRows: 4 }"
          placeholder="发送消息..."
          resize="none"
          class="flex-1 !bg-transparent custom-input"
          @keyup.enter.exact.prevent="sendMessage"
        />
        <el-button 
          type="primary" 
          circle 
          :icon="Promotion" 
          :disabled="!inputMessage.trim() || !isConnected"
          @click="sendMessage"
          class="mb-0.5 shadow-lg hover:scale-105 transition-transform"
        />
      </div>
      <div class="text-[10px] text-gray-400 mt-2 text-right">
        Enter 发送
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Message Animation */
.message-enter-active,
.message-leave-active {
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.message-enter-from {
  opacity: 0;
  transform: scale(0.5) translateY(20px);
}

.message-leave-to {
  opacity: 0;
  transform: scale(0.5);
}

/* Custom Scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.5);
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(156, 163, 175, 0.8);
}

/* Element Plus Input Override */
:deep(.el-textarea__inner) {
  box-shadow: none !important;
  background-color: transparent !important;
  padding: 8px;
}
:deep(.el-textarea__inner:hover),
:deep(.el-textarea__inner:focus) {
  box-shadow: none !important;
}
</style>
