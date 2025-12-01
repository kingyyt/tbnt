import request from '@/utils/request'

export interface UserInfo {
  id: number
  username: string
  nickname: string
  avatar?: string
  chat_color?: string
  number: number
}

export interface FriendRequest {
  id: number
  user_id: number
  friend_id: number
  status: number // 0: Pending
  created_at: string
  friend_info: UserInfo
}

export interface Friend {
  id: number
  user_id: number
  friend_id: number
  status: number // 1: Accepted
  created_at: string
  friend_info: UserInfo
  unread_count?: number
}

export const getFriends = () => {
  return request.get<Friend[]>('/friends/')
}

export const getFriendRequests = () => {
  return request.get<FriendRequest[]>('/friends/requests')
}

export const sendFriendRequest = (targetNumber: number) => {
  return request.post<{ message: string }>('/friends/request', { target_number: targetNumber })
}

export const respondFriendRequest = (requestId: number, status: number) => {
  return request.put<{ message: string }>(`/friends/${requestId}`, { status })
}

export const deleteFriend = (friendId: number) => {
  return request.delete<{ message: string }>(`/friends/${friendId}`)
}
