<template>
  <el-dialog
    v-model="visible"
    :show-close="false"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    width="500px"
    class="success-dialog"
    center
  >
    <div class="success-content">
      <div class="icon-wrapper">
        <el-icon class="success-icon"><CircleCheckFilled /></el-icon>
      </div>
      <h2 class="title">提交成功</h2>
      <p class="description">恭喜，您已成功提交评估！系统会发送消息到邮箱，提醒您及时查看评估结果</p>
      <div class="actions">
        <el-button @click="handleViewProgress">查看进度</el-button>
        <el-button type="primary" @click="handleBackHome">返回首页</el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { CircleCheckFilled } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'view-progress'])
const router = useRouter()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const handleViewProgress = () => {
  emit('view-progress')
  visible.value = false
}

const handleBackHome = () => {
  visible.value = false
  router.push('/home')
}
</script>

<style scoped>
.success-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.icon-wrapper {
  margin-bottom: 24px;
}

.success-icon {
  font-size: 64px;
  color: #67c23a;
}

.title {
  font-size: 24px;
  color: #303133;
  margin: 0 0 16px 0;
  font-weight: 600;
}

.description {
  color: #909399;
  font-size: 14px;
  margin: 0 0 32px 0;
  text-align: center;
}

.actions {
  display: flex;
  gap: 16px;
}
</style>
