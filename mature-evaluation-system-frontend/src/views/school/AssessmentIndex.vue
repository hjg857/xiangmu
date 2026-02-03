<template>
  <div class="assessment-container">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-content">
        <div class="logo-section">
          <el-icon :size="32" color="#409eff">
            <School />
          </el-icon>
          <h1 class="system-title">中小学校数据文化成熟度评估监测系统</h1>
        </div>
        <nav class="nav-menu">
          <router-link to="/home" class="nav-item">返回首页</router-link>
          <el-dropdown class="user-dropdown">
            <span class="user-info">
              <el-icon><User /></el-icon>
              <span>{{ schoolName || '用户' }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </nav>
      </div>
    </header>

    <!-- 提交成功弹窗 -->
    <SubmissionSuccess 
      v-model="showSuccessModal" 
      @view-progress="handleViewProgress"
    />

    <!-- 评估进度展示 -->
    <div v-if="viewingProgress" class="progress-view-container">
      <AssessmentProgress 
        :status="assessmentStatus" 
        :assessment-id="currentAssessmentId"
        :times="assessmentTimes"
      />
    </div>

    <!-- 主体内容区 -->
    <div v-else class="main-container">
      <!-- 左侧导航 -->
      <aside class="sidebar">
        <div class="sidebar-title">评估模块</div>
        <el-menu
          :default-active="activeModule"
          class="assessment-menu"
          @select="handleModuleSelect"
        >
          <el-menu-item index="literacy" :class="menuItemClass('literacy')">
            <el-icon><Reading /></el-icon>
            <span>数据素养</span>

            <!-- 绿色对号：完成才显示 -->
            <el-icon v-if="moduleDone.literacy" class="done-check"><CircleCheckFilled /></el-icon>
          </el-menu-item>

          <el-menu-item index="institution" :class="menuItemClass('institution')">
            <el-icon><Document /></el-icon>
            <span>数据制度</span>
            <el-icon v-if="moduleDone.institution" class="done-check"><CircleCheckFilled /></el-icon>
          </el-menu-item>

          <el-menu-item index="behavior" :class="menuItemClass('behavior')">
            <el-icon><TrendCharts /></el-icon>
            <span>数据行为</span>
            <el-icon v-if="moduleDone.behavior" class="done-check"><CircleCheckFilled /></el-icon>
          </el-menu-item>

<el-menu-item index="asset" :class="menuItemClass('asset')">
  <el-icon><Files /></el-icon>
  <span>数据资产</span>
  <el-icon v-if="moduleDone.asset" class="done-check"><CircleCheckFilled /></el-icon>
</el-menu-item>

<el-menu-item index="technology" :class="menuItemClass('technology')">
  <el-icon><Setting /></el-icon>
  <span>数据技术</span>
  <el-icon v-if="moduleDone.technology" class="done-check"><CircleCheckFilled /></el-icon>
</el-menu-item>

        </el-menu>

        <!-- 提示信息 -->
        <div class="sidebar-tip">
          <el-icon><InfoFilled /></el-icon>
          <p>请逐项填写各模块内容，填写后请点击保存按钮</p>
        </div>

        <!-- 提交评估按钮 -->
        <div class="sidebar-action">
          <el-button
            type="primary"
            size="large"
            style="width: 100%"
            @click="handleSubmitAssessment"
            :loading="generatingReport"
            :disabled="assessmentStatus !== 'draft'"
          >
            {{ getActionButtonText() }}
          </el-button>
          
          <!-- 查看报告按钮 -->
          <el-button
            v-if="assessmentStatus === 'completed'"
            type="success"
            size="large"
            style="width: 100%"
            @click="handleViewReport"
          >
            查看报告
          </el-button>
        </div>
      </aside>

      <!-- 右侧内容区 -->
      <main class="content-area">
        <!-- 数据素养模块 -->
        <div v-if="activeModule === 'literacy'" class="module-content">
          <h2 class="module-title">数据素养评价</h2>
          
          <!-- 只读模式提示 -->
          <el-alert
            v-if="isReadonly"
            title="评价已完成，当前为只读模式，问卷已停止收集"
            type="warning"
            :closable="false"
            style="margin-bottom: 20px"
          />
          
          <p class="module-description">
            为全面评估您所在学校“数据素养”发展水平，请您将以下问卷链接分享给学校更多教师、学生、管理者填写，问卷有限填写期限为48小时
          </p>

          <!-- 教师问卷 -->
          <div class="section-header">
            <el-icon><Link /></el-icon>
            <span>数据素养评测问卷</span>
          </div>

          <div class="survey-card">
            <div class="survey-header">
              <h3 class="survey-title">教师数据素养调查问卷</h3>
              <p class="survey-desc">34题，评估教师数据素养及数据应用效果</p>
            </div>
            
            <div v-if="teacherInstance" class="survey-content">
              <div class="survey-stats">
                <div class="stat-item">
                  <span class="stat-label">已收集：</span>
                  <el-tag type="success">{{ teacherInstance.collected_count }}</el-tag>
                </div>
                <div class="stat-item">
                  <span class="stat-label">截止日期：</span>
                  <el-tag type="warning">{{ formatExpiredTime(teacherInstance.expired_at) }}</el-tag>
                </div>
                <div v-if="isReadonly" class="stat-item">
                  <el-tag type="info">已停止收集</el-tag>
                </div>
              </div>
              
              <div class="share-link-section" v-if="!isReadonly">
                <div class="share-area">
                  <div class="share-left">
                    <el-input :model-value="teacherShareUrl" readonly size="small">
                      <template #append>
                        <el-button @click="copyLink(teacherShareUrl)">
                          <el-icon><DocumentCopy /></el-icon>
                          复制链接
                        </el-button>
                      </template>
                    </el-input>
                  </div>

                  <div class="share-right">
                    <div class="qr-wrapper">
                      <!-- 二维码区域 -->
                      <div class="qr-box">
                        <img
                          v-if="teacherQrUrl"
                          :src="teacherQrUrl"
                          class="qr-img"
                          alt="教师问卷二维码"
                        />
                        <div v-else class="qr-placeholder">二维码生成中...</div>

                        <!-- 中间学校名覆盖 -->
                        <div class="qr-center">
                          <span class="school-name">{{ schoolName }}</span>
                        </div>
                      </div>

                      <!-- 二维码下方提示文字 -->
                      <div class="qr-tip">
                        《教师数据素养及数据应用效果调查问卷》<br />
                        请在48小时内完成问卷填写！
                      </div>
                    </div>
                  </div>

                </div>
              </div>
            </div>
            
            <div v-else class="survey-empty">
              <p>{{ isReadonly ? '未生成问卷链接' : '尚未生成问卷链接' }}</p>
              <el-button v-if="!isReadonly" type="primary" @click="createInstanceDirect('teacher')" :loading="creating">
                生成问卷链接
              </el-button>
            </div>
          </div>

          <!-- 学生问卷 -->
          <div class="section-header">
            <el-icon><Link /></el-icon>
            <span>数据素养评测问卷</span>
          </div>

          <div class="survey-card">
            <div class="survey-header">
              <h3 class="survey-title">学生数据素养调查问卷</h3>
              <p class="survey-desc">28题，评估学生数据素养及数据应用效果</p>
            </div>
            
            <div v-if="studentInstance" class="survey-content">
              <div class="survey-stats">
                <div class="stat-item">
                  <span class="stat-label">已收集：</span>
                  <el-tag type="success">{{ studentInstance.collected_count }}</el-tag>
                </div>
                <div class="stat-item">
                  <span class="stat-label">截止日期：</span>
                  <el-tag type="warning">{{ formatExpiredTime(studentInstance.expired_at) }}</el-tag>
                </div>
                <div v-if="isReadonly" class="stat-item">
                  <el-tag type="info">已停止收集</el-tag>
                </div>
              </div>
              
              <div class="share-link-section" v-if="!isReadonly">
                <div class="share-area">
                  <div class="share-left">
                    <el-input :model-value="studentShareUrl" readonly size="small">
                      <template #append>
                        <el-button @click="copyLink(studentShareUrl)">
                          <el-icon><DocumentCopy /></el-icon>
                          复制链接
                        </el-button>
                      </template>
                    </el-input>
                  </div>

                  <div class="share-right">
                    <div class="qr-wrapper">
                      <!-- 二维码区域 -->
                      <div class="qr-box">
                        <img
                          v-if="studentQrUrl"
                          :src="studentQrUrl"
                          class="qr-img"
                          alt="学生问卷二维码"
                        />
                        <div v-else class="qr-placeholder">二维码生成中...</div>

                        <!-- 中间学校名覆盖 -->
                        <div class="qr-center">
                          <span class="school-name">{{ schoolName }}</span>
                        </div>
                      </div>

                      <!-- 二维码下方提示文字 -->
                      <div class="qr-tip">
                        《学生数据素养及数据应用效果调查问卷》<br />
                        请在48小时内完成问卷填写！
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-else class="survey-empty">
              <p>{{ isReadonly ? '未生成问卷链接' : '尚未生成问卷链接' }}</p>
              <el-button v-if="!isReadonly" type="primary" @click="createInstanceDirect('student')" :loading="creating">
                生成问卷链接
              </el-button>
            </div>
          </div>

          <!-- 管理者问卷 -->
          <div class="section-header">
            <el-icon><Link /></el-icon>
            <span>数据素养评测问卷</span>
          </div>

          <div class="survey-card">
            <div class="survey-header">
              <h3 class="survey-title">管理者数据素养调查问卷</h3>
              <p class="survey-desc">37题，评估管理者数据素养及数据资产意识</p>
            </div>
            
            <div v-if="managerInstance" class="survey-content">
              <div class="survey-stats">
                <div class="stat-item">
                  <span class="stat-label">已收集：</span>
                  <el-tag type="success">{{ managerInstance.collected_count }}</el-tag>
                </div>
                <div class="stat-item">
                  <span class="stat-label">截止日期：</span>
                  <el-tag type="warning">{{ formatExpiredTime(managerInstance.expired_at) }}</el-tag>
                </div>
                <div v-if="isReadonly" class="stat-item">
                  <el-tag type="info">已停止收集</el-tag>
                </div>
              </div>
              
              <div class="share-link-section" v-if="!isReadonly">
                <div class="share-area">
                  <div class="share-left">
                    <el-input :model-value="managerShareUrl" readonly size="small">
                      <template #append>
                        <el-button @click="copyLink(managerShareUrl)">
                          <el-icon><DocumentCopy /></el-icon>
                          复制链接
                        </el-button>
                      </template>
                    </el-input>
                  </div>

                  <div class="share-right">
                    <div class="qr-wrapper">
                      <!-- 二维码区域 -->
                      <div class="qr-box">
                        <img
                          v-if="managerQrUrl"
                          :src="managerQrUrl"
                          class="qr-img"
                          alt="管理者问卷二维码"
                        />
                        <div v-else class="qr-placeholder">二维码生成中...</div>

                        <!-- 中间学校名覆盖 -->
                        <div class="qr-center">
                          <span class="school-name">{{ schoolName }}</span>
                        </div>
                      </div>

                      <!-- 二维码下方提示文字 -->
                      <div class="qr-tip">
                        《管理者数据素养及数据资产意识调查问卷》<br />
                        请在48小时内完成问卷填写！
                      </div>
                    </div>
                  </div>

                </div>
              </div>
            </div>
            
            <div v-else class="survey-empty">
              <p>{{ isReadonly ? '未生成问卷链接' : '尚未生成问卷链接' }}</p>
              <el-button v-if="!isReadonly" type="primary" @click="createInstanceDirect('manager')" :loading="creating">
                生成问卷链接
              </el-button>
            </div>
          </div>
        </div>

        <!-- 其他模块占位 -->
        <div v-else class="module-content">
          <h2 class="module-title">{{ getModuleTitle(activeModule) }}</h2>
          <el-empty description="该模块内容开发中，敬请期待..." />
        </div>
      </main>
    </div>
  </div>

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
import { ref, onMounted, computed, watch, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import QRCode from 'qrcode'
import {
  School,
  User,
  Reading,
  Document,
  TrendCharts,
  Files,
  Setting,
  InfoFilled,
  Link,
  DocumentCopy
} from '@element-plus/icons-vue'
import { getAssessments, createAssessment, generateReport } from '@/api/assessment'
import { getAssessmentSurveys, createSurveyInstance } from '@/api/survey'
import SubmissionSuccess from '@/components/SubmissionSuccess.vue'
import AssessmentProgress from '@/components/AssessmentProgress.vue'
import { CircleCheckFilled } from '@element-plus/icons-vue'


const router = useRouter()
const route = useRoute()
const schoolName = ref('')
const activeModule = ref('literacy')
const currentAssessmentId = ref(null)
const loading = ref(true)
const assessmentStatus = ref('draft')
const assessmentTimes = ref({})

const moduleDone = reactive({
  literacy: false,
  institution: false,
  behavior: false,
  asset: false,
  technology: false
})

// sidebar 灰色样式：未完成 -> 灰色；完成 -> 正常
const menuItemClass = (key) => ({
  'menu-gray': !moduleDone[key],
  'menu-done': moduleDone[key]
})

/**
 * 判空工具：你这里“都填完”的核心
 * - null/undefined -> 未填
 * - '' -> 未填
 * - [] -> 未填
 * - {} -> 未填（可按需放宽）
 * - 0 是有效值（不算空）
 * - false 是有效值（不算空），但 null 才代表没填
 */
const isFilled = (v) => {
  if (v === null || v === undefined) return false
  if (typeof v === 'string') return v.trim().length > 0
  if (Array.isArray(v)) return v.length > 0
  if (typeof v === 'object') return Object.keys(v).length > 0
  return true
}

// ====== 各模块“必填字段”清单（你按实际表单字段微调）======
// ====== 各模块“必填字段”清单：严格对齐你前端 formData ======
const REQUIRED_FIELDS = {
  // 数据素养：用问卷 collected_count>0 判断（不走字段校验）
  literacy: [],

  institution: [],

  behavior: [
    'teacher_login_freq',
    'student_login_freq',
    'manager_login_freq',
    'visit_count',
    'published_paper_count',
    'published_book_count',
    'case_national_count',
    'case_provincial_count',
    'case_city_count',
    'award_national_count',
    'award_provincial_count',
    'award_city_count',
    'media_national_count',
    'media_provincial_count',
    'media_city_count',
    'conference_national_count',
    'conference_provincial_count',
    'conference_city_count'
  ],

  asset: [
    'management_data_volume',
    'resource_data_volume',
    'service_data_volume',
    'other_data_volume'
  ],

  technology: [
    'data_center_standard',
    'cloud_dedicated_service',
    'student_device_ratio',
    'teacher_device_ratio',
    'has_data_platform',
    'security_certified_count',
    'security_certified_ratio',
    'has_security_incident'
  ]
}


// ====== 拉取各模块数据（假设后端已有这些 GET 接口）======
// 你项目里如果封装了 axios api，就替换成你现有的 api 调用即可
const authHeaders = () => ({
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`
})

const fetchModuleData = async (moduleKey) => {
  const id = currentAssessmentId.value
  if (!id) return null

  // ⚠️ 这里的 URL 你按你的后端实际路由改一下
  // 常见是：/api/assessments/:id/institution/ 这类
  const urlMap = {
    institution: `/api/assessments/${id}/institution/`,
    behavior: `/api/assessments/${id}/behavior/`,
    asset: `/api/assessments/${id}/asset/`,
    technology: `/api/assessments/${id}/technology/`
  }
  const url = urlMap[moduleKey]
  if (!url) return null

  const resp = await fetch(url, { headers: authHeaders() })
  if (!resp.ok) return null
  return await resp.json()
}

const calcModuleDoneByFields = (data, fields) => {
  if (!data) return false
  return fields.every((f) => isFilled(data[f]))
}

// institution：条件必填判定
// institution：条件必填判定
const calcInstitutionDone = (data) => {
  if (!data) return false;

  // --- 1. 绝对必填项（这些开关必须有值，不能是 null/undefined） ---
  const absoluteSwitches = [
    'has_leadership_group',     // 是否成立领导小组
    'has_data_staff',           // 是否配备数据管理人员
    'has_training',             // 是否参与培训
    'has_management_doc',       // 是否出台管理文件
    'has_practice_doc'          // 是否出台实践指导文件
  ];

  // 如果任何一个大开关还没选，直接返回不通过
  if (!absoluteSwitches.every(f => isFilled(data[f]))) return false;

  // --- 2. 条件必填逻辑（如果选“是”，则子项必须填；如果选“否”，则跳过） ---

  // A. 领导小组
  if (data.has_leadership_group === true) {
    if (!isFilled(data.meeting_activity_count)) return false;
  }

  // B. 数据人员
  if (data.has_data_staff === true) {
    // 如果有人员，则 专职数、兼职数、职责说明 必须填
    if (!isFilled(data.fulltime_staff_count)) return false;
    if (!isFilled(data.parttime_staff_count)) return false;
    if (!isFilled(data.has_clear_responsibilities)) return false;
  }

  // C. 数据培训
  if (data.has_training === true) {
    // 如果有培训，则 培训次数、证书数量（即使是0也算填了）必须有值
    if (!isFilled(data.training_count)) return false;
    if (!isFilled(data.national_cert_count)) return false;
    if (!isFilled(data.provincial_cert_count)) return false;
    if (!isFilled(data.city_cert_count)) return false;
  }

  // D. 管理文件
  if (data.has_management_doc === true) {
    // 如果有文件，则 数量必须填，且 必须上传了文件
    const countOk = isFilled(data.management_doc_count);
    const filesOk = Array.isArray(data.management_doc_files) && data.management_doc_files.length > 0;
    if (!countOk || !filesOk) return false;
  }

  // E. 实践指导文件
  if (data.has_practice_doc === true) {
    const countOk = isFilled(data.practice_doc_count);
    const filesOk = Array.isArray(data.practice_doc_files) && data.practice_doc_files.length > 0;
    if (!countOk || !filesOk) return false;
  }

  // 如果能走到这里，说明：要么开关选了“否”，要么选了“是”且子项已填。
  return true;
}

// ====== 数据素养：按你规则 collected_count>0 才算完成 ======
const calcLiteracyDone = () => {
  // “问卷完成”=该问卷 collected_count>0
  const teacherOk = !!teacherInstance.value && (teacherInstance.value.collected_count || 0) > 0
  const studentOk = !!studentInstance.value && (studentInstance.value.collected_count || 0) > 0
  const managerOk = !!managerInstance.value && (managerInstance.value.collected_count || 0) > 0

  // 模块是否完成：这里用“三份都完成”
  // 如果你想改成“任意一份完成就算模块完成”，把 && 改成 ||
  return teacherOk && studentOk && managerOk
}

// ====== 统一刷新各模块完成状态 ======
const refreshModuleDone = async () => {
  // 1 literacy
  moduleDone.literacy = calcLiteracyDone()

  // 2 其他模块：拉数据 + 必填字段校验
  const [institution, behavior, asset, technology] = await Promise.all([
    fetchModuleData('institution'),
    fetchModuleData('behavior'),
    fetchModuleData('asset'),
    fetchModuleData('technology')
  ])

  moduleDone.institution = calcInstitutionDone(institution)
  moduleDone.behavior = calcModuleDoneByFields(behavior, REQUIRED_FIELDS.behavior)
  moduleDone.asset = calcModuleDoneByFields(asset, REQUIRED_FIELDS.asset)
  moduleDone.technology = calcModuleDoneByFields(technology, REQUIRED_FIELDS.technology)
}

// 只读模式（非草稿状态都是只读）
const isReadonly = computed(() => assessmentStatus.value !== 'draft')

// UI控制
const showSuccessModal = ref(false)
const viewingProgress = ref(false)

// 问卷实例数据
const teacherInstance = ref(null)
const studentInstance = ref(null)
const managerInstance = ref(null)

// 创建状态
const creating = ref(false)

// 报告生成状态
const generatingReport = ref(false)

// 分享链接
const teacherShareUrl = computed(() => {
  if (!teacherInstance.value) return ''
  return `${window.location.origin}${teacherInstance.value.share_url}`
})

const studentShareUrl = computed(() => {
  if (!studentInstance.value) return ''
  return `${window.location.origin}${studentInstance.value.share_url}`
})

const managerShareUrl = computed(() => {
  if (!managerInstance.value) return ''
  return `${window.location.origin}${managerInstance.value.share_url}`
})

/** ========== 二维码（dataURL） ========== */
const teacherQrUrl = ref('')
const studentQrUrl = ref('')
const managerQrUrl = ref('')

const generateQr = async (text) => {
  if (!text) return ''
  try {
    return await QRCode.toDataURL(text, { width: 128, margin: 1 })
  } catch (e) {
    console.error('二维码生成失败:', e)
    return ''
  }
}

watch(teacherShareUrl, async (url) => {
  teacherQrUrl.value = await generateQr(url)
})

watch(studentShareUrl, async (url) => {
  studentQrUrl.value = await generateQr(url)
})

watch(managerShareUrl, async (url) => {
  managerQrUrl.value = await generateQr(url)
})

onMounted(async () => {
  const storedUser = localStorage.getItem('user')
  if (storedUser) {
    const userInfo = JSON.parse(storedUser)
    schoolName.value = userInfo.school_name || userInfo.username || '用户'
  }

  // 检查是否有 viewProgress 参数
  if (route.query.viewProgress) {
    viewingProgress.value = true
  }

  // 获取或创建评估记录
  await loadOrCreateAssessment()

  // 加载问卷实例
  await loadSurveys()
})

// 加载或创建评估记录
const loadOrCreateAssessment = async () => {
  loading.value = true
  try {
    const data = await getAssessments()

    // 查找已存在的评估记录（一所学校只有一个）
    let targetAssessment = data.length > 0 ? data[0] : null

    if (targetAssessment) {
      currentAssessmentId.value = targetAssessment.id
      assessmentStatus.value = targetAssessment.status
      assessmentTimes.value = {
        collecting: targetAssessment.created_at,
        submitted: targetAssessment.status !== 'draft' ? targetAssessment.updated_at : null,
        analyzing: targetAssessment.status === 'analyzing' || targetAssessment.status === 'completed' ? targetAssessment.updated_at : null,
        completed: targetAssessment.completed_at
      }

      console.log(`加载评估记录: ID=${targetAssessment.id}, 状态=${targetAssessment.status}`)
    } else {
      const newAssessment = await createAssessment()
      currentAssessmentId.value = newAssessment.id
      assessmentStatus.value = 'draft'
      assessmentTimes.value = {
        collecting: newAssessment.created_at
      }
      console.log(`创建新评估记录: ID=${newAssessment.id}`)
    }
  } catch (error) {
    console.error('加载评估记录失败:', error)
    if (error.response?.status === 404 || !currentAssessmentId.value) {
      try {
        const newAssessment = await createAssessment()
        currentAssessmentId.value = newAssessment.id
        assessmentStatus.value = 'draft'
        assessmentTimes.value = {
          collecting: newAssessment.created_at
        }
      } catch (createError) {
        console.error('创建评估记录失败:', createError)
        ElMessage.error('创建评估记录失败')
      }
    }
  } finally {
    loading.value = false
  }
}

// 切换模块
const handleModuleSelect = (index) => {
  activeModule.value = index

  if (currentAssessmentId.value) {
    if (index === 'institution') {
      router.push(`/school/assessment/${currentAssessmentId.value}/institution`)
    } else if (index === 'behavior') {
      router.push(`/school/assessment/${currentAssessmentId.value}/behavior`)
    } else if (index === 'asset') {
      router.push(`/school/assessment/${currentAssessmentId.value}/asset`)
    } else if (index === 'technology') {
      router.push(`/school/assessment/${currentAssessmentId.value}/technology`)
    }
  }
}

// 获取模块标题
const getModuleTitle = (module) => {
  const titles = {
    literacy: '数据素养',
    institution: '数据制度',
    behavior: '数据行为',
    asset: '数据资产',
    technology: '数据技术'
  }
  return titles[module] || ''
}

// 加载问卷实例
const loadSurveys = async () => {
  if (!currentAssessmentId.value) return

  try {
    const data = await getAssessmentSurveys(currentAssessmentId.value)

    teacherInstance.value = null
    studentInstance.value = null
    managerInstance.value = null

    data.forEach(instance => {
      if (instance.template_info.survey_type === 'teacher') {
        teacherInstance.value = instance
      } else if (instance.template_info.survey_type === 'student') {
        studentInstance.value = instance
      } else if (instance.template_info.survey_type === 'manager') {
        managerInstance.value = instance
      }
    })
    await refreshModuleDone()
  } catch (error) {
    console.error('加载问卷实例失败:', error)
  }
}

// 直接创建问卷实例（无需输入目标数量）
const createInstanceDirect = async (surveyType) => {
  if (!currentAssessmentId.value) {
    ElMessage.error('评估记录未加载，请刷新页面')
    return
  }

  creating.value = true
  try {
    await createSurveyInstance({
      assessment_id: currentAssessmentId.value,
      survey_type: surveyType,
      target_count: 9999
    })

    ElMessage.success('问卷链接生成成功')
    await loadSurveys()
  } catch (error) {
    console.error('生成问卷链接失败:', error)
    ElMessage.error(error.response?.data?.error || '生成链接失败，请重试')
  } finally {
    creating.value = false
  }
}

// 复制链接
const copyLink = async (url) => {
  try {
    await navigator.clipboard.writeText(url)
    ElMessage.success('链接已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    const textarea = document.createElement('textarea')
    textarea.value = url
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()
    try {
      document.execCommand('copy')
      ElMessage.success('链接已复制到剪贴板')
    } catch (err) {
      ElMessage.error('复制失败，请手动复制')
    }
    document.body.removeChild(textarea)
  }
}

// 格式化过期时间
const formatExpiredTime = (dateStr) => {
  if (!dateStr) return '无限期'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit' 
  })
}

// 退出登录
const handleLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  ElMessage.success('已退出登录')
  router.push('/login')
}

// 获取按钮文本
const getActionButtonText = () => {
  if (generatingReport.value) return '提交中...'
  if (assessmentStatus.value === 'draft') return '提交评估'
  return '已提交评估'
}

// 提交评估（生成报告）
const handleSubmitAssessment = async () => {
  if (!currentAssessmentId.value) {
    ElMessage.error('评估记录未加载，请刷新页面')
    return
  }

  if (assessmentStatus.value !== 'draft') {
    ElMessage.warning('评估已提交，请勿重复操作')
    return
  }

  try {
    await ElMessageBox.confirm(
      '确认提交评估？提交后将无法修改已填写的内容。',
      '确认提交',
      {
        confirmButtonText: '确认提交',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
  } catch {
    return
  }

  generatingReport.value = true
  try {
    await generateReport(currentAssessmentId.value)

    assessmentStatus.value = 'collecting'
    assessmentTimes.value.submitted = new Date().toLocaleString()
    showSuccessModal.value = true
  } catch (error) {
    console.error('提交评估失败:', error)
    ElMessage.error(error.response?.data?.error || '提交评估失败，请重试')
  } finally {
    generatingReport.value = false
  }
}

// 查看报告
const handleViewReport = () => {
  if (currentAssessmentId.value && assessmentStatus.value === 'completed') {
    router.push(`/school/report/${currentAssessmentId.value}`)
  } else {
    ElMessage.warning('报告尚未生成完成')
  }
}

const handleViewProgress = () => {
  viewingProgress.value = true
}
</script>

<style scoped>
.assessment-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.progress-view-container {
  flex: 1;
  padding: 40px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

/* 顶部导航栏 */
.header {
  background-color: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 40px;
  height: 70px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.system-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 32px;
}

.nav-item {
  color: #606266;
  text-decoration: none;
  font-size: 15px;
  transition: color 0.3s;
}

.nav-item:hover {
  color: #409eff;
}

.user-dropdown {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
  font-size: 14px;
}

.user-info:hover {
  color: #409eff;
}

/* 主体容器 */
.main-container {
  flex: 1;
  max-width: 1600px;
  width: 100%;
  margin: 0 auto;
  padding: 24px 40px;
  display: flex;
  gap: 24px;
}

/* 左侧导航 */
.sidebar {
  width: 280px;
  background-color: #ffffff;
  border-radius: 8px;
  padding: 24px 0;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  height: fit-content;
  position: sticky;
  top: 94px;
  display: flex;
  flex-direction: column;
}

.sidebar-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  padding: 0 24px 16px;
  border-bottom: 1px solid #e4e7ed;
}

.assessment-menu {
  border: none;
  margin-top: 8px;
  flex: 1;
}

.assessment-menu .el-menu-item {
  height: 52px;
  line-height: 52px;
  padding-left: 24px !important;
  font-size: 15px;
}

.sidebar-tip {
  margin: 24px 16px 0;
  padding: 16px;
  background-color: #ecf5ff;
  border-radius: 6px;
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.sidebar-action {
  margin: 16px 16px 0;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sidebar-action .el-button {
  margin: 0 !important;
}

.sidebar-tip .el-icon {
  color: #409eff;
  font-size: 18px;
  flex-shrink: 0;
  margin-top: 2px;
}

.sidebar-tip p {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  margin: 0;
}

/* 右侧内容区 */
.content-area {
  flex: 1;
  background-color: #ffffff;
  border-radius: 8px;
  padding: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  min-height: 600px;
}

.module-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
}

.module-description {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 32px;
}

/* 章节标题 */
.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
  color: #409eff;
  margin: 32px 0 16px 0;
}

.section-header .el-icon {
  font-size: 18px;
}

/* 问卷卡片 */
.survey-card {
  background-color: #f5f7fa;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 16px;
  transition: all 0.3s;
}

.survey-card:hover {
  background-color: #ecf5ff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.survey-header {
  margin-bottom: 16px;
}

.survey-content {
  margin-top: 16px;
}

.survey-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.share-link-section {
  margin-top: 12px;
}

.survey-empty {
  text-align: center;
  padding: 20px 0;
}

.survey-empty p {
  color: #909399;
  margin-bottom: 16px;
}

.survey-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.survey-desc {
  font-size: 14px;
  color: #606266;
  margin: 0 0 4px 0;
}

/* 未完成：整体灰一点（但不禁用点击） */
.menu-gray {
  opacity: 0.45;
  filter: grayscale(0.9);
}

/* 完成：恢复正常 */
.menu-done {
  opacity: 1;
  filter: none;
}

/* 绿色对号，放在右侧 */
.done-check {
  margin-left: auto;
  color: #67c23a; /* element-plus success */
  font-size: 18px;
}


/* 链接 + 二维码布局 */
.share-area {
  display: flex;
  gap: 12px;
  align-items: center;
}

.share-left {
  flex: 1;
  min-width: 0;
}

.share-right {
  width: 140px;
  flex-shrink: 0;
  display: flex;
  justify-content: flex-end;
  align-items: flex-start;
  margin-top: -120px;
}

.qr-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 8px; /* 控制整体往上 */
}

/* 二维码盒子 */
.qr-box {
  position: relative;
  width: 140px;
  height: 140px;
}

/* 二维码图片 */
.qr-img {
  width: 140px;
  height: 140px;
  display: block;
}

/* 占位 */
.qr-placeholder {
  width: 140px;
  height: 140px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 12px;
}

/* 中间覆盖层 */
.qr-center {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 40px;
  height: 40px;
  transform: translate(-50%, -50%);
  background: #ffffff;
  border-radius: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  box-shadow: 0 0 0 1px #e4e7ed;
}

/* 学校名称 */
.school-name {
  font-size: 10px;
  font-weight: 600;
  color: #303133;
  text-align: center;
  line-height: 1.1;
  padding: 2px;
  max-width: 36px;
  word-break: break-all;
}

/* 二维码下方说明 */
.qr-tip {
  margin-top: 10px;
  font-size: 10px;
  color: #606266;
  text-align: center;
  line-height: 1.6;
  max-width: 160px;
}

/* 覆盖 element-plus：已完成模块即使 active 也不显示蓝色 */
.el-menu-item.is-active.menu-done {
  color: #303133 !important; /* 正常正文色 */
}

.el-menu-item.is-active .done-check {
  color: #67c23a !important; /* success 绿 */
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


/* 响应式设计 */
@media (max-width: 1024px) {
  .main-container {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    position: static;
  }

  .share-area {
    flex-direction: column;
  }

  .share-right {
    width: 100%;
    justify-content: flex-start;
  }
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

</style>
