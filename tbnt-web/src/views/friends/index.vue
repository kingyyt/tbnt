<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useFriendStore } from '@/stores/friend'
import { useChatStore } from '@/stores/chat'
import { Promotion, Picture, Search, MoreFilled, Delete, ChatDotRound, Check, Close } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute } from 'vue-router'

import { uploadImage, getPrivateHistory } from '@/api/chat'
import { getImageUrl } from '@/utils/image'

defineOptions({
  name: 'FriendsView'
})

const route = useRoute()
const authStore = useAuthStore()
const friendStore = useFriendStore()
const chatStore = useChatStore()

// State
const activeFriendId = ref<number | null>(null)
const inputMessage = ref('')
const messagesContainer = ref<HTMLElement | null>(null)
const isLoadingHistory = ref(false)
const hasMoreHistory = ref(true)
const pageSize = 50
const searchQuery = ref('')

// Computed
const filteredFriends = computed(() => {
  if (!searchQuery.value) return friendStore.friends
  const query = searchQuery.value.toLowerCase()
  return friendStore.friends.filter(f =>
    f.friend_info.username.toLowerCase().includes(query) ||
    f.friend_info.nickname?.toLowerCase().includes(query)
  )
})

const activeFriend = computed(() => {
  return friendStore.friends.find(f => f.friend_info.id === activeFriendId.value)
})

const currentMessages = computed(() => {
    if (!activeFriendId.value) return []
    return chatStore.privateMessages[activeFriendId.value] || []
})

// Contrast Color Helper (Same as Lobby)
const getContrastColor = (hexcolor: string) => {
  if (!hexcolor) return 'black'
  hexcolor = hexcolor.replace('#', '')
  const r = parseInt(hexcolor.substring(0, 2), 16)
  const g = parseInt(hexcolor.substring(2, 2), 16)
  const b = parseInt(hexcolor.substring(4, 2), 16)
  const yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000
  return yiq >= 128 ? 'black' : 'white'
}

// Chat Logic
const selectFriend = async (friendId: number) => {
  if (activeFriendId.value === friendId) return
  activeFriendId.value = friendId
  hasMoreHistory.value = true

  // Set active chat in store
  chatStore.setActiveChat(friendId)

  // If no messages loaded, fetch history
  if (!chatStore.privateMessages[friendId] || chatStore.privateMessages[friendId].length === 0) {
      await fetchHistory()
  }

  scrollToBottom()
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const fetchHistory = async (isLoadMore = false) => {
  if (!activeFriendId.value || isLoadingHistory.value || (!hasMoreHistory.value && isLoadMore)) return

  isLoadingHistory.value = true
  try {
    const currentMsgs = chatStore.privateMessages[activeFriendId.value] || []
    const skip = isLoadMore ? currentMsgs.length : 0
    const data = await getPrivateHistory(activeFriendId.value, skip, pageSize)

    if (Array.isArray(data)) {
      if (data.length < pageSize) {
        hasMoreHistory.value = false
      }

      if (isLoadMore) {
        const currentScrollHeight = messagesContainer.value?.scrollHeight || 0
        chatStore.prependPrivateHistory(activeFriendId.value, data)
        await nextTick()
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight - currentScrollHeight
        }
      } else {
        chatStore.setPrivateHistory(activeFriendId.value, data)
        scrollToBottom()
      }
    }
  } catch (error) {
    console.error('Failed to fetch history', error)
  } finally {
    isLoadingHistory.value = false
  }
}

const sendMessage = (content: string, type: string = 'text') => {
  if (!activeFriendId.value) return

  chatStore.sendMessage(content, type, activeFriendId.value)

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
    console.error(error)
    ElMessage.error('图片上传失败')
  }
  return false
}

const handleScroll = () => {
  if (!messagesContainer.value) return
  if (messagesContainer.value.scrollTop === 0 && hasMoreHistory.value && !isLoadingHistory.value) {
    fetchHistory(true)
  }
}

