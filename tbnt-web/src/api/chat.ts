import request from '@/utils/request'
import type { ChatMessage } from '@/stores/chat'

export const uploadImage = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post<{ url: string }>('/chat/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const getLobbyHistory = (skip: number = 0, limit: number = 50) => {
  return request.get<ChatMessage[]>(`/chat/history?skip=${skip}&limit=${limit}`)
}

export const getPrivateHistory = (friendId: number, skip: number = 0, limit: number = 50) => {
  return request.get<ChatMessage[]>(`/chat/private/history?friend_id=${friendId}&skip=${skip}&limit=${limit}`)
}

export const markMessagesAsRead = (friendId: number) => {
  return request.post<{ message: string }>(`/chat/private/read`, { friend_id: friendId })
}

export const getUnreadCounts = () => {
  return request.get<Record<number, number>>('/chat/unread')
}
