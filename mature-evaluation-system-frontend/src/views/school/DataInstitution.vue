<template>
  <div class="data-institution-container">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button @click="handleBack" :icon="ArrowLeft">返回</el-button>
            <span class="title">数据制度评价</span>
            <el-tag v-if="isReadonly" type="info" style="margin-left: 10px">只读模式</el-tag>
          </div>
          <el-button type="primary" @click="handleSave" :loading="saving" :disabled="isReadonly" v-if="!isReadonly">
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
        为全面评价您所在学校"数据制度"建设情况，请您按要求完成以下内容的填写。
      </el-alert>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-position="top"
        class="institution-form"
        :hide-required-asterisk="true"
        :disabled="isReadonly"
      >
        <!-- 1. 数据组织机构 -->
        <div class="section-title">1. 数据组织机构</div>
        
        <el-form-item prop="has_leadership_group">
          <template #label>
            <div class="label-with-hint">
              <span>学校是否建立了数据领导小组/工作小组？</span>
              <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
                <template #reference>
                  <span class="hint-tag">填写提示</span>
                </template>
                <div class="hint-body">
                  <p class="hint-text">学校设立的统筹数据管理、应用、安全等相关工作的组织人员（领导小组或工作小组均可）。</p>
                  <p class="hint-example"><em>示例：学校成立了由校长任组长、各部门负责人为成员的“数据治理小组”，则选择「已建立」；若学校未设立任何与数据管理相关的专项组织，则选择「未建立」。</em></p>
                </div>
              </el-popover>
            </div>
          </template>
          <el-radio-group v-model="formData.has_leadership_group">
            <el-radio :label="true">已建立</el-radio>
            <el-radio :label="false">未建立</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item prop="meeting_activity_count">
          <template #label>
            <div class="label-with-hint">
              <span>2020年到2025年，学校数据组织相关会议、活动开展次数？</span>
              <el-popover placement="top-start" :width="300" trigger="hover" popper-class="custom-hint-popper">
                <template #reference>
                  <span class="hint-tag">填写提示</span>
                </template>
                <div class="hint-body">
                  <p class="hint-text">2020年到2025年期间，由学校组织的各类数据相关会议、培训、研讨、专项活动等的总次数。</p>
                  <p class="hint-example"><em>示例：学校2022年开展1次数据安全专项会议、2023年开展2次数据应用研讨、2024年开展3次数据素养培训，则共计6次，填写「6」。</em></p>
                </div>
              </el-popover>
            </div>
          </template>
          <el-input-number v-model="formData.meeting_activity_count" :min="0" :controls="false" />
          <span class="unit">次</span>
        </el-form-item>
        <!-- 2. 数据人员配备 -->
        <div class="section-title">2. 数据人员配备</div>
        
        <el-form-item prop="has_data_staff">
        <template #label>
          <div class="label-with-hint">
            <span>学校是否配备数据专职/兼职管理人员？</span>
            <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
              <template #reference>
                <span class="hint-tag">填写提示</span>
              </template>
              <div class="hint-body">
                <p class="hint-text">学校设有负责数据的收集、整理、维护、分析等日常数据管理工作的专人（全职或兼职）。</p>
                <p class="hint-example"><em>示例:学校设有1名专职数据首席官，负责全校数据管理工作，则选择「已配备」；学校校长兼职统筹全校数据管理工作，也选择「已配备」；若学校无专人负责数据管理，仅由各部门教师零散处理，则选择「未配备」。</em></p>
              </div>
            </el-popover>
          </div>
        </template>
        <el-radio-group v-model="formData.has_data_staff">
          <el-radio :label="true">已配备</el-radio>
          <el-radio :label="false">未配备</el-radio>
        </el-radio-group>
      </el-form-item>

        <template v-if="formData.has_data_staff">
          <el-form-item label="学校数据专职/兼职管理人员数量？">
            <div class="inline-inputs">
              <span>专职成员</span>
              <el-input-number v-model="formData.fulltime_staff_count" :min="0" :controls="false" />
              <span>人</span>
              <span style="margin-left: 30px">兼职成员</span>
              <el-input-number v-model="formData.parttime_staff_count" :min="0" :controls="false" />
              <span>人</span>
            </div>
          </el-form-item>

          <el-form-item label="学校专职兼职数据管理人员是否有明确的职务职责？" prop="has_clear_responsibilities">
            <el-radio-group v-model="formData.has_clear_responsibilities">
              <el-radio :label="true">已明确</el-radio>
              <el-radio :label="false">未明确</el-radio>
            </el-radio-group>
          </el-form-item>
        </template>

        <el-form-item prop="has_training">
        <template #label>
          <div class="label-with-hint">
            <span>2020年到2025年，相关人员是否参与数据相关的进修或培训？</span>
            <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
              <template #reference>
                <span class="hint-tag">填写提示</span>
              </template>
              <div class="hint-body">
                <p class="hint-text">2020年到2025年期间 ，学校数据相关人员参加的与数据管理、数据分析、数据安全等主题相关的外部进修或校内培训。</p>
                <p class="hint-example"><em>示例：数据管理员2023年参加了市级“数据分析”培训、2024年参加了校内“数据安全规范”培训，则选择「有参与」；若未参加任何相关进修、培训，则选择「未参与」。</em></p>
              </div>
            </el-popover>
          </div>
        </template>
        <el-radio-group v-model="formData.has_training">
          <el-radio :label="true">有参与</el-radio>
          <el-radio :label="false">未参与</el-radio>
        </el-radio-group>
      </el-form-item>

        <template v-if="formData.has_training">
          <el-form-item label="2020年到2025年，学校数据人员进修或培训的次数？" prop="training_count">
            <el-input-number v-model="formData.training_count" :min="0" :controls="false" />
            <span class="unit">次</span>
          </el-form-item>

          <el-form-item label="2020年到2025年，相关人员获得的数据相关认证或考核证书数量？">
            <div class="inline-inputs">
              <span>国家级</span>
              <el-input-number v-model="formData.national_cert_count" :min="0" :controls="false" />
              <span>个</span>
              <span style="margin-left: 30px">省级</span>
              <el-input-number v-model="formData.provincial_cert_count" :min="0" :controls="false" />
              <span>个</span>
              <span style="margin-left: 30px">市级及以下</span>
              <el-input-number v-model="formData.city_cert_count" :min="0" :controls="false" />
              <span>个</span>
            </div>
          </el-form-item>
        </template>

        <!-- 3. 数据管理文件 -->
        <div class="section-title">3. 数据管理文件</div>
        
        <el-form-item prop="has_management_doc">
        <template #label>
          <div class="label-with-hint">
            <span>学校是否出台与数据管理制度相关的文件？</span>
            <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
              <template #reference>
                <span class="hint-tag">填写提示</span>
              </template>
              <div class="hint-body">
                <p class="hint-text">学校发布的规范数据采集、存储、使用、安全、共亨等流程的正式制度性文件（如管理办法、规定。细则等）。</p>
                <p class="hint-example"><em>示例：学校印发了《校园数据安全管理办法》《教育数据采集与共享规定》，则选择「已出台」；若未发布任何数据管理制度类文件，则选择未出台」。</em></p>
              </div>
            </el-popover>
          </div>
        </template>
        <el-radio-group v-model="formData.has_management_doc">
          <el-radio :label="true">已出台</el-radio>
          <el-radio :label="false">未出台</el-radio>
        </el-radio-group>
      </el-form-item>

        <template v-if="formData.has_management_doc">
          <el-form-item label="学校出台的与数据管理相关文件的份数？">
            <div class="inline-inputs">
              <el-input-number v-model="formData.management_doc_count" :min="0" :controls="false" />
              <span>份</span>
            </div>
          </el-form-item>

          <el-form-item label="上传数据管理相关文件：">
            <div class="upload-section">
              <el-upload
                v-if="!isReadonly"
                :action="uploadUrl"
                :headers="uploadHeaders"
                :data="{ file_type: 'management' }"
                :on-success="handleManagementUploadSuccess"
                :on-error="handleUploadError"
                :on-remove="handleManagementFileRemove"
                :file-list="managementFileList"
                :before-upload="beforeUpload"
              >
                <el-button type="primary">点击上传</el-button>
              </el-upload>
              <div v-else class="readonly-file-list">
                <div v-for="file in managementFileList" :key="file.uid" class="file-item">
                  <el-link :href="file.url" target="_blank">{{ file.name }}</el-link>
                </div>
                <span v-if="!managementFileList.length" class="no-file">暂无文件</span>
              </div>
              <div class="upload-tip" v-if="!isReadonly">支持上传PDF、Word、图片等格式，单个文件不超过10MB</div>
            </div>
          </el-form-item>
        </template>

        <el-form-item prop="has_practice_doc">
        <template #label>
          <div class="label-with-hint">
            <span>学校是否出台与数据实践指导相关的文件？</span>
            <el-popover placement="top-start" :width="350" trigger="hover" popper-class="custom-hint-popper">
              <template #reference>
                <span class="hint-tag">填写提示</span>
              </template>
              <div class="hint-body">
                <p class="hint-text">学校发布的指导教师、各部门在教学、管理、评价等场景中具体应用数据的操作性文件（如应用指南、实施细则、操作手册等）。</p>
                <p class="hint-example"><em>示例：学校发布了《教学数据分析与应用指南》《学生成长数据解读操作手册》，则选择「已出台」；若未发布任何数据实践指导类文件，则选择「未出台」。</em></p>
              </div>
            </el-popover>
          </div>
        </template>
        <el-radio-group v-model="formData.has_practice_doc">
          <el-radio :label="true">已出台</el-radio>
          <el-radio :label="false">未出台</el-radio>
        </el-radio-group>
      </el-form-item>

        <template v-if="formData.has_practice_doc">
          <el-form-item label="学校出台的与数据实践指导相关文件的份数？">
            <div class="inline-inputs">
              <el-input-number v-model="formData.practice_doc_count" :min="0" :controls="false" />
              <span>份</span>
            </div>
          </el-form-item>

          <el-form-item label="上传数据实践指导相关文件：">
            <div class="upload-section">
              <el-upload
                v-if="!isReadonly"
                :action="uploadUrl"
                :headers="uploadHeaders"
                :data="{ file_type: 'practice' }"
                :on-success="handlePracticeUploadSuccess"
                :on-error="handleUploadError"
                :on-remove="handlePracticeFileRemove"
                :file-list="practiceFileList"
                :before-upload="beforeUpload"
              >
                <el-button type="primary">点击上传</el-button>
              </el-upload>
              <div v-else class="readonly-file-list">
                <div v-for="file in practiceFileList" :key="file.uid" class="file-item">
                  <el-link :href="file.url" target="_blank">{{ file.name }}</el-link>
                </div>
                <span v-if="!practiceFileList.length" class="no-file">暂无文件</span>
              </div>
              <div class="upload-tip" v-if="!isReadonly">支持上传PDF、Word、图片等格式，单个文件不超过10MB</div>
            </div>
          </el-form-item>
        </template>
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
  has_leadership_group: null,
  meeting_activity_count: null,
  has_data_staff: null,
  fulltime_staff_count: null,
  parttime_staff_count: null,
  has_clear_responsibilities: null,
  has_training: null,
  training_count: null,
  national_cert_count: null,
  provincial_cert_count: null,
  city_cert_count: null,
  has_management_doc: null,
  management_doc_count: null,
  management_doc_files: [],
  has_practice_doc: null,
  practice_doc_count: null,
  practice_doc_files: []
})

