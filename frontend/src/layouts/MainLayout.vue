<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { useUserStore } from '@/stores/user'

const MOBILE_WIDTH = 768
const THEME_KEY = 'theme'

const route = useRoute()
const userStore = useUserStore()

const isMobile = ref(false)
const sidebarVisible = ref(true)
const isDark = ref(localStorage.getItem(THEME_KEY) === 'dark')

const activeMenu = computed(() => route.path)
const username = computed(() => userStore.userInfo?.username || '未登录')

function applyTheme() {
  document.documentElement.classList.toggle('dark', isDark.value)
}

function toggleTheme() {
  isDark.value = !isDark.value
  localStorage.setItem(THEME_KEY, isDark.value ? 'dark' : 'light')
  applyTheme()
}

function syncViewport() {
  isMobile.value = window.innerWidth < MOBILE_WIDTH
  sidebarVisible.value = !isMobile.value
}

onMounted(() => {
  applyTheme()
  syncViewport()
  window.addEventListener('resize', syncViewport)
  userStore.initUser()
})

onUnmounted(() => {
  window.removeEventListener('resize', syncViewport)
})

function toggleSidebar() {
  sidebarVisible.value = !sidebarVisible.value
}

function handleCommand(command: string) {
  if (command === 'logout') {
    userStore.logout()
  }
}
</script>

<template>
  <el-container class="layout">
    <el-aside
      v-if="!isMobile || sidebarVisible"
      width="200px"
      class="layout-aside"
    >
      <div class="logo">TaskFlow</div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#001529"
        text-color="#bfcbd9"
        active-text-color="#409eff"
        class="layout-menu"
      >
        <el-menu-item index="/">任务管理</el-menu-item>
        <el-menu-item index="/dashboard">数据概览</el-menu-item>
        <el-menu-item index="/profile">个人中心</el-menu-item>
      </el-menu>
    </el-aside>

    <el-container class="layout-body">
      <el-header class="layout-header">
        <div class="header-left">
          <span v-if="isMobile" class="hamburger" @click="toggleSidebar">☰</span>
        </div>

        <div class="header-right">
          <span class="theme-toggle" :title="isDark ? '切换到浅色' : '切换到深色'" @click="toggleTheme">
            {{ isDark ? '☀' : '☾' }}
          </span>

          <el-dropdown @command="handleCommand">
            <span class="user-trigger">
              {{ username }}
              <span class="user-trigger-arrow">▼</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout {
  height: 100vh;
}

.layout-aside {
  background-color: #001529;
  overflow-x: hidden;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
  color: #ffffff;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 1px;
}

.layout-menu {
  border-right: none;
}

.layout-body {
  min-width: 0;
}

.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.hamburger {
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
  user-select: none;
  color: var(--el-text-color-primary);
}

.theme-toggle {
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  user-select: none;
  color: var(--el-text-color-primary);
}

.user-trigger {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  color: var(--el-text-color-primary);
}

.user-trigger-arrow {
  font-size: 12px;
  line-height: 1;
}

.layout-main {
  background-color: var(--el-bg-color-page);
}

@media (max-width: 767px) {
  .layout-aside {
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
    z-index: 2000;
  }
}
</style>
