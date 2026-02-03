<template>
  <div class="page">
    <!-- 顶部：区域信息 + 刷新 -->
    <el-card class="block">
      <template #header>
        <div class="card-header">
          <div class="title">区域中小学数据文化成熟度评估概览</div>
          <el-button @click="reloadAll" :loading="loadingOverview || loadingList">刷新</el-button>
        </div>
      </template>

      <el-skeleton :loading="loadingOverview" animated>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="省份">{{ overview.region?.province || "-" }}</el-descriptions-item>
          <el-descriptions-item label="城市">{{ overview.region?.city || "-" }}</el-descriptions-item>
          <el-descriptions-item label="区县">{{ overview.region?.name || "-" }}</el-descriptions-item>
          <el-descriptions-item label="行政编码">{{ overview.region?.code || "-" }}</el-descriptions-item>
        </el-descriptions>

        <div class="stat-grid">
          <div class="stat-card">
            <div class="stat-num">{{ overview.school_count || 0 }}</div>
            <div class="stat-label">学校总数</div>
          </div>
          <div class="stat-card">
            <div class="stat-num">{{ overview.has_assessment_count || 0 }}</div>
            <div class="stat-label">已创建评估学校数</div>
          </div>
          <div class="stat-card">
            <div class="stat-num">{{ overview.completed_count || 0 }}</div>
            <div class="stat-label">已完成评估数</div>
          </div>
          <div class="stat-card">
            <div class="stat-num">{{ overview.report_count || 0 }}</div>
            <div class="stat-label">已生成报告数</div>
          </div>
        </div>
      </el-skeleton>
    </el-card>

    <!-- 下方：筛选 + 表格 -->
    <el-card class="block">
      <template #header>
        <div class="card-header">
          <div class="title">学校评估列表</div>
        </div>
      </template>

      <!-- 筛选条 -->
      <!-- 筛选条 -->
<div class="filter-panel">
  <el-form class="filter-form" :model="query" @submit.prevent>
    <el-form-item label="学校名称">
      <el-input
        v-model="query.school_name"
        placeholder="学校名称"
        clearable
        class="w-name"
        @keyup.enter="handleSearch"
      />
    </el-form-item>

    <el-form-item label="学校类型">
      <el-select v-model="query.school_type" clearable class="w-select">
        <el-option label="小学" value="primary" />
        <el-option label="初中" value="junior" />
        <el-option label="高中" value="senior" />
        <el-option label="九年一贯制" value="nine_year" />
        <el-option label="十二年一贯制" value="twelve_year" />
      </el-select>
    </el-form-item>

    <el-form-item label="评估状态">
      <el-select v-model="query.status" clearable class="w-select">
        <el-option label="草稿" value="draft" />
        <el-option label="数据收集中" value="collecting" />
        <el-option label="分析中" value="analyzing" />
        <el-option label="已完成" value="completed" />
      </el-select>
    </el-form-item>

    <el-form-item label="评估时间">
  <el-date-picker
    v-model="query.time_range"
    type="daterange"
    range-separator="至"
    start-placeholder="开始日期"
    end-placeholder="结束日期"
    value-format="YYYY-MM-DD"
    class="w-date"
  />
</el-form-item>

    <el-form-item label="成熟度等级">
      <el-select v-model="query.maturity_level" clearable class="w-select">
        <el-option label="引领级" value="leading" />
        <el-option label="成熟级" value="mature" />
        <el-option label="成长级" value="growing" />
        <el-option label="初始级" value="initial" />
      </el-select>
    </el-form-item>

    <!-- 操作按钮 -->
    <el-form-item class="actions">
      <el-button type="primary" @click="handleSearch" :loading="loadingList">
        查询
      </el-button>
      <el-button @click="handleReset">
        重置
      </el-button>
    </el-form-item>
  </el-form>
