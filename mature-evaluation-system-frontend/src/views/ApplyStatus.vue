<template>
  <div class="status-container">
    <div class="status-box">
      <div class="status-header">
        <h1 class="status-title">账号申请进度</h1>
        <el-button link @click="goToLogin">
          返回登录
        </el-button>
      </div>

      <p class="status-subtitle">
        如您的学校尚未注册过账号，以下是您提交的账号申请进度，请耐心等待审核结果。
      </p>

      <!-- 进度时间线 -->
      <el-timeline class="timeline">
        <el-timeline-item
          :timestamp="formatTime(application.applied_at)"
          placement="top"
          :color="getStepColor(1)"
        >
          <div class="timeline-content">
            <h3>已提交申请</h3>
            <p>您的申请已成功提交，请等待管理员审核</p>
            <p class="time">{{ formatTime(application.applied_at) }}</p>
          </div>
        </el-timeline-item>

        <el-timeline-item
          timestamp="待审核"
          placement="top"
          :color="getStepColor(2)"
        >
          <div class="timeline-content">
            <h3>待管理员审核</h3>
            <p>管理员正在审核您的申请，预计1个工作日内完成</p>
            <p class="time" v-if="application.reviewed_at">
              {{ formatTime(application.reviewed_at) }}
            </p>
          </div>
        </el-timeline-item>

        <el-timeline-item
          timestamp="待发送"
          placement="top"
          :color="getStepColor(3)"
        >
          <div class="timeline-content">
            <h3>账号已发放至邮箱</h3>
            <p>
              系统将自动生成账号和密码，并发送至您的邮箱：
              {{ application.contact_email }}
            </p>
          </div>
        </el-timeline-item>
      </el-timeline>

      <!-- 当前状态 -->
      <el-alert
        v-if="application.status === 'pending'"
        title="审核中"
        type="warning"
        :closable="false"
        show-icon
        class="status-alert"
      >
        您的申请正在审核中，请耐心等待
      </el-alert>

      <el-alert
        v-else-if="application.status === 'approved'"
        title="审核通过"
        type="success"
        :closable="false"
        show-icon
        class="status-alert"
      >
        您的申请已通过审核，账号信息已发送至邮箱
      </el-alert>

      <el-alert
        v-else-if="application.status === 'rejected'"
        title="审核未通过"
        type="error"
        :closable="false"
        show-icon
        class="status-alert"
      >
        <template #default>
          <p>拒绝原因：{{ application.reject_reason || '未提供' }}</p>
        </template>
      </el-alert>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getApplicationStatus } from '@/api/school'
import { formatDateTime } from '@/utils'

const router = useRouter()
const route = useRoute()

const application = ref({
  status: 'pending',
  applied_at: '',
  reviewed_at: '',
  contact_email: ''
})

const formatTime = (time) => {
  return time ? formatDateTime(time) : ''
}

const getStepColor = (step) => {
  const status = application.value.status
  
  if (step === 1) return '#67C23A' // 已提交
  
  if (step === 2) {
    if (status === 'approved' || status === 'rejected') return '#67C23A'
    return '#E6A23C' // 审核中
  }
  
  if (step === 3) {
    if (status === 'approved') return '#67C23A'
    return '#909399' // 未完成
  }
  
  return '#909399'
}

const loadApplicationStatus = async () => {
  const applicationId = route.params.id
  
  if (!applicationId) {
    ElMessage.error('申请编号不存在')
    router.push('/login')
    return
  }
  
  try {
    const res = await getApplicationStatus(applicationId)
    if (res.success) {
      application.value = res.data
    }
  } catch (error) {
    ElMessage.error('查询失败')
  }
}

const goToLogin = () => {
  router.push('/login')
}

onMounted(() => {
  loadApplicationStatus()
})
</script>

<style scoped>
.status-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 40px 20px;
}

.status-box {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.status-title {
  font-size: 24px;
  color: #303133;
  font-weight: 500;
  margin: 0;
}

.status-subtitle {
  color: #606266;
  font-size: 14px;
  margin-bottom: 40px;
  line-height: 1.6;
}

.timeline {
  margin: 40px 0;
}

.timeline-content h3 {
  font-size: 16px;
  color: #303133;
  margin-bottom: 8px;
}

.timeline-content p {
  font-size: 14px;
  color: #606266;
  margin: 4px 0;
}

.timeline-content .time {
  color: #909399;
  font-size: 12px;
}

.status-alert {
  margin-top: 30px;
}
</style>
