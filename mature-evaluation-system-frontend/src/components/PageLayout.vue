<template>
  <div class="page-layout">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-content">
        <div class="logo-section" @click="goHome">
          <el-icon :size="32" color="#409eff">
            <School />
          </el-icon>
          <h1 class="system-title">中小学校数据文化成熟度评估监测系统</h1>
        </div>
        <nav class="nav-menu">
          <router-link to="/about" class="nav-item">关于我们</router-link>
          <router-link to="/culture" class="nav-item">数据文化</router-link>
          <router-link to="/guide" class="nav-item">评估说明</router-link>
          <router-link to="/news" class="nav-item">实践动态</router-link>
          <el-dropdown class="user-dropdown">
            <span class="user-info">
              <el-icon><User /></el-icon>
              <span>{{ userInfo.username || '用户' }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </nav>
      </div>
    </header>

    <!-- 内容区域 -->
    <main class="main-content">
      <slot></slot>
    </main>

    <!-- 底部页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-top">
          <p class="copyright">© 2025 苏师YangTeam 版权所有</p>
        </div>
        <div class="footer-bottom">
          <div class="contact-info">
            <p>地址：江苏省徐州市铜山新区上海路101号</p>
            <p>邮箱：a18398917485@163.com</p>
          </div>
          <div class="qrcode">
            <img src="@/assets/images/Official_Account.png" alt="官方公众号" />
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { School, User } from '@element-plus/icons-vue'

const router = useRouter()

const userInfo = ref({
  username: ''
})

onMounted(() => {
  const storedUser = localStorage.getItem('user')
  if (storedUser) {
    userInfo.value = JSON.parse(storedUser)
  }
})

const goHome = () => {
  router.push('/home')
}

const handleLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.page-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

/* 顶部导航栏 */
.header {
  background-color: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
  height: 70px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.system-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 32px;
}

.nav-item {
  color: #606266;
  text-decoration: none;
  font-size: 15px;
  transition: color 0.3s;
  cursor: pointer;
}

.nav-item:hover,
.nav-item.router-link-active {
  color: #409eff;
}

.user-dropdown {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
  font-size: 14px;
}

.user-info:hover {
  color: #409eff;
}

/* 主体内容区 */
.main-content {
  flex: 1;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  padding: 40px;
}

/* 底部页脚 */
.footer {
  background-color: #2c3e50;
  color: #ecf0f1;
  padding: 40px 0 20px;
  margin-top: auto;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
}

.footer-top {
  text-align: center;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(236, 240, 241, 0.2);
  margin-bottom: 24px;
}

.copyright {
  font-size: 14px;
  color: #bdc3c7;
}

.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.contact-info p {
  font-size: 13px;
  color: #95a5a6;
  margin: 0;
}

.qrcode img {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  background-color: white;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    padding: 0 20px;
    height: auto;
    flex-direction: column;
    padding-top: 16px;
    padding-bottom: 16px;
  }

  .nav-menu {
    flex-wrap: wrap;
    gap: 16px;
    margin-top: 12px;
  }

  .system-title {
    font-size: 16px;
  }

  .main-content {
    padding: 20px;
  }

  .footer-bottom {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
}
</style>
