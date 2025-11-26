import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export interface User {
  id: number
  username: string
  nickname: string | null
  avatar: string | null
  phone: string | null
  role_level: number
  is_active: boolean
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const user = ref<User | null>(null)
  const router = useRouter()

  const login = (accessToken: string, userInfo: User) => {
    token.value = accessToken
    user.value = userInfo
  }

  const logout = () => {
    token.value = null
    user.value = null
    // Redirect handled in component or router usually, but resetting state here
  }

  return { token, user, login, logout }
}, {
  persist: true
})
