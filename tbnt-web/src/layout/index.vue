<script setup lang="ts">
import { ref } from 'vue'
import AppSidebar from './components/AppSidebar.vue'
import AppHeader from './components/AppHeader.vue'
import AppMain from './components/AppMain.vue'

const isCollapse = ref(false)

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}
</script>

<template>
  <div class="flex h-screen w-full bg-gray-100 dark:bg-gray-900 overflow-hidden">
    <!-- Sidebar -->
    <div class="h-full bg-gray-800 transition-all duration-300 shadow-xl z-20 shrink-0" :class="isCollapse ? 'w-[64px]' : 'w-[240px]'">
      <AppSidebar :is-collapse="isCollapse" />
    </div>

    <!-- Main Container -->
    <div class="flex-1 flex flex-col h-full overflow-hidden w-0">
      <!-- Header -->
      <AppHeader :is-collapse="isCollapse" @toggle-collapse="toggleCollapse" />

      <!-- Main Content -->
      <main class="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
        <AppMain />
      </main>
    </div>
  </div>
</template>
