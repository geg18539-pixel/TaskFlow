<script setup lang="ts">
import { computed } from 'vue'

import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const roleLabels: Record<string, string> = {
  admin: '管理员',
  user: '普通用户',
}

const roleText = computed(() => {
  const role = userStore.userInfo?.role
  if (!role) return '-'
  return roleLabels[role] ?? role
})

function formatTime(value?: string) {
  return value ? new Date(value).toLocaleString() : '-'
}
</script>

<template>
  <div class="profile-view">
    <el-card>
      <template #header>
        <span class="card-title">个人中心</span>
      </template>

      <el-skeleton v-if="!userStore.userInfo" :rows="3" animated />

      <el-descriptions v-else :column="1" border>
        <el-descriptions-item label="用户名">
          {{ userStore.userInfo.username }}
        </el-descriptions-item>
        <el-descriptions-item label="角色">
          {{ roleText }}
        </el-descriptions-item>
        <el-descriptions-item label="注册时间">
          {{ formatTime(userStore.userInfo.created_at) }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<style scoped>
.profile-view {
  max-width: 640px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}
</style>
