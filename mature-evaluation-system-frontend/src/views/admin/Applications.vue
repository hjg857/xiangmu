<template>
  <div class="applications-container">
    <div class="page-header">
      <h2 class="page-title">学校账号与申请管理</h2>
      <el-button @click="loadApplications" :icon="Refresh">刷新</el-button>
    </div>

    <!-- 1. 新增：批量导入区域 -->
    <el-card class="import-card">
      <div class="import-wrap">
        <div class="import-left">
          <el-upload
            class="dropbox"
            drag
            :show-file-list="false"
            :auto-upload="false"
            accept=".xlsx,.xls"
            :on-change="onPickFile"
          >
            <div class="drop-title">点击或拖拽 Excel 文件至此处批量导入学校</div>
            <div class="drop-sub">支持 .xlsx/.xls 格式，单次建议不超过100条</div>
          </el-upload>

          <div class="import-actions">
            <el-button @click="downloadTemplate">下载导入模板</el-button>
            <!-- 保留原有或新增单个创建入口（可选） -->
            <el-button
              type="primary"
              @click="goCreateRegionAdmin"
            >
              创建单个区域账号
            </el-button>
          </div>
        </div>

        <div class="import-right">
          <div class="import-tip-title">📌 批量导入须知：</div>
          <ol class="import-tip">
            <li>所有填报信息必须真实有效、准确无误，严格对照表格填报要求及标准示例规范填写；</li>
            <li>不能对模板字段、表头、列序及格式进行任何修改，以确保数据能够正常导入系统；</li>
            <li>填报完成后需逐项核对校验，排查错填、漏填、格式错乱等问题，确认无误后再提交。</li>
          </ol>
        </div>
      </div>
    </el-card>

    <!-- 2. 筛选条件 (保持原有) -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" size="default">
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable style="width: 150px">
            <el-option label="待审批" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="学校类型">
          <el-select v-model="filterForm.school_type" placeholder="全部类型" clearable style="width: 150px">
            <el-option v-for="type in SCHOOL_TYPES" :key="type.value" :label="type.label" :value="type.value" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="申请时间">
          <el-date-picker v-model="filterForm.date_range" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" style="width: 280px" value-format="YYYY-MM-DD" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 3. 申请列表 (保持原有) -->
    <el-card class="table-card">
      <el-table :data="applications" v-loading="loading" stripe style="width: 100%">
        <el-table-column label="ID" width="60" align="center">
  <template #default="{ $index }">
    {{ (pagination.page - 1) * pagination.pageSize + $index + 1 }}
  </template>
