<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div>区域评估</div>
          <el-button @click="load" :loading="loading">刷新</el-button>
        </div>
      </template>

      <el-alert
        v-if="respRegion"
        type="info"
        show-icon
        :closable="false"
        style="margin-bottom:12px;"
        :title="`当前区域：${respRegion.province} / ${respRegion.city} / ${respRegion.name}`"
      />

      <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px;">
        <el-input v-model="filters.school_name" placeholder="学校名称" clearable style="width:220px" />
        <el-select v-model="filters.status" placeholder="状态" clearable style="width:160px">
          <el-option label="草稿" value="draft" />
          <el-option label="数据收集中" value="collecting" />
          <el-option label="分析中" value="analyzing" />
          <el-option label="已完成" value="completed" />
        </el-select>
        <el-select v-model="filters.maturity_level" placeholder="成熟度等级" clearable style="width:160px">
          <el-option label="引领级" value="leading" />
          <el-option label="成熟级" value="mature" />
          <el-option label="成长级" value="growing" />
          <el-option label="初始级" value="initial" />
        </el-select>
        <el-select v-model="filters.has_report" placeholder="是否有报告" clearable style="width:160px">
          <el-option label="有报告" value="true" />
          <el-option label="无报告" value="false" />
        </el-select>

        <el-select v-model="ordering" placeholder="排序" style="width:220px">
          <el-option label="完成时间倒序" value="-completed_at" />
          <el-option label="完成时间正序" value="completed_at" />
          <el-option label="创建时间倒序" value="-created_at" />
          <el-option label="总分倒序" value="-total_score" />
          <el-option label="学校名A-Z" value="school__name" />
        </el-select>

        <el-button type="primary" @click="search">查询</el-button>
        <el-button @click="reset">重置</el-button>
      </div>

      <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:12px;">
        <el-statistic title="学校数" :value="summary.school_count || 0" />
        <el-statistic title="评估数" :value="summary.has_assessment_count || 0" />
        <el-statistic title="完成数" :value="summary.completed_count || 0" />
        <el-statistic title="报告数" :value="summary.report_count || 0" />
      </div>

      <el-table :data="rows" border v-loading="loading" style="width:100%;">
        <el-table-column prop="id" label="评估ID" width="90" />
        <el-table-column label="学校" min-width="220">
          <template #default="{ row }">
            {{ row.school?.name || row.school_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120" />
        <el-table-column prop="maturity_level" label="等级" width="120" />
        <el-table-column label="总分" width="120">
          <template #default="{ row }">
            {{ row.scores?.total_score ?? row.total_score ?? '-' }}
          </template>
        </el-table-column>
        <el-table-column label="完成时间" min-width="170">
          <template #default="{ row }">
            {{ row.times?.completed_at || row.completed_at || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="报告" width="110">
          <template #default="{ row }">
            <el-tag v-if="row.report?.has_report" type="success">有</el-tag>
            <el-tag v-else type="info">无</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="goDetail(row.id)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top:14px;display:flex;justify-content:flex-end;">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          :page-size="pagination.page_size"
          :current-page="pagination.page"
          @size-change="onSizeChange"
          @current-change="onPageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { apiGet } from "@/utils/api";

const router = useRouter();
const loading = ref(false);

const rows = ref([]);
const respRegion = ref(null);

const summary = reactive({
  school_count: 0,
  has_assessment_count: 0,
  completed_count: 0,
  report_count: 0
});

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0,
  total_pages: 0
});

const ordering = ref("-completed_at");

const filters = reactive({
  status: "",
  maturity_level: "",
  school_name: "",
  has_report: ""
});

function buildQuery() {
  const q = new URLSearchParams();
  q.set("page", String(pagination.page));
  q.set("page_size", String(pagination.page_size));
  q.set("ordering", ordering.value);

  if (filters.status) q.set("status", filters.status);
  if (filters.maturity_level) q.set("maturity_level", filters.maturity_level);
  if (filters.school_name) q.set("school_name", filters.school_name);
  if (filters.has_report) q.set("has_report", filters.has_report);

  return q.toString();
}

async function load() {
  loading.value = true;
  try {
    const { data: resp } = await apiGet(`/api/region-admin/assessments/?${buildQuery()}`);
    if (!resp.success) throw new Error(resp.message || "加载失败");

    const d = resp.data || {};
    respRegion.value = d.region || null;
    rows.value = d.assessments || [];

    Object.assign(summary, d.summary || {});
    Object.assign(pagination, d.pagination || pagination);
  } catch (e) {
    ElMessage.error(e.message || "加载失败");
  } finally {
    loading.value = false;
  }
}

function search() {
  pagination.page = 1;
  load();
}

function reset() {
  filters.status = "";
  filters.maturity_level = "";
  filters.school_name = "";
  filters.has_report = "";
  ordering.value = "-completed_at";
  pagination.page = 1;
  pagination.page_size = 10;
  load();
}

function onSizeChange(size) {
  pagination.page_size = size;
  pagination.page = 1;
  load();
}

function onPageChange(page) {
  pagination.page = page;
  load();
}

function goDetail(id) {
  router.push(`/region-admin/assessments/${id}`);
}

onMounted(load);
</script>
