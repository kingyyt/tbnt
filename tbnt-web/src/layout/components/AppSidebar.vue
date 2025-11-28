<script setup lang="ts">
import { useRoute } from 'vue-router'
import {
  Odometer,
  Setting,
  Calendar,
  ChatDotRound
} from '@element-plus/icons-vue'
import { computed } from 'vue'

const props = defineProps<{
  isCollapse: boolean
}>()

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<template>
  <el-menu
    :default-active="activeMenu"
    class="el-menu-vertical-demo min-h-screen border-r-0"
    :collapse="isCollapse"
    background-color="#1f2937"
    text-color="#9ca3af"
    active-text-color="#3b82f6"
    :collapse-transition="true"
    router
  >
    <div class="flex items-center justify-center h-16 bg-gray-900 text-white font-bold text-xl overflow-hidden whitespace-nowrap">
      <span v-if="!isCollapse" class="transition-opacity duration-300">TBNT</span>
      <span v-else class="text-blue-500">T</span>
    </div>

    <el-menu-item index="/">
      <el-icon><Odometer /></el-icon>
      <template #title>仪表盘</template>
    </el-menu-item>

    <el-menu-item index="/history">
      <el-icon><Calendar /></el-icon>
      <template #title>工作记录</template>
    </el-menu-item>

    <el-menu-item index="/settings">
      <el-icon><Setting /></el-icon>
      <template #title>工作配置</template>
    </el-menu-item>

    <el-menu-item index="/lobby">
      <el-icon><ChatDotRound /></el-icon>
      <template #title>大厅</template>
    </el-menu-item>
  </el-menu>
</template>

<style scoped>
.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 240px;
}
</style>
