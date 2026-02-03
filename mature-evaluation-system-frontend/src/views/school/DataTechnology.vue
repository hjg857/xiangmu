<template>
  <div class="data-technology-container">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button @click="handleBack" :icon="ArrowLeft">返回</el-button>
            <span class="title">数据技术评价</span>
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
        为全面评价您所在学校"数据技术"建设情况，请您按要求完成以下内容的填写。
      </el-alert>

      <el-form
        ref="formRef"
        :model="formData"
        label-position="top"
        class="technology-form"
        :hide-required-asterisk="true"
        :disabled="isReadonly"
      >
        <!-- 1. 数据基础设施 -->
        <div class="section-title">1. 数据基础设施</div>
        
        <el-form-item label="学校设有独立数据中心（如独立机房等）目标标准符合GB50174-2017数据中心设计规范的相应标准准要求？">
          <el-radio-group v-model="formData.data_center_standard" class="horizontal-radio-with-desc">
            <el-radio value="fully_compliant">
              <div class="radio-content">
                <div class="radio-title">完全符合</div>
                <div class="radio-desc">设有独立数据中心且完全符合B级要求</div>
              </div>
            </el-radio>
            <el-radio value="partially_compliant">
              <div class="radio-content">
                <div class="radio-title">部分符合</div>
                <div class="radio-desc">设有独立数据中心且部分符合B级要求</div>
              </div>
            </el-radio>
            <el-radio value="not_compliant">
              <div class="radio-content">
                <div class="radio-title">不符合</div>
                <div class="radio-desc">设有独立数据中心但不符合B级要求</div>
              </div>
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="学校未设有独立数据中心，但使用专享云服务，且完全满足学校的数据应用需求？">
          <el-radio-group v-model="formData.cloud_dedicated_service" class="horizontal-radio-with-desc">
            <el-radio value="fully_meets">
              <div class="radio-content">
                <div class="radio-title">完全达到</div>
              </div>
            </el-radio>
            <el-radio value="partially_meets">
              <div class="radio-content">
                <div class="radio-title">部分达到</div>
              </div>
            </el-radio>
            <el-radio value="not_meets">
              <div class="radio-content">
                <div class="radio-title">未达到</div>
              </div>
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="学校数字终端配备生机比/师机比？">
          <div class="ratio-section">
            <div class="ratio-group">
              <el-radio-group v-model="formData.student_device_ratio" class="horizontal-radio">
                <el-radio value="high">生机比 ≥ 15:1</el-radio>
                <el-radio value="medium">15:1 < 生机比 ≤ 6:1</el-radio>
                <el-radio value="low">生机比 < 6:1</el-radio>
              </el-radio-group>
            </div>
            <div class="ratio-group">
              <el-radio-group v-model="formData.teacher_device_ratio" class="horizontal-radio">
                <el-radio value="high">师机比 ≥ 4:1</el-radio>
                <el-radio value="medium">1:1 < 师机比 ≤ 4:1</el-radio>
                <el-radio value="low">师机比 < 1:1</el-radio>
              </el-radio-group>
            </div>
          </div>
        </el-form-item>

        <el-form-item label="学校是否建设数据治理平台，如数据中台、数据交换中心等？">
          <el-radio-group v-model="formData.has_data_platform" class="horizontal-radio-with-desc">
            <el-radio :value="true">
              <div class="radio-content">
                <div class="radio-title">已建立</div>
                <div class="radio-desc">学校已建设数据治理相关平台</div>
              </div>
            </el-radio>
            <el-radio :value="false">
              <div class="radio-content">
                <div class="radio-title">未建立</div>
                <div class="radio-desc">学校未建设数据治理相关平台</div>
              </div>
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 2. 数据安全水平 -->
        <div class="section-title">2. 数据安全水平</div>
        
        <el-form-item label="学校部署的各类平台通过国家安保等级认定的数量？">
          <div class="inline-inputs">
            <span>已认定</span>
            <el-input-number v-model="formData.security_certified_count" :min="0" :controls="false" />
            <span>个</span>
          </div>
        </el-form-item>

        <el-form-item label="学校部署的各类平台通过国家安保等级认定的比例？">
          <el-radio-group v-model="formData.security_certified_ratio" class="horizontal-radio">
            <el-radio value="low">认定比例 < 40%</el-radio>
            <el-radio value="medium">40% < 认定比例 ≤ 80%</el-radio>
            <el-radio value="high">认定比例 > 80%</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="近5年，学校是否发生数据风险事件？">
          <el-radio-group v-model="formData.has_security_incident" class="horizontal-radio-with-desc">
            <el-radio :value="true">
              <div class="radio-content">
                <div class="radio-title">有发生</div>
                <div class="radio-desc">学校发生过数据风险事件</div>
              </div>
            </el-radio>
            <el-radio :value="false">
              <div class="radio-content">
                <div class="radio-title">未发生</div>
                <div class="radio-desc">学校未发生过数据风险事件</div>
              </div>
            </el-radio>
          </el-radio-group>
        </el-form-item>
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
  data_center_standard: null,
  cloud_dedicated_service: null,
  student_device_ratio: null,
  teacher_device_ratio: null,
  has_data_platform: null,
  security_certified_count: null,
  security_certified_ratio: null,
  has_security_incident: null
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
    
    // 获取数据技术数据
    const response = await fetch(`/api/assessments/${assessmentId.value}/technology/`, {
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
    const response = await fetch(`/api/assessments/${assessmentId.value}/save_technology/`, {
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
    console.log('保存数据:', formData.value)
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
.data-technology-container {
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

.technology-form {
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

.inline-inputs {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ratio-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.ratio-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.radio-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.radio-title {
  font-weight: 500;
  color: #303133;
}

.radio-desc {
  font-size: 12px;
  color: #909399;
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
  width: 120px;
}

:deep(.el-input-number .el-input__inner) {
  text-align: center;
}

/* 默认纵向排列的单选按钮组 */
:deep(.el-radio-group) {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

:deep(.el-radio) {
  margin-right: 0;
  height: auto;
  align-items: center;
}

:deep(.el-radio__input) {
  align-self: flex-start;
  margin-top: 2px;
}

:deep(.el-radio__label) {
  white-space: normal;
  line-height: 1.5;
  padding-left: 8px;
}

/* 横向排列的单选按钮组(简单选项) */
:deep(.horizontal-radio) {
  flex-direction: row;
  gap: 30px;
  flex-wrap: wrap;
}

:deep(.horizontal-radio .el-radio) {
  margin-right: 0;
}

/* 横向排列的单选按钮组(带描述) */
:deep(.horizontal-radio-with-desc) {
  flex-direction: row;
  gap: 30px;
  flex-wrap: wrap;
}

:deep(.horizontal-radio-with-desc .el-radio) {
  margin-right: 0;
  flex: 0 0 auto;
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