// 表单验证规则
const formRules = {
  has_clear_responsibilities: [
    { required: true, message: '请选择是否有明确职务职责', trigger: 'change' }
  ]
}

// 文件列表
const managementFileList = computed(() => {
  return (formData.value.management_doc_files || []).map((file, index) => ({
    name: file.name,
    url: file.url,
    uid: file.path || index,  // 使用path作为唯一标识
    path: file.path  // 保存path用于删除
  }))
})

const practiceFileList = computed(() => {
  return (formData.value.practice_doc_files || []).map((file, index) => ({
    name: file.name,
    url: file.url,
    uid: file.path || index,
    path: file.path
  }))
})

// 上传配置
const uploadUrl = computed(() => {
  return `/api/assessments/${assessmentId.value}/institution/upload/`
})

const uploadHeaders = computed(() => {
  const token = localStorage.getItem('access_token')
  return {
    'Authorization': `Bearer ${token}`
  }
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
    
    // 获取数据制度数据
    const response = await fetch(`/api/assessments/${assessmentId.value}/institution/`, {
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
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    saving.value = true
    const response = await fetch(`/api/assessments/${assessmentId.value}/save_institution/`, {
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

// 文件上传
const beforeUpload = (file) => {
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过10MB')
  }
  return isLt10M
}

const handleManagementUploadSuccess = (response) => {
  ElMessage.success('文件上传成功')
  formData.value.management_doc_files = formData.value.management_doc_files || []
  formData.value.management_doc_files.push(response.file)
}

const handlePracticeUploadSuccess = (response) => {
  ElMessage.success('文件上传成功')
  formData.value.practice_doc_files = formData.value.practice_doc_files || []
  formData.value.practice_doc_files.push(response.file)
}

const handleUploadError = (error) => {
  console.error('上传失败:', error)
  ElMessage.error('文件上传失败')
}

// 删除管理制度文件
const handleManagementFileRemove = async (file) => {
  try {
    const filePath = file.path || file.response?.file?.path
    if (!filePath) {
      ElMessage.error('无法获取文件路径')
      return
    }

    // 调用后端删除接口
    const response = await fetch(`/api/assessments/${assessmentId.value}/institution/delete-file/`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({
        file_type: 'management',
        file_path: filePath
      })
    })

    if (response.ok) {
      // 从本地数据中删除
      formData.value.management_doc_files = formData.value.management_doc_files.filter(
        f => f.path !== filePath
      )
      ElMessage.success('文件删除成功')
    } else {
      throw new Error('删除失败')
    }
  } catch (error) {
    console.error('删除文件失败:', error)
    ElMessage.error('文件删除失败')
  }
}

// 删除实践指导文件
const handlePracticeFileRemove = async (file) => {
  try {
    const filePath = file.path || file.response?.file?.path
    if (!filePath) {
      ElMessage.error('无法获取文件路径')
      return
    }

    // 调用后端删除接口
    const response = await fetch(`/api/assessments/${assessmentId.value}/institution/delete-file/`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({
        file_type: 'practice',
        file_path: filePath
      })
    })

    if (response.ok) {
      // 从本地数据中删除
      formData.value.practice_doc_files = formData.value.practice_doc_files.filter(
        f => f.path !== filePath
      )
      ElMessage.success('文件删除成功')
    } else {
      throw new Error('删除失败')
    }
  } catch (error) {
    console.error('删除文件失败:', error)
    ElMessage.error('文件删除失败')
  }
}

// 返回评估列表
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
.data-institution-container {
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

.institution-form {
  margin-top: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #409eff;
  margin: 30px 0 20px 0;
  padding-left: 0;   /* 去掉左侧内边距，让文字对齐左侧 */
  border-left: none; /* 去掉蓝色竖线 */
}

.inline-inputs {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-count-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px 30px;
}

.upload-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
}

.unit {
  margin-left: 10px;
  color: #606266;
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

:deep(.el-upload__tip) {
  margin-top: 5px;
  font-size: 12px;
  color: #909399;
}

:deep(.el-input-number) {
  width: 120px;
}

:deep(.el-input-number .el-input__inner) {
  text-align: center;
}

:deep(.el-radio-group) {
  display: flex;
  gap: 30px;
}

:deep(.el-radio) {
  margin-right: 0;
}

:deep(.el-upload) {
  width: 100%;
}

:deep(.el-upload-list) {
  margin-top: 10px;
}

.readonly-file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.readonly-file-list .file-item {
  padding: 5px 0;
}

.readonly-file-list .no-file {
  color: #909399;
  font-size: 14px;
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
