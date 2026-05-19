<template>
  <div class="page">
    <div class="page-title">学校账户管理</div>

    <!-- 筛选 -->
    <el-card class="block">
      <div class="filter-bar">
        <el-input v-model="query.q" placeholder="学校名称" clearable class="w-220" />

        <el-select v-model="query.apply_status" placeholder="申请状态" clearable class="w-160">
          <el-option label="待审核" value="pending" />
          <el-option label="已通过" value="approved" />
          <el-option label="已拒绝" value="rejected" />
        </el-select>

        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="reset">重置</el-button>
      </div>
    </el-card>

    <!-- 表格 -->
    <el-card class="block">
      <el-table :data="rows" v-loading="loading" stripe>

        <el-table-column prop="id" label="ID" width="60" />

        <el-table-column label="学校名称" min-width="200">
          <template #default="{ row }">
            <div>
              <div>{{ row.name }}</div>
              <div class="sub">账号：{{ row.username || '-' }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            {{ schoolTypeLabel(row.school_type) }}
          </template>
        </el-table-column>

        <el-table-column label="所在地" min-width="150">
          <template #default="{ row }">
            {{ row.province }} {{ row.city }}
          </template>
        </el-table-column>

        <el-table-column label="申请状态" width="100">
          <template #default="{ row }">
            <el-tag :type="tagType(row.apply_status)">
              {{ statusLabel(row.apply_status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button
              type="danger"
              size="small"
              @click="remove(row)"
              :disabled="row._row_type === 'application' && row.apply_status === 'pending'"
            >
              删除
            </el-button>
          </template>
        </el-table-column>

      </el-table>

      <!-- 分页 -->
      <div class="pager">
        <el-pagination
          background
          layout="total, prev, pager, next"
          :total="total"
          :current-page="query.page"
          :page-size="query.page_size"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
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
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { apiGet, apiDelete } from "@/utils/api";

const loading = ref(false);
const rows = ref([]);
const total = ref(0);

const query = reactive({
  q: "",
  apply_status: "",
  page: 1,
  page_size: 10,
});

// ====== 接口 ======
const API_LIST = "/api/region-admin/schools/";

// ====== 加载数据 ======
async function load() {
  loading.value = true;
  try {
    const params = new URLSearchParams();

    if (query.q) params.set("q", query.q);
    if (query.apply_status) params.set("apply_status", query.apply_status);

    params.set("page", query.page);
    params.set("page_size", query.page_size);

    const { data: resp } = await apiGet(`${API_LIST}?${params.toString()}`);

    if (!resp.success) throw new Error(resp.message);

    rows.value = resp.data.results || [];
    total.value = resp.data.pagination.total || 0;

  } catch (e) {
    ElMessage.error(e.message || "加载失败");
  } finally {
    loading.value = false;
  }
}

// ====== 删除（核心）======
async function remove(row) {
  try {
    await ElMessageBox.confirm(
      `删除「${row.name}」将不可恢复，是否继续？`,
      "警告",
      {
        confirmButtonText: "删除",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    let url = "";

    if (row._row_type === "application") {
      url = `/api/region-admin/applications/${row.application_id}/`;
    } else if (row._row_type === "school") {
      url = `/api/region-admin/schools/${row.id}/`;
    } else {
      ElMessage.error("类型错误");
      return;
    }

    const { data: resp } = await apiDelete(url);

    if (!resp.success) throw new Error(resp.message);

    ElMessage.success("删除成功");
    load();

  } catch (e) {
    if (e === "cancel") return;
    ElMessage.error(e.message || "删除失败");
  }
}

// ====== 工具 ======
function statusLabel(v) {
  return {
    pending: "待审核",
    approved: "已通过",
    rejected: "已拒绝",
  }[v] || "-";
}

function tagType(v) {
  return {
    pending: "warning",
    approved: "success",
    rejected: "danger",
  }[v] || "info";
}

function schoolTypeLabel(v) {
  const map = {
    primary: "小学",
    junior: "初中",
    senior: "高中",
    nine_year: "九年一贯制",
    twelve_year: "十二年一贯制",
  };

  return map[v] || v || "-";
}

// ====== 操作 ======
function handleSearch() {
  query.page = 1;
  load();
}

function reset() {
  query.q = "";
  query.apply_status = "";
  query.page = 1;
  load();
}

function handlePageChange(p) {
  query.page = p;
  load();
}

onMounted(load);
</script>

<style scoped>
.page {
  padding: 16px;
  min-height: 100vh;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 12px;
}

.block {
  margin-bottom: 16px;
}

.filter-bar {
  display: flex;
  gap: 10px;
}

.w-220 {
  width: 220px;
}

.w-160 {
  width: 160px;
}

.sub {
  font-size: 12px;
  color: #999;
}

.pager {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

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