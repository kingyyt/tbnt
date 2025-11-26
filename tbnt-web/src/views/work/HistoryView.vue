<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getWorkRecords, getWorkItems, type WorkRecord, type WorkItem } from '@/api/work'
import { Calendar, Timer, Checked, Memo } from '@element-plus/icons-vue'

const loading = ref(false)
const records = ref<WorkRecord[]>([])
const workItems = ref<WorkItem[]>([])
const activeTab = ref('records')

const fetchData = async () => {
  loading.value = true
  try {
    const [recordsData, itemsData] = await Promise.all([
      getWorkRecords(),
      getWorkItems()
    ])
    records.value = recordsData
    workItems.value = itemsData
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const formatTime = (timeStr?: string) => {
  if (!timeStr) return '-'
  return new Date(timeStr).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

const formatDateTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const calculateDuration = (record: WorkRecord) => {
  if (!record.clock_in_time || !record.clock_out_time) return '-'
  const start = new Date(record.clock_in_time).getTime()
  const end = new Date(record.clock_out_time).getTime()
  const diff = end - start

  if (diff < 0) return '-'

  const h = Math.floor(diff / (1000 * 60 * 60))
  const m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))

  return `${h}小时 ${m}分钟`
}

const sortedWorkItems = computed(() => {
  return [...workItems.value].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
})

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="p-6">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
      <div class="flex items-center mb-6">
        <el-icon class="mr-2 text-blue-500 text-xl"><Calendar /></el-icon>
        <h2 class="text-xl font-bold text-gray-800 dark:text-white">工作历史</h2>
      </div>

      <el-tabs v-model="activeTab" class="demo-tabs">
        <el-tab-pane label="打卡记录" name="records">
          <el-table :data="records" v-loading="loading" style="width: 100%" class="rounded-lg overflow-hidden">
            <el-table-column prop="date" label="日期" min-width="120">
              <template #default="scope">
                <span class="font-medium">{{ scope.row.date }}</span>
              </template>
            </el-table-column>

            <el-table-column prop="clock_in_time" label="上班打卡" min-width="150">
              <template #default="scope">
                <div class="flex items-center">
                  <el-tag size="small" type="success" effect="plain" class="mr-2">In</el-tag>
                  {{ formatTime(scope.row.clock_in_time) }}
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="clock_out_time" label="下班打卡" min-width="150">
              <template #default="scope">
                <div class="flex items-center">
                  <el-tag size="small" type="danger" effect="plain" class="mr-2">Out</el-tag>
                  {{ formatTime(scope.row.clock_out_time) }}
                </div>
              </template>
            </el-table-column>

            <el-table-column label="工作时长" min-width="120">
              <template #default="scope">
                <div class="flex items-center text-gray-600 dark:text-gray-400">
                  <el-icon class="mr-1"><Timer /></el-icon>
                  {{ calculateDuration(scope.row) }}
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="工作事项" name="items">
          <el-table :data="sortedWorkItems" v-loading="loading" style="width: 100%" class="rounded-lg overflow-hidden">
             <el-table-column prop="created_at" label="创建时间" min-width="160">
              <template #default="scope">
                <span class="text-gray-500">{{ formatDateTime(scope.row.created_at) }}</span>
              </template>
            </el-table-column>

            <el-table-column prop="type" label="类型" width="100">
              <template #default="scope">
                 <el-tag v-if="scope.row.type === 'plan'" type="success"><el-icon class="mr-1"><Checked /></el-icon>计划</el-tag>
                 <el-tag v-else type="primary"><el-icon class="mr-1"><Memo /></el-icon>备忘</el-tag>
              </template>
            </el-table-column>

            <el-table-column prop="content" label="内容" min-width="300">
              <template #default="scope">
                <span :class="{ 'line-through text-gray-400': scope.row.status === 'done' }">{{ scope.row.content }}</span>
              </template>
            </el-table-column>

            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.status === 'done' ? 'success' : 'warning'" effect="dark">
                  {{ scope.row.status === 'done' ? '已完成' : '进行中' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>
