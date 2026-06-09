<template>
  <div class="dashboard-container">
    <!-- 1. 顶部 KPI 卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6" v-for="(val, key) in kpiLabels" :key="key">
        <el-card shadow="never" class="kpi-card" v-loading="loadingStats">
          <div class="kpi-value">{{ kpiData[key] || 0 }}</div>
          <div class="kpi-label">{{ val }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 2. 中部：区域分布统计表 -->
    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="section-header">各省份及下属区域评估学校数量统计</div>
      </template>
      <el-table :data="distribution" border stripe height="350" v-loading="loadingStats">
        <el-table-column type="index" label="序号" width="80" align="center" />
        <el-table-column prop="province" label="所属省份" align="center" />
        <el-table-column prop="district" label="参评区域名称" align="center" />
        <el-table-column prop="school_count" label="区域评估学校数量" align="center" />
      </el-table>
    </el-card>

    <!-- 3. 下部：评估列表 -->
    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="section-header">学校评估列表</div>
      </template>

      <!-- 搜索筛选 -->
      <div class="search-box">
        <el-form :inline="true" :model="filters" size="default">
          <el-form-item label="学校名称">
            <el-input v-model="filters.school_name" placeholder="请输入名称" clearable />
          </el-form-item>

          <el-form-item label="所在地区">
            <el-cascader
              v-model="filters.regionCodes"
              :options="chinaArea"
              placeholder="省/市/区"
              clearable
              :props="{ checkStrictly: true }"
            />
          </el-form-item>

          <el-form-item label="评估状态">
            <el-select v-model="filters.status" placeholder="全部" clearable style="width: 120px">
              <el-option label="已完成" value="completed" />
              <el-option label="采集中" value="collecting" />
            </el-select>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 数据表格 -->
      <el-table :data="listData" v-loading="loadingList" stripe>
        <el-table-column label="ID" width="80" align="center">
  <template #default="{ $index }">
    {{ (page - 1) * pageSize + $index + 1 }}
  </template>
</el-table-column>
        <el-table-column prop="school_name" label="学校名称" min-width="200" />
        <el-table-column prop="school_type_display" label="学校类型" width="120" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'info'">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_score" label="总分" width="100" align="center" />
        <el-table-column prop="maturity_level_display" label="成熟度等级" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewReport(row.id)">查看报告</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-bar">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next"
          :total="totalCount"
          v-model:current-page="page"
          v-model:page-size="pageSize"
          @current-change="loadList"
        />
      </div>
    </el-card>
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
import { regionData, codeToText } from 'element-china-area-data'
import request from '@/api/request'
import { useRouter } from 'vue-router'
// 1. 修正导入路径（根据你说的 assessment 在 utils 中）
import { getReportDataDetail } from '@/api/assessment' 

const router = useRouter()
const chinaArea = regionData

const kpiLabels = { provinces: '参评省份总数', regions: '参评区域总数', total_schools: '参评学校总数量', completed: '已完成评估学校数' }
const kpiData = ref({})
const distribution = ref([])
const listData = ref([])
const totalCount = ref(0)
const page = ref(1)
const pageSize = ref(20)

const loadingStats = ref(false)
const loadingList = ref(false)

const filters = reactive({ school_name: '', regionCodes: [], status: '' })

// 1. 获取统计数据
const loadStats = async () => {
  loadingStats.value = true
  try {
    const res = await request.get('/dashboard-stats/')
    // 
    console.log('统计接口返回原始数据:', res)

    const root = res.data || res
    
    // 如果后端返回的是 { "success": true, "data": { "kpi": ..., "distribution": ... } }
    const actualData = root.data || root

    kpiData.value = actualData.kpi || {}
    distribution.value = actualData.distribution || []
  } catch (err) {
    console.error('统计加载失败:', err)
  } finally {
    loadingStats.value = false
  }
}

// 2. 获取列表数据
const loadList = async () => {
  loadingList.value = true
  let prov = '', city = '', dist = ''
  if (filters.regionCodes?.length > 0) {
    prov = codeToText[filters.regionCodes[0]]
    city = codeToText[filters.regionCodes[1]] || ''
    dist = codeToText[filters.regionCodes[2]] || ''
  }

  try {
    const res = await request.get('/assessment-list/', {
      params: {
        page: page.value,
        page_size: pageSize.value,
        school_name: filters.school_name,
        status: filters.status,
        province: prov,
        city: city,
        district: dist
      }
    })
    console.log('列表接口返回原始数据:', res)

    // 自动适配分页数据的层级
    const root = res.data || res
    
    listData.value = root.results || [] // 重点：直接读取 root 里的 results
    totalCount.value = root.count || 0
  } catch (err) {
    console.error('列表加载失败:', err)
  } finally {
    loadingList.value = false
  }
}

const handleSearch = () => { page.value = 1; loadList() }
const handleReset = () => {
  filters.school_name = ''; filters.regionCodes = []; filters.status = '';
  handleSearch()
}
const viewReport = (id) => router.push(`/school/report/${id}`)

onMounted(() => {
  loadStats()
  loadList()
})
</script>

<style scoped>
.dashboard-container { padding: 20px; background: #f4f6f9; min-height: 100vh; }
.stat-row { margin-bottom: 25px; }
.kpi-card { text-align: center; border-radius: 8px; border: none; }
.kpi-value { font-size: 44px; font-weight: bold; color: #1a3a6e; margin-bottom: 8px; }
.kpi-label { font-size: 14px; color: #909399; }
.section-card { margin-bottom: 25px; border-radius: 8px; }
.section-header { font-weight: bold; font-size: 16px; border-left: 4px solid #409eff; padding-left: 12px; }
.search-box { background: #fafafa; padding: 18px 18px 0; border-radius: 8px; margin-bottom: 20px; border: 1px solid #eee; }
.pagination-bar { margin-top: 20px; display: flex; justify-content: flex-end; }
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