</el-table-column>
        <el-table-column label="学校名称" min-width="200">
          <template #default="{ row }">
            {{ getApplicationName(row) }}
          </template>
        </el-table-column>
        <el-table-column label="学校类型" width="120">
          <template #default="{ row }">
            {{ getSchoolTypeText(row) }}
          </template>
        </el-table-column>
        <el-table-column label="所在地" width="200">
          <template #default="{ row }">{{ row.province }} {{ row.city }}</template>
        </el-table-column>
        <el-table-column prop="contact_name" label="联系人" width="100" />
        <el-table-column prop="contact_phone" label="联系电话" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="applied_at" label="申请时间" width="160">
          <template #default="{ row }">{{ formatDateTime(row.applied_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending'" type="success" size="small" @click="handleApprove(row)">通过</el-button>
            <el-button v-if="row.status === 'pending'" type="danger" size="small" @click="handleReject(row)">拒绝</el-button>
            <el-button v-if="row.status !== 'pending'" type="info" size="small" @click="handleViewDetail(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.pageSize" :total="pagination.total" :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper" @size-change="loadApplications" @current-change="loadApplications" />
      </div>
    </el-card>

    <!-- 4. 新增：导入预览弹窗 -->
    <el-dialog v-model="previewVisible" title="批量导入预览" width="1000px" top="5vh">
      <div v-loading="previewLoading">
        <div v-if="previewErrors.length">
          <el-alert type="error" show-icon title="文件解析错误" style="margin-bottom: 15px">
            <div v-for="(err, i) in previewErrors" :key="i">{{ err }}</div>
          </el-alert>
        </div>
        <div v-else>
          <div class="preview-stats">
            <el-tag>总行数：{{ previewSummary.total }}</el-tag>
            <el-tag type="success">可导入：{{ previewSummary.valid }}</el-tag>
            <el-tag type="warning">跳过（重名）：{{ previewSummary.skip }}</el-tag>
            <el-tag type="danger">无效数据：{{ previewSummary.invalid }}</el-tag>
          </div>
          <el-table :data="previewRows" stripe height="400px" size="small">
            <el-table-column prop="__rownum" label="行号" width="60" />
            <el-table-column prop="index" label="序号" width="60" />
            <el-table-column prop="school_name" label="学校名称" min-width="160" show-overflow-tooltip />
            <el-table-column prop="school_type_display" label="学校类型" width="110" />
            <el-table-column label="所在地" min-width="180">
              <template #default="{ row }">
                {{ row.province }} / {{ row.city }} / {{ row.district }}
              </template>
            </el-table-column>
            <el-table-column prop="contact_name" label="负责人" width="90" />
            <el-table-column prop="contact_position" label="职务" width="120" show-overflow-tooltip />
            <el-table-column prop="contact_phone" label="联系电话" width="130" />
            <el-table-column prop="contact_email" label="邮箱" min-width="150" show-overflow-tooltip />
            <el-table-column prop="username" label="登录用户名" width="130" show-overflow-tooltip />
            <el-table-column prop="password" label="登录密码" width="110" show-overflow-tooltip />
            <el-table-column label="校验状态" width="100">
  <template #default="{ row }">
    <el-tag
      v-if="row.__status === 'created'"
      type="success"
      size="small"
    >
      已创建
    </el-tag>

    <el-tag
      v-else-if="row.__status === 'valid'"
      type="success"
      size="small"
    >
      正常
    </el-tag>

    <el-tag
      v-else-if="row.__status === 'skip'"
      type="warning"
      size="small"
    >
      跳过
    </el-tag>

    <el-tag
      v-else
      type="danger"
      size="small"
    >
      错误
    </el-tag>
  </template>
</el-table-column>
            <el-table-column prop="__reason" label="原因说明" min-width="150" show-overflow-tooltip />
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="previewVisible = false">取消</el-button>
        <el-button type="primary" :disabled="previewSummary.valid === 0" :loading="previewLoading" @click="startImport">确认导入</el-button>
      </template>
    </el-dialog>

    <!-- 原有 Dialog 保持不变 -->
    <el-dialog v-model="rejectDialogVisible" title="拒绝申请" width="500px">
      <el-form :model="rejectForm" label-width="100px">
        <el-form-item label="拒绝原因" required>
          <el-input v-model="rejectForm.reject_reason" type="textarea" :rows="4" placeholder="请输入拒绝原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmReject" :loading="rejecting">确认拒绝</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailDialogVisible" title="申请详情" width="600px">
      <el-descriptions :column="2" border v-if="currentApplication">
        <el-descriptions-item label="名称" :span="2">
          {{ getApplicationName(currentApplication) }}
        </el-descriptions-item>

        <el-descriptions-item label="账号类型">
          {{ getSchoolTypeText(currentApplication) }}
        </el-descriptions-item>
        <el-descriptions-item label="所在地">{{ currentApplication.province }} {{ currentApplication.city }}</el-descriptions-item>
        <el-descriptions-item label="联系人">{{ currentApplication.contact_name }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ currentApplication.contact_email }}</el-descriptions-item>
        <el-descriptions-item label="状态" :span="2">
          <el-tag :type="getStatusType(currentApplication.status)">{{ getStatusText(currentApplication.status) }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import * as XLSX from 'xlsx-js-style'
import { getApplicationList, approveApplication, rejectApplication } from '@/api/admin'
import { apiPost } from '@/utils/api' // 确保你的 utils 下有通用 post
import { formatDateTime } from '@/utils'
import { SCHOOL_TYPES } from '@/utils/constants'
import { useRouter } from 'vue-router'

const router = useRouter()

// --- 基础状态 ---
const loading = ref(false)
const applications = ref([])
const filterForm = reactive({ status: '', school_type: '', date_range: [] })
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })

// --- 导入状态 ---
const previewVisible = ref(false)
const previewLoading = ref(false)
const previewRows = ref([])
const previewErrors = ref([])
const previewSummary = reactive({ total: 0, valid: 0, skip: 0, invalid: 0 })

