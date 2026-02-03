<template>
  <div class="reports-container">
    <div class="page-header">
      <h2 class="page-title">评估报告管理</h2>
      <el-button @click="loadReports" :icon="Refresh">
        刷新
      </el-button>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" size="default">
        <el-form-item label="学校名称">
          <el-input
            v-model="filterForm.school_name"
            placeholder="请输入学校名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select 
            v-model="filterForm.status" 
            placeholder="全部状态" 
            clearable
            style="width: 150px"
          >
            <el-option label="草稿" value="draft" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            查询
          </el-button>
          <el-button @click="handleReset">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 报告列表 -->
    <el-card class="table-card">
      <el-table
        :data="reports"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="school_name" label="学校名称" min-width="200" />
        <el-table-column label="评估状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="总分" width="100">
          <template #default="{ row }">
            <span v-if="row.total_score">{{ parseFloat(row.total_score).toFixed(1) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="成熟度等级" width="150">
          <template #default="{ row }">
            <el-tag v-if="row.maturity_level" size="small" effect="plain">
              {{ row.maturity_level_display }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="row.status === 'completed'"
              link 
              type="primary" 
              @click="viewReport(row.id)"
            >
              查看报告
            </el-button>
            <span v-else class="text-gray">暂无报告</span>
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
          @size-change="loadReports"
          @current-change="loadReports"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Refresh } from '@element-plus/icons-vue'
import { getAssessmentReports } from '@/api/admin'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 状态
const loading = ref(false)
const reports = ref([])
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const filterForm = reactive({
  school_name: '',
  status: ''
})

// 生命周期
onMounted(() => {
  loadReports()
})

// 方法
const loadReports = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      school_name: filterForm.school_name || undefined,
      status: filterForm.status || undefined
    }
    
    const res = await getAssessmentReports(params)
    reports.value = res.results
    pagination.total = res.count
  } catch (error) {
    console.error('获取报告列表失败:', error)
    ElMessage.error('获取报告列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadReports()
}

const handleReset = () => {
  filterForm.school_name = ''
  filterForm.status = ''
  handleSearch()
}

const viewReport = (id) => {
  router.push(`/school/report/${id}`)
}

const getStatusType = (status) => {
  const map = {
    'draft': 'info',
    'completed': 'success'
  }
  return map[status] || 'info'
}

const formatDateTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString()
}
</script>

<style scoped>
.reports-container {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.filter-card {
  margin-bottom: 20px;
}

.table-card {
  min-height: 500px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.text-gray {
  color: #909399;
  font-size: 12px;
}
</style>
