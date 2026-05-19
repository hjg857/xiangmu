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
          </div>
        </div>

        <div class="import-right">
          <div class="import-tip-title">📌 批量导入须知：</div>
          <ol class="import-tip">
            <li><strong>自动发信：</strong>导入成功后，系统将自动生成账号并发送至联系人邮箱。</li>
            <li><strong>地域必填：</strong>超级管理员导入请务必填准确的“省、市、区”全称。</li>
            <li><strong>账号规则：</strong>账号为学校拼音首字母+随机码，密码为8位随机字符。</li>
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
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="school_name" label="学校名称" min-width="200" />
        <el-table-column prop="school_type" label="学校类型" width="120">
          <template #default="{ row }">{{ getSchoolTypeText(row.school_type) }}</template>
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
            <el-table-column prop="school_name" label="学校名称" min-width="150" show-overflow-tooltip />
            <!-- 找到预览弹窗里的 el-table，插入这一列 -->
            <el-table-column label="所在地" min-width="180">
              <template #default="{ row }">
                {{ row.province }} / {{ row.city }} / {{ row.district }}
              </template>
            </el-table-column>
            <el-table-column prop="contact_email" label="邮箱" min-width="150" />
            <el-table-column label="校验状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.__status === 'valid' ? 'success' : (row.__status === 'skip' ? 'warning' : 'danger')" size="small">
                  {{ row.__status === 'valid' ? '正常' : (row.__status === 'skip' ? '跳过' : '错误') }}
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
        <el-descriptions-item label="学校名称" :span="2">{{ currentApplication.school_name }}</el-descriptions-item>
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
import * as XLSX from 'xlsx'
import { getApplicationList, approveApplication, rejectApplication } from '@/api/admin'
import { apiPost } from '@/utils/api' // 确保你的 utils 下有通用 post
import { formatDateTime } from '@/utils'
import { SCHOOL_TYPES } from '@/utils/constants'

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

// --- 辅助函数 ---
const getSchoolTypeText = (type) => SCHOOL_TYPES.find(t => t.value === type)?.label || type
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
  // 1. 定义表头：加入了省(province)、市(city)、区/县(district)
  const header = [
    "学校名称(name)*", 
    "学校类型(school_type)*", 
    "省(province)*", 
    "市(city)*", 
    "区/县(district)*", 
    "联系人(contact_name)*", 
    "职务(contact_position)*", 
    "联系电话(contact_phone)*", 
    "邮箱(contact_email)*",
    "用户名(username,可选)",
    "初始密码(password,可选,>=8)"
  ];

  // 2. 示例行
  const example = [
    "示例小学", 
    "primary", 
    "江苏省", 
    "徐州市", 
    "泉山区", 
    "张老师", 
    "主任", 
    "13800000000", 
    "test@edu.cn",
    "",
    ""
  ];

  // 3. 组装并设置列宽
  const ws = XLSX.utils.aoa_to_sheet([header, example]);
  ws["!cols"] = header.map(() => ({ wch: 20 })); // 设置每列宽度为20

  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "Template");
  
  // 4. 下载文件
  XLSX.writeFile(wb, "超级管理员-学校账号批量导入模板.xlsx");
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
  
  try {
    const data = await file.arrayBuffer()
    const workbook = XLSX.read(data)
    const worksheet = workbook.Sheets[workbook.SheetNames[0]]
    // 使用 header: 1 以获取二维数组，方便根据索引取值
    const json = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: "" })
    
    if (json.length < 2) throw new Error("文件内无有效数据")
    
    const rows = json.slice(1) // 去掉表头
    const existingNames = new Set(applications.value.map(a => a.school_name))

    previewRows.value = rows.map((r, i) => {
      // 按照新模板顺序解构：名称、类型、省、市、区、联系人、职务、电话、邮箱、用户名、密码
      const [name, type, prov, city, dist, contact, pos, phone, email, username, pwd] = r.map(v => String(v || '').trim())
      
      let status = 'valid'
      let reason = ''
      
      // 1. 必填项校验（超级管理员多了省市区）
      if (!name || !type || !prov || !city || !dist || !contact || !phone || !email) {
        status = 'invalid'
        reason = '必填项缺失（学校、类型、省市区、联系人、电话、邮箱均为必填）'
      } 
      // 2. 邮箱格式校验
      else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        status = 'invalid'
        reason = '邮箱格式不正确'
      } 
      // 3. 手机号校验
      else if (!/^1[3-9]\d{9}$/.test(phone)) {
        status = 'invalid'
        reason = '手机号格式不正确'
      }
      // 4. 系统重名校验
      else if (existingNames.has(name)) {
        status = 'skip'
        reason = '系统当前列表中已存在同名学校'
      }

      return {
        __rownum: i + 2, 
        school_name: name, 
        school_type: type, 
        province: prov, 
        city: city, 
        district: dist,
        contact_name: contact, 
        contact_position: pos, 
        contact_phone: phone, 
        contact_email: email,
        username: username, // 传递给后端
        password: pwd,      // 传递给后端
        __status: status, 
        __reason: reason
      }
    }).filter(r => r.school_name) // 过滤掉空行

    // 更新预览统计
    previewSummary.total = previewRows.value.length
    previewSummary.valid = previewRows.value.filter(r => r.__status === 'valid').length
    previewSummary.skip = previewRows.value.filter(r => r.__status === 'skip').length
    previewSummary.invalid = previewRows.value.filter(r => r.__status === 'invalid').length

  } catch (e) {
    console.error('解析失败:', e)
    previewErrors.value.push(e.message)
  } finally {
    previewLoading.value = false
  }
}

const startImport = async () => {
  // 只提交校验状态为 'valid' 的行
  const validData = previewRows.value.filter(r => r.__status === 'valid')
  
  if (validData.length === 0) {
    ElMessage.warning('没有可导入的有效数据')
    return
  }

  previewLoading.value = true
  try {
    // 构造后端需要的格式
    const payload = {
      rows: validData.map(r => ({
        school_name: r.school_name,
        school_type: r.school_type,
        province: r.province,
        city: r.city,
        district: r.district,
        contact_name: r.contact_name,
        contact_position: r.contact_position,
        contact_phone: r.contact_phone,
        contact_email: r.contact_email,
        username: r.username || "",
        password: r.password || ""
      }))
    }

    const res = await apiPost('/api/schools/import/', { rows: validData })
    
    if (res.data.success || res.success) {
      const result = res.data?.data || res.data
      ElMessage.success(`导入完成！成功：${result.created}，跳过：${result.skipped}`)
      previewVisible.value = false
      loadApplications() // 刷新下方列表
    }
  } catch (e) {
    console.error('导入失败:', e)
    ElMessage.error(e.response?.data?.message || '导入请求失败，请检查网络或权限')
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