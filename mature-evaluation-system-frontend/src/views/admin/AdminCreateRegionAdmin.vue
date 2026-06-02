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

        <el-form-item label="省份" prop="province">
          <el-input v-model="form.province" placeholder="请输入省份，如：江苏省" />
        </el-form-item>

        <el-form-item label="城市" prop="city">
          <el-input v-model="form.city" placeholder="请输入城市，如：徐州市" />
        </el-form-item>

        <el-form-item label="区县" prop="district">
          <el-input v-model="form.district" placeholder="请输入区县，如：铜山区" />
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
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { apiPost } from '@/utils/api'

const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)

const form = reactive({
  province: '',
  city: '',
  district: '',
  contact_name: '',
  contact_position: '',
  contact_phone: '',
  contact_email: '',
  username: '',
  password: ''
})

const rules = {
  province: [{ required: true, message: '请输入省份', trigger: 'blur' }],
  city: [{ required: true, message: '请输入城市', trigger: 'blur' }],
  district: [{ required: true, message: '请输入区县', trigger: 'blur' }],
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
  form.username = ''
  form.password = ''
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
    console.error(error)
    ElMessage.error(error?.message || '创建失败')
  } finally {
    submitting.value = false
  }
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