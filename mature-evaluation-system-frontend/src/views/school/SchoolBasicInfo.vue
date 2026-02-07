<template>
  <div class="basic-info-page">
    <!-- 顶部深色横幅 -->
    <div class="info-banner">
      <div class="banner-content">
        <h2 class="banner-title">学校基本信息采集</h2>
        <p class="subtitle">欢迎参加中小学校数据文化成熟度评估！在开始五个维度的评估之前，请先填写学校的基础信息。</p>
        <p class="promise">请确保每部分填写的信息准确无误，这将有助于我们为您提供更精准的评估分析结果。我们郑重承诺，所有信息将严格保密，仅用于评估分析目的。</p>
      </div>
    </div>

    <main class="info-main" v-loading="loading">
      <!-- 顶部流程示意图卡片 -->
      <div class="process-card">
        <div class="process-steps">
          <div class="step-item active">
            <div class="step-icon literacy"><el-icon><TrendCharts /></el-icon></div>
            <span class="step-text">数据素养</span>
          </div>
          <div class="step-arrow"><el-icon><ArrowRightBold /></el-icon></div>
          <div class="step-item">
            <div class="step-icon institution"><el-icon><Checked /></el-icon></div>
            <span class="step-text">数据制度</span>
          </div>
          <div class="step-arrow"><el-icon><ArrowRightBold /></el-icon></div>
          <div class="step-item">
            <div class="step-icon behavior"><el-icon><UserFilled /></el-icon></div>
            <span class="step-text">数据行为</span>
          </div>
          <div class="step-arrow"><el-icon><ArrowRightBold /></el-icon></div>
          <div class="step-item">
            <div class="step-icon asset"><el-icon><Coin /></el-icon></div>
            <span class="step-text">数据资产</span>
          </div>
          <div class="step-arrow"><el-icon><ArrowRightBold /></el-icon></div>
          <div class="step-item">
            <div class="step-icon tech"><el-icon><Connection /></el-icon></div>
            <span class="step-text">数据技术</span>
          </div>
        </div>
        <div class="process-tip">
          温馨提示：完成基础信息填写后，系统将引导您按上述流程完成五个板块的分析评估。
        </div>
      </div>

      <!-- 表单区域卡片 -->
      <div class="form-card">
        <el-form 
          ref="formRef"
          :model="form" 
          :rules="rules"
          label-position="top" 
          class="info-form"
        >
          <el-row :gutter="40">
            <el-col :span="12">
              <el-form-item label="学校全称">
                <el-input v-model="form.school_name" disabled placeholder="请输入公章全称" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="办学类型">
                <el-input v-model="form.school_type" disabled />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="40">
            <el-col :span="12">
              <el-form-item label="所属地区">
                <el-input v-model="form.area_display" disabled placeholder="省/市/区（县）" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="建校年份" prop="founding_year" required>
                <el-input v-model="form.founding_year" placeholder="如：1985" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="40">
            <el-col :span="12">
              <el-form-item label="在校学生总数" prop="student_count" required>
                <el-input v-model.number="form.student_count" placeholder="人数" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="教职工总数" prop="teacher_count" required>
                <el-input v-model.number="form.teacher_count" placeholder="人数" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>

        <div class="submit-wrapper">
          <el-button type="primary" size="large" class="start-btn" @click="handleStart">
            开始评估
          </el-button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  TrendCharts, Checked, UserFilled, Coin, Connection, 
  ArrowRightBold 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const router = useRouter()
const formRef = ref(null)
const loading = ref(true)

const form = reactive({
  school_name: '',
  school_type: '',
  area_display: '',
  founding_year: '',
  student_count: null,
  teacher_count: null
})

const rules = {
  founding_year: [{ required: true, message: '请输入建校年份', trigger: 'blur' }],
  student_count: [{ required: true, message: '请输入学生总数', trigger: 'blur' }],
  teacher_count: [{ required: true, message: '请输入教职工总数', trigger: 'blur' }]
}

const typeMap = {
  'primary': '小学',
  'junior': '初中',
  'senior': '高中',
  'nine_year': '九年一贯制',
  'twelve_year': '十二年一贯制'
}

