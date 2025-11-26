import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

// Define the response structure
interface ApiResponse<T = any> {
  code: number
  data: T
  message: string
}

class Request {
  private instance: AxiosInstance

  constructor(config: AxiosRequestConfig) {
    this.instance = axios.create(config)

    // Request interceptor
    this.instance.interceptors.request.use(
      (config) => {
        const authStore = useAuthStore()
        if (authStore.token) {
          config.headers.Authorization = `Bearer ${authStore.token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        // Direct return data for now, as FastAPI standard return might be just JSON
        // If your API wraps everything in code/data/message, uncomment the logic below
        return response.data
        
        // const { code, message, data } = response.data
        // // Assuming 200 is success code, adjust based on your API
        // if (code === 200) {
        //   return data
        // } else {
        //   ElMessage.error(message || 'Error')
        //   return Promise.reject(new Error(message || 'Error'))
        // }
      },
      (error) => {
        let message = ''
        if (error.response) {
            // Get error detail from FastAPI
            const detail = error.response.data?.detail
            
          switch (error.response.status) {
            case 401:
              message = detail || 'Unauthorized, please login again'
              const authStore = useAuthStore()
              authStore.logout()
              break
            case 403:
              message = detail || 'Forbidden'
              break
            case 404:
              message = detail || 'Resource not found'
              break
            case 500:
              message = detail || 'Internal server error'
              break
            default:
              message = detail || `Error: ${error.response.status}`
          }
        } else {
          message = 'Network error'
        }
        ElMessage.error(message)
        return Promise.reject(error)
      }
    )
  }

  request<T = any>(config: AxiosRequestConfig): Promise<T> {
    return this.instance.request(config)
  }

  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.get(url, config)
  }

  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.post(url, data, config)
  }

  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.put(url, data, config)
  }

  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.delete(url, config)
  }
}

const request = new Request({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export default request