</div>


      <!-- 表格（注意：这里展示的是拍平后的 list） -->
      <el-table
        class="table"
        :data="list"
        v-loading="loadingList"
        stripe
        @sort-change="handleSortChange"
      >
        <el-table-column prop="id" label="ID" width="80" />

        <el-table-column prop="school_name" label="学校名称" min-width="220" show-overflow-tooltip />

        <el-table-column prop="school_type" label="学校类型" width="140">
          <template #default="{ row }">
            <span>{{ schoolTypeLabel(row.school_type) }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="评估状态" width="130">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="total_score" label="总分" width="120" sortable="custom">
          <template #default="{ row }">
            <span class="score">{{ formatScore(row.total_score) }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="maturity_level" label="成熟度等级" width="140">
          <template #default="{ row }">
            <el-tag v-if="row.maturity_level" type="info" effect="plain">
              {{ maturityLabel(row.maturity_level) }}
            </el-tag>
            <span v-else class="muted">-</span>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="创建时间" width="190" sortable="custom">
          <template #default="{ row }">
            {{ row.created_at || "-" }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
    <!-- 参考 Admin：只有状态为 completed 时才允许点击 -->
    <el-button 
      v-if="row.status === 'completed'" 
      type="primary" 
      link 
      @click="viewReport(row.id)"
    >
      查看报告
    </el-button>
    
    <!-- 否则显示灰色文字提示 -->
    <span v-else style="color: #909399; font-size: 12px;">暂无报告</span>
  </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pager">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          :page-size="query.page_size"
          :current-page="query.page"
          :page-sizes="[10, 20, 50]"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { apiGet } from "@/utils/api";
import { useRouter } from 'vue-router'
import { getAssessmentData } from '@/utils/assessments' 

const router = useRouter()

const loadingOverview = ref(false);
const loadingList = ref(false);

const overview = ref({
  region: null,
  school_count: 0,
  has_assessment_count: 0,
  completed_count: 0,
  report_count: 0
});

const list = ref([]);
const total = ref(0);

const query = reactive({
  school_name: "",
  school_type: "",      // ✅ 新增：学校类型
  status: "",
  time_range: [],
  maturity_level: "",

  page: 1,
  page_size: 20,
  ordering: ""          // total_score / -total_score / created_at / -created_at
});

function parseScoreRange(range) {
  if (!range) return {};
  const [a, b] = range.split("_").map(Number);
  if (Number.isNaN(a) || Number.isNaN(b)) return {};
  return { score_min: a, score_max: b };
}

/** ✅ 统一构建 querystring（你现在的 loadList 用这个） */
function buildQueryString() {
  const params = new URLSearchParams();

  if (query.school_name) params.set("school_name", query.school_name);
  if (query.school_type) params.set("school_type", query.school_type); // ✅ 新增
  if (query.status) params.set("status", query.status);
  if (query.maturity_level) params.set("maturity_level", query.maturity_level);

  if (query.time_range && query.time_range.length === 2) {
    params.set("start_at", query.time_range[0]); // 对应后端开始时间字段
    params.set("end_at", query.time_range[1]);   // 对应后端结束时间字段
  }

  params.set("page", String(query.page));
  params.set("page_size", String(query.page_size));

  if (query.ordering) params.set("ordering", query.ordering);

  return params.toString();
}

async function loadOverview() {
  loadingOverview.value = true;
  try {
    const { data: resp } = await apiGet("/api/region-admin/overview/");
    if (!resp.success) throw new Error(resp.message || "加载失败");
    overview.value = resp.data;
  } catch (e) {
    ElMessage.error(e.message || "加载失败");
  } finally {
    loadingOverview.value = false;
  }
}

async function loadList() {
  loadingList.value = true;
  try {
    const qs = buildQueryString();
    const { data: resp } = await apiGet(`/api/region-admin/assessments/?${qs}`);
    if (!resp.success) throw new Error(resp.message || "加载失败");

    // ✅ 后端返回：data.assessments（嵌套结构）=> 这里拍平给 el-table 用
    const raw = resp.data?.assessments || [];
    list.value = raw.map((it) => ({
      id: it.id,
      status: it.status,
      maturity_level: it.maturity_level,

      school_id: it.school?.id,
      school_name: it.school?.name || "-",
      school_type: it.school?.school_type || "",

      total_score: it.scores?.total_score,
      created_at: it.times?.created_at,

      report_available: !!it.report?.has_report,
      report_url: it.report?.report_url || null
    }));

    total.value = resp.data?.pagination?.total || 0;
  } catch (e) {
    console.error(e);
    ElMessage.error(e.message || "加载失败");
  } finally {
    loadingList.value = false;
  }
}

async function reloadAll() {
  await Promise.all([loadOverview(), loadList()]);
}

async function handleSearch() {
  query.page = 1;
  await loadList();
}

async function handleReset() {
  query.school_name = "";
  query.school_type = "";   // 
  query.status = "";
  query.time_range = [];
  query.maturity_level = "";
  query.page = 1;
  query.page_size = 20;
  query.ordering = "";
  await loadList();
}

async function handlePageChange(p) {
  query.page = p;
  await loadList();
}

async function handleSizeChange(s) {
  query.page_size = s;
  query.page = 1;
  await loadList();
}

/** ✅ 排序：ElementPlus custom sort（字段要对齐后端 allowed） */
async function handleSortChange({ prop, order }) {
  if (!order) query.ordering = "";
  else query.ordering = order === "ascending" ? prop : `-${prop}`;
  await loadList();
}

const viewReport = (id) => {
  if (!id) {
    ElMessage.warning('报告 ID 不存在')
    return
  }
  // 跳转到报告详情页
  router.push(`/school/report/${id}`)
}

/** ======= label utils ======= */
function statusLabel(s) {
  const m = { draft: "草稿", collecting: "数据收集中", analyzing: "分析中", completed: "已完成" };
  return m[s] || "-";
}

function statusTagType(s) {
  if (s === "completed") return "success";
  if (s === "draft") return "info";
  if (s === "collecting") return "warning";
  if (s === "analyzing") return "primary";
  return "info";
}

function maturityLabel(v) {
  const m = { leading: "引领级", mature: "成熟级", growing: "成长级", initial: "初始级" };
  return m[v] || v || "-";
}

function schoolTypeLabel(v) {
  const m = {
    primary: "小学",
    junior: "初中",
    senior: "高中",
    nine_year: "九年一贯制",
    twelve_year: "十二年一贯制"
  };
  return m[v] || "-";
}

function formatScore(v) {
  if (v === null || v === undefined || v === "") return "-";
  const n = Number(v);
  if (Number.isNaN(n)) return "-";
  return n.toFixed(1);
}

onMounted(async () => {
  await reloadAll();
});
</script>

<style scoped>
.page {
  padding: 16px;
  background: #f5f7fa;
  min-height: calc(100vh - 0px);
}
.block {
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
  margin-bottom: 14px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title {
  font-weight: 600;
  color: #303133;
}

.stat-grid {
  margin-top: 14px;
  display: grid;
  grid-template-columns: repeat(4, minmax(200px, 1fr));
  gap: 14px;
}
.stat-card {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 14px 10px;
  text-align: center;
}
.stat-num {
  font-size: 32px;
  font-weight: 700;
  color: #1f5fbf;
  line-height: 1.1;
}
.stat-label {
  margin-top: 6px;
  font-size: 13px;
  color: #606266;
}

.filter-panel {
  padding: 6px 2px 10px;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 10px;
}
.filter-actions {
  display: inline-flex;
  gap: 10px;
  align-items: center;
  margin-left: auto;
}

.table { width: 100%; }
.score { font-weight: 600; color: #303133; }
.muted { color: #909399; }

.pager {
  padding: 12px 4px 0;
  display: flex;
  justify-content: flex-end;
}

/* ===== 筛选条一行布局 ===== */
.filter-form {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;   /* 🔴 关键：不允许换行 */
  gap: 12px;
}

.filter-form .el-form-item {
  margin-bottom: 0;    /* 去掉 el-form 默认下边距 */
}

/* 学校名称稍微宽一点 */
.w-name {
  width: 220px;
}

/* 下拉统一宽度 */
.w-select {
  width: 140px;
}

/* 按钮靠右一点但仍在一行 */
.actions {
  margin-left: auto;     /* 将按钮推向最右侧 */
  flex-shrink: 0;        /* 强制不压缩按钮区域 */
  margin-right: 0;       /* 确保没有右边距 */
}

/* 关键：强制 el-form-item 内部的内容（即两个按钮）不换行 */
.actions :deep(.el-form-item__content) {
  display: flex;
  flex-wrap: nowrap;     /* 强制按钮水平排列 */
  gap: 10px;             /* 按钮之间的间距 */
  align-items: center;
}


.w-date {
  width: 120px !important; /* 根据实际视觉调整 */
}


@media (max-width: 1200px) {
  .stat-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 720px) {
  .stat-grid { grid-template-columns: 1fr; }
}
</style>
