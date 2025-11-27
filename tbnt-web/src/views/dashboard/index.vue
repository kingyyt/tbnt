<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { getWorkSettings, getWorkItems, createWorkItem, updateWorkItem, deleteWorkItem, clockOut, getTodayWorkRecord, type WorkItem, type WorkRecord } from '@/api/work'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Checked, Memo, Timer, CircleCheck, RefreshLeft } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const router = useRouter()
const loading = ref(false)
const now = ref(new Date())
const timer = ref<number>()
const clockOutLoading = ref(false)
const todayRecord = ref<WorkRecord>()

// Work Data
const workSettings = ref({ start_time: '09:00', end_time: '18:00' })
const memos = ref<WorkItem[]>([])
const plans = ref<WorkItem[]>([])

// Forms
const newMemo = ref('')
const newPlan = ref('')

// Computed
const workStatus = computed(() => {
  if (todayRecord.value?.clock_out_time) return 'off-work'

  const parts = workSettings.value.end_time.split(':').map(Number)
  const endH = parts[0] || 0
  const endM = parts[1] || 0
  const endTime = new Date(now.value)
  endTime.setHours(endH, endM, 0)

  return now.value > endTime ? 'overtime' : 'working'
})

const timeLeft = computed(() => {
  const parts = workSettings.value.end_time.split(':').map(Number)
  const endH = parts[0] || 0
  const endM = parts[1] || 0
  const endTime = new Date(now.value)
  endTime.setHours(endH, endM, 0)

  let diff = 0
  let isOver = false

  // If clocked out, use clock_out_time for calculation if it was overtime
  if (todayRecord.value?.clock_out_time) {
    const clockOutTime = new Date(todayRecord.value.clock_out_time.replace(/-/g, '/'))
    // If clocked out after end time, show overtime duration
    if (clockOutTime > endTime) {
      diff = clockOutTime.getTime() - endTime.getTime()
      isOver = true
    } else {
      // Clocked out early or on time
      diff = endTime.getTime() - clockOutTime.getTime()
      isOver = false // Not overtime
    }
  } else {
    // Live calculation
    if (now.value > endTime) {
      diff = now.value.getTime() - endTime.getTime()
      isOver = true
    } else {
      diff = endTime.getTime() - now.value.getTime()
      isOver = false
    }
  }

  const h = Math.floor(diff / (1000 * 60 * 60))
  const m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  const s = Math.floor((diff % (1000 * 60)) / 1000)

  return {
    h: h.toString().padStart(2, '0'),
    m: m.toString().padStart(2, '0'),
    s: s.toString().padStart(2, '0'),
    isOver
  }
})

