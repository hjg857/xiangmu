<template>
  <div class="apply-container">
    <div class="apply-box">
      <!-- 头部 -->
      <div class="apply-header">
        <el-icon :size="32" color="#409EFF">
          <UserFilled />
        </el-icon>
        <h1 class="apply-title">账号申请</h1>
        <el-button
          class="back-button"
          @click="goToLogin"
        >
        <el-icon class="back-icon">
        <ArrowLeft />
        </el-icon>
          返回登录
        </el-button>

      </div>

      <div class="apply-info">
        如您尚未注册账号，请填写以下信息进行申请，系统将在一个工作日内将账号和密码发送至您的邮箱。
      </div>


      <!-- 申请表单 -->
      <el-form
        ref="applyFormRef"
        :model="applyForm"
        :rules="applyRules"
        label-width="100px"
        size="large"
      >
        <!-- 学校基本信息 -->
        <div class="form-section">
          <h3 class="section-title">学校基本信息</h3>
          
          <el-form-item label="学校全称" prop="school_name">
            <el-input
              v-model="applyForm.school_name"
              placeholder="请输入学校官方全称"
            />
          </el-form-item>

          <el-form-item label="学校类型" prop="school_type">
            <el-select
              v-model="applyForm.school_type"
              placeholder="请选择学校类型"
              style="width: 100%"
            >
              <el-option label="小学" value="primary" />
              <el-option label="初中" value="junior" />
              <el-option label="高中" value="senior" />
              <el-option label="九年一贯制" value="nine_year" />
              <el-option label="十二年一贯制" value="twelve_year" />
            </el-select>
          </el-form-item>

          <el-form-item label="省份" prop="provinceCode">
            <el-select
              v-model="applyForm.provinceCode"
              placeholder="请选择省份"
              style="width: 100%"
              @change="onProvinceChange"
            >
              <el-option
                v-for="item in provinceOptions"
                :key="item.code"
                :label="item.name"
                :value="item.code"
              />
            </el-select>
          </el-form-item>

          <!-- 市 -->
          <el-form-item label="城市" prop="cityCode">
            <el-select
              v-model="applyForm.cityCode"
              placeholder="请选择城市"
              style="width: 100%"
              :disabled="!applyForm.provinceCode"
              @change="onCityChange"
            >
              <el-option
                v-for="item in cityOptions"
                :key="item.code"
                :label="item.name"
                :value="item.code"
              />
            </el-select>
          </el-form-item>

          <!-- 区县 -->
          <el-form-item label="区县" prop="districtCode">
            <el-select
              v-model="applyForm.districtCode"
              placeholder="请选择区县"
              style="width: 100%"
              :disabled="!applyForm.cityCode"
            >
              <el-option
                v-for="item in districtOptions"
                :key="item.code"
                :label="item.name"
                :value="item.code"
              />
            </el-select>
          </el-form-item>
        </div>
        <!-- 联系人信息 -->
        <div class="form-section">
          <h3 class="section-title">联系人信息</h3>
          
          <el-form-item label="联系人姓名" prop="contact_name">
            <el-input
              v-model="applyForm.contact_name"
              placeholder="负责系统的主要联系人"
            />
          </el-form-item>

          <el-form-item label="职务" prop="contact_position">
            <el-input
              v-model="applyForm.contact_position"
              placeholder="请输入您的职务或岗位"
            />
          </el-form-item>

          <el-form-item label="联系电话" prop="contact_phone">
            <el-input
              v-model="applyForm.contact_phone"
              placeholder="请填写真实联系电话"
            />
          </el-form-item>

          <el-form-item label="电子邮箱" prop="contact_email">
            <el-input
              v-model="applyForm.contact_email"
              placeholder="常用邮箱地址"
            />
            <div class="form-tip">
              审核通过后，系统将自动生成账号和密码并发送至此邮箱
            </div>
          </el-form-item>
        </div>



        <!-- 提交按钮 -->
        <el-button
          type="warning"
          size="large"
          :loading="loading"
          @click="handleSubmit"
          class="submit-button"
        >
          提交申请
        </el-button>
      </el-form>
    </div>

    <div class="footer">
      © 2025 苏师YangTeam 版权所有
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createApplication } from '@/api/school'
import { ArrowLeft } from '@element-plus/icons-vue'
import { regionData, codeToText} from 'element-china-area-data'
import { gatProvinces, gatChildren, gatCodeToText } from '@/utils/gat_area_patch'

