<template>
  <div class="success-container">
    <div class="success-box">
      <el-icon :size="80" color="#67C23A" class="success-icon">
        <CircleCheck />
      </el-icon>
      
      <h1 class="success-title">提交成功</h1>
      
      <p class="success-message">
        恭喜，您的申请已提交成功。管理员审核后会在1个工作日内，发送账号密码到您的邮箱！
      </p>

      <div class="button-group">
        <el-button size="large" @click="checkStatus">
          查看进度
        </el-button>
        <el-button type="primary" size="large" @click="goToHome">
          返回首页
        </el-button>
      </div>

      <div class="application-info" v-if="applicationId">
        <p>申请编号：{{ applicationId }}</p>
        <p class="tip">请保存此编号，可用于查询申请进度</p>
      </div>
    </div>

    <div class="footer">
      © 2025 苏师YangTeam 版权所有
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { CircleCheck } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const applicationId = ref('')

onMounted(() => {
  applicationId.value = route.params.id || ''
})

const checkStatus = () => {
  if (applicationId.value) {
    router.push(`/apply/status/${applicationId.value}`)
  }
}

const goToHome = () => {
  router.push('/')
}
</script>

<style scoped>
.success-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  padding: 20px;
}

.success-box {
  background: white;
  border-radius: 8px;
  padding: 60px 80px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.success-icon {
  margin-bottom: 24px;
}

.success-title {
  font-size: 28px;
  color: #303133;
  font-weight: 500;
  margin-bottom: 16px;
}

.success-message {
  font-size: 16px;
  color: #606266;
  line-height: 1.8;
  margin-bottom: 40px;
  max-width: 500px;
}

.button-group {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-bottom: 30px;
}

.application-info {
  padding-top: 30px;
  border-top: 1px solid #ebeef5;
  color: #606266;
  font-size: 14px;
}

.application-info p {
  margin: 8px 0;
}

.application-info .tip {
  color: #909399;
  font-size: 12px;
}

.footer {
  margin-top: 40px;
  color: #909399;
  font-size: 14px;
}
</style>
