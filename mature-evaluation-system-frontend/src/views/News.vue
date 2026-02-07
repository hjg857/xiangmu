<template>
  <div class="news-page">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-content">
        <div class="logo-section" @click="goHome">
          <el-icon :size="32" color="#409eff"><School /></el-icon>
          <h1 class="system-title">中小学校数据文化成熟度评估监测系统</h1>
        </div>
        <nav class="nav-menu">
          <router-link to="/home" class="nav-item">首页</router-link>
          <router-link to="/about" class="nav-item">关于我们</router-link>
          <router-link to="/culture" class="nav-item">数据文化</router-link>
          <router-link to="/guide" class="nav-item">评估说明</router-link>
          <router-link to="/news" class="nav-item">实践动态</router-link>
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

    <!-- 主体内容区 -->
    <main class="main-content">
      <div class="content-container">
        <h2 class="page-title">实践动态</h2>
        <div class="title-underline"></div>
        <p class="page-subtitle">探索数据教育应用新趋势</p>
        
        <!-- 管理员操作按钮 -->
        <div v-if="isAdmin" class="admin-toolbar">
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            发布动态
          </el-button>
        </div>

        <!-- 动态列表 -->
        <div v-loading="loading" class="news-grid">
          <div v-for="item in newsList" :key="item.id" class="news-card">
            <div class="card-image">
              <img :src="item.cover_image_url || 'https://via.placeholder.com/400x225'" :alt="item.title" />
              <div class="date-badge">{{ item.publish_date }}</div>
            </div>
            <div class="card-content">
              <h3 class="card-title">{{ item.title }}</h3>
              <p class="card-summary">{{ item.summary }}</p>
              <div class="card-footer">
                <el-button type="primary" link @click="viewDetail(item)">阅读更多</el-button>
                <div v-if="isAdmin" class="admin-actions">
                  <el-button size="small" @click="editNews(item)">编辑</el-button>
                  <el-button size="small" type="danger" @click="confirmDelete(item)">删除</el-button>
                </div>
              </div>
            </div>
          </div>
          <el-empty v-if="!loading && newsList.length === 0" description="暂无实践动态" />
        </div>
      </div>
    </main>

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

    <!-- 详情对话框 -->
    <el-dialog v-model="detailDialogVisible" :title="currentNews.title" width="800px">
      <div class="news-detail">
        <div class="detail-meta">
          <span>{{ currentNews.publish_date }}</span>
          <span>浏览：{{ currentNews.view_count || 0 }}</span>
        </div>
        <div class="detail-content" v-html="currentNews.content"></div>
      </div>
    </el-dialog>

    <!-- 发布/编辑对话框 -->
    <el-dialog v-model="formDialogVisible" :title="isEdit ? '编辑动态' : '发布动态'" width="900px">
      <el-form :model="newsForm" :rules="formRules" ref="newsFormRef" label-width="100px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="newsForm.title" placeholder="请输入标题" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item label="摘要" prop="summary">
          <el-input v-model="newsForm.summary" type="textarea" :rows="3" placeholder="请输入摘要" maxlength="500" show-word-limit />
        </el-form-item>
        <el-form-item label="封面图片">
          <el-upload
            class="cover-uploader"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleFileChange"
            accept="image/*"
          >
            <img v-if="newsForm.cover_image_url" :src="newsForm.cover_image_url" class="cover-preview" />
            <el-icon v-else class="cover-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <div class="upload-tip">建议尺寸：800x450px，支持JPG、PNG格式，大小不超过5MB</div>
        </el-form-item>
        <el-form-item label="详细内容" prop="content">
          <el-input v-model="newsForm.content" type="textarea" :rows="10" placeholder="请输入详细内容" />
        </el-form-item>
        <el-form-item label="发布日期" prop="publish_date">
          <el-date-picker v-model="newsForm.publish_date" type="date" placeholder="选择发布日期" format="YYYY-MM-DD" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="是否发布">
          <el-switch v-model="newsForm.is_published" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { School, User, Location, Message, Plus } from '@element-plus/icons-vue'
import { getNewsList, getNewsDetail, createNews, updateNews, deleteNews } from '@/api/news'

const router = useRouter()
const userInfo = ref({ username: '', role: '' })
const schoolName = ref('')
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

const isAdmin = computed(() => userInfo.value.role === 'admin')

onMounted(() => {
  const storedUser = localStorage.getItem('user')
  if (storedUser) {
    userInfo.value = JSON.parse(storedUser)
    schoolName.value = userInfo.value.school_name || userInfo.value.username || '用户'
  }
  loadNewsList()
})

const loadNewsList = async () => {
  loading.value = true
  try {
    const res = await getNewsList()
    if (res.success) newsList.value = res.data || []
  } catch (error) {
    ElMessage.error('加载动态列表失败')
  } finally {
    loading.value = false
  }
}

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