// --- 其他弹窗状态 ---
const rejectDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const rejecting = ref(false)
const currentApplication = ref(null)
const rejectForm = reactive({ reject_reason: '' })

const goCreateRegionAdmin = () => {
  router.push('/admin/region-admin/create')
}

// --- 辅助函数 ---
const getApplicationName = (row) => {
  if (row.apply_role === 'region_admin' || row.school_type === 'region_admin') {
    return row.display_name || row.school_name || `${row.district || ''}区域管理`
  }

  return row.display_name || row.school_name || '-'
}

const getSchoolTypeText = (row) => {
  if (!row) return '-'

  if (row.apply_role === 'region_admin' || row.school_type === 'region_admin') {
    return '区域管理'
  }

  const map = {
    primary: '小学',
    junior: '初中',
    senior: '高中',
    nine_year: '九年一贯制',
    twelve_year: '十二年一贯制',

    小学: '小学',
    初中: '初中',
    高中: '高中',
    九年一贯制: '九年一贯制',
    十二年一贯制: '十二年一贯制'
  }

  return (
    map[row.school_type] ||
    map[row.school_type_display] ||
    SCHOOL_TYPES.find(t => t.value === row.school_type)?.label ||
    SCHOOL_TYPES.find(t => t.value === row.school_type_display)?.label ||
    row.school_type_display ||
    row.school_type ||
    '-'
  )
}
const getStatusText = (s) => ({ pending: '待审批', approved: '已通过', rejected: '已拒绝' }[s] || s)
const getStatusType = (s) => ({ pending: 'warning', approved: 'success', rejected: 'danger' }[s] || 'info')

