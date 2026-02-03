<template>
  <div class="schools-container">
    <div class="page-header">
      <h2 class="page-title">学校管理</h2>
      <el-button @click="loadSchools" :icon="Refresh">
        刷新
      </el-button>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" size="default">
        <el-form-item label="学校名称">
          <el-input
            v-model="filterForm.name"
            placeholder="请输入学校名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        
        <el-form-item label="学校类型">
          <el-select 
            v-model="filterForm.school_type" 
            placeholder="全部类型" 
            clearable
            style="width: 150px"
          >
            <el-option 
              v-for="type in SCHOOL_TYPES" 
              :key="type.value" 
              :label="type.label" 
              :value="type.value" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="省份">
          <el-input
            v-model="filterForm.province"
            placeholder="省份"
            clearable
            style="width: 150px"
          />
        </el-form-item>

        <el-form-item label="城市">
          <el-input
            v-model="filterForm.city"
            placeholder="城市"
            clearable
            style="width: 150px"
          />
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

    <!-- 学校列表 -->
    <el-card class="table-card">
      <el-table
        :data="schools"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="学校名称" min-width="200" />
        <el-table-column prop="school_type" label="学校类型" width="120">
          <template #default="{ row }">
            {{ getSchoolTypeText(row.school_type) }}
          </template>
        </el-table-column>
        <el-table-column label="所在地" width="180">
          <template #default="{ row }">
            {{ row.province }} {{ row.city }}
          </template>
        </el-table-column>
        <el-table-column prop="contact_name" label="联系人" width="100" />
        <el-table-column prop="contact_phone" label="联系电话" width="120" />
        <el-table-column label="评估状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getAssessmentStatusType(row.latest_assessment?.status)">
              {{ row.latest_assessment?.status_display || '数据采集中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="评估结果" min-width="200">
          <template #default="{ row }">
            <div v-if="row.latest_assessment?.status === 'completed'">
              <span class="score-text">总分: {{ parseFloat(row.latest_assessment.total_score).toFixed(1) }}</span>
              <el-tag size="small" effect="plain" class="level-tag">
                {{ row.latest_assessment.maturity_level_display }}
              </el-tag>
            </div>
            <span v-else class="no-result">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
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
          @size-change="loadSchools"
          @current-change="loadSchools"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { getSchools, deleteSchool } from '@/api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'

// 常量
const SCHOOL_TYPES = [
  { label: '小学', value: 'primary' },
  { label: '初中', value: 'junior' },
  { label: '高中', value: 'senior' },
  { label: '九年一贯制', value: 'nine_year' },
  { label: '十二年一贯制', value: 'twelve_year' }
]

// 状态
const loading = ref(false)
const schools = ref([])
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const filterForm = reactive({
  name: '',
  school_type: '',
  province: '',
  city: ''
})

// 生命周期
onMounted(() => {
  loadSchools()
})

// 方法
const loadSchools = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      name: filterForm.name || undefined,
      school_type: filterForm.school_type || undefined,
      province: filterForm.province || undefined,
      city: filterForm.city || undefined
    }
    
    const res = await getSchools(params)
    schools.value = res.results
    pagination.total = res.count
  } catch (error) {
    console.error('获取学校列表失败:', error)
    ElMessage.error('获取学校列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadSchools()
}

const handleReset = () => {
  filterForm.name = ''
  filterForm.school_type = ''
  filterForm.province = ''
  filterForm.city = ''
  handleSearch()
}

const getSchoolTypeText = (type) => {
  const found = SCHOOL_TYPES.find(t => t.value === type)
  return found ? found.label : type
}

const getAssessmentStatusType = (status) => {
  const map = {
    'draft': 'info',
    'collecting': 'primary',
    'analyzing': 'warning',
    'completed': 'success'
  }
  return map[status] || 'info'
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除学校"${row.name}"吗？\n\n此操作将同时删除：\n• 该学校的用户账号\n• 所有评估记录及数据\n• 对应的账号申请记录\n\n此操作不可恢复！`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    loading.value = true
    const res = await deleteSchool(row.id)
    
    if (res.success) {
      ElMessage.success(res.message || '删除成功')
      loadSchools()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.error?.message || '删除失败')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.schools-container {
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

.score-text {
  font-weight: 500;
  color: #409eff;
  margin-right: 8px;
}

.level-tag {
  font-size: 12px;
}

.no-result {
  color: #909399;
}
</style>
