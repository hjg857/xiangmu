<template>
  <div class="page">
    <el-card>
      <template #header>
        <div class="header">
          <div>
            <div class="title">新增学校</div>
            <div class="sub">为当前区县创建学校账号并绑定学校基础信息</div>
          </div>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="110px"
        size="large"
      >
        <el-divider content-position="left">账号信息</el-divider>

        <el-form-item label="学校账号" prop="username">
          <el-input v-model="form.username" placeholder="可选，不填则自动生成" />
        </el-form-item>

        <el-form-item label="登录邮箱" prop="email">
          <el-input v-model="form.email" placeholder="必填，用于登录/找回" />
        </el-form-item>

        <el-form-item label="初始密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            placeholder="必填，至少8位"
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="password2">
          <el-input
            v-model="form.password2"
            type="password"
            show-password
            placeholder="再次输入密码"
          />
        </el-form-item>

        <el-divider content-position="left">学校基础信息</el-divider>

        <el-form-item label="学校全称" prop="name">
          <el-input v-model="form.name" placeholder="例如：南京市XX中学" />
        </el-form-item>

        <el-form-item label="学校类型" prop="school_type">
          <el-select v-model="form.school_type" placeholder="请选择">
            <el-option label="小学" value="primary" />
            <el-option label="初中" value="junior" />
            <el-option label="高中" value="senior" />
            <el-option label="九年一贯制" value="nine_year" />
            <el-option label="十二年一贯制" value="twelve_year" />
          </el-select>
        </el-form-item>

        <el-form-item label="省份" prop="province">
          <el-input v-model="form.province" placeholder="例如：江苏省" />
        </el-form-item>

        <el-form-item label="城市" prop="city">
          <el-input v-model="form.city" placeholder="例如：南京市" />
        </el-form-item>

        <el-form-item label="区县" prop="district">
          <el-input v-model="form.district" placeholder="例如：玄武区" />
        </el-form-item>

        <el-divider content-position="left">联系人信息</el-divider>

        <el-form-item label="联系人姓名" prop="contact_name">
          <el-input v-model="form.contact_name" />
        </el-form-item>

        <el-form-item label="联系人职务" prop="contact_position">
          <el-input v-model="form.contact_position" />
        </el-form-item>

        <el-form-item label="联系电话" prop="contact_phone">
          <el-input v-model="form.contact_phone" />
        </el-form-item>

        <el-form-item label="联系邮箱" prop="contact_email">
          <el-input v-model="form.contact_email" />
        </el-form-item>

        <el-alert
          type="warning"
          show-icon
          :closable="false"
          class="tip"
          title="提示"
          description="请将生成的学校账号和初始密码安全地告知学校。学校首次登录后建议修改密码。"
        />

        <div class="actions">
          <el-button @click="reset">重置</el-button>
          <el-button type="primary" :loading="loading" @click="submit">
            创建学校
          </el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { regionCreateSchool } from '@/api/regionAdmin'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  password: '',
  password2: '',
  name: '',
  school_type: '',
  province: '',
  city: '',
  district: '',
  contact_name: '',
  contact_position: '',
  contact_phone: '',
  contact_email: ''
})

const validatePassword2 = (rule, value, callback) => {
  if (!value) return callback(new Error('请再次输入密码'))
  if (value !== form.password) return callback(new Error('两次输入的密码不一致'))
  callback()
}

const rules = {
  email: [{ required: true, message: '请输入登录邮箱', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入初始密码', trigger: 'blur' },
    { min: 8, message: '密码至少8位', trigger: 'blur' }
  ],
  password2: [{ validator: validatePassword2, trigger: 'blur' }],

  name: [{ required: true, message: '请输入学校全称', trigger: 'blur' }],
  school_type: [{ required: true, message: '请选择学校类型', trigger: 'change' }],
  province: [{ required: true, message: '请输入省份', trigger: 'blur' }],
  city: [{ required: true, message: '请输入城市', trigger: 'blur' }],
  district: [{ required: true, message: '请输入区县', trigger: 'blur' }],

  contact_name: [{ required: true, message: '请输入联系人姓名', trigger: 'blur' }],
  contact_position: [{ required: true, message: '请输入联系人职务', trigger: 'blur' }],
  contact_phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
  contact_email: [{ required: true, message: '请输入联系邮箱', trigger: 'blur' }]
}

const goBack = () => router.back()

const reset = () => {
  if (!formRef.value) return
  formRef.value.resetFields()
}

const submit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      const payload = { ...form }
      delete payload.password2

      const res = await regionCreateSchool(payload)

      if (res?.success) {
        ElMessage.success(res.message || '创建成功')

        // 创建成功后跳回学校列表（你可以改成你想去的页面）
        router.push('/admin/region/schools')
      } else {
        ElMessage.error(res?.message || '创建失败')
      }
    } catch (e) {
      ElMessage.error(e?.response?.data?.message || e?.message || '创建失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.page { padding: 16px; }
.header { display:flex; justify-content:space-between; align-items:flex-start; gap:12px; }
.title { font-size: 18px; font-weight: 600; }
.sub { margin-top: 4px; font-size: 13px; color: #909399; }
.actions { margin-top: 16px; display:flex; justify-content:flex-end; gap: 10px; }
.tip { margin-top: 12px; }
</style>
