<template>
  <div class="create-region-admin-page">
    <el-card class="form-card">
      <template #header>
        <div class="card-header">
          <span>创建单个区域账号</span>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="110px"
        class="region-form"
      >
        <div class="section-title">区域基本信息</div>

        <el-form-item label="省份" prop="provinceCode">
        <el-select
          v-model="form.provinceCode"
          placeholder="请选择省份"
          style="width: 100%"
          filterable
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

      <el-form-item label="城市" prop="cityCode">
        <el-select
          v-model="form.cityCode"
          placeholder="请选择城市"
          style="width: 100%"
          filterable
          :disabled="!form.provinceCode"
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

      <el-form-item label="区县" prop="districtCode">
        <el-select
          v-model="form.districtCode"
          placeholder="请选择区县"
          style="width: 100%"
          filterable
          :disabled="!form.cityCode"
        >
          <el-option
            v-for="item in districtOptions"
            :key="item.code"
            :label="item.name"
            :value="item.code"
          />
        </el-select>
      </el-form-item>

        <el-divider />

        <div class="section-title">联系人信息</div>

        <el-form-item label="联系人姓名" prop="contact_name">
          <el-input v-model="form.contact_name" placeholder="请输入负责人姓名" />
        </el-form-item>

        <el-form-item label="职务" prop="contact_position">
          <el-input v-model="form.contact_position" placeholder="请输入职务或岗位" />
        </el-form-item>

        <el-form-item label="联系电话" prop="contact_phone">
          <el-input v-model="form.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>

        <el-divider />

        <div class="section-title">账号信息</div>

        <el-form-item label="联系邮箱" prop="contact_email">
          <el-input v-model="form.contact_email" placeholder="请输入联系人邮箱" />
        </el-form-item>

        <el-form-item label="用户名" prop="username">
          <div class="inline-row">
            <el-input
              v-model="form.username"
              placeholder="可手动填写，或随机生成"
            />
            <el-button @click="generateUsername">随机生成</el-button>
          </div>
        </el-form-item>

        <el-form-item label="初始密码" prop="password">
          <div class="inline-row">
            <el-input
              v-model="form.password"
              show-password
              placeholder="8位数字或字母组合"
            />
            <el-button @click="generatePassword">重新生成</el-button>
            <el-button @click="copyPassword">复制</el-button>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="submitForm">
            创建
          </el-button>
          <el-button @click="resetForm">
            重置
          </el-button>
          <el-button @click="goBack">
            返回列表
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>
<script setup>
import { reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { apiPost } from '@/utils/api'
import { regionData, codeToText } from 'element-china-area-data'
import { gatProvinces, gatChildren, gatCodeToText } from '@/utils/gat_area_patch'

const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)

const form = reactive({
  province: '',
  city: '',
  district: '',
  district_code: '',

  provinceCode: '',
  cityCode: '',
  districtCode: '',

  contact_name: '',
  contact_position: '',
  contact_phone: '',
  contact_email: '',
  username: '',
  password: ''
})

const codeToTextFull = {
  ...codeToText,
  ...gatCodeToText
}

const provinceOptions = ref([])
const cityOptions = ref([])
const districtOptions = ref([])

provinceOptions.value = [
  ...regionData.map(p => ({
    code: p.value,
    name: p.label,
    children: p.children || []
  })),
  ...gatProvinces.map(p => ({
    code: p.code,
    name: p.name,
    children: []
  }))
]

const onProvinceChange = (provinceCode) => {
  form.cityCode = ''
  form.districtCode = ''
  form.city = ''
  form.district = ''
  form.district_code = ''

  cityOptions.value = []
  districtOptions.value = []

  form.province = codeToTextFull[provinceCode] || ''

  // 港澳：用自身作为“城市”层
  if (provinceCode === '810000' || provinceCode === '820000') {
    cityOptions.value = [
      {
        code: provinceCode,
        name: form.province,
        children: []
      }
    ]
    return
  }

  // 台湾
  if (provinceCode === '710000') {
    const m = gatChildren['710000'] || {}
    cityOptions.value = Object.entries(m).map(([code, name]) => ({
      code,
      name,
      children: []
    }))
    return
  }

  // 大陆地区
  const provinceItem = regionData.find(item => item.value === provinceCode)
  cityOptions.value = (provinceItem?.children || []).map(city => ({
    code: city.value,
    name: city.label,
    children: city.children || []
  }))
}