// --- 加载列表 ---
const loadApplications = async () => {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.pageSize, ...filterForm }
    if (filterForm.date_range?.length === 2) {
      params.start_date = filterForm.date_range[0]
      params.end_date = filterForm.date_range[1]
    }
    const res = await getApplicationList(params)
    applications.value = res.results || res.data?.results || []
    pagination.total = res.count || res.data?.count || 0
  } catch (error) { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

const handleSearch = () => { pagination.page = 1; loadApplications() }
const handleReset = () => { filterForm.status = ''; filterForm.school_type = ''; filterForm.date_range = []; handleSearch() }

// --- 批量导入逻辑 ---

const downloadTemplate = () => {
  const rows = [
    [
      "序号",
      "学校名称",
      "学校类型",
      "省",
      "市",
      "区/县",
      "负责人",
      "职务",
      "联系电话",
      "邮箱",
      "登录用户名",
      "登录密码",
    ],
    [
      "填报说明",
      "填写学校官方完整全称",
      "仅限选择：小学、初中、高中、九年一贯制、十二年一贯制",
      "填写学校所在省份全称，如：江苏省",
      "填写学校所在城市全称，如：徐州市",
      "填写学校所在区县全称，如：泉山区",
      "填写各学校负责人姓名",
      "填写负责人岗位职务",
      "填写负责人有效联系电话",
      "填写负责人有效邮箱",
      "学校全称大写首字母组合，无特殊字符",
      "8位字符（数字或字母组合）",
    ],
    [
      "填报示例",
      "徐州市泉山实验小学",
      "小学",
      "江苏省",
      "徐州市",
      "泉山区",
      "易XX",
      "信息中心主任",
      "18864471307",
      "204142312@gq.com",
      "XZQSSYXX",
      "QSSYXX11",
    ],
    [
      "① 所有填报信息必须真实有效、准确无误，严格对照表格填报要求及标准示例规范填写；\n② 不能对模板字段、表头、列序及格式进行任何修改，以确保数据能够正常导入系统；\n③ 填报完成后需逐项核对校验，排查错填、漏填、格式错乱等问题，确认无误后再提交。",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
    ],
  ]

  // 第5行开始预留正式填写区域
  for (let i = 1; i <= 100; i++) {
    rows.push([i, "", "", "", "", "", "", "", "", "", "", ""])
  }

  const ws = XLSX.utils.aoa_to_sheet(rows)

  // 合并第4行说明区域：A4-L4
  ws["!merges"] = [
    {
      s: { r: 3, c: 0 },
      e: { r: 3, c: 11 },
    },
  ]

  // 列宽
  ws["!cols"] = [
    { wch: 8 },   // 序号
    { wch: 28 },  // 学校名称
    { wch: 34 },  // 学校类型
    { wch: 16 },  // 省
    { wch: 16 },  // 市
    { wch: 16 },  // 区/县
    { wch: 18 },  // 负责人
    { wch: 18 },  // 职务
    { wch: 18 },  // 联系电话
    { wch: 26 },  // 邮箱
    { wch: 24 },  // 登录用户名
    { wch: 20 },  // 登录密码
  ]

  // 行高
  ws["!rows"] = [
    { hpt: 28 },
    { hpt: 44 },
    { hpt: 26 },
    { hpt: 60 },
  ]

  const borderStyle = {
    top: { style: "thin", color: { rgb: "000000" } },
    bottom: { style: "thin", color: { rgb: "000000" } },
    left: { style: "thin", color: { rgb: "000000" } },
    right: { style: "thin", color: { rgb: "000000" } },
  }

  const headerStyle = {
    font: {
      name: "宋体",
      bold: true,
      color: { rgb: "FFFFFF" },
      sz: 12,
    },
    fill: {
      fgColor: { rgb: "305496" },
    },
    alignment: {
      horizontal: "center",
      vertical: "center",
      wrapText: true,
    },
    border: borderStyle,
  }

  const noteStyle = {
    font: {
      name: "宋体",
      color: { rgb: "000000" },
      sz: 11,
    },
    fill: {
      fgColor: { rgb: "D9E2F3" },
    },
    alignment: {
      horizontal: "center",
      vertical: "center",
      wrapText: true,
    },
    border: borderStyle,
  }

  const mergedNoteStyle = {
    font: {
      name: "宋体",
      color: { rgb: "000000" },
      sz: 11,
    },
    fill: {
      fgColor: { rgb: "D9E2F3" },
    },
    alignment: {
      horizontal: "left",
      vertical: "center",
      wrapText: true,
    },
    border: borderStyle,
  }

  const emptyStyle = {
    font: {
      name: "宋体",
      color: { rgb: "000000" },
      sz: 11,
    },
    alignment: {
      horizontal: "center",
      vertical: "center",
      wrapText: true,
    },
    border: borderStyle,
  }

  // 前4行样式
  for (let r = 0; r <= 3; r++) {
    for (let c = 0; c <= 11; c++) {
      const cellRef = XLSX.utils.encode_cell({ r, c })

      if (!ws[cellRef]) {
        ws[cellRef] = { t: "s", v: "" }
      }

      if (r === 0) {
        ws[cellRef].s = headerStyle
      } else if (r === 3) {
        ws[cellRef].s = mergedNoteStyle
      } else {
        ws[cellRef].s = noteStyle
      }
    }
  }

  // 第5行以后正式填写区域样式
  for (let r = 4; r < rows.length; r++) {
    for (let c = 0; c <= 11; c++) {
      const cellRef = XLSX.utils.encode_cell({ r, c })

      if (!ws[cellRef]) {
        ws[cellRef] = { t: "s", v: "" }
      }

      ws[cellRef].s = emptyStyle
    }
  }

  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, "学校账号导入模板")

  XLSX.writeFile(wb, "超级管理员-学校账号批量导入模板.xlsx")
}

const onPickFile = (file) => {
  const raw = file.raw
  if (!raw) return
  parseExcel(raw)
}

