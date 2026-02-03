<template>
  <div class="progress-page">
    <div class="page-header">
      <div class="header-left">
        <span class="title">数据文化成熟度评估</span>
        <el-tag type="warning" effect="dark" round size="small">处理中</el-tag>
      </div>
      <div class="header-desc">您的数据文化成熟度评估正在处理中，以下是最新的评估进度</div>
    </div>

    <div class="timeline-container">
      <div class="timeline-item" :class="{ active: currentStep >= 1 }">
        <div class="timeline-icon">
          <el-icon v-if="currentStep > 1"><Check /></el-icon>
          <el-icon v-else><EditPen /></el-icon>
        </div>
        <div class="timeline-content">
          <div class="step-title">正在收集评估数据</div>
          <div class="step-desc">系统正在收集您的企业数据文化评估所需的数据</div>
          <div class="step-time" v-if="times.collecting">{{ times.collecting }}</div>
        </div>
      </div>

      <div class="timeline-item" :class="{ active: currentStep >= 2 }">
        <div class="timeline-icon">
          <el-icon v-if="currentStep > 2"><Check /></el-icon>
          <el-icon v-else><DocumentChecked /></el-icon>
        </div>
        <div class="timeline-content">
          <div class="step-title">评估数据已提交</div>
          <div class="step-desc">您的评估数据已成功提交，系统将开始分析处理</div>
          <div class="step-time" v-if="times.submitted">{{ times.submitted }}</div>
        </div>
      </div>

      <div class="timeline-item" :class="{ active: currentStep >= 3 }">
        <div class="timeline-icon">
          <el-icon v-if="currentStep > 3"><Check /></el-icon>
          <el-icon v-else><TrendCharts /></el-icon>
        </div>
        <div class="timeline-content">
          <div class="step-title">正在分析结果</div>
          <div class="step-desc">系统正在分析您提交的数据，计算成熟度评分和改进建议</div>
          <div class="step-time" v-if="times.analyzing">{{ times.analyzing }}</div>
        </div>
      </div>

      <div class="timeline-item" :class="{ active: currentStep >= 4 }">
        <div class="timeline-icon">
          <el-icon><Document /></el-icon>
        </div>
        <div class="timeline-content">
          <div class="step-title">评估报告已生成</div>
          <div class="step-desc">您的数据文化成熟度评估报告已生成，请到个人中心查看详细分析结果</div>
          <div class="step-time" v-if="times.completed">{{ times.completed }}</div>
        </div>
      </div>
    </div>
    
    <div class="page-footer" v-if="currentStep >= 4">
        <el-button type="primary" @click="viewReport">查看报告</el-button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Check, EditPen, DocumentChecked, TrendCharts, Document } from '@element-plus/icons-vue'

const props = defineProps({
  status: {
    type: String,
    required: true
  },
  assessmentId: {
    type: [Number, String],
    required: true
  },
  times: {
    type: Object,
    default: () => ({})
  }
})

const router = useRouter()

const currentStep = computed(() => {
  switch (props.status) {
    case 'draft':
      return 1
    case 'collecting':
      return 2  // Using collecting as submitted state for now as backend transitions quickly
    case 'analyzing':
      return 3
    case 'completed':
      return 4
    default:
      return 1
  }
})

const viewReport = () => {
    router.push(`/school/report/${props.assessmentId}`)
}
</script>

<style scoped>
.progress-page {
  background: #fff;
  border-radius: 8px;
  padding: 40px;
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 40px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-desc {
  color: #909399;
  font-size: 14px;
}

.timeline-container {
  position: relative;
  padding-left: 20px;
}

.timeline-container::before {
  content: '';
  position: absolute;
  left: 35px;
  top: 20px;
  bottom: 20px;
  width: 2px;
  background-color: #e4e7ed;
  z-index: 1;
}

.timeline-item {
  position: relative;
  display: flex;
  gap: 24px;
  margin-bottom: 32px;
  z-index: 2;
}

.timeline-item:last-child {
  margin-bottom: 0;
}

.timeline-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #fff;
  border: 2px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
  transition: all 0.3s;
}

.timeline-item.active .timeline-icon {
  border-color: #ff9900;
  background-color: #ff9900;
  color: #fff;
}

.timeline-content {
  flex: 1;
  background-color: #f8f9fa;
  padding: 16px 24px;
  border-radius: 4px;
}

.step-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
}

.step-desc {
  font-size: 14px;
  color: #909399;
  line-height: 1.5;
  margin-bottom: 8px;
}

.step-time {
  font-size: 12px;
  color: #c0c4cc;
}

.page-footer {
    margin-top: 30px;
    text-align: center;
}
</style>