const onCityChange = (cityCode) => {
  form.districtCode = ''
  form.district = ''
  form.district_code = ''

  districtOptions.value = []
  form.city = codeToTextFull[cityCode] || ''

  // 港澳
  if (cityCode === '810000' || cityCode === '820000') {
    const m = gatChildren[cityCode] || {}
    districtOptions.value = Object.entries(m).map(([code, name]) => ({
      code,
      name
    }))
    return
  }

  // 台湾
  if (cityCode && cityCode.startsWith('71')) {
    const m = gatChildren[cityCode] || {}
    districtOptions.value = Object.entries(m).map(([code, name]) => ({
      code,
      name
    }))
    return
  }

  // 大陆地区
  const cityItem = cityOptions.value.find(item => item.code === cityCode)
  districtOptions.value = (cityItem?.children || []).map(district => ({
    code: district.value,
    name: district.label
  }))
}

watch(
  () => form.districtCode,
  (newCode) => {
    form.district = codeToTextFull[newCode] || ''
    form.district_code = newCode || ''
  }
)

const rules = {
  provinceCode: [
  { required: true, message: '请选择省份', trigger: 'change' }
  ],
  cityCode: [
    { required: true, message: '请选择城市', trigger: 'change' }
  ],
  districtCode: [
    { required: true, message: '请选择区县', trigger: 'change' }
  ],
  contact_name: [{ required: true, message: '请输入联系人姓名', trigger: 'blur' }],
  contact_position: [{ required: true, message: '请输入职务', trigger: 'blur' }],
  contact_phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    {
      pattern: /^1[3-9]\d{9}$/,
      message: '请输入正确的11位手机号',
      trigger: 'blur'
    }
  ],
  contact_email: [
    { required: true, message: '请输入联系邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    {
      pattern: /^[A-Za-z0-9]+$/,
      message: '用户名只能包含数字或字母',
      trigger: 'blur'
    }
  ],
  password: [
    { required: true, message: '请输入初始密码', trigger: 'blur' },
    {
      pattern: /^[A-Za-z0-9]{8}$/,
      message: '密码必须为8位数字或字母组合',
      trigger: 'blur'
    }
  ]
}

function randomString(length = 8) {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789'
  let result = ''
  for (let i = 0; i < length; i++) {
    result += chars[Math.floor(Math.random() * chars.length)]
  }
  return result
}

function generateUsername() {
  const city = form.city || ''
  const district = form.district || ''
  const seed = `${city}${district}`.replace(/\s+/g, '')

  if (seed) {
    form.username = `REGION${randomString(4).toUpperCase()}`
  } else {
    form.username = `REGION${randomString(4).toUpperCase()}`
  }
}

function generatePassword() {
  form.password = randomString(8)
}

function copyPassword() {
  if (!form.password) {
    ElMessage.warning('暂无密码可复制')
    return
  }

  navigator.clipboard.writeText(form.password)
  ElMessage.success('密码已复制')
}

function resetForm() {
  formRef.value?.resetFields()

  form.province = ''
  form.city = ''
  form.district = ''
  form.district_code = ''

  form.provinceCode = ''
  form.cityCode = ''
  form.districtCode = ''

  form.username = ''
  form.password = ''

  cityOptions.value = []
  districtOptions.value = []
}

function goBack() {
  router.push('/admin/applications')
}

async function submitForm() {
  await formRef.value?.validate()

  submitting.value = true

  try {
    const payload = {
    province: form.province,
    city: form.city,
    district: form.district,
    district_code: form.district_code,

    contact_name: form.contact_name,
    contact_position: form.contact_position,
    contact_phone: form.contact_phone,
    contact_email: form.contact_email,
    username: form.username,
    password: form.password
  }

    const { data: resp } = await apiPost('/api/admin/create-region-admin/', payload)

    if (!resp?.success) {
      throw new Error(resp?.message || '创建失败')
    }

    ElMessage.success('区域管理员账号创建成功')
    router.push('/admin/applications')
  } catch (error) {
  console.error('创建区域管理员失败:', error)

  ElMessage.error(
    getErrorMessage(error, '创建失败，请检查区域、邮箱或用户名是否已存在')
  )
} finally {
  submitting.value = false
}
}

function getErrorMessage(error, fallback = '操作失败') {
  const data = error?.response?.data

  if (data?.message) return data.message
  if (data?.error?.message) return data.error.message
  if (data?.detail) return data.detail

  if (error?.message && error.message !== '非JSON响应') {
    return error.message
  }

  return fallback
}
</script>
<style scoped>
.create-region-admin-page {
  padding: 20px;
  background: #f4f6f9;
  min-height: 100vh;
}

.form-card {
  max-width: 980px;
  margin: 0 auto;
}

.card-header {
  font-size: 18px;
  font-weight: 700;
}

.region-form {
  max-width: 720px;
}

.section-title {
  margin: 18px 0 14px;
  padding-left: 10px;
  border-left: 3px solid #409eff;
  font-size: 15px;
  font-weight: 700;
  color: #303133;
}

.inline-row {
  display: flex;
  gap: 10px;
  width: 100%;
}

.inline-row .el-input {
  flex: 1;
}
</style>