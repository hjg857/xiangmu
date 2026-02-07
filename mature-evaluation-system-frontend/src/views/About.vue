<template>
  <div class="about-page">
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
  <!-- ✅ 卡片1：关于我们 -->
  <div class="content-card">
    <h2 class="page-title">关于我们</h2>
    <div class="title-underline"></div>

    <div class="about-content">
      <!-- 左侧文字内容 -->
      <div class="text-section">
        <p class="content-text">
          本系统由江苏师范大学杨现民教授领衔的教育信息化研究团队打造，在数字化浪潮席卷教育领域的背景下，数据成为推动全球教育变革的重要力量。然而，中小学在数据文化建设方面面临诸多挑战，如数据意识淡薄，数据应用能力不足、数据管理机制不完善等。为助力中小学突破瓶颈，提升数据文化成熟度，杨现民教授团队结合多年教育信息化研究与实践经验，开发了"中小学校数据文化成熟度评估监测系统"。
        </p>

        <p class="content-text">
          该系统旨在为中小学校提供科学、全面、便捷的数据文化评估工具，通过精准的评估指标体系，帮助学校清晰了解自身数据文化建设的现状与不足，从而促进切实可行的发展策略，以评促驱动中小学数据治理水平提升，为数据文化发展提供有力支持。
        </p>

        <p class="content-text">
          数据文化建设是一个持续探索与实践的过程，本系统旨在激发中小学校对数据文化的重视，引导学校积极探索数据驱动型组织的建设，为培养适应数字时代需求的创新型人才奠定基础。
        </p>
      </div>

      <!-- 右侧图片 -->
      <div class="image-section">
        <img src="@/assets/images/about_us.png" alt="关于我们" class="about-image" />
      </div>
    </div>
  </div>

  <!-- ✅ 卡片2：联系我们 -->
  <div class="content-card">
    <h2 class="page-title">联系我们</h2>
    <div class="title-underline"></div>

    <section class="contact-section">
      <div class="contact-content">
        <!-- 左侧说明 -->
        <div class="contact-left">
          <p class="contact-desc">
            我们期待与各级教育行政部门、中小学、研究机构开展广泛合作，
            共同推进中小学数据文化建设与评估工作。
          </p>

          <div class="contact-email">
            <el-icon><Message /></el-icon>
            2020250606@jsnu.edu.cn
          </div>
          <p class="contact-note">
            我们将尽快与您取得联系，共同探讨合作可能。
          </p>

        </div>

        <!-- 右侧表单 -->
        <!-- 右侧表单 -->
<div class="contact-right">
<el-form :model="contactForm" class="form-style">
  <el-form-item label="联系人员">
    <el-input v-model="contactForm.name" placeholder="您的姓名" />
  </el-form-item>

  <el-form-item label="联系电话">
    <el-input v-model="contactForm.phone" placeholder="您的手机号码" />
  </el-form-item>

  <el-form-item label="联系邮箱">
    <el-input v-model="contactForm.email" placeholder="您的邮箱地址" />
  </el-form-item>

  <el-form-item label="合作意向">
    <el-select v-model="contactForm.type" placeholder="请选择">
      <el-option label="学校整体评估" value="学校整体评估" />
      <el-option label="数据文化建设" value="数据文化建设" />
      <el-option label="研究合作" value="研究合作" />
      <el-option label="其他" value="其他" />
    </el-select>
  </el-form-item>

  <el-form-item label="留言内容">
    <el-input v-model="contactForm.message" type="textarea" :rows="4" />
  </el-form-item>

  <el-button type="primary" class="submit-btn" :loading="submitLoading"  @click="submitContact">
    提交合作咨询 →
  </el-button>
</el-form>

</div>

      </div>
    </section>
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
import { ElMessage } from 'element-plus'
import { School, User, Location, Message } from '@element-plus/icons-vue'
import { reactive } from 'vue'
import { apiPost } from '@/utils/api'

const contactForm = reactive({
  name: '',
  phone: '',
  email: '',
  type: '',
  message: ''
})

const submitLoading = ref(false)

