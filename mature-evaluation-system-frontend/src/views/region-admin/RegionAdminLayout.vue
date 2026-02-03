<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <el-aside class="sidebar" width="210px">
      <div class="logo">
        <el-icon :size="24" color="#fff">
          <School />
        </el-icon>
        <span class="logo-text">区域评估管理平台</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        background-color="#2c5f9e"
        text-color="#ffffff"
        active-text-color="#ffffff"
        @select="handleMenuSelect"
      >
        <el-menu-item index="/region-admin/overview">
          <el-icon><DataAnalysis /></el-icon>
          <span>区域概览</span>
        </el-menu-item>

          <el-menu-item index="/region-admin/schools">
            <el-icon><List /></el-icon>
            <span>学校管理</span>
          </el-menu-item>

        <el-menu-item index="/region-admin/assessments">
          <el-icon><DataLine /></el-icon>
          <span>区域评估</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container class="main-container">
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <span class="current-page-title">{{ pageTitle }}</span>
        </div>

        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" :icon="UserFilled" />
              <span class="username">{{ userInfo?.username || '区域管理员' }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区域 -->
      <el-main class="content">
        <router-view />
      </el-main>

      <!-- 页脚 -->
      <el-footer class="footer">
        <span>© 2025 苏师YangTeam 版权所有</span>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  School,
  DataAnalysis,
  DataLine,
  UserFilled,
  Plus,
  List
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const userInfo = computed(() => userStore.userInfo)
const activeMenu = computed(() => route.path)

// 顶部标题：根据当前路由动态显示（简单可用版）
const pageTitle = computed(() => {
  const p = route.path
  if (p.startsWith('/region-admin/overview')) return '区域概览'
  if (p.startsWith('/region-admin/schools/create')) return '新增学校'
  if (p.startsWith('/region-admin/schools')) return '学校管理'
  if (p.startsWith('/region-admin/assessments/')) return '评估详情'
  if (p.startsWith('/region-admin/assessments')) return '区域评估'
  return '区域管理后台'
})

const handleMenuSelect = (index) => {
  router.push(index)
}

const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
    ElMessage.success('已退出登录')
  }
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  background: #f0f2f5;
}

.sidebar {
  background: #2c5f9e;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 16px;
  color: white;
  font-size: 16px;
  font-weight: 500;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-text {
  font-size: 14px;
  line-height: 1.2;
}

.sidebar-menu {
  border: none;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
  margin: 4px 8px;
  border-radius: 4px;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.1) !important;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: rgba(255, 255, 255, 0.2) !important;
}

.sidebar-menu :deep(.el-sub-menu__title) {
  height: 50px;
  line-height: 50px;
  margin: 4px 8px;
  border-radius: 4px;
}

.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background-color: rgba(255, 255, 255, 0.1) !important;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.header {
  background: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-left {
  flex: 1;
}

.current-page-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  font-size: 14px;
  color: #303133;
}

.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.footer {
  height: 48px;
  line-height: 48px;
  text-align: center;
  background: white;
  color: #909399;
  font-size: 14px;
  border-top: 1px solid #e4e7ed;
}
</style>
