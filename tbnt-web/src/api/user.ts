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

// Keep the old user methods if needed, but they seem to be for demo
export interface UserInfo {
  id: number
  name: string
  email: string
}

export const getUserInfo = (id: number) => {
  return request.get<UserInfo>(`/users/${id}`)
}

export const createUser = (data: Omit<UserInfo, 'id'>) => {
  return request.post<UserInfo>('/users', data)
}