const parseExcel = async (file) => {
  previewLoading.value = true
  previewVisible.value = true
  previewErrors.value = []
  previewRows.value = []

  try {
    const data = await file.arrayBuffer()
    const workbook = XLSX.read(data, { type: "array" })
    const worksheet = workbook.Sheets[workbook.SheetNames[0]]

    const aoa = XLSX.utils.sheet_to_json(worksheet, {
      header: 1,
      defval: ""
    })

    if (!aoa || aoa.length < 5) {
      throw new Error("Excel格式不正确：第5行开始才是正式数据，请使用新版导入模板")
    }

    const headerRow = (aoa[0] || []).map((x) => String(x || "").trim())
    const idx = buildHeaderIndex(headerRow)

    const requiredFields = [
      "index",
      "school_name",
      "school_type",
      "province",
      "city",
      "district",
      "contact_name",
      "contact_position",
      "contact_phone",
      "contact_email",
      "username",
      "password"
    ]

    const fieldNameMap = {
      index: "序号",
      school_name: "学校名称",
      school_type: "学校类型",
      province: "省",
      city: "市",
      district: "区/县",
      contact_name: "负责人",
      contact_position: "职务",
      contact_phone: "联系电话",
      contact_email: "邮箱",
      username: "登录用户名",
      password: "登录密码"
    }

    const missing = requiredFields.filter((key) => idx[key] == null)

    if (missing.length) {
      previewErrors.value.push(
        `表头缺少必要列：${missing.map((key) => fieldNameMap[key] || key).join("、")}。请使用新版导入模板。`
      )
      return
    }

    // 第2、3、4行是说明和示例，第5行开始才是正式数据
    const dataRows = aoa
      .slice(4)
      .map((row, i) => ({
        excelRowNum: i + 5,
        row
      }))
      .filter(({ row }) => {
        // A列是序号，可能自动填了数字；判断 B-L 是否有实际内容
        return row.slice(1, 12).some((cell) => String(cell || "").trim() !== "")
      })
      .slice(0, 100)

    const existingNames = new Set(
      applications.value.map((a) => normalizeName(a.school_name))
    )

    const seenName = new Set()
    const seenEmail = new Set()
    const seenUsername = new Set()

    previewRows.value = dataRows.map(({ row, excelRowNum }) => {
      const get = (key) => String(row[idx[key]] ?? "").trim()

      const schoolTypeText = get("school_type")
      const schoolTypeValue = normalizeSchoolType(schoolTypeText)

      const item = {
        __rownum: excelRowNum,
        index: get("index"),
        school_name: get("school_name"),
        school_type: schoolTypeValue,
        school_type_display: schoolTypeText,
        province: get("province"),
        city: get("city"),
        district: get("district"),
        contact_name: get("contact_name"),
        contact_position: get("contact_position"),
        contact_phone: get("contact_phone"),
        contact_email: get("contact_email"),
        username: get("username"),
        password: get("password"),
        __status: "valid",
        __reason: ""
      }

      const errs = []

      if (!item.index) errs.push("序号必填")
      if (!item.school_name) errs.push("学校名称必填")
      if (!item.school_type_display) errs.push("学校类型必填")
      if (!item.school_type) errs.push("学校类型不合法")
      if (!item.province) errs.push("省必填")
      if (!item.city) errs.push("市必填")
      if (!item.district) errs.push("区/县必填")
      if (!item.contact_name) errs.push("负责人必填")
      if (!item.contact_position) errs.push("职务必填")
      if (!item.contact_phone) errs.push("联系电话必填")
      if (!item.contact_email) errs.push("邮箱必填")
      if (!item.username) errs.push("登录用户名必填")
      if (!item.password) errs.push("登录密码必填")

      if (item.contact_phone && !isValidPhone(item.contact_phone)) {
        errs.push("联系电话格式不正确")
      }

      if (item.contact_email && !isValidEmail(item.contact_email)) {
        errs.push("邮箱格式不正确")
      }

      if (item.username && !/^[A-Za-z0-9]+$/.test(item.username)) {
        errs.push("登录用户名只能包含数字或字母，不能包含特殊字符")
      }

      if (item.password && !/^[A-Za-z0-9]{8}$/.test(item.password)) {
        errs.push("登录密码必须为8位数字或字母组合")
      }

      const normName = normalizeName(item.school_name)
      const normEmail = item.contact_email.toLowerCase()
      const normUsername = item.username.toLowerCase()

      if (normName) {
        if (seenName.has(normName)) {
          errs.push("文件内学校名称重复")
        }
        seenName.add(normName)
      }

      if (normEmail) {
        if (seenEmail.has(normEmail)) {
          errs.push("文件内邮箱重复")
        }
        seenEmail.add(normEmail)
      }

      if (normUsername) {
        if (seenUsername.has(normUsername)) {
          errs.push("文件内登录用户名重复")
        }
        seenUsername.add(normUsername)
      }

      if (normName && existingNames.has(normName)) {
        item.__status = "skip"
        item.__reason = "系统当前列表中已存在同名学校"
        return item
      }

      if (errs.length) {
        item.__status = "invalid"
        item.__reason = errs.join("；")
      }

      return item
    })

    previewSummary.total = previewRows.value.length
    previewSummary.valid = previewRows.value.filter((r) => r.__status === "valid").length
    previewSummary.skip = previewRows.value.filter((r) => r.__status === "skip").length
    previewSummary.invalid = previewRows.value.filter((r) => r.__status === "invalid").length
  } catch (e) {
    console.error("解析失败:", e)
    previewErrors.value.push(e.message || "解析失败")
  } finally {
    previewLoading.value = false
  }
}