const timeProgress = computed(() => {
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

const memoProgress = computed(() => {
  if (memos.value.length === 0) return 0
  const completed = memos.value.filter(i => i.status === 'done').length
  return Math.floor((completed / memos.value.length) * 100)
})

const planProgress = computed(() => {
  if (plans.value.length === 0) return 0
  const completed = plans.value.filter(i => i.status === 'done').length
  return Math.floor((completed / plans.value.length) * 100)
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

    // Fetch today's record
    try {
      todayRecord.value = await getTodayWorkRecord()
    } catch {
      // No record for today, that's fine
      todayRecord.value = undefined
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const addMemo = async () => {
  if (!newMemo.value.trim()) return
  try {
    const item = await createWorkItem({ type: 'memo', content: newMemo.value, status: 'pending' })
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

const toggleItemStatus = async (item: WorkItem) => {
  const newStatus = item.status === 'done' ? 'pending' : 'done'
  try {
    await updateWorkItem(item.id, { status: newStatus })
    item.status = newStatus
  } catch (error) {
    console.error(error)
    ElMessage.error('更新状态失败')
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

const handleClockOut = async () => {
  clockOutLoading.value = true
  try {
    const record = await clockOut()
    todayRecord.value = record
    ElMessage.success('打卡成功！')
  } catch (error) {
    console.error(error)
    ElMessage.error('打卡失败')
  } finally {
    clockOutLoading.value = false
  }
}

const goToProfile = () => {
  router.push('/profile')
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
  <div>
    <!-- Overtime Alert Overlay -->
    <div
      v-if="workStatus === 'overtime'"
      class="fixed inset-0 z-50 pointer-events-none flex items-center justify-center overflow-hidden"
    >
       <div class="absolute inset-0 border-[20px] border-red-500/50 animate-pulse shadow-[inset_0_0_100px_rgba(239,68,68,0.5)]"></div>
       <div class="absolute inset-0 bg-red-900/10 animate-pulse"></div>
    </div>

    <div class="space-y-6">
    <!-- Header Banner -->
    <div
      class="rounded-2xl p-8 text-white shadow-xl relative overflow-hidden transition-all duration-1000"
      :class="workStatus !== 'working' ? 'bg-gray-900 border border-gray-800' : 'bg-gradient-to-br from-blue-500 to-cyan-500 shadow-blue-500/30'"
    >
      <div class="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <div class="flex items-center space-x-4 mb-4 cursor-pointer hover:opacity-80 transition-opacity" @click="goToProfile">
            <el-avatar :size="64" :src="authStore.user?.avatar ? `http://localhost:8000${authStore.user.avatar}` : ''" class="border-2 border-white/30">
              {{ authStore.user?.nickname?.charAt(0) || authStore.user?.username?.charAt(0) }}
            </el-avatar>
            <div>
              <h1 class="text-2xl font-bold">{{ authStore.user?.nickname || authStore.user?.username }}</h1>
              <p class="text-white/80 text-sm mt-1">996, thanks… but no thanks.</p>
            </div>
          </div>

          <div class="flex items-center space-x-4">
             <el-button
               :type="workStatus === 'overtime' ? 'danger' : (workStatus === 'off-work' ? 'success' : 'default')"
               :class="workStatus === 'working' ? 'text-blue-500' : ''"
               size="large"
               @click="handleClockOut"
               :loading="clockOutLoading"
               :disabled="workStatus === 'off-work'"
             >
               <el-icon class="mr-2"><Timer /></el-icon> {{ workStatus === 'off-work' ? '打卡成功' : '下班打卡' }}
             </el-button>
          </div>
        </div>

        <div class="flex flex-col items-center md:items-end">
           <div class="mb-2 text-sm font-medium" :class="workStatus === 'overtime' ? 'text-red-400 animate-bounce' : 'text-blue-100'">
             {{ workStatus === 'overtime' ? '已加班时间' : (workStatus === 'off-work' ? (timeLeft.isOver ? '加班时长' : '今日工作结束') : '距离下班还有') }}
           </div>
           <div
             class="font-mono text-5xl font-bold tracking-widest flex items-center transition-all duration-500"
             :class="[
               workStatus === 'overtime' ? 'text-red-500 animate-breathe drop-shadow-[0_0_20px_rgba(239,68,68,0.8)]' : 'text-white drop-shadow-md',
               workStatus === 'off-work' && !timeLeft.isOver ? 'text-green-400' : '',
               workStatus === 'off-work' && timeLeft.isOver ? 'text-red-400' : ''
             ]"
           >
             <span class="px-2 rounded" :class="workStatus === 'overtime' ? 'bg-red-900/30' : 'bg-white/20'">{{ timeLeft.h }}</span>
             <span class="animate-pulse mx-1">:</span>
             <span class="px-2 rounded" :class="workStatus === 'overtime' ? 'bg-red-900/30' : 'bg-white/20'">{{ timeLeft.m }}</span>
             <span class="animate-pulse mx-1">:</span>
             <span class="px-2 rounded" :class="workStatus === 'overtime' ? 'bg-red-900/30' : 'bg-white/20'">{{ timeLeft.s }}</span>
           </div>
           <div class="mt-4 w-64">
             <div class="flex justify-between text-xs mb-1" :class="workStatus === 'overtime' ? 'text-red-300' : 'text-blue-100'">
               <span>今日时间进度</span>
               <span>{{ timeProgress }}%</span>
             </div>
             <el-progress
               :percentage="timeProgress"
               :stroke-width="8"
               striped
               striped-flow
               :status="timeLeft.isOver ? 'exception' : ''"
               :color="timeLeft.isOver ? '#ef4444' : '#ffffff'"
               :show-text="false"
               class="!w-full"
             />
           </div>
        </div>
      </div>

      <!-- Decorative elements -->
      <div class="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>
      <div class="absolute bottom-0 left-0 w-64 h-64 bg-black/10 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2"></div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Memos -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 border border-gray-100 dark:border-gray-700">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-gray-800 dark:text-white flex items-center">
            <el-icon class="mr-2 text-blue-500"><Memo /></el-icon> 工作备忘录
          </h3>
          <el-progress type="circle" :percentage="memoProgress" :width="40" :stroke-width="4" :show-text="false">
            <template #default>
              <span class="text-xs">{{ memoProgress }}%</span>
            </template>
          </el-progress>
        </div>

        <div class="flex space-x-2 mb-4">
          <el-input v-model="newMemo" placeholder="添加新备忘..." @keyup.enter="addMemo" />
          <el-button type="primary" :icon="Plus" @click="addMemo" />
        </div>

        <ul class="space-y-2 max-h-[300px] overflow-y-auto custom-scrollbar">
          <li v-for="item in memos" :key="item.id" class="flex items-center bg-gray-50 dark:bg-gray-700 p-3 rounded-lg group hover:shadow-sm transition-shadow">
            <span
              class="flex-1 text-gray-700 dark:text-gray-200 transition-all cursor-pointer"
              :class="{ 'line-through text-gray-400 dark:text-gray-500': item.status === 'done' }"
              @click="toggleItemStatus(item)"
            >
              {{ item.content }}
            </span>
            <div class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <el-button
                :type="item.status === 'done' ? 'warning' : 'success'"
                link
                :icon="item.status === 'done' ? RefreshLeft : CircleCheck"
                @click="toggleItemStatus(item)"
                :title="item.status === 'done' ? '标记为未完成' : '标记为完成'"
              />
              <el-button
                type="danger"
                link
                :icon="Delete"
                @click="removeWorkItem(item.id, 'memo')"
              />
            </div>
          </li>
          <li v-if="memos.length === 0" class="text-center text-gray-400 py-4">暂无备忘</li>
        </ul>
      </div>

      <!-- Plans -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 border border-gray-100 dark:border-gray-700">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-gray-800 dark:text-white flex items-center">
            <el-icon class="mr-2 text-green-500"><Checked /></el-icon> 工作计划
          </h3>
          <el-progress type="circle" :percentage="planProgress" :width="40" :stroke-width="4" :show-text="false" status="success">
             <template #default>
              <span class="text-xs">{{ planProgress }}%</span>
            </template>
          </el-progress>
        </div>

        <div class="flex space-x-2 mb-4">
          <el-input v-model="newPlan" placeholder="添加新计划..." @keyup.enter="addPlan" />
          <el-button type="success" :icon="Plus" @click="addPlan" />
        </div>

        <ul class="space-y-2 max-h-[300px] overflow-y-auto custom-scrollbar">
           <li v-for="item in plans" :key="item.id" class="flex items-center bg-gray-50 dark:bg-gray-700 p-3 rounded-lg group hover:shadow-sm transition-shadow">
            <span
              class="flex-1 text-gray-700 dark:text-gray-200 transition-all cursor-pointer"
               :class="{ 'line-through text-gray-400 dark:text-gray-500': item.status === 'done' }"
               @click="toggleItemStatus(item)"
            >
              {{ item.content }}
            </span>
            <div class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <el-button
                :type="item.status === 'done' ? 'warning' : 'success'"
                link
                :icon="item.status === 'done' ? RefreshLeft : CircleCheck"
                @click="toggleItemStatus(item)"
                :title="item.status === 'done' ? '标记为未完成' : '标记为完成'"
              />
              <el-button
                type="danger"
                link
                :icon="Delete"
                @click="removeWorkItem(item.id, 'plan')"
              />
            </div>
          </li>
          <li v-if="plans.length === 0" class="text-center text-gray-400 py-4">暂无计划</li>
        </ul>
      </div>
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

@keyframes breathe {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.animate-breathe {
  animation: breathe 2s infinite ease-in-out;
}
</style>