const router = useRouter()

const applyFormRef = ref(null)
const loading = ref(false)

/**
 * ✅ 保留原来的 province/city/district（提交后端用）
 * ✅ 新增 provinceCode/cityCode/districtCode（选择联动用）
 */
const applyForm = reactive({
  school_name: '',
  school_type: '',

  province: '',
  city: '',
  district: '',

  provinceCode: '',
  cityCode: '',
  districtCode: '',

  contact_name: '',
  contact_position: '',
  contact_phone: '',
  contact_email: ''
})

/** ✅ 合并后的 codeToText（港澳台补全） */
const codeToTextFull = { ...codeToText, ...gatCodeToText }

/** 省市区选项 */
const provinceOptions = ref([])
const cityOptions = ref([])
const districtOptions = ref([])

/** ✅ 初始化省份：大陆 + 港澳台 */
provinceOptions.value = [
  ...regionData.map(p => ({
    code: p.value,
    name: p.label,
    children: p.children || []
  })),
  ...gatProvinces.map(p => ({
    code: p.code,
    name: p.name,
    children: [] // 港澳台不走 regionData children
  }))
]

/** 省变化 -> 重置市/区 + 填充市列表 + 写回 province 文本 */
const onProvinceChange = (provinceCode) => {
  applyForm.cityCode = ''
  applyForm.districtCode = ''
  cityOptions.value = []
  districtOptions.value = []

  // 回填 province 中文
  applyForm.province = codeToTextFull[provinceCode] || ''

  // --- 港澳：没有市层级，但你要保留三个栏 -> 给一个“虚拟市”（省本身） ---
  if (provinceCode === '810000' || provinceCode === '820000') {
    cityOptions.value = [{ code: provinceCode, name: applyForm.province, children: [] }]
    // 这里不自动选中市，让用户点一下也行；想自动选中就取消下面两行注释
    // applyForm.cityCode = provinceCode
    // onCityChange(provinceCode)
    return
  }

  // --- 台湾：省 -> 市（7101xx...） ---
  if (provinceCode === '710000') {
    const m = gatChildren['710000'] || {}
    cityOptions.value = Object.entries(m).map(([code, name]) => ({
      code,
      name,
      children: [] // 台湾区县在 onCityChange 再取
    }))
    return
  }

  // --- 大陆：按 regionData 走 ---
  const p = regionData.find(x => x.value === provinceCode)
  cityOptions.value = (p?.children || []).map(c => ({
    code: c.value,
    name: c.label,
    children: c.children || []
  }))
}

const onCityChange = (cityCode) => {
  applyForm.districtCode = ''
  districtOptions.value = []

  // 回填 city 中文
  applyForm.city = codeToTextFull[cityCode] || ''

  // --- 港澳：cityCode == provinceCode，district 直接取省下面的区县 ---
  if (cityCode === '810000' || cityCode === '820000') {
    const m = gatChildren[cityCode] || {}
    districtOptions.value = Object.entries(m).map(([code, name]) => ({ code, name }))
    return
  }

  // --- 台湾：district 取 cityCode 下的子项 ---
  if (cityCode && cityCode.startsWith('71')) {
    const m = gatChildren[cityCode] || {}
    districtOptions.value = Object.entries(m).map(([code, name]) => ({ code, name }))
    return
  }

  // --- 大陆：从 cityOptions.children 取区县 ---
  const c = cityOptions.value.find(x => x.code === cityCode)
  districtOptions.value = (c?.children || []).map(d => ({
    code: d.value,
    name: d.label
  }))
}

// 监听区县变化，回填 district 文本
watch(() => applyForm.districtCode, (newCode) => {
  applyForm.district = codeToTextFull[newCode] || ''
})