function normalizeName(value) {
  return String(value || "")
    .trim()
    .replace(/\s+/g, "")
    .toLowerCase()
}

function normalizeSchoolType(value) {
  const text = String(value || "").trim()

  const map = {
    小学: "primary",
    初中: "junior",
    高中: "senior",
    九年一贯制: "nine_year",
    十二年一贯制: "twelve_year",

    primary: "primary",
    junior: "junior",
    senior: "senior",
    nine_year: "nine_year",
    twelve_year: "twelve_year"
  }

  return map[text] || ""
}

function isValidPhone(value) {
  return /^1[3-9]\d{9}$/.test(String(value || "").trim())
}

function isValidEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value || "").trim())
}

function buildHeaderIndex(headers) {
  const normalizeHeader = (value) => {
    return String(value || "")
      .trim()
      .replace(/\s+/g, "")
      .replace(/[()（）]/g, "")
      .toLowerCase()
  }

  const normalizedHeaders = headers.map(normalizeHeader)

  const findByNames = (names) => {
    const normalizedNames = names.map(normalizeHeader)

    const idx = normalizedHeaders.findIndex((header) => {
      return normalizedNames.some((name) => header === name || header.includes(name))
    })

    return idx >= 0 ? idx : null
  }

  return {
    index: findByNames(["序号", "序列号", "编号", "no", "no."]),
    school_name: findByNames(["学校名称", "学校全称"]),
    school_type: findByNames(["学校类型", "办学类型"]),
    province: findByNames(["省", "省份", "province"]),
    city: findByNames(["市", "城市", "city"]),
    district: findByNames(["区/县", "区县", "区", "县", "district"]),
    contact_name: findByNames(["负责人", "联系人", "联系人姓名"]),
    contact_position: findByNames(["职务", "岗位", "负责人职务"]),
    contact_phone: findByNames(["联系电话", "电话", "手机号码", "手机号"]),
    contact_email: findByNames(["邮箱", "联系邮箱", "电子邮箱"]),
    username: findByNames(["登录用户名", "用户名", "账号", "登录账号"]),
    password: findByNames(["登录密码", "初始密码", "密码"])
  }
}

function formatImportReason(reason) {
  if (!reason) {
    return "导入失败"
  }

  if (typeof reason === "string") {
    return reason
  }

  if (Array.isArray(reason)) {
    return reason.join("；")
  }

  if (typeof reason === "object") {
    const messages = []

    Object.entries(reason).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        messages.push(`${key}：${value.join("；")}`)
      } else if (typeof value === "string") {
        messages.push(`${key}：${value}`)
      } else {
        messages.push(`${key}：${JSON.stringify(value)}`)
      }
    })

    return messages.join("；") || "导入失败"
  }

  return String(reason)
}

