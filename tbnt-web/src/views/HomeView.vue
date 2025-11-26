<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { getWorkSettings, getWorkItems, createWorkItem, deleteWorkItem, type WorkItem } from '@/api/work'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Checked, Memo } from '@element-plus/icons-vue'

const loading = ref(false)
const now = ref(new Date())
const timer = ref<number>()

// Work Data
const workSettings = ref({ start_time: '09:00', end_time: '18:00' })
const memos = ref<WorkItem[]>([])
const plans = ref<WorkItem[]>([])

// Forms
const newMemo = ref('')
const newPlan = ref('')

// Computed
const timeLeft = computed(() => {
  const parts = workSettings.value.end_time.split(':').map(Number)
  const endH = parts[0] || 0
  const endM = parts[1] || 0
  const endTime = new Date(now.value)
  endTime.setHours(endH, endM, 0)

  if (now.value > endTime) return '已下班'

  const diff = endTime.getTime() - now.value.getTime()
  const h = Math.floor(diff / (1000 * 60 * 60))
  const m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  const s = Math.floor((diff % (1000 * 60)) / 1000)

  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
})

const progressPercentage = computed(() => {
  const startParts = workSettings.value.start_time.split(':').map(Number)
  const startH = startParts[0] || 0
  const startM = startParts[1] || 0

  const endParts = workSettings.value.end_time.split(':').map(Number)
  const endH = endParts[0] || 0
  const endM = endParts[1] || 0

  const startTime = new Date(now.value)
  startTime.setHours(startH, startM, 0)

  const endTime = new Date(now.value)
  endTime.setHours(endH, endM, 0)

  const total = endTime.getTime() - startTime.getTime()
  const current = now.value.getTime() - startTime.getTime()

  if (current <= 0) return 0
  if (current >= total) return 100

  return Math.floor((current / total) * 100)
})

// Actions
const fetchData = async () => {
  loading.value = true
  try {
    const settings = await getWorkSettings()
    workSettings.value = { start_time: settings.start_time, end_time: settings.end_time }

    const items = await getWorkItems()
    memos.value = items.filter(i => i.type === 'memo')
    plans.value = items.filter(i => i.type === 'plan')
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const addMemo = async () => {
  if (!newMemo.value.trim()) return
  try {
    const item = await createWorkItem({ type: 'memo', content: newMemo.value })
    memos.value.push(item)
    newMemo.value = ''
    ElMessage.success('添加成功')
  } catch (error) {
    console.error(error)
  }
}

const addPlan = async () => {
  if (!newPlan.value.trim()) return
  try {
    const item = await createWorkItem({ type: 'plan', content: newPlan.value, status: 'pending' })
    plans.value.push(item)
    newPlan.value = ''
    ElMessage.success('添加成功')
  } catch (error) {
    console.error(error)
  }
}

const removeWorkItem = async (id: number, type: 'memo' | 'plan') => {
  try {
    await ElMessageBox.confirm('确定删除吗？', '提示', { type: 'warning' })
    await deleteWorkItem(id)
    if (type === 'memo') {
      memos.value = memos.value.filter(i => i.id !== id)
    } else {
      plans.value = plans.value.filter(i => i.id !== id)
    }
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

onMounted(() => {
  fetchData()
  timer.value = window.setInterval(() => {
    now.value = new Date()
  }, 1000)
})

onUnmounted(() => {
  clearInterval(timer.value)
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header Banner -->
    <div class="bg-linear-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white shadow-lg relative overflow-hidden">
      <div class="relative z-10">
        <h1 class="text-4xl font-bold mb-2">996, Thanks... But No Thanks.</h1>
        <p class="text-xl opacity-90">996，谢谢你……但还是算了吧。</p>
        <div class="mt-6 flex items-center space-x-4">
          <div class="bg-white/20 backdrop-blur-sm rounded-lg p-3">
            <p class="text-sm opacity-80">下班倒计时</p>
            <p class="text-3xl font-mono font-bold">{{ timeLeft }}</p>
          </div>
          <div class="flex-1 max-w-xs">
             <p class="text-sm opacity-80 mb-1">今日进度</p>
             <el-progress :percentage="progressPercentage" :stroke-width="15" striped striped-flow status="success" :text-inside="true" />
          </div>
        </div>
      </div>
      <!-- Decorative circle -->
      <div class="absolute -right-10 -bottom-10 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Memos -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-gray-800 dark:text-white flex items-center">
            <el-icon class="mr-2"><Memo /></el-icon> 工作备忘录
          </h3>
        </div>

        <div class="flex space-x-2 mb-4">
          <el-input v-model="newMemo" placeholder="添加新备忘..." @keyup.enter="addMemo" />
          <el-button type="primary" :icon="Plus" @click="addMemo" />
        </div>

        <ul class="space-y-2 max-h-[300px] overflow-y-auto custom-scrollbar">
          <li v-for="item in memos" :key="item.id" class="flex justify-between items-center bg-gray-50 dark:bg-gray-700 p-3 rounded-lg group">
            <span class="text-gray-700 dark:text-gray-200">{{ item.content }}</span>
            <el-button
              type="danger"
              link
              :icon="Delete"
              class="opacity-0 group-hover:opacity-100 transition-opacity"
              @click="removeWorkItem(item.id, 'memo')"
            />
          </li>
          <li v-if="memos.length === 0" class="text-center text-gray-400 py-4">暂无备忘</li>
        </ul>
      </div>

      <!-- Plans -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-gray-800 dark:text-white flex items-center">
            <el-icon class="mr-2"><Checked /></el-icon> 工作计划
          </h3>
        </div>

        <div class="flex space-x-2 mb-4">
          <el-input v-model="newPlan" placeholder="添加新计划..." @keyup.enter="addPlan" />
          <el-button type="success" :icon="Plus" @click="addPlan" />
        </div>

        <ul class="space-y-2 max-h-[300px] overflow-y-auto custom-scrollbar">
           <li v-for="item in plans" :key="item.id" class="flex justify-between items-center bg-gray-50 dark:bg-gray-700 p-3 rounded-lg group">
            <div class="flex items-center">
              <span class="text-gray-700 dark:text-gray-200">{{ item.content }}</span>
            </div>
            <el-button
              type="danger"
              link
              :icon="Delete"
              class="opacity-0 group-hover:opacity-100 transition-opacity"
              @click="removeWorkItem(item.id, 'plan')"
            />
          </li>
          <li v-if="plans.length === 0" class="text-center text-gray-400 py-4">暂无计划</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #e5e7eb;
  border-radius: 3px;
}
.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #4b5563;
}
</style>
