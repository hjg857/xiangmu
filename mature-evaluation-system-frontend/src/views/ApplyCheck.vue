<template>
  <div class="check-container">
    <div class="check-box">
      <div class="check-header">
        <el-icon :size="32" color="#409EFF">
          <Search />
        </el-icon>
        <h1 class="check-title">查看申请进度</h1>
        <el-button
          class="back-button"
          @click="goToLogin"
        >
        <el-icon class="back-icon">
        <ArrowLeft />
        </el-icon>
          返回登录
        </el-button>
      </div>

      <div class="apply-info">
        请输入申请账号时填写的邮箱地址
      </div>

      <!-- 查询表单 -->
      <el-form
        ref="checkFormRef"
        :model="checkForm"
        :rules="checkRules"
        size="large"
      >
        <el-form-item prop="email">
          <el-input
            v-model="checkForm.email"
            placeholder="请输入申请时填写的邮箱地址"
            prefix-icon="Message"
            @keyup.enter="handleCheck"
          />
        </el-form-item>

        <el-button
          type="primary"
          size="large"
          :loading="loading"
          @click="handleCheck"
          class="check-button"
        >
          查询进度
        </el-button>
      </el-form>

      <!-- 查询结果 -->
      <div v-if="application" class="result-box">
        <el-alert
          :title="getStatusTitle()"
          :type="getStatusType()"
          :closable="false"
          show-icon
          class="status-alert"
        >
          <template #default>
            <div class="status-content">
              <p><strong>学校名称：</strong>{{ application.school_name }}</p>
              <p><strong>申请时间：</strong>{{ formatDateTime(application.applied_at) }}</p>
              <p v-if="application.reviewed_at">
                <strong>审批时间：</strong>{{ formatDateTime(application.reviewed_at) }}
              </p>
              <p v-if="application.reject_reason" class="reject-reason">
                <strong>拒绝原因：</strong>{{ application.reject_reason }}
              </p>
            </div>
          </template>
        </el-alert>

        <!-- 进度时间线 -->
        <el-timeline class="timeline">
          <el-timeline-item
            :timestamp="formatDateTime(application.applied_at)"
            placement="top"
            color="#67C23A"
          >
            <h4>已提交申请</h4>
            <p>您的申请已成功提交</p>
          </el-timeline-item>

          <el-timeline-item
            :timestamp="application.reviewed_at ? formatDateTime(application.reviewed_at) : '待审核'"
            placement="top"
            :color="application.status === 'pending' ? '#E6A23C' : '#67C23A'"
          >
            <h4>{{ application.status === 'pending' ? '待管理员审核' : '审核完成' }}</h4>
            <p v-if="application.status === 'pending'">
              管理员正在审核您的申请，预计1个工作日内完成
            </p>
            <p v-else-if="application.status === 'approved'">
              您的申请已通过审核
            </p>
            <p v-else-if="application.status === 'rejected'">
              您的申请未通过审核
            </p>
          </el-timeline-item>

          <el-timeline-item
            v-if="application.status === 'approved'"
            timestamp="已发送"
            placement="top"
            color="#67C23A"
          >
            <h4>账号已发放至邮箱</h4>
            <p>账号信息已发送至您的邮箱：{{ application.contact_email }}</p>
          </el-timeline-item>
        </el-timeline>
      </div>
    </div>

    <div class="footer">
      © 2025 苏师YangTeam 版权所有
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils'
import request from '@/api/request'

const router = useRouter()

const checkFormRef = ref(null)
const loading = ref(false)
const application = ref(null)

const checkForm = reactive({
  email: ''
})

const validateEmail = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入邮箱地址'))
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    callback(new Error('请输入有效的邮箱地址'))
  } else {
    callback()
  }
}

const checkRules = {
  email: [
    { required: true, validator: validateEmail, trigger: 'blur' }
  ]
}

const getStatusTitle = () => {
  if (!application.value) return ''
  
  const statusMap = {
    pending: '审核中',
    approved: '审核通过',
    rejected: '审核未通过'
  }
  return statusMap[application.value.status] || ''
}

const getStatusType = () => {
  if (!application.value) return 'info'
  
  const typeMap = {
    pending: 'warning',
    approved: 'success',
    rejected: 'error'
  }
  return typeMap[application.value.status] || 'info'
}

const handleCheck = async () => {
  if (!checkFormRef.value) return
  
  await checkFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    application.value = null
    
    try {
      // 调用后端API查询申请
      const res = await request({
        url: '/application/check-by-email/',
        method: 'post',
        data: {
          email: checkForm.email
        }
      })
      
      if (res.data) {
        application.value = res.data
      } else {
        ElMessage.warning('未找到该邮箱的申请记录')
      }
    } catch (error) {
      if (error.response?.status === 404) {
        ElMessage.warning('未找到该邮箱的申请记录')
      } else {
        ElMessage.error(error.response?.data?.error?.message || '查询失败')
      }
    } finally {
      loading.value = false
    }
  })
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.check-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 40px 20px;
}

.check-box {
  max-width: 700px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.check-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  position: relative;
}

.check-title {
  font-size: 24px;
  color: #303133;
  font-weight: 500;
  margin: 0;
}

.back-button {
  position: absolute;
  right: 0;
}

.check-subtitle {
  color: #606266;
  font-size: 14px;
  margin-bottom: 30px;
  line-height: 1.6;
}

.check-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  margin-top: 10px;
  background: #ff9800;
  border-color: #ff9800;
}

.check-button:hover {
  background: #fb8c00;
  border-color: #fb8c00;
}

.result-box {
  margin-top: 30px;
  padding-top: 30px;
  border-top: 1px solid #ebeef5;
}

.status-alert {
  margin-bottom: 30px;
}

.apply-info {
  width: 100%;
  background: #f0f9eb;          
  color: #67c23a;               /* 绿色文字 */
  border: 1px solid #e1f3d8;    /* 浅边框 */
  border-radius: 6px;

  padding: 10px 14px;
  margin-bottom: 24px;

  font-size: 13px;
  line-height: 1.6;
}

.back-button {
  display: inline-flex;
  align-items: center;
  gap: 6px;

  padding: 6px 14px;
  height: 34px;

  background: #ffffff;
  border: 1px solid #cfe5ff;
  border-radius: 6px;

  color: #409eff;
  font-size: 13px;
  font-weight: 500;

  transition: all 0.2s ease;
}

.back-button:hover {
  background: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

.back-icon {
  font-size: 14px;
}

.status-content p {
  margin: 8px 0;
  font-size: 14px;
  line-height: 1.6;
}

.reject-reason {
  color: #f56c6c;
}

.timeline {
  margin-top: 20px;
}

.timeline h4 {
  font-size: 16px;
  color: #303133;
  margin-bottom: 8px;
}

.timeline p {
  font-size: 14px;
  color: #606266;
  margin: 4px 0;
}

.footer {
  text-align: center;
  color: #909399;
  font-size: 14px;
  margin-top: 30px;
}
</style>
