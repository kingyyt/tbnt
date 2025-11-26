<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import {
  Fold,
  Expand,
  FullScreen,
  SwitchButton
} from '@element-plus/icons-vue'
import ThemeSwitch from '@/components/ThemeSwitch.vue'
import { useFullscreen } from '@vueuse/core'

defineProps<{
  isCollapse: boolean
}>()

const emit = defineEmits<{
  (e: 'toggleCollapse'): void
}>()

const authStore = useAuthStore()
const router = useRouter()
const { toggle } = useFullscreen()

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="h-16 bg-white dark:bg-gray-800 shadow-sm flex items-center justify-between px-4 transition-colors duration-300">
    <!-- Left: Collapse Button -->
    <div class="flex items-center">
      <el-button
        link
        @click="emit('toggleCollapse')"
        class="text-gray-600 dark:text-gray-300 hover:text-blue-500 dark:hover:text-blue-400 text-xl!"
      >
        <el-icon>
          <Expand v-if="isCollapse" />
          <Fold v-else />
        </el-icon>
      </el-button>

      <!-- Breadcrumb could go here -->
    </div>

    <!-- Right: Tools -->
    <div class="flex items-center space-x-4">
      <!-- Fullscreen Toggle -->
      <el-button
        circle
        text
        @click="toggle"
        class="text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
      >
        <el-icon :size="20"><FullScreen /></el-icon>
      </el-button>

      <!-- Theme Switch -->
      <ThemeSwitch />

      <!-- User Profile -->
      <div class="flex items-center space-x-2 text-gray-700 dark:text-gray-200 ml-2">
        <el-avatar :size="32" :src="authStore.user?.avatar || ''" class="bg-blue-100 text-blue-600">
          {{ authStore.user?.username?.charAt(0).toUpperCase() }}
        </el-avatar>
        <span class="hidden md:inline font-medium text-sm">{{ authStore.user?.nickname || authStore.user?.username }}</span>
      </div>

      <!-- Logout -->
      <el-button circle :icon="SwitchButton" type="danger" plain @click="handleLogout" title="退出登录" size="small" />
    </div>
  </div>
</template>
