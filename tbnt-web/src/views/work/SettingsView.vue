<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getWorkSettings, updateWorkSettings, type WorkSettings } from '@/api/work'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const settingsForm = reactive({
  start_time: '09:00',
  end_time: '18:00'
})

const fetchSettings = async () => {
  loading.value = true
  try {
    const res = await getWorkSettings()
    settingsForm.start_time = res.start_time
    settingsForm.end_time = res.end_time
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleSave = async () => {
  loading.value = true
  try {
    await updateWorkSettings(settingsForm)
    ElMessage.success('配置已保存')
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchSettings()
})
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
      <h2 class="text-2xl font-bold text-gray-800 dark:text-white mb-6">工作配置</h2>
      
      <el-form label-position="top">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <el-form-item label="上班时间">
            <el-time-select
              v-model="settingsForm.start_time"
              start="06:00"
              step="00:30"
              end="12:00"
              placeholder="选择上班时间"
              class="w-full"
            />
          </el-form-item>
          
          <el-form-item label="下班时间">
            <el-time-select
              v-model="settingsForm.end_time"
              start="12:00"
              step="00:30"
              end="23:00"
              placeholder="选择下班时间"
              class="w-full"
            />
          </el-form-item>
        </div>

        <div class="flex justify-end mt-6">
          <el-button type="primary" :loading="loading" @click="handleSave">
            保存配置
          </el-button>
        </div>
      </el-form>
    </div>
    
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <h3 class="text-xl font-bold text-gray-800 dark:text-white mb-4">关于本页</h3>
      <p class="text-gray-600 dark:text-gray-300">
        在此设置您的工作时间，首页仪表盘将根据此配置自动计算您的下班倒计时和工作进度。
      </p>
    </div>
  </div>
</template>
