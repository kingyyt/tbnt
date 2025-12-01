import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAuthStore } from './auth'
import { ElMessage } from 'element-plus'
import { markMessagesAsRead, getUnreadCounts } from '@/api/chat'

export interface ChatMessage {
  id: number
  content: string
  message_type: string
  user_id: number
  created_at: string
  is_read?: boolean
  to_user_id?: number | null
  sender?: {
    id: number
    username: string
    nickname: string
    avatar: string | null
    chat_color?: string
    number?: number
  }
}

export const useChatStore = defineStore('chat', () => {
  const authStore = useAuthStore()
  const ws = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const reconnectTimer = ref<number | null>(null)

  // Messages
  const lobbyMessages = ref<ChatMessage[]>([])
  const privateMessages = ref<Record<number, ChatMessage[]>>({})

  // Unread Counts
  const unreadCounts = ref<Record<number, number>>({})
  const activeChatId = ref<number | null>(null)
  const totalUnreadCount = computed(() => {
    return Object.values(unreadCounts.value).reduce((a, b) => a + b, 0)
  })

  const fetchUnreadCounts = async () => {
    if (!authStore.token) return
    try {
      const counts = await getUnreadCounts()
      unreadCounts.value = counts
    } catch (error) {
      console.error('Failed to fetch unread counts', error)
    }
  }

  const connect = () => {
    if (!authStore.token || isConnected.value) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//localhost:8000/api/v1/chat/ws/${authStore.token}`

    ws.value = new WebSocket(wsUrl)

    ws.value.onopen = () => {
      isConnected.value = true
      console.log('Connected to chat server')
      // Clear reconnect timer if successful
      if (reconnectTimer.value) {
        clearTimeout(reconnectTimer.value)
        reconnectTimer.value = null
      }
      // Fetch unread counts
      fetchUnreadCounts()
    }

    ws.value.onmessage = (event) => {
      try {
        const message: ChatMessage = JSON.parse(event.data)
        handleIncomingMessage(message)
      } catch (e) {
        console.error('Failed to parse message', e)
      }
    }

    ws.value.onclose = () => {
      isConnected.value = false
      console.log('Disconnected from chat server')

      // Reconnect logic
      if (!reconnectTimer.value) {
        reconnectTimer.value = window.setTimeout(() => {
          console.log('Attempting to reconnect...')
          reconnectTimer.value = null
          connect()
        }, 3000)
      }
    }

    ws.value.onerror = (error) => {
      console.error('WebSocket error:', error)
      ws.value?.close()
    }
  }

  const disconnect = () => {
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
    if (reconnectTimer.value) {
      clearTimeout(reconnectTimer.value)
      reconnectTimer.value = null
    }
    isConnected.value = false
  }

  const handleIncomingMessage = (message: ChatMessage) => {
    const currentUserId = authStore.user?.id

    // 1. Private Message
    if (message.to_user_id || (message.user_id === currentUserId && message.to_user_id !== null)) {
        // Determine the "other" person in the conversation
        let otherId: number

        if (message.user_id === currentUserId) {
            // Sent by me
            otherId = message.to_user_id!
        } else {
            // Received from someone
            otherId = message.user_id
        }

        // Initialize array if needed
        if (!privateMessages.value[otherId]) {
            privateMessages.value[otherId] = []
        }

        const chatList = privateMessages.value[otherId]
        // Check for duplicates (simple check by ID)
        if (chatList && !chatList.some(m => m.id === message.id)) {
            chatList.push(message)
        }

        // Increment unread if it's from someone else
        if (message.user_id !== currentUserId) {
            // Only increment if we are NOT currently viewing this chat
            if (activeChatId.value !== otherId) {
              const currentCount = unreadCounts.value[otherId] || 0
              unreadCounts.value[otherId] = currentCount + 1
            }
        }
    }
    // 2. Lobby Message
    else {
        if (!lobbyMessages.value.some(m => m.id === message.id)) {
            lobbyMessages.value.push(message)
        }
    }
  }

  const sendMessage = (content: string, type: string = 'text', toUserId?: number) => {
    if (!ws.value || ws.value.readyState !== WebSocket.OPEN) {
        ElMessage.warning('聊天服务未连接')
        return
    }

    const payload = {
      content,
      type,
      to_user_id: toUserId
    }

    ws.value.send(JSON.stringify(payload))
  }

  const markAsRead = async (friendId: number) => {
      if (unreadCounts.value[friendId]) {
          unreadCounts.value[friendId] = 0
      }
      // Notify backend
      try {
        await markMessagesAsRead(friendId)
      } catch (error) {
        console.error('Failed to mark messages as read', error)
      }
  }

  const setPrivateHistory = (friendId: number, messages: ChatMessage[]) => {
      privateMessages.value[friendId] = messages
  }

  const setLobbyHistory = (messages: ChatMessage[]) => {
      lobbyMessages.value = messages
  }

  const prependLobbyHistory = (messages: ChatMessage[]) => {
      lobbyMessages.value = [...messages, ...lobbyMessages.value]
  }

  const prependPrivateHistory = (friendId: number, messages: ChatMessage[]) => {
      if (!privateMessages.value[friendId]) {
          privateMessages.value[friendId] = []
      }
      privateMessages.value[friendId] = [...messages, ...privateMessages.value[friendId]]
  }

  const setUnreadCounts = (counts: Record<number, number>) => {
    unreadCounts.value = { ...counts }
  }

  const setActiveChat = (friendId: number | null) => {
    activeChatId.value = friendId
    if (friendId) {
      markAsRead(friendId)
    }
  }

  return {
    ws,
    isConnected,
    lobbyMessages,
    privateMessages,
    unreadCounts,
    totalUnreadCount,
    activeChatId,
    connect,
    disconnect,
    sendMessage,
    markAsRead,
    setActiveChat,
    setUnreadCounts,
    setPrivateHistory,
    setLobbyHistory,
    prependLobbyHistory,
    prependPrivateHistory,
    fetchUnreadCounts
  }
})