/** 校验 */
const validatePhone = (rule, value, callback) => {
  if (!value) callback(new Error('请输入联系电话'))
  else if (!/^1[3-9]\d{9}$/.test(value)) callback(new Error('请输入有效的手机号码'))
  else callback()
}

const validateEmail = (rule, value, callback) => {
  if (!value) callback(new Error('请输入电子邮箱'))
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) callback(new Error('请输入有效的邮箱地址'))
  else callback()
}

const applyRules = {
  school_name: [{ required: true, message: '请输入学校全称', trigger: 'blur' }],
  school_type: [{ required: true, message: '请选择学校类型', trigger: 'change' }],

  // 这里把 trigger 从 blur 改成 change（因为是 select）
  provinceCode: [{ required: true, message: '请选择省份', trigger: 'change' }],
  cityCode: [{ required: true, message: '请选择城市', trigger: 'change' }],
  districtCode: [{ required: true, message: '请选择区县', trigger: 'change' }],

  contact_name: [{ required: true, message: '请输入联系人姓名', trigger: 'blur' }],
  contact_position: [{ required: true, message: '请输入职务', trigger: 'blur' }],
  contact_phone: [{ required: true, validator: validatePhone, trigger: 'blur' }],
  contact_email: [{ required: true, validator: validateEmail, trigger: 'blur' }]
}

// 提交申请（你原逻辑基本不动）
const handleSubmit = async () => {
  if (!applyFormRef.value) return

  await applyFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      const res = await createApplication({
        school_name: applyForm.school_name,
        school_type: applyForm.school_type,
        province: applyForm.province,
        city: applyForm.city,
        district: applyForm.district,
        district_code: applyForm.districtCode, 
        contact_name: applyForm.contact_name,
        contact_position: applyForm.contact_position,
        contact_phone: applyForm.contact_phone,
        contact_email: applyForm.contact_email
      })

      if (res.success) {
        router.push({ name: 'apply-success', params: { id: res.data.id } })
      }
    } catch (error) {
      ElMessage.error(error.response?.data?.error?.message || '提交失败')
    } finally {
      loading.value = false
    }
  })
}

// 返回登录
const goToLogin = () => router.push('/login')
</script>


<style scoped>
.apply-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
}

.apply-box {
  max-width: 1000px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.apply-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  position: relative;
}

.apply-info {
  width: 100%;
  background: #f0f9eb;          
  color: #67c23a;               /* 绿色文字 */
  border: 1px solid #e1f3d8;    /* 浅边框 */
  border-radius: 6px;

  padding: 10px 14px;
  margin-bottom: 24px;

  font-size: 13px;
  line-height: 1.6;
}

.back-button {
  display: inline-flex;
  align-items: center;
  gap: 6px;

  padding: 6px 14px;
  height: 34px;

  background: #ffffff;
  border: 1px solid #cfe5ff;
  border-radius: 6px;

  color: #409eff;
  font-size: 13px;
  font-weight: 500;

  transition: all 0.2s ease;
}

.back-button:hover {
  background: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

.back-icon {
  font-size: 14px;
}


.apply-title {
  font-size: 24px;
  color: #303133;
  font-weight: 500;
  margin: 0;
}

.back-button {
  position: absolute;
  right: 0;
}

.apply-subtitle {
  color: #606266;
  font-size: 14px;
  margin-bottom: 30px;
  line-height: 1.6;
}

.form-section {
  margin-bottom: 30px;
}

.section-title {
  font-size: 16px;
  color: #303133;
  font-weight: 500;
  margin-bottom: 20px;
  padding-left: 12px;
  border-left: none;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.agreement-text {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
  margin-bottom: 16px;
}

.submit-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  background: #ff9800;
  border-color: #ff9800;
  margin-top: 20px;
}

.submit-button:hover {
  background: #fb8c00;
  border-color: #fb8c00;
}

.footer {
  text-align: center;
  color: #909399;
  font-size: 14px;
  margin-top: 30px;
}
</style>
