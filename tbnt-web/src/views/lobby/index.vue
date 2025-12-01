<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useAuthStore, type User } from '@/stores/auth'
import { useFriendStore } from '@/stores/friend'
import { useChatStore } from '@/stores/chat'
import { Promotion, Picture } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import UserContextMenu from '@/components/UserContextMenu.vue'
import { useRouter } from 'vue-router'
import { uploadImage, getLobbyHistory } from '@/api/chat'
import { getImageUrl } from '@/utils/image'

defineOptions({
  name: 'LobbyView'
})

const authStore = useAuthStore()
const friendStore = useFriendStore()
const chatStore = useChatStore()
const router = useRouter()

const inputMessage = ref('')
const messagesContainer = ref<HTMLElement | null>(null)
const isLoadingHistory = ref(false)
const hasMoreHistory = ref(true)
const pageSize = 50

const contextMenu = ref<{
  visible: boolean
  x: number
  y: number
  user: User | null
  isFriend: boolean
}>({
  visible: false,
  x: 0,
  y: 0,
  user: null,
  isFriend: false
})

// Contrast Color Helper
const getContrastColor = (hexcolor: string) => {
  if (!hexcolor) return 'black'
  // Remove # if present
  hexcolor = hexcolor.replace('#', '')
  const r = parseInt(hexcolor.substring(0, 2), 16)
  const g = parseInt(hexcolor.substring(2, 2), 16)
  const b = parseInt(hexcolor.substring(4, 2), 16)
  const yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000
  return yiq >= 128 ? 'black' : 'white'
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const handleContextMenu = (event: MouseEvent, user?: any) => {
  if (!user) return
  event.preventDefault()
  // Don't show for self
  if (user.id === authStore.user?.id) return

  // Check if already friend
  const isFriend = friendStore.friends.some(f => f.friend_info.id === user.id)

  contextMenu.value = {
    visible: true,
    x: event.clientX,
    y: event.clientY,
    user,
    isFriend
  }
}

const handleAddFriend = async (user: User) => {
  contextMenu.value.visible = false
  try {
    await ElMessageBox.confirm(`确定要添加 ${user.nickname || user.username} (ID: ${user.number}) 为好友吗?`, '添加好友', {
      confirmButtonText: '发送申请',
      cancelButtonText: '取消',
      type: 'info'
    })

    if (user.number !== undefined) {
      await friendStore.sendRequest(user.number)
      ElMessage.success('好友申请已发送')
    } else {
      ElMessage.error('无法获取用户ID')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const handlePrivateMessage = (user: User) => {
  contextMenu.value.visible = false
  router.push({ name: 'friends', query: { userId: user.id } })
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const sendMessage = (content: string, type: string = 'text') => {
  chatStore.sendMessage(content, type)
  if (type === 'text') {
    inputMessage.value = ''
  }
}

const sendTextMessage = () => {
  if (!inputMessage.value.trim()) return
  sendMessage(inputMessage.value, 'text')
}

const handleImageUpload = async (file: File) => {
  try {
    const data = await uploadImage(file)
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
    const skip = isLoadMore ? chatStore.lobbyMessages.length : 0
    const data = await getLobbyHistory(skip, pageSize)
    if (Array.isArray(data)) {
      if (data.length < pageSize) {
        hasMoreHistory.value = false
      }

      if (isLoadMore) {
        // Prepend messages
        const currentScrollHeight = messagesContainer.value?.scrollHeight || 0
        chatStore.prependLobbyHistory(data)

        // Restore scroll position
        await nextTick()
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight - currentScrollHeight
        }
      } else {
        chatStore.setLobbyHistory(data)
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

// Watch for new messages to scroll to bottom
watch(() => chatStore.lobbyMessages.length, (newLen, oldLen) => {
    // Only scroll to bottom if we added a new message (not loading history)
    // However, our fetchHistory handles scroll position for history loading.
    // So we should only scroll if it's an append (new message).
    // But simpler logic: if difference is 1 (one new message), scroll to bottom.
    // If we are at the bottom, stay at bottom.

    if (newLen > oldLen) {
        const isAtBottom = messagesContainer.value ?
            (messagesContainer.value.scrollHeight - messagesContainer.value.scrollTop - messagesContainer.value.clientHeight < 50)
            : false

        if (isAtBottom || newLen - oldLen === 1) {
             scrollToBottom()
        }
    }
})

onMounted(() => {
  // Ensure connected
  if (!chatStore.isConnected) {
      chatStore.connect()
  }

  if (chatStore.lobbyMessages.length === 0) {
      fetchHistory()
  } else {
      scrollToBottom()
  }
})

</script>

<template>
  <div class="h-[calc(100vh-100px)] flex flex-col bg-gray-50 dark:bg-gray-900 rounded-xl overflow-hidden shadow-lg border border-gray-200 dark:border-gray-700">
    <!-- Chat Header -->
    <div class="p-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center shadow-sm z-10">
      <h2 class="text-lg font-bold text-gray-800 dark:text-white flex items-center">
        <span class="w-2 h-2 rounded-full mr-2" :class="chatStore.isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'"></span>
        大厅聊天
      </h2>
      <span class="text-xs text-gray-500">{{ chatStore.isConnected ? '在线' : '离线' }}</span>
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
          v-for="msg in chatStore.lobbyMessages"
          :key="msg.id"
          class="flex w-full"
          :class="msg.user_id === authStore.user?.id ? 'justify-end' : 'justify-start'"
        >
          <!-- Other User Avatar -->
          <el-avatar
            v-if="msg.user_id !== authStore.user?.id"
            :size="36"
            :src="getImageUrl(msg.sender?.avatar)"
            class="mr-2 shrink-0 cursor-pointer hover:opacity-80 transition-opacity"
            @contextmenu.prevent.stop="handleContextMenu($event, msg.sender)"
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
                :src="getImageUrl(msg.content)"
                :preview-src-list="[getImageUrl(msg.content)]"
                fit="cover"
                class="max-w-[200px] max-h-[200px]"
                @load="scrollToBottom"
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
            :src="getImageUrl(authStore.user?.avatar)"
            class="ml-2 shrink-0"
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
            class="border-none! bg-transparent! text-gray-500 hover:text-blue-500"
          />
        </el-upload>

        <el-input
          v-model="inputMessage"
          type="textarea"
          :autosize="{ minRows: 1, maxRows: 4 }"
          placeholder="发送消息..."
          resize="none"
          class="flex-1 bg-transparent! custom-input"
          @keyup.enter.exact.prevent="sendTextMessage"
        />
        <el-button
          type="primary"
          circle
          :icon="Promotion"
          :disabled="!inputMessage.trim() || !chatStore.isConnected"
          @click="sendTextMessage"
          class="mb-0.5 shadow-lg hover:scale-105 transition-transform"
        />
      </div>
      <div class="text-[10px] text-gray-400 mt-2 text-right">
        Enter 发送
      </div>
    </div>

    <!-- User Context Menu -->
    <UserContextMenu
      v-model:visible="contextMenu.visible"
      :x="contextMenu.x"
      :y="contextMenu.y"
      :user="contextMenu.user"
      :is-friend="contextMenu.isFriend"
      @add-friend="handleAddFriend"
      @send-message="handlePrivateMessage"
    />
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
