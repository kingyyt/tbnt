<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { Promotion, Picture } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const messages = ref<any[]>([])
const inputMessage = ref('')
const ws = ref<WebSocket | null>(null)
const messagesContainer = ref<HTMLElement | null>(null)
const isConnected = ref(false)
const isLoadingHistory = ref(false)
const hasMoreHistory = ref(true)
const pageSize = 50

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

const sendMessage = (content: string, type: string = 'text') => {
  if (!ws.value || ws.value.readyState !== WebSocket.OPEN) return

  const payload = JSON.stringify({
    content: content,
    type: type
  })

  ws.value.send(payload)

  if (type === 'text') {
    inputMessage.value = ''
  }
}

const sendTextMessage = () => {
  if (!inputMessage.value.trim()) return
  sendMessage(inputMessage.value, 'text')
}

const handleImageUpload = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)

  try {
    const res = await fetch('http://localhost:8000/api/v1/chat/upload', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      },
      body: formData
    })

    if (!res.ok) throw new Error('Upload failed')

    const data = await res.json()
    if (data.url) {
      sendMessage(data.url, 'image')
    }
  } catch (error) {
    ElMessage.error('图片上传失败')
    console.error(error)
  }
  return false // Prevent default upload behavior
}

const fetchHistory = async (isLoadMore = false) => {
  if (isLoadingHistory.value || (!hasMoreHistory.value && isLoadMore)) return

  isLoadingHistory.value = true
  try {
    const skip = isLoadMore ? messages.value.length : 0
    const res = await fetch(`http://localhost:8000/api/v1/chat/history?skip=${skip}&limit=${pageSize}`, {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    const data = await res.json()
    if (Array.isArray(data)) {
      if (data.length < pageSize) {
        hasMoreHistory.value = false
      }

      if (isLoadMore) {
        // Prepend messages
        const currentScrollHeight = messagesContainer.value?.scrollHeight || 0
        messages.value = [...data, ...messages.value]

        // Restore scroll position
        await nextTick()
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight - currentScrollHeight
        }
      } else {
        messages.value = data
        scrollToBottom()
      }
    }
  } catch (error) {
    console.error('Failed to fetch history', error)
  } finally {
    isLoadingHistory.value = false
  }
}

const handleScroll = () => {
  if (!messagesContainer.value) return

  if (messagesContainer.value.scrollTop === 0 && hasMoreHistory.value && !isLoadingHistory.value) {
    fetchHistory(true)
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
      class="flex-1 overflow-y-auto overflow-x-hidden p-4 space-y-4 custom-scrollbar bg-gray-100 dark:bg-gray-900"
      @scroll="handleScroll"
    >
      <div v-if="isLoadingHistory" class="text-center py-2 text-gray-400 text-xs">
        加载中...
      </div>

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
            <div class="text-xs text-gray-500 mb-1 px-1 flex items-center gap-1">
              <span>{{ msg.sender?.nickname || msg.sender?.username }}</span>
            </div>

            <div
              v-if="msg.message_type === 'text' || !msg.message_type"
              class="p-3 rounded-2xl shadow-sm text-sm break-all whitespace-pre-wrap relative transition-all duration-300 transform"
              :style="{
                backgroundColor: msg.sender?.chat_color || '#3b82f6',
                color: getContrastColor(msg.sender?.chat_color || '#3b82f6')
              }"
              :class="msg.user_id === authStore.user?.id ? 'rounded-tr-sm' : 'rounded-tl-sm'"
            >
              {{ msg.content }}
            </div>

            <div
              v-else-if="msg.message_type === 'image'"
              class="rounded-xl overflow-hidden shadow-sm border border-gray-200 dark:border-gray-700"
            >
              <el-image
                :src="msg.content.startsWith('/') ? `http://localhost:8000${msg.content}` : msg.content"
                :preview-src-list="[msg.content.startsWith('/') ? `http://localhost:8000${msg.content}` : msg.content]"
                fit="cover"
                class="max-w-[200px] max-h-[200px]"
              />
            </div>

            <div class="text-[10px] text-gray-400 mt-1 px-1">
              {{ new Date(msg.created_at).toLocaleTimeString() }}
            </div>
          </div>

          <!-- Current User Avatar -->
          <el-avatar
            v-if="msg.user_id === authStore.user?.id"
            :size="36"
            :src="authStore.user?.avatar ? `http://localhost:8000${authStore.user.avatar}` : ''"
            class="ml-2 flex-shrink-0"
          >
            {{ authStore.user?.nickname?.charAt(0) || authStore.user?.username?.charAt(0) }}
          </el-avatar>
        </div>
      </TransitionGroup>
    </div>

    <!-- Input Area -->
    <div class="p-4 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
      <div class="flex items-end space-x-2 bg-gray-50 dark:bg-gray-700 rounded-xl p-2 border border-gray-200 dark:border-gray-600 focus-within:ring-2 ring-blue-500/50 transition-all">
        <!-- Image Upload -->
        <el-upload
          class="upload-demo flex items-center justify-center"
          action="#"
          :show-file-list="false"
          :before-upload="handleImageUpload"
          accept="image/*"
        >
          <el-button
            circle
            :icon="Picture"
            class="!border-none !bg-transparent text-gray-500 hover:text-blue-500"
          />
        </el-upload>

        <el-input
          v-model="inputMessage"
          type="textarea"
          :autosize="{ minRows: 1, maxRows: 4 }"
          placeholder="发送消息..."
          resize="none"
          class="flex-1 !bg-transparent custom-input"
          @keyup.enter.exact.prevent="sendTextMessage"
        />
        <el-button
          type="primary"
          circle
          :icon="Promotion"
          :disabled="!inputMessage.trim() || !isConnected"
          @click="sendTextMessage"
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
