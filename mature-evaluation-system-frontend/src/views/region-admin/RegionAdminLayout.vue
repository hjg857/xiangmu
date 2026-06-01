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
          <span>区域评估概览</span>
        </el-menu-item>

          <el-menu-item index="/region-admin/schools">
            <el-icon><List /></el-icon>
            <span>学校账户申请</span>
          </el-menu-item>

        <el-menu-item index="/region-admin/assessments">
          <el-icon><DataLine /></el-icon>
          <span>学校评估报告</span>
        </el-menu-item>

        <el-menu-item index="/region-admin/region-report">
          <el-icon><Document /></el-icon>
          <span>区域评估报告</span>
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
    </el-container>
  </div>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
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
import { useRegionStore } from '@/stores/region'
import { apiGet } from '@/utils/api'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const userInfo = computed(() => userStore.userInfo)
const activeMenu = computed(() => route.path)


const regionStore = useRegionStore()

const refreshCurrentRegion = async () => {
  regionStore.currentRegion = null

  try {
    const { data: resp } = await apiGet('/api/region-admin/overview/')

    if (resp?.success && resp?.data?.region) {
      regionStore.currentRegion = resp.data.region
    }
  } catch (error) {
    console.error('刷新区域信息失败:', error)
  }
}

const pageTitle = computed(() => {
  const r = regionStore.currentRegion
  const p = route.path

  if (
    p.startsWith('/region-admin/assessments') ||
    p.startsWith('/region-admin/schools') ||
    p.startsWith('/region-admin/overview') ||
    p.startsWith('/region-admin/school-count')
  ) {
    if (r) {
      return `${r.province || ''}${r.city || ''}${r.name || ''}文化成熟度评估`
    }
    return '区域评估管理平台'
  }

  return '区域管理后台'
})

onMounted(async () => {
  await refreshCurrentRegion()
})

watch(
  () => userStore.userInfo?.id || userStore.userInfo?.username,
  async () => {
    await refreshCurrentRegion()
  }
)

const handleMenuSelect = (index) => {
  router.push(index)
}

const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()

    if (regionStore.$reset) {
      regionStore.$reset()
    } else {
      regionStore.currentRegion = null
    }

    localStorage.removeItem('region')
    localStorage.removeItem('regionStore')
    localStorage.removeItem('pinia-region')

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

/* 底部页脚 */
/* ===== Footer（深色条，按截图）===== */
.footer {
  margin-top: auto;
  width: 100%;
}

.footer-bar {
  background: #2f3d4a; /* 深蓝灰色背景 */
  padding: 8px 0;    /* 增加上下内边距，让比例更协调 */
}

.footer-inner {
  /* 核心：必须与 header-content 的宽度和对齐逻辑完全一致 */
  max-width: 99%;
  margin: 0 auto;
  padding: 0 20px;    /* 与 header 保持一致的左右内边距 */
  
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 10px;
  /* 彻底删除之前的 margin-left: -200px */
}

.footer-logo .logo-img {
  height: 80px;
  width: auto;
  display: block;
}

.footer-text {
  color: rgba(255, 255, 255, 0.85);
  font-size: 14px;      /* 标准页脚字号 */
  line-height: 1.8;
  text-align: left;
}

.footer-text .line {
  white-space: nowrap; /* 强制不换行，保持整齐 */
}

.footer-right {
  /* 彻底删除之前的 margin-right: -200px */
  display: flex;
  align-items: center;
}

.qr-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.footer-qrcode {
  width: 80px;
  height: 80px;
  border-radius: 4px;
  background: #ffffff;
  padding: 3px;
}

.qr-label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
}

.contact-note {
  margin-top: 18px;          /* 与邮箱拉开距离 */
  font-size: 13px;           /* 比正文小 */
  color: #9ca3af;            /* 浅灰色 */
  font-style: italic;        /* 微斜体，学术/说明感 */
  line-height: 1.6;
}
</style>
