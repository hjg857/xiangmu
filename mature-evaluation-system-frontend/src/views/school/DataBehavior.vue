<template>
  <div class="data-behavior-container">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button @click="handleBack" :icon="ArrowLeft">返回</el-button>
            <span class="title">数据行为评价</span>
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
        为全面评价您所在学校"数据行为"建设情况，请您按要求完成以下内容的填写。
      </el-alert>

      <el-form
        ref="formRef"
        :model="formData"
        label-position="top"
        class="behavior-form"
        :hide-required-asterisk="true"
        :disabled="isReadonly"
      >
        <!-- 1. 数据行为监测 -->
        <div class="section-title">1. 数据行为监测</div>
        
        <el-form-item label="2020年到2025年，全校教师/学生/管理者登录数据相关平台的人均频次？">
          <div class="inline-inputs">
            <span>教师人均登录平台</span>
            <el-input-number v-model="formData.teacher_login_freq" :min="0" :controls="false" />
            <span>次</span>
            <span style="margin-left: 30px">学生人均登录平台</span>
            <el-input-number v-model="formData.student_login_freq" :min="0" :controls="false" />
            <span>次</span>
            <span style="margin-left: 30px">管理者人均登录平台</span>
            <el-input-number v-model="formData.manager_login_freq" :min="0" :controls="false" />
            <span>次</span>
          </div>
        </el-form-item>

        <!-- 2. 数据应用成效 -->
        <div class="section-title">2. 数据应用成效</div>
        
        <el-form-item label="学校公开发表数据相关应用成果（论文、著作等）？">
          <div class="inline-inputs">
            <span>已发表论文</span>
            <el-input-number v-model="formData.published_paper_count" :min="0" :controls="false" />
            <span>篇</span>
            <span style="margin-left: 30px">已出版著作</span>
            <el-input-number v-model="formData.published_book_count" :min="0" :controls="false" />
            <span>部</span>
          </div>
        </el-form-item>

        <el-form-item label="学校数据相关应用成果入选教育信息化/数字化转型优秀或典型案例的情况？">
          <div class="inline-inputs">
            <span>国家级</span>
            <el-input-number v-model="formData.case_national_count" :min="0" :controls="false" />
            <span>个</span>
            <span style="margin-left: 30px">省级</span>
            <el-input-number v-model="formData.case_provincial_count" :min="0" :controls="false" />
            <span>个</span>
            <span style="margin-left: 30px">市级及以下</span>
            <el-input-number v-model="formData.case_city_count" :min="0" :controls="false" />
            <span>个</span>
          </div>
        </el-form-item>

        <el-form-item label="学校相关应用成果受到市级及以上荣誉奖励的情况？">
          <div class="inline-inputs">
            <span>国家级</span>
            <el-input-number v-model="formData.award_national_count" :min="0" :controls="false" />
            <span>个</span>
            <span style="margin-left: 30px">省级</span>
            <el-input-number v-model="formData.award_provincial_count" :min="0" :controls="false" />
            <span>个</span>
            <span style="margin-left: 30px">市级及以下</span>
            <el-input-number v-model="formData.award_city_count" :min="0" :controls="false" />
            <span>个</span>
          </div>
        </el-form-item>

        <el-form-item label="学校数据相关应用被官方媒体宣传报道的情况？">
          <div class="inline-inputs">
            <span>国家级</span>
            <el-input-number v-model="formData.media_national_count" :min="0" :controls="false" />
            <span>个</span>
            <span style="margin-left: 30px">省级</span>
            <el-input-number v-model="formData.media_provincial_count" :min="0" :controls="false" />
            <span>个</span>
            <span style="margin-left: 30px">市级及以下</span>
            <el-input-number v-model="formData.media_city_count" :min="0" :controls="false" />
            <span>个</span>
          </div>
        </el-form-item>

        <el-form-item label="学校在教育信息化/数字化转型会议、活动上作交流发言或经验分享的情况？">
          <div class="inline-inputs">
            <span>国家级</span>
            <el-input-number v-model="formData.conference_national_count" :min="0" :controls="false" />
            <span>个</span>
            <span style="margin-left: 30px">省级</span>
            <el-input-number v-model="formData.conference_provincial_count" :min="0" :controls="false" />
            <span>个</span>
            <span style="margin-left: 30px">市级及以下</span>
            <el-input-number v-model="formData.conference_city_count" :min="0" :controls="false" />
            <span>个</span>
          </div>
        </el-form-item>

        <el-form-item label="其他学校到本校参观学习数据建设、应用相关经验的情况？">
          <div class="inline-inputs">
            <span>其他学校参观学习</span>
            <el-input-number v-model="formData.visit_count" :min="0" :controls="false" />
            <span>次</span>
          </div>
        </el-form-item>

        <!-- 3. 学生/管理者/教师对数据应用效果的主观评价 -->
        <div class="section-title">学生/管理者/教师对数据应用效果的主观评价</div>
        
        <el-alert
          type="success"
          :closable="false"
          style="margin-bottom: 20px"
        >
          <p>该维度将通过问卷调查的方式，了解各主体对学校数据应用效果的主观评价。为便于数据采集，问卷（<strong>中小学校数据应用效果调查问卷</strong>）已全部整合到"数据素养评价"板块。</p>
        </el-alert>
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
  teacher_login_freq: null,
  student_login_freq: null,
  manager_login_freq: null,
  visit_count: null,
  published_paper_count: null,
  published_book_count: null,
  case_national_count: null,
  case_provincial_count: null,
  case_city_count: null,
  award_national_count: null,
  award_provincial_count: null,
  award_city_count: null,
  media_national_count: null,
  media_provincial_count: null,
  media_city_count: null,
  conference_national_count: null,
  conference_provincial_count: null,
  conference_city_count: null
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
    
    // 获取数据行为数据
    const response = await fetch(`/api/assessments/${assessmentId.value}/behavior/`, {
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
    const response = await fetch(`/api/assessments/${assessmentId.value}/save_behavior/`, {
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
.data-behavior-container {
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

.behavior-form {
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
  flex-wrap: wrap;
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

:deep(.el-input-number) {
  width: 120px;
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
