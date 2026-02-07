<template>
  <div class="home-container">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-content">
        <div class="logo-section">
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
      <div class="hero-section">
        <h2 class="hero-title">数据驱动决策 文化赋能教育</h2>
        <p class="hero-description">
          本系统为中小学校提供全方位数据文化成熟度评估与诊断服务，通过科学量化的评估模型，帮助学校深度数据应用现状，定位差距瓶颈，提炼数据驱动文化建设，评估结果将生成可视化诊断的改进路线图，推动学校建立数据驱动的教育决策机制。
        </p>
        
        <div class="action-buttons">
          <el-button 
            type="warning" 
            size="large" 
            class="action-btn start-btn"
            @click="handleStartAssessment"
          >
            开始评估
          </el-button>
          <el-button 
            type="warning" 
            size="large" 
            class="action-btn report-btn"
            plain
            @click="handleViewReport"
          >
            查看报告
          </el-button>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { School, User } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getAssessments, createAssessment } from '@/api/assessment'

const loading = ref(false) 
const router = useRouter()
const userStore = useUserStore()

const userInfo = ref({
  username: ''
})

const schoolName = ref('')
const currentAssessment = ref(null)

onMounted(async () => {
  // 获取用户信息
  const storedUser = localStorage.getItem('user')
  if (storedUser) {
    userInfo.value = JSON.parse(storedUser)
    // 获取学校名称
    schoolName.value = userInfo.value.school_name || userInfo.value.username || '用户'
  }

  // 获取评估状态
  try {
    const assessments = await getAssessments()
    if (assessments && assessments.length > 0) {
      currentAssessment.value = assessments[0]
    }
  } catch (error) {
    console.error('获取评估状态失败:', error)
  }
})

// 开始评估
const handleStartAssessment = async () => {
  // 情况 A：没有任何记录，或者最近的一份已经完成了
  // 我们需要开启一轮新的评估
  if (!currentAssessment.value || currentAssessment.value.status === 'completed') {
    try {
      loading.value = true // 如果你有加载状态的话
      const res = await createAssessment()
      
      // 后端会返回新创建的评估对象（或者是之前没写完的草稿）
      // 我们直接跳转到评估填写页面
      ElMessage.success('已为您开启新一轮评估')
      router.push('/school/basic-info')
    } catch (error) {
      console.error('开启评估失败:', error)
      ElMessage.error(error.response?.data?.error || '无法开启新评估，请联系管理员')
    } finally {
      loading.value = false
    }
    return
  }

  // 情况 B：当前有一份评估是“草稿”状态 (draft)
  if (currentAssessment.value.status === 'draft') {
    // 直接进去接着填
    router.push('/school/basic-info')
    return
  }

  // 情况 C：当前评估正在处理中 (collecting / analyzing)
  // 这种状态下既不能改，也不能开新的（必须等这份出结果）
  if (['collecting', 'analyzing'].includes(currentAssessment.value.status)) {
    ElMessageBox.alert(
      '您当前有一份评估正在计算中，请等待结果生成后再开启新一轮评估。',
      '提示',
      { confirmButtonText: '查看进度' }
    ).then(() => {
      router.push('/school/assessment?viewProgress=true')
    })
  }
}

// 查看报告
const handleViewReport = () => {
  // 之前的逻辑：检查是否有评估，状态等
  // 现在的逻辑：直接跳转到概览页，让用户在那边看历史记录
  router.push('/school/overview')
}

// 退出登录
const handleLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.home-container {
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

.nav-item:hover {
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
  padding: 60px 40px;
}

.hero-section {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border-radius: 16px;
  padding: 80px 60px;
  text-align: center;
  color: #303133;
  margin-bottom: 60px;
  box-shadow: 0 8px 24px rgba(100, 181, 246, 0.2);
}

.hero-title {
  font-size: 42px;
  font-weight: 700;
  margin-bottom: 24px;
  letter-spacing: 2px;
}

.hero-description {
  font-size: 16px;
  line-height: 1.8;
  max-width: 900px;
  margin: 0 auto 48px;
  opacity: 0.95;
}

.action-buttons {
  display: flex;
  gap: 24px;
  justify-content: center;
}

.action-btn {
  min-width: 200px;
  height: 56px;
  font-size: 18px;
  font-weight: 600;
  border-radius: 28px;
  transition: all 0.3s;
}

.start-btn {
  background-color: #ff9800;
  border-color: #ff9800;
}

.start-btn:hover {
  background-color: #fb8c00;
  border-color: #fb8c00;
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(255, 152, 0, 0.4);
}

.report-btn {
  background-color: transparent;
  border: 2px solid #ff9800;
  color: #ff9800;
}

.report-btn:hover {
  background-color: rgba(255, 152, 0, 0.1);
  border-color: #fb8c00;
  color: #fb8c00;
  transform: translateY(-2px);
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

  .hero-section {
    padding: 40px 24px;
  }

  .hero-title {
    font-size: 28px;
  }

  .hero-description {
    font-size: 14px;
  }

  .action-buttons {
    flex-direction: column;
    gap: 16px;
  }

  .action-btn {
    width: 100%;
  }

  .main-content {
    padding: 30px 20px;
  }

  .footer-bottom {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
}
</style>
