<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import type { User } from '@/stores/auth'
import { getImageUrl } from '@/utils/image'
import { Plus, ChatDotRound } from '@element-plus/icons-vue'

defineProps<{
  visible: boolean
  x: number
  y: number
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  user: User | any
  isFriend: boolean
}>()

const emit = defineEmits(['update:visible', 'addFriend', 'sendMessage'])

const menuRef = ref<HTMLElement | null>(null)

const handleClickOutside = (event: MouseEvent) => {
  if (menuRef.value && !menuRef.value.contains(event.target as Node)) {
    emit('update:visible', false)
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('contextmenu', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('contextmenu', handleClickOutside)
})
</script>

<template>
  <Transition name="scale">
    <div
      v-if="visible"
      ref="menuRef"
      class="fixed z-50 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden min-w-[220px] p-4 flex flex-col items-center gap-3"
      :style="{ top: `${y}px`, left: `${x}px` }"
      @click.stop
    >
      <!-- User Info Header -->
      <div class="flex flex-col items-center w-full pb-3 border-b border-gray-100 dark:border-gray-700">
        <div class="relative mb-2">
            <el-avatar
                :size="60"
                :src="getImageUrl(user?.avatar)"
                class="shadow-md"
            >
                {{ user?.nickname?.charAt(0) || user?.username?.charAt(0) }}
            </el-avatar>
            <div class="absolute bottom-0 right-0 w-4 h-4 bg-green-500 border-2 border-white dark:border-gray-800 rounded-full"></div>
        </div>
        <h3 class="text-lg font-bold text-gray-800 dark:text-white">{{ user?.nickname || user?.username }}</h3>
        <div class="flex items-center gap-1 text-xs text-gray-500 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded-full mt-1">
            <span>ID:</span>
            <span class="font-mono font-medium text-blue-500">{{ user?.number || 'Unknown' }}</span>
        </div>
      </div>

      <!-- Actions -->
      <div class="w-full flex flex-col gap-2">
        <button
            v-if="!isFriend"
            class="w-full py-2 px-4 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
            @click="$emit('addFriend', user)"
        >
            <el-icon><Plus /></el-icon>
            添加好友
        </button>

        <button
            v-else
            class="w-full py-2 px-4 bg-green-500 hover:bg-green-600 text-white rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
            @click="$emit('sendMessage', user)"
        >
            <el-icon><ChatDotRound /></el-icon>
            发送消息
        </button>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.scale-enter-active,
.scale-leave-active {
  transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.scale-enter-from,
.scale-leave-to {
  opacity: 0;
  transform: scale(0.8);
}
</style>
