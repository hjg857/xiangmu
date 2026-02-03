<template>
  <div class="admin-page">
    <div class="page-header">
      <h2 class="page-title">实践动态管理</h2>
      <el-button type="primary" @click="showAddDialog">
        <el-icon><Plus /></el-icon>
        发布动态
      </el-button>
    </div>

    <!-- 动态列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="newsList"
        style="width: 100%"
        stripe
      >
        <el-table-column type="index" label="序号" width="60" />
        
        <el-table-column label="封面" width="100">
          <template #default="{ row }">
            <el-image
              v-if="row.cover_image_url"
              :src="row.cover_image_url"
              fit="cover"
              style="width: 60px; height: 40px; border-radius: 4px;"
              :preview-src-list="[row.cover_image_url]"
            />
            <span v-else class="no-image">无封面</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        
        <el-table-column prop="summary" label="摘要" min-width="250" show-overflow-tooltip />
        
        <el-table-column prop="publish_date" label="发布日期" width="110" />
        
        <el-table-column prop="view_count" label="浏览量" width="80" align="center" />
        
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_published ? 'success' : 'info'" size="small">
              {{ row.is_published ? '已发布' : '未发布' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetail(row)">查看</el-button>
            <el-button type="primary" link size="small" @click="editNews(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="confirmDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 空状态 -->
      <el-empty v-if="!loading && newsList.length === 0" description="暂无实践动态" />
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="currentNews.title"
      width="800px"
    >
      <div class="news-detail">
        <div class="detail-meta">
          <span class="detail-date">发布日期：{{ currentNews.publish_date }}</span>
          <span class="detail-views">浏览量：{{ currentNews.view_count || 0 }}</span>
          <el-tag :type="currentNews.is_published ? 'success' : 'info'" size="small">
            {{ currentNews.is_published ? '已发布' : '未发布' }}
          </el-tag>
        </div>
        
        <div v-if="currentNews.cover_image_url" class="detail-cover">
          <el-image :src="currentNews.cover_image_url" fit="cover" />
        </div>
        
        <div class="detail-summary">
          <h4>摘要</h4>
          <p>{{ currentNews.summary }}</p>
        </div>
        
        <div class="detail-content">
          <h4>详细内容</h4>
          <div v-html="currentNews.content"></div>
        </div>
      </div>
    </el-dialog>

    <!-- 发布/编辑对话框 -->
    <el-dialog
      v-model="formDialogVisible"
      :title="isEdit ? '编辑动态' : '发布动态'"
      width="900px"
      :close-on-click-modal="false"
    >
      <el-form :model="newsForm" :rules="formRules" ref="newsFormRef" label-width="100px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="newsForm.title" placeholder="请输入标题" maxlength="200" show-word-limit />
        </el-form-item>
        
        <el-form-item label="摘要" prop="summary">
          <el-input
            v-model="newsForm.summary"
            type="textarea"
            :rows="3"
            placeholder="请输入摘要"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="封面图片" prop="cover_image">
          <el-upload
            class="cover-uploader"
            :action="uploadUrl"
            :headers="uploadHeaders"
            name="image"
            :show-file-list="false"
            :on-success="handleCoverSuccess"
            :on-error="handleCoverError"
            :before-upload="beforeCoverUpload"
          >
            <img v-if="newsForm.cover_image_url" :src="newsForm.cover_image_url" class="cover-preview" />
            <div v-else class="upload-placeholder">
              <el-icon class="upload-icon"><Plus /></el-icon>
              <div class="upload-text">点击上传封面</div>
            </div>
          </el-upload>
          <div class="upload-tip">建议尺寸：800x450px，支持JPG、PNG格式，大小不超过5MB</div>
        </el-form-item>
        
        <el-form-item label="详细内容" prop="content">
          <el-input
            v-model="newsForm.content"
            type="textarea"
            :rows="12"
            placeholder="请输入详细内容（支持HTML格式）"
          />
          <div class="content-tip">提示：可以使用HTML标签来格式化内容，如 &lt;p&gt;、&lt;h3&gt;、&lt;strong&gt; 等</div>
        </el-form-item>
        
        <el-form-item label="发布日期" prop="publish_date">
          <el-date-picker
            v-model="newsForm.publish_date"
            type="date"
            placeholder="选择发布日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="是否发布" prop="is_published">
          <el-switch v-model="newsForm.is_published" />
          <span class="form-tip">关闭后，动态将不会在前台显示</span>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          {{ isEdit ? '保存' : '发布' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getNewsList, getNewsDetail, createNews, updateNews, deleteNews } from '@/api/news'

const loading = ref(false)
const newsList = ref([])
const currentNews = ref({})
const detailDialogVisible = ref(false)
const formDialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const newsFormRef = ref(null)

const newsForm = ref({
  title: '',
  summary: '',
  content: '',
  cover_image: '',
  cover_image_url: '',
  publish_date: new Date().toISOString().split('T')[0],
  is_published: true
})

const formRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  summary: [{ required: true, message: '请输入摘要', trigger: 'blur' }],
  content: [{ required: true, message: '请输入详细内容', trigger: 'blur' }],
  publish_date: [{ required: true, message: '请选择发布日期', trigger: 'change' }]
}

const uploadUrl = computed(() => {
  // 使用相对路径，通过vite代理转发到后端
  return '/api/admin/news/upload-image/'
})

const uploadHeaders = computed(() => {
  const token = localStorage.getItem('access_token')
  return {
    'Authorization': `Bearer ${token}`
  }
})

onMounted(() => {
  loadNewsList()
})

// 加载动态列表
const loadNewsList = async () => {
  loading.value = true
  try {
    const res = await getNewsList()
    if (res.success) {
      newsList.value = res.data || []
    }
  } catch (error) {
    ElMessage.error('加载动态列表失败')
  } finally {
    loading.value = false
  }
}

// 查看详情
const viewDetail = async (item) => {
  try {
    const res = await getNewsDetail(item.id)
    if (res.success) {
      currentNews.value = res.data
      detailDialogVisible.value = true
    }
  } catch (error) {
    ElMessage.error('加载详情失败')
  }
}

// 显示发布对话框
const showAddDialog = () => {
  isEdit.value = false
  newsForm.value = {
    title: '',
    summary: '',
    content: '',
    cover_image: '',
    cover_image_url: '',
    publish_date: new Date().toISOString().split('T')[0],
    is_published: true
  }
  formDialogVisible.value = true
}

// 编辑动态
const editNews = (item) => {
  isEdit.value = true
  newsForm.value = {
    id: item.id,
    title: item.title,
    summary: item.summary,
    content: item.content,
    cover_image: item.cover_image,
    cover_image_url: item.cover_image_url,
    publish_date: item.publish_date,
    is_published: item.is_published
  }
  formDialogVisible.value = true
}

// 确认删除
const confirmDelete = (item) => {
  ElMessageBox.confirm(
    `确定要删除动态"${item.title}"吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const res = await deleteNews(item.id)
      if (res.success) {
        ElMessage.success('删除成功')
        loadNewsList()
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// 封面上传成功
const handleCoverSuccess = (response) => {
  if (response.success) {
    newsForm.value.cover_image_url = response.data.url
    newsForm.value.cover_image = response.data.path
    ElMessage.success('上传成功')
  } else {
    ElMessage.error(response.message || '上传失败')
  }
}

// 封面上传失败
const handleCoverError = (error) => {
  console.error('上传失败:', error)
  ElMessage.error('上传失败，请重试')
}

// 封面上传前验证
const beforeCoverUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}

// 提交表单
const submitForm = async () => {
  if (!newsFormRef.value) return
  
  await newsFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    
    try {
      const data = {
        title: newsForm.value.title,
        summary: newsForm.value.summary,
        content: newsForm.value.content,
        cover_image: newsForm.value.cover_image,
        publish_date: newsForm.value.publish_date,
        is_published: newsForm.value.is_published
      }
      
      let res
      if (isEdit.value) {
        res = await updateNews(newsForm.value.id, data)
      } else {
        res = await createNews(data)
      }
      
      if (res.success) {
        ElMessage.success(isEdit.value ? '更新成功' : '发布成功')
        formDialogVisible.value = false
        loadNewsList()
      }
    } catch (error) {
      ElMessage.error(error.response?.data?.error?.message || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}
</script>

<style scoped>
.admin-page {
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

.table-card {
  min-height: 400px;
}

.no-image {
  color: #909399;
  font-size: 12px;
}

/* 详情对话框 */
.news-detail {
  padding: 10px 0;
}

.detail-meta {
  display: flex;
  gap: 20px;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
  color: #606266;
  font-size: 14px;
}

.detail-cover {
  margin-bottom: 20px;
}

.detail-cover .el-image {
  width: 100%;
  border-radius: 8px;
}

.detail-summary,
.detail-content {
  margin-bottom: 20px;
}

.detail-summary h4,
.detail-content h4 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.detail-summary p {
  font-size: 14px;
  line-height: 1.8;
  color: #606266;
  margin: 0;
}

.detail-content :deep(p) {
  font-size: 14px;
  line-height: 1.8;
  color: #303133;
  margin: 12px 0;
}

/* 表单样式 */
.cover-uploader {
  width: 300px;
  height: 169px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  overflow: hidden;
  transition: border-color 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cover-uploader:hover {
  border-color: #409eff;
}

.cover-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.upload-icon {
  font-size: 28px;
  color: #8c939d;
  margin-bottom: 8px;
}

.upload-text {
  font-size: 14px;
  color: #606266;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
  line-height: 1.5;
}

.content-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
  line-height: 1.5;
}

.form-tip {
  margin-left: 12px;
  font-size: 12px;
  color: #909399;
}
</style>