onMounted(async () => {
  const storedUser = JSON.parse(localStorage.getItem('user'))
  if (storedUser) {
    form.school_name = storedUser.school_name || ''
  }

  try {
    const res = await request({ url: '/school/info/', method: 'get' })
    if (res.data) {
      const data = res.data
      form.school_name = data.school_name || form.school_name
      form.school_type = data.school_type_display || typeMap[data.school_type] || data.school_type
      form.area_display = `${data.province}/${data.city}/${data.district}`
      form.founding_year = data.founding_year || ''
      form.student_count = data.student_count || null
      form.teacher_count = data.teacher_count || null
    }
  } catch (error) {
    ElMessage.error('无法加载学校信息')
  } finally {
    loading.value = false
  }
})

const handleStart = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await request({
          url: '/school/update-count/',
          method: 'post',
          data: {
            student_count: form.student_count,
            teacher_count: form.teacher_count
          }
        })
        ElMessage.success('基础信息确认成功，进入评估')
        router.push('/school/assessment')
      } catch (error) {
        ElMessage.error('保存失败，请重试')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.basic-info-page {
  min-height: 100vh;
  background-color: #f0f2f5;
  padding-bottom: 60px;
  display: flex;
  flex-direction: column;
}

/* 顶部横幅 - 深蓝色 */
.info-banner {
  background-color: #34495e; 
  color: white;
  padding: 40px 20px 40px;
  text-align: left;
}

.banner-content {
  width: 95%;
  max-width: 1600px;
  margin: 0 auto;
}

.banner-title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 20px;
  color: #fff;
}

.subtitle {
  font-size: 16px;
  margin-bottom: 12px;
  color: #ecf0f1;
}

.promise {
  font-size: 14px;
  line-height: 1.6;
  color: #bdc3c7;
}

/* 主体容器 */
.info-main {
  width: 95%; 
  max-width: 1600px;
  margin: 30px auto 0;
  padding: 0 20px;
}

/* 流程图卡片 */
.process-card {
  background: white;
  border-radius: 15px;
  padding: 30px;
  margin-bottom: 25px;
  border: 1px solid #e0e6ed;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.process-steps {
  display: flex;
  justify-content: space-around;
  align-items: center;
  margin-bottom: 20px;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.step-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: white;
  background-color: #2C3E50; /* 默认深灰蓝 */
}

/* 维度颜色还原 */
.step-icon.literacy { background-color: #1abc9c; } /* 绿色 */
.step-icon.institution { background-color: #9b59b6; } /* 紫色 */
.step-icon.behavior { background-color: #f39c12; } /* 橙色 */
.step-icon.asset { background-color: #34495e; } /* 深蓝灰 */
.step-icon.tech { background-color: #16a085; } /* 青色 */

.step-text {
  font-size: 14px;
  color: #7f8c8d;
}

.step-item.active .step-text {
  color: #1abc9c;
  font-weight: bold;
}

.step-arrow {
  color: #dcdfe6;
  font-size: 16px;
}

.process-tip {
  font-size: 14px;
  color: #3498db;
  text-align: center;
  margin-top: 10px;
}

/* 表单卡片 */
.form-card {
  background: white;
  border-radius: 15px;
  padding: 40px;
  border: 1px solid #e0e6ed;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.info-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #34495e;
  padding-bottom: 8px;
}

/* 输入框圆角和背景还原 */
.info-form :deep(.el-input__wrapper) {
  height: 48px;
  border-radius: 10px;
  background-color: #ffffff;
  box-shadow: 0 0 0 1px #dcdfe6 inset;
}

.info-form :deep(.el-input.is-disabled .el-input__wrapper) {
  background-color: #f8f9fa;
}

.submit-wrapper {
  text-align: center;
  margin-top: 30px;
}

/* 按钮样式 */
.start-btn {
  width: 200px;
  height: 48px;
  font-size: 16px;
  font-weight: bold;
  border-radius: 10px;
  background-color: #3498db;
  border: none;
}

.start-btn:hover {
  background-color: #2980b9;
}
</style>