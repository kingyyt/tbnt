<script setup lang="ts">
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { getInvestmentTrend, type TrendPoint } from '@/api/investment'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('gold')
const loading = ref(false)
const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const initChart = () => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
    window.addEventListener('resize', resizeChart)
  }
}

const resizeChart = () => {
  chartInstance?.resize()
}

const fetchData = async () => {
  loading.value = true
  try {
    const data = await getInvestmentTrend(activeTab.value as 'gold' | 'nasdaq')
    updateChart(data)
    ElMessage.success('数据已更新')
  } catch (error) {
    console.error('Fetch investment data failed:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const updateChart = (data: TrendPoint[]) => {
  if (!chartInstance) return

  const dates = data.map(item => item.time)
  const values = data.map(item => item.value)

  const name = activeTab.value === 'gold' ? '黄金ETF' : '纳指科技ETF'
  const color = activeTab.value === 'gold' ? '#FFD700' : '#00BFFF'

  const option = {
    title: {
      text: `${name} 趋势图`,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      scale: true // Avoid starting from 0 to show trend better
    },
    series: [
      {
        name: name,
        type: 'line',
        data: values,
        smooth: true,
        itemStyle: {
          color: color
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {
              offset: 0,
              color: color
            },
            {
              offset: 1,
              color: 'rgba(255, 255, 255, 0)'
            }
          ])
        }
      }
    ]
  }

  chartInstance.setOption(option)
}

const handleTabChange = () => {
  // Clear chart or show loading
  if (chartInstance) {
    chartInstance.clear()
  }
  fetchData()
}

onMounted(() => {
  nextTick(() => {
    initChart()
    fetchData()
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeChart)
  chartInstance?.dispose()
})
</script>

<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">投资项目</h2>
      <el-button type="primary" :icon="Refresh" @click="fetchData" :loading="loading">
        刷新数据
      </el-button>
    </div>

    <el-card class="box-card">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="黄金" name="gold"></el-tab-pane>
        <el-tab-pane label="纳指科技ETF" name="nasdaq"></el-tab-pane>
      </el-tabs>

      <div ref="chartRef" class="w-full h-[500px] mt-4"></div>
    </el-card>
  </div>
</template>

<style scoped>
/* Ensure the chart container has a height */
</style>
