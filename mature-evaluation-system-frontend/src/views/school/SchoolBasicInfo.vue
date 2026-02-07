<template>
  <div class="basic-info-page">
    <!-- 顶部蓝色横幅 -->
    <div class="info-banner">
      <div class="banner-content">
        <h2>学校基本信息采集</h2>
        <p class="subtitle">欢迎参加中小学校数据文化成熟度评估！在开始五个维度的评估之前，请先填写学校的基础信息。</p>
        <p class="promise">请确保每部分填写的信息准确无误，这将有助于我们为您提供更精准的评估分析结果。我们郑重承诺，所有信息将严格保密，仅用于评估分析目的。</p>
      </div>
    </div>

    <main class="info-main", v-loading="loading">
      <div class="info-card">
        <!-- 顶部流程示意图 -->
        <div class="process-wrapper">
          <div class="process-steps">
            <div class="step-item active">
              <div class="step-icon literacy"><el-icon><User /></el-icon></div>
              <span class="step-text">数据素养</span>
            </div>
            <div class="step-arrow"><el-icon><ArrowRight /></el-icon></div>
            <div class="step-item">
              <div class="step-icon system"><el-icon><Checked /></el-icon></div>
              <span class="step-text">数据制度</span>
            </div>
            <div class="step-arrow"><el-icon><ArrowRight /></el-icon></div>
            <div class="step-item">
              <div class="step-icon behavior"><el-icon><DataLine /></el-icon></div>
              <span class="step-text">数据行为</span>
            </div>
            <div class="step-arrow"><el-icon><ArrowRight /></el-icon></div>
            <div class="step-item">
              <div class="step-icon asset"><el-icon><Box /></el-icon></div>
              <span class="step-text">数据资产</span>
            </div>
            <div class="step-arrow"><el-icon><ArrowRight /></el-icon></div>
            <div class="step-item">
              <div class="step-icon tech"><el-icon><Cpu /></el-icon></div>
              <span class="step-text">数据技术</span>
            </div>
          </div>
          <div class="process-tip">
            温馨提示：完成基础信息填写后，系统将引导您按上述流程完成五个板块的分析评估。
          </div>
        </div>

        <!-- 表单区域 -->
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
                <!-- 设置为 disabled，因为这是账号固有的信息 -->
                <el-input v-model="form.school_name" disabled />
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
                <!-- 自动填充的地区，设置为只读 -->
                <el-input v-model="form.area_display" disabled placeholder="省/市/区（县）" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="建校年份" prop="founding_year">
                <!-- 允许填写的补充信息 -->
                <el-input v-model="form.founding_year" placeholder="如：1985" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="40">
            <el-col :span="12">
              <el-form-item label="在校学生总数" prop="student_count">
                <el-input v-model.number="form.student_count" placeholder="人数" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="教职工总数" prop="teacher_count">
                <el-input v-model.number="form.teacher_count" placeholder="人数" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>

      <div class="submit-wrapper">
        <el-button type="primary" size="large" class="start-btn" @click="handleStart">
          开始评估
        </el-button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive,onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User, ArrowRight, DataLine, Checked, Box, Cpu } from '@element-plus/icons-vue'
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
  // 先把本地有的名字填上，避免页面完全空白
  const storedUser = JSON.parse(localStorage.getItem('user'))
  if (storedUser) {
    form.school_name = storedUser.school_name || storedUser.username || ''
  }

  // 
  try {
    const res = await request({
      url: '/school/info/', 
      method: 'get'
    })
    
    if (res.data) {
      const data = res.data
      form.school_name = data.school_name || data.name || data.full_name || form.school_name
      // 优先使用后端返回的显示名称，没有则手动映射
      form.school_type = data.school_type_display || typeMap[data.school_type] || data.school_type
      // 拼接地区
      form.area_display = `${data.province} / ${data.city} / ${data.district}`
      
      // 如果之前填过，也可以顺便把这几个填上
      form.founding_year = data.founding_year || ''
      form.student_count = data.student_count || null
      form.teacher_count = data.teacher_count || null
    }
  } catch (error) {
    console.error('获取学校详情失败:', error)
    ElMessage.error('无法加载学校信息，请刷新页面')
  } finally {
    loading.value = false
  }
})

const handleStart = async () => {
  if (!formRef.value) return
  
  // 1. 表单校验
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // 2. 调用你后端的 school/update/ 接口
        const res = await request({
          url: '/school/update-count/', // 👈 对应你刚才给我的后端路由
          method: 'post',         // 对应视图里的 @api_view(['POST'])
          data: {
            student_count: form.student_count,
            teacher_count: form.teacher_count
          }
        })
        
        // 3. 判断是否成功（根据后端返回结构判断，通常 res.success 或 res.data 存在即可）
        if (res) {
          ElMessage.success('基础信息确认成功，进入评估')
          // 4. 跳转到正式评估导航页
          router.push('/school/assessment')
        }
      } catch (error) {
        console.error('保存信息失败:', error)
        ElMessage.error(error.response?.data?.error || '服务器开小差了，请重试')
      } finally {
        loading.value = false
      }
    } else {
      ElMessage.warning('请检查输入内容是否完整')
    }
  })
}
</script>

<style scoped>
.basic-info-page {
  min-height: 100vh;
  background-color: #f0f2f5;
  padding-bottom: 50px;
}

.info-banner {
  background-color: #1e5ba0; /* 深蓝色背景 */
  background: linear-gradient(135deg, #1e5ba0 0%, #2980b9 100%);
  color: white;
  padding: 60px 20px;
  text-align: left;
}

.banner-content {
  max-width: 1000px;
  margin: 0 auto;
}

.banner-content h2 {
  font-size: 28px;
  margin-bottom: 20px;
}

.banner-content .subtitle {
  font-size: 18px;
  margin-bottom: 15px;
  opacity: 0.9;
}

.banner-content .promise {
  font-size: 15px;
  line-height: 1.6;
  opacity: 0.8;
}

.info-main {
  max-width: 1000px;
  margin: -40px auto 0;
}

.info-card {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}

/* 流程图样式 */
.process-wrapper {
  background-color: #f0f7ff;
  border: 1px solid #d0e4ff;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 40px;
  text-align: center;
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
  gap: 10px;
  color: #606266;
}

.step-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  background-color: #909399; /* 默认灰色 */
}

/* 各个维度的颜色 */
.step-icon.literacy { background-color: #1abc9c; }
.step-icon.system { background-color: #9b59b6; }
.step-icon.behavior { background-color: #e67e22; }
.step-icon.asset { background-color: #5c6bc0; }
.step-icon.tech { background-color: #26c6da; }

.step-text {
  font-size: 14px;
  font-weight: bold;
}

.step-arrow {
  color: #dcdfe6;
  font-size: 20px;
}

.process-tip {
  font-size: 14px;
  color: #409eff;
}

/* 表单样式 */
.info-form :deep(.el-form-item__label) {
  font-weight: bold;
  color: #303133;
}

.info-form :deep(.el-input__wrapper) {
  height: 45px;
  background-color: #f8f9fb;
}

.submit-wrapper {
  text-align: center;
  margin-top: 40px;
}

.start-btn {
  width: 280px;
  height: 50px;
  font-size: 18px;
  background-color: #4da1ff;
  border: none;
  border-radius: 8px;
}

.start-btn:hover {
  background-color: #3d8ae5;
}
</style>