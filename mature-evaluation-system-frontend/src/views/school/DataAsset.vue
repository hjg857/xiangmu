<template>
  <div class="data-asset-container">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button @click="handleBack" :icon="ArrowLeft">返回</el-button>
            <span class="title">数据资产评价</span>
            <el-tag v-if="isReadonly" type="info" style="margin-left: 10px">只读模式</el-tag>
          </div>
          <el-button type="primary" @click="handleSave" :loading="saving" v-if="!isReadonly">
            保存
          </el-button>
        </div>
      </template>

      <el-alert
        v-if="isReadonly"
        title="评价已完成，当前为只读模式，无法修改数据"
        type="warning"
        :closable="false"
        style="margin-bottom: 20px"
      />

      <el-alert
        v-else
        title="评价说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        为全面评价您所在学校"数据资产"建设情况，请您按要求完成以下内容的填写。
      </el-alert>

      <el-form
        ref="formRef"
        :model="formData"
        label-position="top"
        class="asset-form"
        :hide-required-asterisk="true"
        :disabled="isReadonly"
      >
        <!-- 1. 数据资产意识 -->
        <div class="section-title">1. 数据资产意识</div>
        
        <div class="section-subtitle">管理者的数据资产意识</div>
        
        <el-alert
          type="success"
          :closable="false"
          style="margin-bottom: 20px"
        >
          <p>该维度将通过问卷调查的方式，了解管理者的数据资产意识。为便于数据采集，同卷（<strong>中小学校管理者数据资产意识调查问卷</strong>）已全部整合到"数据素养评价"板块。</p>
        </el-alert>

        <!-- 2. 数据资产积累 -->
        <div class="section-title">2. 数据资产积累</div>

        <div class="form-section">
          <div class="form-section-label">学校现有的数据累积总量（包括数据库、各种文档视频资源等，请分别列出各类数据的总量）？</div>
          
          <div class="data-volume-section">
            <div class="data-volume-item">
              <span class="volume-label">教学管理数据总量：</span>
              <el-input-number v-model="formData.management_data_volume" :min="0" :controls="false" />
              <span>GB</span>
            </div>
            <div class="volume-hint">
              数据来源示例：学校存储的与师生相关的数据，如基本信息、教学安排等；<br>
              统计方式示例：可通过查看学校教学管理系统的数据库，得到教学管理数据总量，具体统计方式可根据学校实际情况进行调整。
            </div>

            <div class="data-volume-item">
              <span class="volume-label">教学资源数据总量：</span>
              <el-input-number v-model="formData.resource_data_volume" :min="0" :controls="false" />
              <span>GB</span>
            </div>
            <div class="volume-hint">
              数据来源示例：学校存储的教案、课件、教学视频等资源的总量；<br>
              统计方式示例：可通过登录学校教学资源平台，查看平台当前存储教案、课件、教学视频等的总量，具体统计方式可根据学校实际情况进行调整。
            </div>

            <div class="data-volume-item">
              <span class="volume-label">校园服务数据总量：</span>
              <el-input-number v-model="formData.service_data_volume" :min="0" :controls="false" />
              <span>GB</span>
            </div>
            <div class="volume-hint">
              数据来源示例：学校存储的校园监控视频、门禁记录等的数据总量；<br>
              统计方式示例：可通过登录校园一卡通、校园安防平台等，查看存储监控视频、学生消费记录等的总量，具体统计方式可根据学校实际情况进行调整。
            </div>

            <div class="data-volume-item">
              <span class="volume-label">其他沉淀数据总量：</span>
              <el-input-number v-model="formData.other_data_volume" :min="0" :controls="false" />
              <span>GB</span>
            </div>
            <div class="volume-hint">
              数据来源示例：学校存储的未分类数据的总量，如校史资料、行政文件等；<br>
              统计方式示例：将学校未分类数据量相加，得到其他沉淀数据总量，具体统计方式可根据学校实际情况进行调整。
            </div>
          </div>
        </div>
      </el-form>
    </el-card>
  </div>
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
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const assessmentId = computed(() => route.params.id)

const loading = ref(true)
const saving = ref(false)
const formRef = ref(null)
const isReadonly = ref(false)  // 只读模式

// 表单数据
const formData = ref({
  management_data_volume: null,
  resource_data_volume: null,
  service_data_volume: null,
  other_data_volume: null
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    // 先获取评估状态
    const assessmentResponse = await fetch(`/api/assessments/${assessmentId.value}/`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    const assessmentData = await assessmentResponse.json()
    isReadonly.value = assessmentData.status !== 'draft'
    
    // 获取数据资产数据
    const response = await fetch(`/api/assessments/${assessmentId.value}/asset/`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    const data = await response.json()
    Object.assign(formData.value, data)
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 保存数据
const handleSave = async () => {
  saving.value = true
  try {
    const response = await fetch(`/api/assessments/${assessmentId.value}/save_asset/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(formData.value)
    })
    
    if (response.ok) {
      ElMessage.success('保存成功')
    } else {
      throw new Error('保存失败')
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 返回评估导航页面
const handleBack = () => {
  router.push('/school/assessment')
}

// 自动保存（只读模式下不自动保存）
let autoSaveTimer = null
const startAutoSave = () => {
  if (isReadonly.value) return
  autoSaveTimer = setInterval(() => {
    if (!isReadonly.value) {
      handleSave()
    }
  }, 120000) // 2分钟自动保存一次
}

onMounted(async () => {
  await loadData()
  startAutoSave()
})

onBeforeUnmount(() => {
  if (autoSaveTimer) {
    clearInterval(autoSaveTimer)
  }
})
</script>

<style scoped>
.data-asset-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.asset-form {
  margin-top: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #409eff;
  margin: 30px 0 20px 0;
  padding-left: 0;
  border-left: none;
}

.section-subtitle {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 15px;
}

.inline-inputs {
  display: flex;
  align-items: center;
  gap: 10px;
}

.form-section {
  margin-bottom: 30px;
}

.form-section-label {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 15px;
  line-height: 1.6;
}

.data-volume-section {
  width: 100%;
  padding-left: 20px;
}

.data-volume-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.volume-label {
  font-weight: 500;
  color: #606266;
  min-width: 150px;
}

.volume-hint {
  font-size: 12px;
  color: #909399;
  line-height: 1.6;
  margin-bottom: 20px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

:deep(.el-form-item) {
  margin-bottom: 22px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  line-height: 1.6;
  white-space: normal;
  word-break: break-word;
  margin-bottom: 8px;
  color: #303133;
}

:deep(.el-form-item__content) {
  flex-wrap: wrap;
}

:deep(.el-input-number) {
  width: 150px;
}

:deep(.el-input-number .el-input__inner) {
  text-align: center;
}

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
</style>
