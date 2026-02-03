<template>
  <div class="admin-page">
    <div class="page-header">
      <h2 class="page-title">账号申请管理</h2>
      <el-button @click="loadData" :icon="Refresh">刷新</el-button>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="queryForm" size="default">
        <el-form-item label="状态" style="margin-left: 0;">
          <el-select
            v-model="queryForm.status"
            placeholder="全部状态"
            clearable
            style="width: 150px"
          >
            <el-option label="待审批" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>

        <el-form-item label="学校类型">
          <el-select
            v-model="queryForm.school_type"
            placeholder="全部类型"
            clearable
            style="width: 150px"
          >
            <el-option label="小学" value="primary" />
            <el-option label="初中" value="junior" />
            <el-option label="高中" value="senior" />
            <el-option label="九年一贯制" value="nine_year" />
            <el-option label="十二年一贯制" value="twelve_year" />
          </el-select>
        </el-form-item>

        <el-form-item label="申请时间">
          <el-date-picker
            v-model="queryForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 240px"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <!-- 批量操作 -->
      <div class="batch-actions" v-if="selectedRows.length > 0">
        <el-alert :title="`已选择 ${selectedRows.length} 条申请`" type="info" :closable="false">
          <template #default>
            <el-button type="success" size="small" @click="handleBatchApprove">批量通过</el-button>
            <el-button type="danger" size="small" @click="handleBatchReject">批量拒绝</el-button>
          </template>
        </el-alert>
      </div>

      <el-table
        :data="tableData"
        v-loading="loading"
        @selection-change="handleSelectionChange"
        stripe
        style="width: 100%"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="school_name" label="学校名称" min-width="180" />
        <el-table-column prop="school_type" label="学校类型" width="100">
          <template #default="{ row }">
            {{ getSchoolTypeText(row.school_type) }}
          </template>
        </el-table-column>
        <el-table-column label="所在地" width="150">
          <template #default="{ row }">
            {{ row.province }} {{ row.city }}
          </template>
        </el-table-column>
        <el-table-column prop="contact_name" label="联系人" width="80" />
        <el-table-column prop="contact_phone" label="联系电话" width="120" />
        <el-table-column prop="contact_email" label="邮箱" min-width="180" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="applied_at" label="申请时间" width="150">
          <template #default="{ row }">
            {{ formatDateTime(row.applied_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button type="success" link size="small" @click="handleApprove(row)">通过</el-button>
              <el-button type="danger" link size="small" @click="handleReject(row)">拒绝</el-button>
            </template>
            <el-button type="primary" link size="small" @click="handleViewDetail(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleQuery"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- 拒绝原因对话框 -->
    <el-dialog
      v-model="rejectDialogVisible"
      title="拒绝申请"
      width="500px"
    >
      <el-form :model="rejectForm" label-width="100px">
        <el-form-item label="拒绝原因" required>
          <el-input
            v-model="rejectForm.reject_reason"
            type="textarea"
            :rows="4"
            placeholder="请输入拒绝原因"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button
          type="danger"
          @click="confirmReject"
          :loading="rejectLoading"
        >
          确认拒绝
        </el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="申请详情"
      width="600px"
    >
      <el-descriptions :column="2" border v-if="currentRow">
        <el-descriptions-item label="申请ID">
          {{ currentRow.id }}
        </el-descriptions-item>
        <el-descriptions-item label="申请状态">
          <el-tag :type="getStatusType(currentRow.status)">
            {{ getStatusText(currentRow.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="学校名称" :span="2">
          {{ currentRow.school_name }}
        </el-descriptions-item>
        <el-descriptions-item label="学校类型">
          {{ getSchoolTypeText(currentRow.school_type) }}
        </el-descriptions-item>
        <el-descriptions-item label="所在地">
          {{ currentRow.province }} {{ currentRow.city }} {{ currentRow.district }}
        </el-descriptions-item>
        <el-descriptions-item label="联系人姓名">
          {{ currentRow.contact_name }}
        </el-descriptions-item>
        <el-descriptions-item label="联系人职务">
          {{ currentRow.contact_position }}
        </el-descriptions-item>
        <el-descriptions-item label="联系电话">
          {{ currentRow.contact_phone }}
        </el-descriptions-item>
        <el-descriptions-item label="联系邮箱">
          {{ currentRow.contact_email }}
        </el-descriptions-item>
        <el-descriptions-item label="申请时间" :span="2">
          {{ formatDateTime(currentRow.applied_at) }}
        </el-descriptions-item>
        <el-descriptions-item
          label="审批时间"
          :span="2"
          v-if="currentRow.reviewed_at"
        >
          {{ formatDateTime(currentRow.reviewed_at) }}
        </el-descriptions-item>
        <el-descriptions-item
          label="拒绝原因"
          :span="2"
          v-if="currentRow.status === 'rejected'"
        >
          {{ currentRow.reject_reason || '无' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import {
  getApplicationList,
  approveApplication,
  rejectApplication
} from '@/api/admin'

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loading = ref(false)
const tableData = ref([])
const selectedRows = ref([])

const queryForm = reactive({
  school_type: '',
  status: 'pending',
  search: '',
  dateRange: null
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const rejectDialogVisible = ref(false)
const rejectLoading = ref(false)
const rejectForm = reactive({
  reject_reason: '',
  application_id: null,
  is_batch: false,
  application_ids: []
})

const detailDialogVisible = ref(false)
const currentRow = ref(null)

// 获取学校类型文本
const getSchoolTypeText = (type) => {
  const map = {
    primary: '小学',
    junior: '初中',
    senior: '高中',
    nine_year: '九年一贯制',
    twelve_year: '十二年一贯制'
  }
  return map[type] || type
}

// 获取状态文本
const getStatusText = (status) => {
  const map = {
    pending: '待审批',
    approved: '已通过',
    rejected: '已拒绝'
  }
  return map[status] || status
}

// 获取状态类型
const getStatusType = (status) => {
  const map = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return map[status] || 'info'
}

// 加载数据
const loadData = async () => {
  loading.value = true
  
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...queryForm
    }
    
    const res = await getApplicationList(params)
    
    if (res.success) {
      tableData.value = res.data.results
      pagination.total = res.data.count
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 查询
const handleQuery = () => {
  pagination.page = 1
  loadData()
}

// 重置
const handleReset = () => {
  queryForm.school_type = ''
  queryForm.status = 'pending'
  queryForm.search = ''
  queryForm.dateRange = null
  handleQuery()
}

// 选择变化
const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

// 审批通过
const handleApprove = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确认通过 ${row.school_name} 的申请吗？系统将自动生成账号并发送邮件。`,
      '确认审批',
      {
        confirmButtonText: '确认通过',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    loading.value = true
    const res = await approveApplication(row.id)
    
    if (res.success) {
      ElMessage.success('审批成功，账号信息已发送至邮箱')
      loadData()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.error?.message || '审批失败')
    }
  } finally {
    loading.value = false
  }
}

// 拒绝申请
const handleReject = (row) => {
  currentRow.value = row
  rejectForm.reject_reason = ''
  rejectForm.application_id = row.id
  rejectForm.is_batch = false
  rejectDialogVisible.value = true
}

// 确认拒绝
const confirmReject = async () => {
  if (!rejectForm.reject_reason.trim()) {
    ElMessage.warning('请输入拒绝原因')
    return
  }
  
  rejectLoading.value = true
  
  try {
    const res = await rejectApplication(rejectForm.application_id, {
      reject_reason: rejectForm.reject_reason
    })
    
    if (res.success) {
      ElMessage.success('已拒绝申请')
      rejectDialogVisible.value = false
      loadData()
    }
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    rejectLoading.value = false
  }
}

// 批量通过
const handleBatchApprove = async () => {
  const pendingRows = selectedRows.value.filter(row => row.status === 'pending')
  
  if (pendingRows.length === 0) {
    ElMessage.warning('请选择待审批的申请')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确认通过选中的 ${pendingRows.length} 条申请吗？`,
      '批量审批',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    loading.value = true
    
    // 逐个审批
    let successCount = 0
    for (const row of pendingRows) {
      try {
        await approveApplication(row.id)
        successCount++
      } catch (error) {
        console.error(`审批失败: ${row.school_name}`, error)
      }
    }
    
    ElMessage.success(`成功审批 ${successCount} 条申请`)
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量审批失败')
    }
  } finally {
    loading.value = false
  }
}

// 批量拒绝
const handleBatchReject = () => {
  const pendingRows = selectedRows.value.filter(row => row.status === 'pending')
  
  if (pendingRows.length === 0) {
    ElMessage.warning('请选择待审批的申请')
    return
  }
  
  rejectForm.reject_reason = ''
  rejectForm.is_batch = true
  rejectForm.application_ids = pendingRows.map(row => row.id)
  rejectDialogVisible.value = true
}

// 查看详情
const handleViewDetail = (row) => {
  currentRow.value = row
  detailDialogVisible.value = true
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.admin-page {
  padding: 0;
  background: transparent;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: transparent;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
  margin: 0;
}

.filter-card {
  margin-bottom: 20px;
}

.table-card {
  min-height: 500px;
}

.batch-actions {
  margin-bottom: 16px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