const startImport = async () => {
  const validRows = previewRows.value.filter((row) => row.__status === "valid")

  if (validRows.length === 0) {
    ElMessage.warning("没有可导入的有效数据")
    return
  }

  const payload = {
    rows: validRows.map((row) => ({
      school_name: row.school_name,
      school_type: row.school_type,
      province: row.province,
      city: row.city,
      district: row.district,
      contact_name: row.contact_name,
      contact_position: row.contact_position,
      contact_phone: row.contact_phone,
      contact_email: row.contact_email,
      username: row.username,
      password: row.password,
    })),
  }

  previewLoading.value = true

  try {
    const { data: resp } = await apiPost("/api/schools/import/", payload)

    if (!resp?.success) {
      throw new Error(resp?.message || "导入失败")
    }

    const result = resp.data || {
      created: 0,
      skipped: 0,
      failed: 0,
      details: [],
    }

    /**
     * 后端返回的 row_index 通常是 validRows 的下标，
     * 不是 previewRows 的原始下标。
     * 所以这里通过 validRows[row_index].__rownum 找回原 Excel 行号。
     */
    const detailByExcelRow = new Map()

    ;(result.details || []).forEach((detail) => {
      const validRow = validRows[detail.row_index]

      if (validRow) {
        detailByExcelRow.set(validRow.__rownum, detail)
      }
    })

    previewRows.value = previewRows.value.map((row) => {
      const detail = detailByExcelRow.get(row.__rownum)

      if (!detail) {
        return row
      }

      if (detail.status === "created") {
        return {
          ...row,
          __status: "created",
          __reason: `已创建，用户名：${detail.username || row.username}`,
        }
      }

      if (detail.status === "skipped") {
        return {
          ...row,
          __status: "skip",
          __reason: detail.reason || "已跳过",
        }
      }

      return {
        ...row,
        __status: "invalid",
        __reason: formatImportReason(detail.reason),
      }
    })

    previewSummary.total = previewRows.value.length
    previewSummary.valid = previewRows.value.filter((row) => row.__status === "valid").length
    previewSummary.skip = previewRows.value.filter((row) => row.__status === "skip").length
    previewSummary.invalid = previewRows.value.filter((row) => row.__status === "invalid").length

    ElMessage.success(
      `导入完成：成功${result.created || 0}，跳过${result.skipped || 0}，失败${result.failed || 0}`
    )

    await loadApplications()
  } catch (error) {
    console.error("导入失败:", error)
    ElMessage.error(error?.message || "导入请求失败，请检查网络或权限")
  } finally {
    previewLoading.value = false
  }
}

// --- 原有审批逻辑 (已适配你的代码) ---
const handleApprove = (row) => {
  ElMessageBox.confirm(`确认通过 ${row.school_name} 吗？系统将自动生成账号并发送邮件。`, '审批确认', { type: 'success' })
    .then(async () => {
      const res = await approveApplication(row.id)
      if (res.success) { ElMessage.success('审批成功'); loadApplications() }
    })
}

const handleReject = (row) => { currentApplication.value = row; rejectForm.reject_reason = ''; rejectDialogVisible.value = true }
const confirmReject = async () => {
  if (!rejectForm.reject_reason.trim()) return ElMessage.warning('请输入原因')
  rejecting.value = true
  try {
    const res = await rejectApplication(currentApplication.value.id, { reject_reason: rejectForm.reject_reason })
    if (res.success) { ElMessage.success('已拒绝'); rejectDialogVisible.value = false; loadApplications() }
  } finally { rejecting.value = false }
}
const handleViewDetail = (row) => { currentApplication.value = row; detailDialogVisible.value = true }

onMounted(loadApplications)
</script>

<style scoped>
.applications-container { padding: 20px; background: #f5f7fa; min-height: 100vh; }
.import-card { margin-bottom: 20px; }
.import-wrap { display: flex; gap: 20px; }
.import-left { flex: 1; }
.import-right { width: 300px; background: #fafafa; padding: 15px; border-radius: 8px; border: 1px solid #eee; }
.dropbox { border: 1px dashed #dcdfe6; border-radius: 8px; padding: 20px; text-align: center; }
.drop-title { font-weight: bold; color: #303133; margin-bottom: 8px; }
.drop-sub { font-size: 12px; color: #909399; }
.import-actions { margin-top: 15px; }
.import-tip-title { font-weight: bold; color: #E6A23C; margin-bottom: 10px; }
.import-tip { font-size: 13px; color: #606266; line-height: 1.8; padding-left: 18px; }
.preview-stats { margin-bottom: 15px; display: flex; gap: 10px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { font-size: 20px; font-weight: bold; }
.filter-card, .table-card { margin-bottom: 20px; }
.pagination { margin-top: 20px; display: flex; justify-content: flex-end; }
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

.contact-note {
  margin-top: 18px;          /* 与邮箱拉开距离 */
  font-size: 13px;           /* 比正文小 */
  color: #9ca3af;            /* 浅灰色 */
  font-style: italic;        /* 微斜体，学术/说明感 */
  line-height: 1.6;
}
</style>