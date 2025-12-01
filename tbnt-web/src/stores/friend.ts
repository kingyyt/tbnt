import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'
import { useChatStore } from './chat'
import {
  getFriends,
  getFriendRequests,
  sendFriendRequest,
  respondFriendRequest,
  deleteFriend as apiDeleteFriend,
  type Friend,
  type FriendRequest
} from '@/api/friend'

export const useFriendStore = defineStore('friend', () => {
  const authStore = useAuthStore()
  const chatStore = useChatStore()
  const friends = ref<Friend[]>([])
  const requests = ref<FriendRequest[]>([])
  const isLoading = ref(false)

  // Fetch friends list
  const fetchFriends = async () => {
    if (!authStore.token) return
    try {
      const data = await getFriends()
      friends.value = data

      // Sync unread counts (only if provided by backend)
      const counts: Record<number, number> = {}
      let hasUnreadData = false

      data.forEach(f => {
        if (f.unread_count !== undefined && f.unread_count !== null) {
          counts[f.friend_info.id] = f.unread_count
          hasUnreadData = true
        }
      })

      if (hasUnreadData) {
        chatStore.setUnreadCounts(counts)
      }
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (error: any) {
      console.error('Failed to fetch friends', error)
    }
  }

  // Fetch pending requests
  const fetchRequests = async () => {
    if (!authStore.token) return
    try {
      const data = await getFriendRequests()
      requests.value = data
    } catch (error) {
      console.error('Failed to fetch friend requests', error)
    }
  }

  // Send friend request
  const sendRequest = async (targetNumber: number) => {
    if (!authStore.token) return
    try {
      await sendFriendRequest(targetNumber)
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (error: any) {
       // Re-throw properly or handle
       throw new Error(error.message || 'Failed to send request')
    }
  }

  // Respond to request
  const respondRequest = async (requestId: number, status: number) => {
    if (!authStore.token) return
    try {
      await respondFriendRequest(requestId, status)
      // Remove from requests
      requests.value = requests.value.filter(r => r.id !== requestId)
      // If accepted, refresh friends list
      if (status === 1) {
        fetchFriends()
      }
      return true
    } catch (error) {
      console.error(error)
      return false
    }
  }

  // Delete friend
  const deleteFriend = async (friendId: number) => {
     if (!authStore.token) return
     try {
         await apiDeleteFriend(friendId)
         friends.value = friends.value.filter(f => f.friend_info.id !== friendId)
     } catch (error) {
         console.error(error)
         throw error
     }
  }

  return {
    friends,
    requests,
    isLoading,
    fetchFriends,
    fetchRequests,
    sendRequest,
    respondRequest,
    deleteFriend
  }
})
