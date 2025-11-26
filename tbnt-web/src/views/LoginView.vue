<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { login, register, type LoginParams, type RegisterParams } from '@/api/user'
import { ElMessage } from 'element-plus'
import { User, Lock, Avatar, Phone } from '@element-plus/icons-vue'
import ThemeSwitch from '@/components/ThemeSwitch.vue'

const router = useRouter()
const authStore = useAuthStore()

const isLogin = ref(true)
const loading = ref(false)

const loginForm = reactive<LoginParams>({
  username: '',
  password: ''
})

const registerForm = reactive<RegisterParams>({
  username: '',
  password: '',
  nickname: '',
  phone: ''
})

const handleLogin = async () => {
  if (!loginForm.username || !loginForm.password) {
    ElMessage.warning('请填写所有必填项')
    return
  }

  loading.value = true
  try {
    const res = await login(loginForm)
    authStore.login(res.access_token, res.user)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!registerForm.username || !registerForm.password) {
    ElMessage.warning('请填写所有必填项')
    return
  }

  loading.value = true
  try {
    await register(registerForm)
    ElMessage.success('注册成功，请登录')
    isLogin.value = true
    // Pre-fill login
    loginForm.username = registerForm.username
    loginForm.password = ''
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const toggleMode = () => {
  isLogin.value = !isLogin.value
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden transition-colors duration-300 tech-bg">
    <!-- Animated Background Layers -->
    <div class="absolute inset-0 z-0 opacity-80 dark:opacity-60 bg-linear-to-r from-blue-100 via-purple-100 to-pink-100 dark:from-gray-900 dark:via-blue-900 dark:to-purple-900 animate-gradient-xy"></div>
    <div class="absolute inset-0 z-0 opacity-30 dark:opacity-20 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMSIgY3k9IjEiIHI9IjEiIGZpbGw9IiM4ODgiIG9wYWNpdHk9IjAuNSIvPjwvc3ZnPg==')] animate-pan"></div>

    <div class="absolute top-4 right-4 z-20">
      <ThemeSwitch />
    </div>

    <div class="max-w-md w-full p-8 rounded-2xl shadow-2xl z-10 backdrop-blur-md bg-white/70 dark:bg-gray-800/60 border border-white/20 dark:border-gray-700/50 transition-all duration-300 hover:shadow-blue-500/20 dark:hover:shadow-purple-500/20">
      <div class="text-center mb-8">
        <h1 class="text-4xl font-extrabold bg-clip-text text-transparent bg-linear-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400 mb-2 tracking-tight">
          TBNT
        </h1>
        <p class="text-xs font-bold uppercase tracking-[0.2em] text-gray-500 dark:text-gray-400 mb-6">
          996, Thanks... But No Thanks.
        </p>
        <h2 class="text-2xl font-bold text-gray-800 dark:text-white">
          {{ isLogin ? '欢迎回来' : '创建账号' }}
        </h2>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">
          {{ isLogin ? '请登录您的账号以继续' : '注册一个新账号以开始' }}
        </p>
      </div>

      <!-- Login Form -->
      <div v-if="isLogin" class="space-y-5">
        <el-input
          v-model="loginForm.username"
          placeholder="用户名"
          :prefix-icon="User"
          size="large"
          class="tech-input"
        />
        <el-input
          v-model="loginForm.password"
          type="password"
          placeholder="密码"
          :prefix-icon="Lock"
          size="large"
          show-password
          @keyup.enter="handleLogin"
          class="tech-input"
        />

        <el-button
          type="primary"
          class="w-full h-12! text-lg! rounded-lg shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 transition-all duration-300"
          :loading="loading"
          @click="handleLogin"
        >
          登录
        </el-button>
      </div>

      <!-- Register Form -->
      <div v-else class="space-y-5">
        <el-input
          v-model="registerForm.username"
          placeholder="用户名"
          :prefix-icon="User"
          size="large"
          class="tech-input"
        />
        <el-input
          v-model="registerForm.nickname"
          placeholder="昵称 (选填)"
          :prefix-icon="Avatar"
          size="large"
          class="tech-input"
        />
        <el-input
          v-model="registerForm.phone"
          placeholder="手机号 (选填)"
          :prefix-icon="Phone"
          size="large"
          class="tech-input"
        />
        <el-input
          v-model="registerForm.password"
          type="password"
          placeholder="密码"
          :prefix-icon="Lock"
          size="large"
          show-password
          class="tech-input"
        />

        <el-button
          type="success"
          class="w-full h-12! text-lg! rounded-lg shadow-lg shadow-green-500/30 hover:shadow-green-500/50 transition-all duration-300"
          :loading="loading"
          @click="handleRegister"
        >
          注册
        </el-button>
      </div>

      <div class="mt-8 text-center">
        <button
          @click="toggleMode"
          class="group relative inline-flex items-center justify-center px-6 py-2 overflow-hidden font-medium text-blue-600 transition duration-300 ease-out border-2 border-blue-500 rounded-full shadow-md group dark:text-blue-400 dark:border-blue-400"
        >
          <span class="absolute inset-0 flex items-center justify-center w-full h-full text-white duration-300 -translate-x-full bg-blue-500 group-hover:translate-x-0 ease">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
          </span>
          <span class="absolute flex items-center justify-center w-full h-full text-blue-500 dark:text-blue-400 transition-all duration-300 transform group-hover:translate-x-full ease">{{ isLogin ? "没有账号？去注册" : "已有账号？去登录" }}</span>
          <span class="relative invisible">{{ isLogin ? "没有账号？去注册" : "已有账号？去登录" }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-gradient-xy {
  background-size: 400% 400%;
  animation: gradient-xy 15s ease infinite;
}

.animate-pan {
  background-size: 20px 20px;
  animation: pan 60s linear infinite;
}

@keyframes gradient-xy {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

@keyframes pan {
  0% {
    background-position: 0% 0%;
  }
  100% {
    background-position: 100% 100%;
  }
}

/* Custom Input Styles for transparency */
:deep(.tech-input .el-input__wrapper) {
  background-color: rgba(255, 255, 255, 0.5) !important;
  backdrop-filter: blur(4px);
  box-shadow: none !important;
  border: 1px solid rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

:deep(.tech-input .el-input__wrapper.is-focus) {
  background-color: rgba(255, 255, 255, 0.9) !important;
  border-color: var(--el-color-primary);
  box-shadow: 0 0 0 1px var(--el-color-primary) !important;
}

.dark :deep(.tech-input .el-input__wrapper) {
  background-color: rgba(0, 0, 0, 0.2) !important;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.dark :deep(.tech-input .el-input__wrapper.is-focus) {
  background-color: rgba(0, 0, 0, 0.4) !important;
}

.dark :deep(.tech-input .el-input__inner) {
  color: #fff;
}
</style>