const handleDeleteFriend = async (friendId: number, nickname: string) => {
  try {
    await ElMessageBox.confirm(`确定要删除好友 ${nickname} 吗?`, '删除好友', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await friendStore.deleteFriend(friendId)
    if (activeFriendId.value === friendId) {
      activeFriendId.value = null
      // Clear messages from store? Maybe keep them for cache but UI clears
    }
    ElMessage.success('好友已删除')
  } catch {
    // Cancelled
  }
}

// Watch for new messages to scroll to bottom
watch(() => (activeFriendId.value ? chatStore.privateMessages[activeFriendId.value]?.length : 0), (newLen: number | undefined, oldLen: number | undefined) => {
    if ((newLen || 0) > (oldLen || 0)) {
         // Simple logic: if new message added, scroll to bottom
         // Similar to LobbyView logic
        const isAtBottom = messagesContainer.value ?
            (messagesContainer.value.scrollHeight - messagesContainer.value.scrollTop - messagesContainer.value.clientHeight < 50)
            : false

        if (isAtBottom || (newLen || 0) - (oldLen || 0) === 1) {
             scrollToBottom()
        }
    }
})

// Lifecycle
onMounted(async () => {
  await friendStore.fetchFriends()

  // Ensure connected
  if (!chatStore.isConnected) {
      chatStore.connect()
  }

  // Check query param for initial friend selection
  const queryUserId = route.query.userId
  if (queryUserId) {
    const friend = friendStore.friends.find(f => f.friend_info.id === Number(queryUserId))
    if (friend) {
      selectFriend(friend.friend_info.id)
    }
  }
})

onUnmounted(() => {
  chatStore.setActiveChat(null)
})
</script>

<template>
  <div class="h-[calc(100vh-100px)] flex bg-gray-50 dark:bg-gray-900 rounded-xl overflow-hidden shadow-lg border border-gray-200 dark:border-gray-700">

    <!-- Left: Chat Area -->
    <div class="flex-1 flex flex-col min-w-0 bg-white dark:bg-gray-800 relative">
      <template v-if="activeFriend">
        <!-- Chat Header -->
        <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center shadow-sm z-10">
          <div class="flex items-center space-x-3">
             <el-avatar :size="40" :src="activeFriend.friend_info.avatar ? `http://localhost:8000${activeFriend.friend_info.avatar}` : ''">
                {{ activeFriend.friend_info.nickname?.charAt(0) || activeFriend.friend_info.username?.charAt(0) }}
             </el-avatar>
             <div>
               <div class="font-bold text-gray-800 dark:text-white">{{ activeFriend.friend_info.nickname || activeFriend.friend_info.username }}</div>
               <div class="text-xs text-gray-500">ID: {{ activeFriend.friend_info.number }}</div>
             </div>
          </div>
          <div class="flex items-center">
             <el-dropdown trigger="click">
               <el-button circle text>
                 <el-icon><MoreFilled /></el-icon>
               </el-button>
               <template #dropdown>
                 <el-dropdown-menu>
                   <el-dropdown-item @click="handleDeleteFriend(activeFriend.friend_info.id, activeFriend.friend_info.nickname || activeFriend.friend_info.username)" class="text-red-500">
                     <el-icon><Delete /></el-icon> 删除好友
                   </el-dropdown-item>
                 </el-dropdown-menu>
               </template>
             </el-dropdown>
          </div>
        </div>

        <!-- Messages -->
        <div
          ref="messagesContainer"
          class="flex-1 overflow-y-auto overflow-x-hidden p-4 space-y-4 custom-scrollbar bg-gray-50 dark:bg-gray-900"
          @scroll="handleScroll"
        >
          <div v-if="isLoadingHistory" class="text-center py-2 text-gray-400 text-xs">
            加载中...
          </div>

          <TransitionGroup name="message">
            <div
              v-for="msg in currentMessages"
              :key="msg.id"
              class="flex w-full"
              :class="msg.user_id === authStore.user?.id ? 'justify-end' : 'justify-start'"
            >
             <!-- Friend Avatar -->
            <el-avatar
              v-if="msg.user_id !== authStore.user?.id"
              :size="36"
              :src="getImageUrl(activeFriend.friend_info.avatar)"
              class="mr-2 shrink-0"
            >
              {{ activeFriend.friend_info.nickname?.charAt(0) || activeFriend.friend_info.username?.charAt(0) }}
            </el-avatar>

            <div class="flex flex-col max-w-[70%]" :class="msg.user_id === authStore.user?.id ? 'items-end' : 'items-start'">
              <div
                v-if="msg.message_type === 'text' || !msg.message_type"
                class="p-3 rounded-2xl shadow-sm text-sm break-all whitespace-pre-wrap relative transition-all duration-300 transform"
                :style="{
                  backgroundColor: msg.user_id === authStore.user?.id ? (authStore.user?.chat_color || '#3b82f6') : (activeFriend.friend_info.chat_color || '#e5e7eb'),
                  color: msg.user_id === authStore.user?.id ? getContrastColor(authStore.user?.chat_color || '#3b82f6') : getContrastColor(activeFriend.friend_info.chat_color || '#e5e7eb')
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

            <!-- My Avatar -->
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
            <el-upload
              class="upload-demo flex items-center justify-center"
              action="#"
              :show-file-list="false"
              :before-upload="handleImageUpload"
              accept="image/*"
            >
              <el-button circle :icon="Picture" class="border-none! bg-transparent! text-gray-500 hover:text-blue-500" />
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
        </div>
      </template>

      <div v-else class="flex-1 flex items-center justify-center text-gray-400 flex-col">
        <el-icon :size="64" class="mb-4 opacity-20"><ChatDotRound /></el-icon>
        <p>选择一个好友开始聊天</p>
      </div>
    </div>

    <!-- Right: Friend List -->
    <div class="w-72 border-l border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex flex-col">
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 class="font-bold text-gray-800 dark:text-white mb-3">我的好友</h3>
        <el-input
          v-model="searchQuery"
          placeholder="搜索好友..."
          :prefix-icon="Search"
          clearable
          size="small"
        />
      </div>

      <div class="flex-1 overflow-y-auto custom-scrollbar">
        <!-- Friend Requests Section -->
        <div v-if="friendStore.requests.length > 0" class="mb-2">
          <div class="px-4 py-2 text-xs font-bold text-gray-500 uppercase tracking-wider">
            新的朋友
          </div>
          <div
            v-for="req in friendStore.requests"
            :key="req.id"
            class="px-3 py-2 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <div class="flex items-center overflow-hidden">
              <el-avatar :size="32" :src="getImageUrl(req.friend_info.avatar)" class="shrink-0">
                {{ req.friend_info.nickname?.charAt(0) || req.friend_info.username?.charAt(0) }}
              </el-avatar>
              <div class="ml-2 truncate text-sm font-medium text-gray-700 dark:text-gray-300">
                {{ req.friend_info.nickname || req.friend_info.username }}
              </div>
            </div>
            <div class="flex space-x-1 shrink-0">
              <el-button type="success" size="small" circle class="p-1! h-6! w-6!" @click.stop="friendStore.respondRequest(req.id, 1)">
                <el-icon :size="12"><Check /></el-icon>
              </el-button>
              <el-button type="danger" size="small" circle class="p-1! h-6! w-6!" @click.stop="friendStore.respondRequest(req.id, 2)">
                <el-icon :size="12"><Close /></el-icon>
              </el-button>
            </div>
          </div>
          <div class="border-b border-gray-100 dark:border-gray-700 my-1"></div>
        </div>

        <div
          v-for="friend in filteredFriends"
          :key="friend.id"
          class="p-3 flex items-center cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors border-b border-gray-50 dark:border-gray-800"
          :class="activeFriendId === friend.friend_info.id ? 'bg-blue-50 dark:bg-gray-700 border-l-4 border-l-blue-500' : 'border-l-4 border-l-transparent'"
          @click="selectFriend(friend.friend_info.id)"
        >
          <div class="relative">
             <el-avatar :size="40" :src="getImageUrl(friend.friend_info.avatar)" class="shrink-0">
                {{ friend.friend_info.nickname?.charAt(0) || friend.friend_info.username?.charAt(0) }}
             </el-avatar>
             <div v-if="(chatStore.unreadCounts[friend.friend_info.id] || 0) > 0" class="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] px-1.5 py-0.5 rounded-full min-w-[18px] text-center border-2 border-white dark:border-gray-800">
                 {{ chatStore.unreadCounts[friend.friend_info.id] }}
             </div>
          </div>
          <div class="ml-3 overflow-hidden">
            <div class="font-medium text-gray-800 dark:text-gray-200 truncate">
              {{ friend.friend_info.nickname || friend.friend_info.username }}
            </div>
            <div class="text-xs text-gray-400 truncate">
              ID: {{ friend.friend_info.number }}
            </div>
          </div>
        </div>

        <div v-if="filteredFriends.length === 0" class="text-center text-gray-400 py-8 text-sm">
          {{ searchQuery ? '未找到相关好友' : '暂无好友' }}
        </div>
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
