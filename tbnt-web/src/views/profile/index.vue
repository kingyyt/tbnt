<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { updateProfile, updatePassword, uploadAvatar } from '@/api/user'
import { getImageUrl } from '@/utils/image'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import type { UploadFile } from 'element-plus'

defineOptions({
  name: 'ProfileView'
})

const authStore = useAuthStore()
const loading = ref(false)

const profileForm = ref({
  nickname: authStore.user?.nickname || '',
  phone: authStore.user?.phone || '',
  avatar: authStore.user?.avatar || ''
})

const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const passwordDialogVisible = ref(false)

const handleAvatarChange = async (uploadFile: UploadFile) => {
  if (!uploadFile.raw) return

  const isJPG = uploadFile.raw.type === 'image/jpeg' || uploadFile.raw.type === 'image/png'
  const isLt2M = uploadFile.raw.size / 1024 / 1024 < 2

  if (!isJPG) {
    ElMessage.error('Avatar picture must be JPG/PNG format!')
    return
  }
  if (!isLt2M) {
    ElMessage.error('Avatar picture size can not exceed 2MB!')
    return
  }

  try {
    const res = await uploadAvatar(uploadFile.raw)
    // Prepend API base URL if needed, but for now assuming proxy or full URL handling
    // Actually the backend returns relative path /static/...
    // We should probably store the full URL or handle it.
    // For now, let's just save what backend returns.
    profileForm.value.avatar = res.url
    await handleUpdateProfile() // Auto save after upload
  } catch (error) {
    console.error(error)
  }
}

const handleUpdateProfile = async () => {
  loading.value = true
  try {
    const user = await updateProfile({
      nickname: profileForm.value.nickname,
      phone: profileForm.value.phone,
      avatar: profileForm.value.avatar
    })
    authStore.setUser(user)
    ElMessage.success('个人信息更新成功')
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleUpdatePassword = async () => {
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    ElMessage.error('两次输入的密码不一致')
    return
  }

  loading.value = true
  try {
    await updatePassword({
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password
    })
    ElMessage.success('密码修改成功，请重新登录')
    passwordDialogVisible.value = false
    authStore.logout()
    // Redirect handled by store or router guard usually, but let's force it
    window.location.reload()
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="p-6 max-w-4xl mx-auto">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 transition-colors duration-300">
      <h2 class="text-2xl font-bold mb-6 text-gray-900 dark:text-white">个人中心</h2>

      <div class="flex flex-col md:flex-row gap-8">
        <!-- Avatar Section -->
        <div class="flex flex-col items-center space-y-4">
          <el-upload
            class="avatar-uploader"
            :show-file-list="false"
            :auto-upload="false"
            :on-change="handleAvatarChange"
          >
            <div v-if="profileForm.avatar" class="relative group w-32 h-32 rounded-full overflow-hidden cursor-pointer ring-4 ring-gray-100 dark:ring-gray-700">
              <img :src="getImageUrl(profileForm.avatar)" class="w-full h-full object-cover" />
              <div class="absolute inset-0 bg-black/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                <span class="text-white text-sm">更换头像</span>
              </div>
            </div>
            <div v-else class="w-32 h-32 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors ring-4 ring-gray-50 dark:ring-gray-800">
              <el-icon class="text-4xl text-gray-400"><Plus /></el-icon>
            </div>
          </el-upload>
          <p class="text-sm text-gray-500 dark:text-gray-400">点击上传头像</p>
        </div>

        <!-- Form Section -->
        <div class="flex-1">
          <el-form label-position="top" size="large">
            <el-form-item label="账号">
              <el-input :model-value="authStore.user?.username || ''" disabled />
            </el-form-item>

            <el-form-item label="昵称" required>
              <el-input v-model="profileForm.nickname" placeholder="请输入昵称" />
            </el-form-item>

            <el-form-item label="手机号">
              <el-input v-model="profileForm.phone" placeholder="请输入手机号" />
            </el-form-item>

            <div class="flex items-center justify-between mt-8 pt-6 border-t border-gray-100 dark:border-gray-700">
              <el-button type="default" @click="passwordDialogVisible = true">修改密码</el-button>
              <el-button type="primary" :loading="loading" @click="handleUpdateProfile">保存修改</el-button>
            </div>
          </el-form>
        </div>
      </div>
    </div>

    <!-- Password Dialog -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="修改密码"
      width="400px"
      align-center
    >
      <el-form label-position="top">
        <el-form-item label="原密码" required>
          <el-input v-model="passwordForm.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" required>
          <el-input v-model="passwordForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认新密码" required>
          <el-input v-model="passwordForm.confirm_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="passwordDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="loading" @click="handleUpdatePassword">
            确认修改
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>
