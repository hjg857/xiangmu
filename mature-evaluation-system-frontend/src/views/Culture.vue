<template>
  <div class="culture-page">
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
          <router-link to="/home" class="nav-item">首页</router-link>
          <router-link to="/about" class="nav-item">关于我们</router-link>
          <router-link to="/culture" class="nav-item">数据文化</router-link>
          <router-link to="/guide" class="nav-item">评估说明</router-link>
          <router-link to="/news" class="nav-item">实践动态</router-link>
          <el-dropdown class="user-dropdown">
            <span class="user-info">
              <el-icon><User /></el-icon>
              <span>{{ schoolName || '用户' }}</span>
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

    <!-- 主体内容区 -->
    <main class="main-content">
      <div class="content-container">
        <h2 class="page-title">数据文化</h2>
        <div class="title-underline"></div>
        <p class="page-subtitle">赋能教育决策的核心驱动力</p>
        
        <!-- 三个卡片区域 -->
        <div class="cards-container">
          <!-- 卡片1：关键构成 -->
          <div class="culture-card">
            <div class="card-icon">
              <img src="@/assets/images/DataCulture_1.png" alt="关键构成" />
            </div>
            <h3 class="card-title">关键构成</h3>
            <p class="card-content">
              学校数据文化主要由主体文化、制度文化、行为文化和技术文化构成。主体文化体现为教育主体对数据价值的认同程度以及数据应用的素养水平。制度文化指学校为推进数据文化建设而创设的有组织的规范体系。行为文化是学校数据文化的外化彰显，是教育主体围绕数据开展实践的全部集合。技术文化是学校数据文化的支撑基座，表现为先进数据基础设施与高水平数据技术的整体总和。
            </p>
          </div>

          <!-- 卡片2：数据定义 -->
          <div class="culture-card">
            <div class="card-icon">
              <img src="@/assets/images/DataCulture_2.png" alt="数据定义" />
            </div>
            <h3 class="card-title">数据定义</h3>
            <p class="card-content">
              学校数据文化是指学校在开展教育活动时，围绕数据使用与管理所形成的一套制度、规范、实践和价值观的集合。
            </p>
          </div>

          <!-- 卡片3：核心价值 -->
          <div class="culture-card">
            <div class="card-icon">
              <img src="@/assets/images/DataCulture_3.png" alt="核心价值" />
            </div>
            <h3 class="card-title">核心价值</h3>
            <p class="card-content">
              学校数据文化有助于组织内部塑造数据驱动的思维模式，培养数据驱动的行为方式，推动数据资产的积累与价值转化，进而提升学校现代化治理能力与水平。
            </p>
          </div>
        </div>
      </div>
    </main>

    <!-- 底部页脚 -->
    <footer class="footer">
  <div class="footer-bar">
    <div class="footer-inner">
      <!-- 左侧：LOGO + 文案 -->
      <div class="footer-left">
        <div class="footer-logo">
          <img src="@/assets/images/ila_logo.png" class="logo-img" alt="ILA" /> 
        </div>

        <div class="footer-text">
          <div class="line">
            Copyright © 2026 版权所有：智能学习与评价江苏省产业技术工程化中心
          </div>
          <div class="line">
            邮箱：2020250606@jsnu.edu.cn　
            地址：江苏省徐州市铜山新区上海路101号
          </div>
        </div>
      </div>

      <!-- 右侧：二维码 -->
      <div class="footer-right">
        <img
          src="@/assets/images/Official_Account1.png"
          alt="官方公众号"
          class="footer-qrcode"
        />
      </div>
    </div>
  </div>
</footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { School, User, Location, Message } from '@element-plus/icons-vue'

const router = useRouter()

const userInfo = ref({
  username: ''
})

const schoolName = ref('')

onMounted(() => {
  const storedUser = localStorage.getItem('user')
  if (storedUser) {
    userInfo.value = JSON.parse(storedUser)
    // 获取学校名称
    schoolName.value = userInfo.value.school_name || userInfo.value.username || '用户'
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
.culture-page {
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
  padding: 60px 40px 80px;
}

.content-container {
  max-width: 1400px;
  margin: 0 auto;
}

.page-title {
  font-size: 36px;
  font-weight: 700;
  color: #303133;
  text-align: center;
  margin-bottom: 8px;
}

.title-underline {
  width: 60px;
  height: 4px;
  background-color: #ff9800;
  margin: 0 auto 16px;
  border-radius: 2px;
}

.page-subtitle {
  font-size: 16px;
  color: #909399;
  text-align: center;
  margin-bottom: 60px;
}

/* 卡片容器 */
.cards-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 40px;
}

.culture-card {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 40px 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  height: 380px;
  position: relative;
  overflow: visible;
}

.culture-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  z-index: 10;
  height: auto;
  min-height: 380px;
}

.card-icon {
  width: 80px;
  height: 80px;
  margin-bottom: 24px;
  flex-shrink: 0;
}

.card-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.card-title {
  font-size: 22px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
  flex-shrink: 0;
}

.card-content {
  font-size: 18px;
  line-height: 1.8;
  color: #606266;
  text-align: justify;
  margin: 0;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  transition: all 0.3s ease;
}

.culture-card:hover .card-content {
  display: block;
  overflow: visible;
  -webkit-line-clamp: unset;
}

/* 底部页脚 */
/* 底部页脚 */
/* ===== Footer（深色条，按截图）===== */
.footer {
  margin-top: auto;
}

/* 深色条背景 */
.footer-bar {
  background: #2f3d4a; /* 接近截图那种蓝灰 */
  padding: 16px 0;
}

/* 内容容器 */
.footer-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 80px;

  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

/* 左侧区域：logo + 文案 */
.footer-left {
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 0;
  margin-left: -200px;
}

/* logo */
.footer-logo {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

/* 如果你用图片logo */
.logo-img {
  height: 62px;
  width: auto;
  display: block;
}

/* 文案两行 */
.footer-text {
  min-width: 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 16px;
  line-height: 1.5;
}

.footer-text .line {
  white-space: nowrap;         /* 默认不换行，像截图那样一行一行 */
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 右侧二维码 */
.footer-right {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  margin-right: -200px;
  height: 62px;
  width: auto;
}

.footer-qrcode {
  width: 80px;
  height: 80px;
  border-radius: 6px;
  background: #ffffff;
  padding: 4px; /* 让二维码像“贴纸”一样 */
}

.contact-section {
  flex: 1;
}

.contact-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.contact-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.contact-details p {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
  margin: 0;
}

.contact-details .el-icon {
  color: #409eff;
}

.qrcode-section {
  flex-shrink: 0;
}

.qrcode {
  width: 100px;
  height: 100px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .cards-container {
    grid-template-columns: repeat(2, 1fr);
    gap: 30px;
  }
}

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
    padding: 40px 20px 60px;
  }

  .page-title {
    font-size: 28px;
  }

  .cards-container {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .culture-card {
    padding: 30px 24px;
  }

  .footer-content {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }

  .contact-details p {
    justify-content: center;
  }
}
</style>
