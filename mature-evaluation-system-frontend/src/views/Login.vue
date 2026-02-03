<template>
  <div class="login-page">
    <!-- 左侧：宣传区 -->
    <div class="left-panel">
      <div class="left-content">
        <h1 class="left-title">中小学数据文化</h1>
        <h1 class="left-title">成熟度评估监测系统</h1>
      </div>
    </div>

    <!-- 右侧：登录区 -->
    <div class="right-panel">
      <div class="form-card">
        <div class="form-header">账号登录</div>

        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          size="large"
          class="login-form"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入学校账号"
              prefix-icon="User"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入登录密码"
              prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <el-form-item prop="captcha_code">
            <div class="captcha-row">
              <el-input
                v-model="loginForm.captcha_code"
                placeholder="请输入验证码"
                prefix-icon="Key"
                @keyup.enter="handleLogin"
              />
              <img
                v-if="captchaImage"
                :src="captchaImage"
                class="captcha-image"
                @click="refreshCaptcha"
                alt="验证码"
                title="点击刷新"
              />
            </div>
          </el-form-item>

          <div class="form-extra">
            <el-checkbox v-model="rememberPassword">记住我</el-checkbox>
            <el-link type="primary" @click="handleForgotPassword">忘记密码？</el-link>
          </div>

          <el-button
            type="warning"
            size="large"
            :loading="loading"
            @click="handleLogin"
            class="login-btn"
          >
            登录
          </el-button>

          <div class="register-line">
            还没有账户？
            <el-button type="primary" link @click="goToApply">申请账号</el-button>
            <span class="sep">|</span>
            <el-button type="primary" link @click="goToCheckStatus">查看申请进度</el-button>
          </div>
        </el-form>
      </div>
      <div class="copyright">
          © 智能学习与评价江苏省产业技术工程化中心 版权所有
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getCaptcha, login } from '@/api/auth'
import { useUserStore } from '@/stores/user'

import illustrationPng from '@/assets/images/login-illustration.png'

const illustrationUrl = computed(() => illustrationPng)

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref(null)
const loading = ref(false)
const captchaImage = ref('')
const captchaKey = ref('')
const rememberPassword = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  captcha_code: '',
  captcha_key: ''
})

// 记住密码相关
const REMEMBER_KEY = 'remembered_login'

const loadRememberedLogin = () => {
  try {
    const remembered = localStorage.getItem(REMEMBER_KEY)
    if (remembered) {
      const data = JSON.parse(atob(remembered))
      loginForm.username = data.username || ''
      loginForm.password = data.password || ''
      rememberPassword.value = true
    }
  } catch (e) {
    localStorage.removeItem(REMEMBER_KEY)
  }
}

const saveRememberedLogin = () => {
  if (rememberPassword.value) {
    const data = btoa(JSON.stringify({
      username: loginForm.username,
      password: loginForm.password
    }))
    localStorage.setItem(REMEMBER_KEY, data)
  } else {
    localStorage.removeItem(REMEMBER_KEY)
  }
}

const loginRules = {
  username: [{ required: true, message: '请输入学校账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入登录密码', trigger: 'blur' }],
  captcha_code: [{ required: true, message: '请输入验证码', trigger: 'blur' }]
}

// 获取验证码
const refreshCaptcha = async () => {
  try {
    const res = await getCaptcha()
    if (res.success) {
      captchaImage.value = res.data.captcha_image
      captchaKey.value = res.data.captcha_key
      loginForm.captcha_key = res.data.captcha_key
    }
  } catch (error) {
    ElMessage.error('获取验证码失败')
  }
}

// 登录
const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      const res = await login(loginForm)

      if (res.success && res.data) {
        saveRememberedLogin()

        localStorage.setItem('access_token', res.data.access)
        localStorage.setItem('refresh_token', res.data.refresh)
        localStorage.setItem('user', JSON.stringify(res.data.user))

        userStore.setToken(res.data.access)
        userStore.setUserInfo(res.data.user)

        ElMessage.success(res.message || '登录成功')

        setTimeout(() => {
          if (res.data.user.role === 'admin') {
            router.push('/admin/applications')
          } else if (res.data.user.role === 'region_admin') {
            router.push('/region-admin/overview')
          } else {
            router.push('/home')
          }
        }, 100)
      } else {
        ElMessage.error(res.message || '登录失败')
        refreshCaptcha()
      }
    } catch (error) {
      ElMessage.error(error.response?.data?.error?.message || error.message || '登录失败')
      refreshCaptcha()
    } finally {
      loading.value = false
    }
  })
}

const handleForgotPassword = () => {
  ElMessage.info('请联系管理员重置密码')
}

const goToApply = () => router.push('/apply')
const goToCheckStatus = () => router.push('/apply/check')

onMounted(() => {
  loadRememberedLogin()
  refreshCaptcha()
})
</script>

<style scoped>
/* 整体左右分栏 */
.login-page {
  min-height: 100vh;
  display: flex;
  background: #ffffff;
}

/* 左侧 */
.left-panel {
  flex: 1;
  background: #E1E5EB;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 60px;
  background-image: url('@/assets/images/login-illustration.png');
  background-repeat: no-repeat;
  background-position: center;
  background-size: contain;  
}

.left-content {
  position: absolute;
  left: 80px;              
  top: 120px;
  z-index: 1;
}

.left-title .t1 {
  font-size: 32px;
  font-weight: 700;
  color: #1f2d3d;
  letter-spacing: 0.5px;
}
.left-title .t2 {
  margin-top: 10px;
  font-size: 32px;
  font-weight: 700;
  color: #1f2d3d;
  letter-spacing: 0.5px;
}

/* 插画 */
.illustration {
  margin-top: 26px;
  width: 80%;
  max-width: 640px;
  height: auto;
  display: block;
}

/* 右侧 */
.right-panel {
  flex: 1;
  width: auto;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 80px;
  background: #ffffff;
}

/* 登录卡片 */
.form-card {
  width: 100%;
  max-width: 480px;
  padding: 200px 0;
}

.form-header {
  text-align: center;
  font-size: 22px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 18px;
}

.form-title {
  text-align: center;
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 28px;
}

.login-form :deep(.el-input__wrapper) {
  height: 50px;
  font-size: 16px;
}

.captcha-row {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}
.captcha-row :deep(.el-form-item__content) {
  display: flex;
  gap: 12px;
}

.captcha-image {
  width: 110px;
  height: 42px;
  cursor: pointer;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.form-extra {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 8px 0 14px;
  font-size: 14px;
}

.login-btn {
  width: 100%;
  height: 50px;
  font-size: 18px;
  font-weight: 600;
  background: #ff9800;
  border-color: #ff9800;
}
.login-btn:hover {
  background: #fb8c00;
  border-color: #fb8c00;
}

.register-line {
  margin-top: 14px;
  text-align: center;
  color: #606266;
  font-size: 13px;
}
.sep {
  margin: 0 6px;
  color: #dcdfe6;
}

.footer {
  margin-top: 18px;
  text-align: center;
  color: #9ca3af;
  font-size: 12px;
  line-height: 1.5;
}
.copyright {
  margin-top: auto;       
  padding-top: 40px;
  text-align: center;
  font-size: 16px;
  color: #9ca3af;          
  line-height: 1.6;
}


/* 响应式：窄屏时上下排列 */
@media (max-width: 980px) {
  .login-page {
    flex-direction: column;
  }
  .right-panel {
    width: 100%;
    min-width: 0;
  }
  .left-panel {
    padding: 28px 20px;
  }
}
</style>