const submitContact = async () => {
  // 1. 基础校验
  if (!contactForm.name || !contactForm.phone || !contactForm.message) {
    ElMessage.warning('请填写联系人、联系电话和留言内容')
    return
  }

  submitLoading.value = true
  try {
    // 2. 发起请求 (路径根据你urls.py的父级前缀调整，通常是 /api/public/...)
    // 这里我使用你之前能跑通的路径风格
    const { res, data } = await apiPost('/api/contact-collaboration/', contactForm)
    
    if (res.ok || data.success) {
      ElMessage.success('提交成功！我们已收到您的咨询，会尽快联系您。')
      // 3. 成功后重置表单
      Object.assign(contactForm, {
        name: '',
        phone: '',
        email: '',
        type: '',
        message: ''
      })
    } else {
      ElMessage.error(data.message || '提交失败，请稍后重试')
    }
  } catch (error) {
    console.error('提交合作咨询出错:', error)
    ElMessage.error('网络请求失败，请检查网络连接')
  } finally {
    submitLoading.value = false
  }
}






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
.about-page {
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
  background-color: #ffffff;
  border-radius: 12px;
  padding: 60px 80px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
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
  margin: 0 auto 50px;
  border-radius: 2px;
}

.about-content {
  display: flex;
  gap: 60px;
  align-items: flex-start;
}

.text-section {
  flex: 1;
  min-width: 0;
}

.section-subtitle {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 24px;
  line-height: 1.6;
}

.content-text {
  font-size: 15px;
  line-height: 2;
  color: #606266;
  margin-bottom: 20px;
  text-align: justify;
  text-indent: 2em;
}

.image-section {
  flex-shrink: 0;
  width: 400px;
}

.about-image {
  width: 100%;
  height: auto;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.contact-section {
  margin-top: 80px;
}

.section-title {
  text-align: center;
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 40px;
}

.contact-content {
  display: flex;
  gap: 60px;
}

.contact-left {
  flex: 1;
}

.contact-desc {
  font-size: 15px;
  line-height: 1.9;
  color: #606266;
  margin-bottom: 20px;
}

.contact-email {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #f5f7fa;
  border-radius: 6px;
  color: #409eff;
  font-size: 14px;
}

.contact-right {
  flex: 1;
  background: #ffffff;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.submit-btn {
  width: 100%;
  margin-top: 10px;
  height: 44px;
  font-size: 15px;
  font-weight: 600;
}

/* ✅ 主体：让两个卡片之间出现“留白间隔” */
.main-content {
  flex: 1;
  padding: 60px 40px 80px;
  background-color: #f5f7fa;
  display: flex;
  flex-direction: column;
  gap: 40px; /* 👈 这里就是你截图那种间隔 */
}

/* ✅ 两块内容各自一个白色卡片 */
.content-card {
  max-width: 1400px;
  margin: 0 auto;
  background-color: #ffffff;
  border-radius: 12px;
  padding: 60px 80px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

/* 联系我们布局（如果你已有就不用重复） */
.contact-content {
  display: flex;
  gap: 50px;
  align-items: flex-start;
}

.contact-left {
  flex: 1;
  min-width: 0;
}

.contact-right {
  width: 520px;
  flex-shrink: 0;
}

.contact-email {
  margin-top: 18px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 8px;
  background: #f5f7ff;
  color: #1d4ed8;
  font-weight: 500;
}

.submit-btn {
  width: 100%;
  height: 42px;
  font-weight: 600;
}

/* 响应式：小屏改为上下结构 */
@media (max-width: 1024px) {
  .content-card {
    padding: 40px 24px;
  }

  .contact-content {
    flex-direction: column;
  }

  .contact-right {
    width: 100%;
  }
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


/* 小屏适配：允许换行且上下布局 */
@media (max-width: 900px) {
  .footer-inner {
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 0 20px;
  }

  .footer-left {
    flex-direction: column;
    gap: 10px;
  }

  .footer-text .line {
    white-space: normal; /* 小屏允许换行 */
  }
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
  .about-content {
    flex-direction: column;
    gap: 40px;
  }

  .image-section {
    width: 100%;
    max-width: 500px;
    margin: 0 auto;
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

  .content-container {
    padding: 40px 24px;
  }

  .page-title {
    font-size: 28px;
  }

  .section-subtitle {
    font-size: 18px;
  }

  .content-text {
    font-size: 14px;
  }

  .contact-details p {
    justify-content: center;
  }
}
</style>
