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
        
                <el-form-item prop="data_center_standard">
          <template #label>
            <div class="label-with-hint">
              <span>学校设有独立数据中心（如独立机房等）目标标准符合GB50174-2017数据中心设计规范的相应标准准要求？</span>
              <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
                <template #reference>
                  <span class="hint-tag">填写提示</span>
                </template>
                <div class="hint-body">
                  <p class="hint-text">学校是否拥有独立数据中心（独立机房），且该数据中心的建设标准是否符合 GB50174-2017《数据中心设计规范》的对应要求，按实际情况选择对应选项。</p>
                  <p class="hint-example"><em>示例：学校建有独立机房且各项指标完全满足 GB50174-2017 B 级要求，则选择「完全符合」；学校有独立机房但仅部分指标符合 B 级要求，则选择「部分符合」；学校有独立机房但未达到 B 级要求，则选择「不符合」。</em></p>
                </div>
              </el-popover>
            </div>
          </template>
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

        <el-form-item prop="cloud_dedicated_service">
        <template #label>
          <div class="label-with-hint">
            <span>学校未设有独立数据中心，但使用专享云服务，且完全满足学校的数据应用需求？</span>
            <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
              <template #reference>
                <span class="hint-tag">填写提示</span>
              </template>
              <div class="hint-body">
                <p class="hint-text">若学校无独立数据中心，需考虑学校是否使用专享云服务，且该服务是否能满足学校全部数据应用需求，按实际情况选择对应选项。</p>
                <p class="hint-example"><em>示例：学校无独立数据中心，使用教育局统一部署的专享云服务且能满足所有数据存储、处理需求，则选择「完全达到」；仅能满足大部分数据需求则选择「部分达到」；无法满足核心数据应用需求则选择「未达到」。</em></p>
              </div>
            </el-popover>
          </div>
        </template>
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

      <!-- 3. 生机比 -->
      <el-form-item prop="student_device_ratio">
        <template #label>
          <div class="label-with-hint">
            <span>学校数字终端配备生机比（学生用机数量与在校生人数之比）？</span>
            <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
              <template #reference>
                <span class="hint-tag">填写提示</span>
              </template>
              <div class="hint-body">
                <p class="hint-text">生机比指 “学生人数：数字终端数量”，按实际计算结果选择对应区间选项（数字终端含电脑、平板等教学用智能终端）。</p>
                <p class="hint-example"><em>示例：全校学生 1000 人、数字终端 200 台，生机比 = 5:1（＜6:1），则选择「生机比 < 6:1」。</em></p>
              </div>
            </el-popover>
          </div>
        </template>
        <el-radio-group v-model="formData.student_device_ratio" class="horizontal-radio">
          <el-radio value="low">生机比 < 6:1</el-radio>
          <el-radio value="medium"> 6:1 < 生机比 ≤ 15:1</el-radio>
          <el-radio value="high">生机比 ≥ 15:1</el-radio>
        </el-radio-group>
      </el-form-item>

      <!-- 4. 师机比 -->
      <el-form-item prop="teacher_device_ratio">
        <template #label>
          <div class="label-with-hint">
            <span>学校数字终端配备师机比（专任教师用机数量与专任教师人数之比）？</span>
            <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
              <template #reference>
                <span class="hint-tag">填写提示</span>
              </template>
              <div class="hint-body">
                <p class="hint-text">师机比指 “教师人数：数字终端数量”，按实际计算结果选择对应区间选项（数字终端含电脑、平板等教学用智能终端）。</p>
                <p class="hint-example"><em>示例：全校教师 100 人、数字终端 80 台，师机比 = 1.25:1（1:1 < 师机比 ≤ 4:1），则选择「1:1 < 师机比 ≤ 4:1」。</em></p>
              </div>
            </el-popover>
          </div>
        </template>
        <el-radio-group v-model="formData.teacher_device_ratio" class="horizontal-radio">
          <el-radio value="low">师机比 < 1:1</el-radio>
          <el-radio value="medium">1:1 < 师机比 ≤ 4:1</el-radio>
          <el-radio value="high">师机比 ≥ 4:1</el-radio>
        </el-radio-group>
      </el-form-item>

                <el-form-item prop="has_data_platform">
          <template #label>
            <div class="label-with-hint">
              <span>学校是否建设数据治理平台，如数据中台、数据交换中心等？</span>
              <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
                <template #reference>
                  <span class="hint-tag">填写提示</span>
                </template>
                <div class="hint-body">
                  <p class="hint-text">判断学校是否搭建了专门的数治理平台（含数据中台、数据交换中心、数据管理平台等。</p>
                  <p class="hint-example"><em>示例：学校已建成校级数据中台，实现全校数据统一归集和交换，则选择「已建立」；学校未搭建任何数据治理类平台，仅零散存储数据，则选择「未建立」。</em></p>
                </div>
              </el-popover>
            </div>
          </template>
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
        
        <el-form-item prop="security_certified_count">
            <template #label>
              <div class="label-with-hint">
                <span>学校部署的各类平台通过国家安保等级认定的数量？</span>
                <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
                  <template #reference>
                    <span class="hint-tag">填写提示</span>
                  </template>
                  <div class="hint-body">
                    <p class="hint-text">统计学校当前部署的所有信息化平台中，通过国家网络安全等级保护认证（等保认证）的平台数量。</p>
                    <p class="hint-example"><em>示例：学校部署了教务管理平台、学生评价平台、校园安全平台共 3 个平台，其中教务管理平台和校园安全平台通过等保认证，则填写「2」；所有平台均未通过则填写「0」。</em></p>
                  </div>
                </el-popover>
              </div>
            </template>
            <div class="inline-inputs">
              <span>已认定</span>
              <el-input-number v-model="formData.security_certified_count" :min="0" :controls="false" />
              <span>个</span>
            </div>
          </el-form-item>

          <!-- 7. 安保等级认定比例 -->
          <el-form-item prop="security_certified_ratio">
            <template #label>
              <div class="label-with-hint">
                <span>学校部署的各类平台通过国家安保等级认定的比例？</span>
                <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
                  <template #reference>
                    <span class="hint-tag">填写提示</span>
                  </template>
                  <div class="hint-body">
                    <p class="hint-text">计算 “通过国家安保等级认定的平台数量 ÷ 学校部署的所有平台总数” 的百分比，按结果选择对应区间选项。</p>
                    <p class="hint-example"><em>示例：学校共部署 5 个平台，3 个通过等保认证（认定比例 = 60%，40% < 认定比例 ≤ 80%），则选择「40% < 认定比例 ≤ 80%」；仅 1 个通过（认定比例 = 20% < 40%），则选择「认定比例 < 40%」。</em></p>
                  </div>
                </el-popover>
              </div>
            </template>
            <el-radio-group v-model="formData.security_certified_ratio" class="horizontal-radio">
              <el-radio value="low">认定比例 < 40%</el-radio>
              <el-radio value="medium">40% < 认定比例 ≤ 80%</el-radio>
              <el-radio value="high">认定比例 > 80%</el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- 8. 数据风险事件 -->
          <el-form-item prop="has_security_incident">
            <template #label>
              <div class="label-with-hint">
                <span>2020年到2025年，学校是否发生数据风险事件？</span>
                <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
                  <template #reference>
                    <span class="hint-tag">填写提示</span>
                  </template>
                  <div class="hint-body">
                    <p class="hint-text">2020年到 2025 年期间， 学校是否发生过数据泄露、数据篡改、数据丢失、数据被非法访问等数据安全风险事件。</p>
                    <p class="hint-example"><em>示例：2023 年学校发生过学生信息泄露事件，则选择「有发生」；2020-2025年期间未发生任何数据安全问题，则选择「未发生」。</em></p>
                  </div>
                </el-popover>
              </div>
            </template>
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

:deep(.horizontal-radio) {
  flex-direction: row;
  gap: 20px;
  flex-wrap: wrap;
  padding: 15px;
  border-radius: 4px;
  width: 100%;
}

/* 调整只读模式下的样式，使其更清晰 */
.el-form-item.is-disabled :deep(.el-radio__label) {
  color: #606266;
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

/* 标题与提示并列的布局容器 */
.label-with-hint {
  display: flex;
  align-items: center;
  flex-wrap: wrap; /* 如果标题太长，允许提示换行 */
  gap: 10px;
}

/* 填写提示小标签样式 */
.hint-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 2px 10px;
  font-size: 12px;
  color: #409eff;
  background-color: #ecf5ff;
  border: 1px solid #cfe5ff;
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap; /* 强制标签不换行 */
  transition: all 0.2s;
  line-height: 1.2;
}

.hint-tag:hover {
  background-color: #409eff;
  color: #ffffff;
}

/* 弹出框内容样式 */
.hint-body {
  padding: 8px 4px;
}

.hint-text {
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
  margin-bottom: 10px;
}

.hint-example {
  font-size: 13px;
  line-height: 1.5;
  color: #909399;
}

.hint-example em {
  font-style: italic;
}

</style>
