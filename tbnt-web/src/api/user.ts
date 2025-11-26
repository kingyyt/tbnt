import request from '@/utils/request'
import type { User } from '@/stores/auth'

export interface LoginParams {
  username: string
  password: string
}

export interface RegisterParams {
  username: string
  password: string
  nickname?: string
  avatar?: string
  phone?: string
  role_level?: number
}

interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export const login = (data: LoginParams) => {
  // Use URLSearchParams for application/x-www-form-urlencoded
  const params = new URLSearchParams()
  params.append('username', data.username)
  params.append('password', data.password)

  return request.post<LoginResponse>('/auth/login', params, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

export const register = (data: RegisterParams) => {
  return request.post<User>('/auth/register', data)
}

export const getMe = () => {
  return request.get<User>('/auth/me')
}

export const updateProfile = (data: { nickname: string; avatar?: string; phone?: string }) => {
  return request.put<User>('/auth/profile', data)
}

export const updatePassword = (data: { old_password: string; new_password: string }) => {
  return request.put<{ message: string }>('/auth/password', data)
}

export const uploadAvatar = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post<{ url: string }>('/auth/upload-avatar', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
