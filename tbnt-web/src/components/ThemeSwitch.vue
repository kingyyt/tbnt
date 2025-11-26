<script setup lang="ts">
import { Moon, Sunny } from '@element-plus/icons-vue'
import { useDark } from '@vueuse/core'

const isDark = useDark()
</script>

<template>
  <el-switch
    v-model="isDark"
    inline-prompt
    :active-icon="Moon"
    :inactive-icon="Sunny"
    style="--el-switch-on-color: #2c2c2c; --el-switch-off-color: #f2f2f2; --el-switch-border-color: #dcdfe6"
  />
</template>