const confirmDelete = (item) => {
  ElMessageBox.confirm(`确定要删除动态"${item.title}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
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

const handleFileChange = async (file) => {
  // 验证文件
  const isImage = file.raw.type.startsWith('image/')
  const isLt5M = file.raw.size / 1024 / 1024 < 5
  
  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return
  }
  
  try {
    const { uploadNewsImage } = await import('@/api/news')
    const res = await uploadNewsImage(file.raw)
    
    if (res.success) {
      newsForm.value.cover_image_url = res.data.url
      newsForm.value.cover_image = res.data.path
      ElMessage.success('上传成功')
    } else {
      ElMessage.error(res.message || '上传失败')
    }
  } catch (error) {
    console.error('上传错误:', error)
    ElMessage.error(error.response?.data?.error?.message || '上传失败')
  }
}

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
        cover_image: newsForm.value.cover_image || '',
        publish_date: newsForm.value.publish_date,
        is_published: newsForm.value.is_published
      }
      
      console.log('提交的数据:', data)
      
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
      console.error('提交错误:', error)
      ElMessage.error(error.response?.data?.error?.message || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

const goHome = () => router.push('/home')
const handleLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.news-page { min-height: 100vh; display: flex; flex-direction: column; background-color: #f5f7fa; }
.header { background-color: #ffffff; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); position: sticky; top: 0; z-index: 1000; }
.header-content { max-width: 1400px; margin: 0 auto; padding: 0 40px; height: 70px; display: flex; justify-content: space-between; align-items: center; }
.logo-section { display: flex; align-items: center; gap: 12px; cursor: pointer; }
.system-title { font-size: 20px; font-weight: 600; color: #303133; margin: 0; }
.nav-menu { display: flex; align-items: center; gap: 32px; }
.nav-item { color: #606266; text-decoration: none; font-size: 15px; transition: color 0.3s; }
.nav-item:hover, .nav-item.router-link-active { color: #409eff; }
.user-dropdown { cursor: pointer; }
.user-info { display: flex; align-items: center; gap: 6px; color: #606266; font-size: 14px; }
.user-info:hover { color: #409eff; }
.main-content { flex: 1; padding: 60px 40px 80px; }
.content-container { max-width: 1400px; margin: 0 auto; }
.page-title { font-size: 36px; font-weight: 700; color: #303133; text-align: center; margin-bottom: 8px; }
.title-underline { width: 60px; height: 4px; background-color: #ff9800; margin: 0 auto 16px; border-radius: 2px; }
.page-subtitle { font-size: 16px; color: #909399; text-align: center; margin-bottom: 40px; }
.admin-toolbar { text-align: right; margin-bottom: 30px; }
.news-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px; min-height: 200px; }
.news-card { background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08); transition: all 0.3s; display: flex; flex-direction: column; }
.news-card:hover { transform: translateY(-8px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); }
.card-image { position: relative; width: 100%; height: 200px; overflow: hidden; }
.card-image img { width: 100%; height: 100%; object-fit: cover; }
.date-badge { position: absolute; top: 16px; left: 16px; background-color: #ff9800; color: white; padding: 4px 12px; border-radius: 4px; font-size: 13px; font-weight: 500; }
.card-content { padding: 20px; flex: 1; display: flex; flex-direction: column; }
.card-title { font-size: 18px; font-weight: 600; color: #303133; margin-bottom: 12px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.card-summary { font-size: 14px; color: #606266; line-height: 1.6; margin-bottom: 16px; flex: 1; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.card-footer { display: flex; justify-content: space-between; align-items: center; margin-top: auto; }
.admin-actions { display: flex; gap: 8px; }
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
.contact-section { flex: 1; }
.contact-title { font-size: 16px; font-weight: 600; color: #303133; margin-bottom: 12px; }
.contact-details { display: flex; flex-direction: column; gap: 8px; }
.contact-details p { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #606266; margin: 0; }
.contact-details .el-icon { color: #409eff; }
.qrcode-section { flex-shrink: 0; }
.qrcode { width: 100px; height: 100px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); }
.news-detail { padding: 20px 0; }
.detail-meta { display: flex; gap: 20px; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid #e4e7ed; color: #909399; font-size: 14px; }
.detail-content { font-size: 15px; line-height: 1.8; color: #303133; }
.cover-uploader { width: 300px; height: 169px; border: 1px dashed #d9d9d9; border-radius: 6px; cursor: pointer; overflow: hidden; transition: border-color 0.3s; }
.cover-uploader:hover { border-color: #409eff; }
.cover-preview { width: 100%; height: 100%; object-fit: cover; }
.cover-uploader-icon { font-size: 28px; color: #8c939d; width: 300px; height: 169px; display: flex; align-items: center; justify-content: center; }
.upload-tip { font-size: 12px; color: #909399; margin-top: 8px; }
@media (max-width: 1024px) { .news-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) { .news-grid { grid-template-columns: 1fr; } }
</style>
