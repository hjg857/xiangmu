<template>
  <div class="page">
    <div class="page-title">学校账户管理</div>

    <!-- 顶部：导入区（按图样式做展示，但你说不用批量导入，我保留外观 + 单个创建入口） -->
    <el-card class="block">
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
          <div class="drop-title">点击或拖拽文件至此处上传</div>
          <div class="drop-sub">支持格式：Excel（.xlsx/.xls），单次最多导入100条</div>
          </el-upload>


          <div class="import-actions">
            <el-button @click="downloadTemplate">下载导入模板</el-button>
            <el-button type="primary" @click="goCreateOne">
              创建单个学校账号
            </el-button>
          </div>

          <!-- 导入预览弹窗 -->
<el-dialog v-model="previewVisible" title="批量导入预览" width="980px">
  <div v-loading="previewLoading">
    <el-alert
      v-if="previewErrors.length"
      type="error"
      :closable="false"
      show-icon
      title="解析失败"
      style="margin-bottom: 12px"
    >
      <div v-for="(e, i) in previewErrors" :key="i">{{ e }}</div>
    </el-alert>

    <div v-else>
      <div style="display:flex; gap:12px; margin-bottom:12px; flex-wrap:wrap;">
        <el-tag>总行数：{{ previewSummary.total }}</el-tag>
        <el-tag type="success">可导入：{{ previewSummary.valid }}</el-tag>
        <el-tag type="warning">将跳过：{{ previewSummary.skipDuplicate }}</el-tag>
        <el-tag type="danger">无效：{{ previewSummary.invalid }}</el-tag>
      </div>

      <el-alert
        v-if="duplicatedNames.length"
        type="warning"
        :closable="false"
        show-icon
        title="存在重复学校名称（导入时会自动跳过）"
        style="margin-bottom: 12px"
      >
        <div style="line-height: 1.8">
          {{ duplicatedNames.join("、") }} <span v-if="duplicatedNames.length>=50">…</span>
        </div>
      </el-alert>

      <el-table :data="previewRows" stripe height="420" style="width:100%">
        <el-table-column prop="__rownum" label="行号" width="70" />
        <el-table-column prop="name" label="学校名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="school_type" label="类型" width="110" />
        <el-table-column prop="contact_name" label="联系人" width="110" />
        <el-table-column prop="contact_phone" label="电话" width="140" />
        <el-table-column prop="contact_email" label="邮箱" min-width="180" show-overflow-tooltip />

        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag
              v-if="row.__status==='valid'"
              type="success"
            >可导入</el-tag>
            <el-tag
              v-else-if="row.__status==='skip'"
              type="warning"
            >将跳过</el-tag>
            <el-tag
              v-else
              type="danger"
            >无效</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="__reason" label="说明" min-width="200" show-overflow-tooltip />
      </el-table>
    </div>
  </div>

  <template #footer>
  <el-button @click="closePreview">关闭</el-button>
  <el-button type="primary" :disabled="previewSummary.valid===0" :loading="previewLoading" @click="startImport">
    开始导入
  </el-button>
</template>
</el-dialog>

        </div>

        <div class="import-right">
          <div class="import-tip-title">📌 导入说明：</div>
          <ol class="import-tip">
            <li>账号规则：学校名称首字母 + 6位随机数（示例：XWZS3Z123456）</li>
            <li>密码规则：8位随机字母数字组合（创建后可重置）</li>
            <li>重复学校名称会自动跳过，避免重复创建</li>
          </ol>
        </div>
      </div>
    </el-card>

    <!-- 列表卡片 -->
    <el-card class="block">
      <!-- 筛选条：一行 -->
      <div class="filter-bar">
        <el-input
          v-model="query.q"
          placeholder="请输入学校名称/ID"
          clearable
          class="w-220"
          @keyup.enter="handleSearch"
        />

        <el-select
          v-model="query.apply_status"
          placeholder="全部申请状态"
          clearable
          class="w-160"
        >
          <el-option label="待审核" value="pending" />
          <el-option label="已通过" value="approved" />
          <el-option label="已拒绝" value="rejected" />
        </el-select>

        <!-- ✅ 学校类型（你要求先补这一块） -->
        <el-select
          v-model="query.school_type"
          placeholder="全部学校类型"
          clearable
          class="w-160"
        >
          <el-option label="小学" value="primary" />
          <el-option label="初中" value="junior" />
          <el-option label="高中" value="senior" />
          <el-option label="九年一贯制" value="nine_year" />
          <el-option label="十二年一贯制" value="twelve_year" />
        </el-select>

        <!-- 在“全部学校类型”选择框后面插入 -->
        <el-date-picker
          v-model="query.time_range"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          class="w-300" 
        />

        <el-button type="primary" class="btn-query" :loading="loading" @click="handleSearch">
          查询
        </el-button>
        <el-button class="btn-reset" @click="reset">
          重置
        </el-button>
      </div>

      <el-table
  :data="rows"
  v-loading="loading"
  stripe
  class="table"
  header-cell-class-name="thead"
>
  <el-table-column prop="id" label="ID" width="60" />

  <!-- 学校名称 + 账号 -->
  <el-table-column label="学校名称" min-width="200" show-overflow-tooltip>
    <template #default="{ row }">
      <div class="name-cell">
        <div class="name">{{ row.name }}</div>
        <div class="sub">账号：{{ row.username || row.account || row.user?.username || "-" }}</div>
      </div>
    </template>
  </el-table-column>

  <el-table-column label="学校类型" width="90">
    <template #default="{ row }">
      {{ schoolTypeLabel(row.school_type) }}
    </template>
  </el-table-column>

  <el-table-column label="所在地" min-width="130" show-overflow-tooltip>
    <template #default="{ row }">
      {{ formatLocation(row) }}
    </template>
  </el-table-column>

  <!-- 联系人 + 电话 -->
  <el-table-column label="联系人" width="120">
    <template #default="{ row }">
      <div>
        <div>{{ row.contact_name || "-" }}</div>
        <div class="sub">{{ row.contact_phone || "-" }}</div>
      </div>
    </template>
  </el-table-column>

  <!-- ✅ 邮箱：单独一列 -->
  <el-table-column label="邮箱" min-width="180" show-overflow-tooltip>
    <template #default="{ row }">
      {{ row.contact_email || "-" }}
    </template>
  </el-table-column>

  <el-table-column label="申请状态" width="100">
    <template #default="{ row }">
      <el-tag :type="applyTagType(row.apply_status || row.status)">
        {{ applyStatusLabel(row.apply_status || row.status) }}
      </el-tag>
    </template>
  </el-table-column>

  <el-table-column label="申请时间" width="150">
    <template #default="{ row }">
      {{ formatDateTime(row.created_at || row.applied_at) }}
    </template>
  </el-table-column>

  <!-- 操作：下拉，防止重叠 -->
  <el-table-column label="操作" width="100" fixed="right">
  <template #default="{ row }">
    <el-dropdown trigger="click">
      <el-button type="primary" size="small">操作</el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item
                    :disabled="row.apply_status !== 'pending'"
                    @click="approve(row)"
                  >
                    通过
                  </el-dropdown-item>

          <el-dropdown-item
              :disabled="row.apply_status !== 'pending'"
              @click="reject(row)"
            >
              拒绝
            </el-dropdown-item>

          <el-dropdown-item
           :disabled="row._row_type !== 'school'"
           @click="resetPassword(row)">
            修改密码
          </el-dropdown-item>

          <el-dropdown-item
           :disabled="row.apply_status == 'pending'"
           divided @click="remove(row)">
            删除
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </template>
</el-table-column>

</el-table>




      <!-- 分页 -->
      <div class="pager">
        <el-pagination
          background
          layout="total, prev, pager, next, jumper"
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
import { onMounted, reactive, ref, computed } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { apiGet, apiPost, apiDelete, apiPostForm } from "@/utils/api";
import * as XLSX from "xlsx";

const router = useRouter();

const loading = ref(false);
const rows = ref([]);
const total = ref(0);
const API_TEMPLATE = "/api/region-admin/schools/template/";
const API_IMPORT = "/api/region-admin/schools/import/";


const query = reactive({
  q: "",
  apply_status: "",
  school_type: "",
  time_range: [],
  page: 1,
  page_size: 10,
});

// ✅ 你后端“混合列表”的接口
const API_LIST = "/api/region-admin/schools/";

// ✅ 申请审批接口（按你要求：对齐后端 reject 接口）
const API_APP_APPROVE = (applicationId) => `/api/region-admin/applications/${applicationId}/approve/`;
const API_APP_REJECT  = (applicationId) => `/api/region-admin/applications/${applicationId}/reject/`;
const API_APP_DELETE  = (applicationId) => `/api/region-admin/applications/${applicationId}/`;

// ✅ 学校账号操作接口
const API_SCHOOL_RESET_PWD = (schoolId) => `/api/region-admin/schools/${schoolId}/reset-password/`;
const API_SCHOOL_DELETE    = (schoolId) => `/api/region-admin/schools/${schoolId}/`;

function goCreateOne() {
  router.push("/region-admin/schools/create");
}

function buildQueryString() {
  const params = new URLSearchParams();

  if (query.q && query.q.trim()) params.set("q", query.q.trim());
  if (query.apply_status) params.set("apply_status", query.apply_status);
  if (query.school_type) params.set("school_type", query.school_type);

  if (query.time_range && query.time_range.length === 2) {
    params.set("start_at", query.time_range[0]);
    params.set("end_at", query.time_range[1]);
  }

  params.set("page", String(query.page));
  params.set("page_size", String(query.page_size));

  return params.toString();
}

async function load() {
  loading.value = true;
  try {
    const qs = buildQueryString();
    const url = qs ? `${API_LIST}?${qs}` : API_LIST;

    const { data: resp } = await apiGet(url);
    if (!resp?.success) throw new Error(resp?.message || "加载失败");

    // ✅ 对齐你当前后端返回：data.results + data.pagination
    rows.value = resp.data?.results || [];
    total.value = resp.data?.pagination?.total || 0;
  } catch (e) {
    console.error(e);
    ElMessage.error(e?.message || "加载失败");
    rows.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  query.page = 1;
  load();
}

function reset() {
  query.q = "";
  query.apply_status = "";
  query.school_type = "";
  query.time_range = [];
  query.page = 1;
  query.page_size = 10;
  load();
}

function handlePageChange(p) {
  query.page = p;
  load();
}

/** ===== 展示工具 ===== */
function schoolTypeLabel(v) {
  const m = {
    primary: "小学",
    junior: "初中",
    senior: "高中",
    nine_year: "九年一贯制",
    twelve_year: "十二年一贯制",
  };
  return m[v] || v || "-";
}

function formatLocation(row) {
  const parts = [row.province, row.city, row.district].filter(Boolean);
  return parts.length ? parts.join(" ") : "-";
}

function applyStatusLabel(v) {
  const m = { pending: "待审核", approved: "已通过", rejected: "已拒绝" };
  return m[v] || v || "-";
}

function applyTagType(v) {
  if (v === "approved") return "success";
  if (v === "rejected") return "danger";
  if (v === "pending") return "warning";
  return "info";
}

function formatDateTime(raw) {
  if (!raw) return "-";
  // raw 可能是 "2026-01-20 21:37:48"（Date 解析不稳定），解析失败就原样显示
  const d = new Date(raw);
  if (Number.isNaN(d.getTime())) return String(raw);
  const pad = (x) => String(x).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(
    d.getHours()
  )}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

/** ====== 操作：通过/拒绝（只允许 pending 申请）====== */
async function approve(row) {
  // ✅ 只有 pending 能通过；rejected/approved 都不允许
  if (row.apply_status !== "pending") {
    ElMessage.warning("只有待审核的申请才能通过");
    return;
  }
  if (row._row_type !== "application" || !row.application_id) {
    ElMessage.error("该记录不是申请记录，无法审批");
    return;
  }

  try {
    await ElMessageBox.confirm(
      `确认通过「${row.name}」的申请？`,
      "通过确认",
      { confirmButtonText: "确认通过", cancelButtonText: "取消", type: "warning" }
    );

    const { data: resp } = await apiPost(API_APP_APPROVE(row.application_id), {});
    if (!resp?.success) throw new Error(resp?.message || "审批失败");

    ElMessage.success("已通过");
    await load();
  } catch (e) {
    if (e === "cancel" || e === "close") return;
    console.error(e);
    ElMessage.error(e?.message || "审批失败");
  }
}

async function reject(row) {
  if (row.apply_status !== "pending") {
    ElMessage.warning("只有待审核的申请才能拒绝");
    return;
  }
  if (row._row_type !== "application" || !row.application_id) {
    ElMessage.error("该记录不是申请记录，无法拒绝");
    return;
  }

  try {
    const ret = await ElMessageBox.prompt(
      `请输入拒绝「${row.name}」的原因`,
      "拒绝申请",
      {
        inputType: "textarea",
        confirmButtonText: "确认拒绝",
        cancelButtonText: "取消",
        closeOnClickModal: false,
        closeOnPressEscape: false,
        inputValidator: (v) => (v && v.trim() ? true : "请填写拒绝原因"),
      }
    );
    const reason = ret?.value?.trim();
    if (!reason) return;

    const { data: resp } = await apiPost(API_APP_REJECT(row.application_id), {
      reject_reason: reason,
    });
    if (!resp?.success) throw new Error(resp?.message || "拒绝失败");

    ElMessage.success("已拒绝");
    await load();
  } catch (e) {
    if (e === "cancel" || e === "close") return;
    console.error(e);
    ElMessage.error(e?.message || "拒绝失败");
  }
}

/** ====== 修改密码：只对 school 生效 ====== */
async function resetPassword(row) {
  if (row._row_type !== "school") {
    ElMessage.warning("只有已通过的学校账号才能修改密码");
    return;
  }

  try {
    const ret = await ElMessageBox.prompt(
      `为学校「${row.name}」设置新密码`,
      "修改密码",
      {
        inputType: "password",
        confirmButtonText: "确认",
        cancelButtonText: "取消",
        closeOnClickModal: false,
        closeOnPressEscape: false,
        inputValidator: (val) => (val && val.length >= 6 ? true : "密码至少 6 位"),
      }
    );

    const password = ret?.value;
    if (!password) return;

    const { data: resp } = await apiPost(API_SCHOOL_RESET_PWD(row.id), { password });
    if (!resp?.success) throw new Error(resp?.message || "修改失败");

    ElMessage.success("密码已修改");
  } catch (e) {
    if (e === "cancel" || e === "close") return;
    console.error(e);
    ElMessage.error(e?.message || "修改失败");
  }
}

/** ====== 删除：application 删申请；school 删学校 ====== */
async function remove(row) {
  try {
    await ElMessageBox.confirm(
      `删除「${row.name}」将不可恢复，是否继续？`,
      "危险操作",
      {
        confirmButtonText: "确认删除",
        cancelButtonText: "取消",
        type: "error",
        closeOnClickModal: false,
        closeOnPressEscape: false,
      }
    );

    let path = "";
    if (row._row_type === "application") {
      // ✅ 删除申请记录（pending/rejected）
      if (!row.application_id) {
        ElMessage.error("缺少 application_id，无法删除该申请记录");
        return;
      }
      path = API_APP_DELETE(row.application_id);
    } else {
      // ✅ 删除学校账号（approved）
      path = API_SCHOOL_DELETE(row.id);
    }

    const { data: resp } = await apiDelete(path);
    if (!resp?.success) throw new Error(resp?.message || "删除失败");

    ElMessage.success("删除成功");
    await load();
  } catch (e) {
    if (e === "cancel" || e === "close") return;
    console.error(e);
    ElMessage.error(e?.message || "删除失败");
  }
}

onMounted(load);

/** 当前选中的文件（只保留一个） */
const pickedFile = ref(null);




function downloadTemplate() {
  // 1 表头
  const header = [
    "学校名称(name)",
    "学校类型(school_type)",
    "联系人(contact_name)",
    "职务(contact_position)",
    "联系电话(contact_phone)",
    "邮箱(contact_email)",
    "用户名(username，可选)",
    "初始密码(password，可选，>=8)",
  ];

  // 2 示例行
  const example = [
    "玄武一小",
    "primary",
    "张三",
    "信息中心主任",
    "13800000000",
    "xw001@example.com",
    "",
    "",
  ];

  // 3 组装成 sheet
  const ws = XLSX.utils.aoa_to_sheet([header, example]);

  // 4 设置列宽
  ws["!cols"] = header.map((h) => ({ wch: Math.max(16, h.length + 2) }));

  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "schools");

  // 5 下载
  const fileName = "学校账号导入模板.xlsx";
  XLSX.writeFile(wb, fileName);
}

/** ====== 1预览状态 ====== */


const previewVisible = ref(false);
const previewLoading = ref(false);

const previewRows = ref([]);   // 解析后的行（含校验信息）
const previewSummary = ref({
  total: 0,
  valid: 0,
  skipDuplicate: 0,
  invalid: 0,
});

const previewErrors = ref([]); // 全局错误（比如表头不对）
const duplicatedNames = ref([]); // 汇总重复学校名（可展示给用户）

/** 当前列表已有学校名，用于“与现有记录重复也跳过” */
const existingNameSet = computed(() => {
  const set = new Set();
  // rows 是你已有的表格数据 ref([])
  (rows.value || []).forEach((r) => {
    const n = normalizeName(r?.name);
    if (n) set.add(n);
  });
  return set;
});

/** ====== 2 选文件后：解析并打开预览 ====== */
async function onPickFile(uploadFile) {
  const raw = uploadFile?.raw;
  if (!raw) return;

  const name = raw.name || "";
  const lower = name.toLowerCase();
  if (!lower.endsWith(".xlsx") && !lower.endsWith(".xls")) {
    ElMessage.error("只支持 .xlsx / .xls 文件");
    return;
  }

  const maxMB = 5;
  const sizeMB = raw.size / 1024 / 1024;
  if (sizeMB > maxMB) {
    ElMessage.error(`文件过大（>${maxMB}MB），请分批导入`);
    return;
  }

  pickedFile.value = raw;
  await parseAndPreview(raw);
}

/** ======  解析 Excel 核心 ====== */
async function parseAndPreview(file) {
  previewLoading.value = true;
  previewErrors.value = [];
  previewRows.value = [];
  duplicatedNames.value = [];

  try {
    const buf = await readFileAsArrayBuffer(file);
    const wb = XLSX.read(buf, { type: "array" });

    const firstSheetName = wb.SheetNames?.[0];
    if (!firstSheetName) throw new Error("Excel 为空或没有工作表");

    const ws = wb.Sheets[firstSheetName];

    // 用 AOA 保留表头行
    const aoa = XLSX.utils.sheet_to_json(ws, { header: 1, defval: "" });
    if (!aoa || aoa.length < 2) throw new Error("Excel 至少需要表头 + 1 行数据");

    const headerRow = (aoa[0] || []).map((x) => String(x || "").trim());
    const dataRows = aoa.slice(1);

    // 根据表头识别字段列索引（兼容你模板里的中英混合表头）
    const idx = buildHeaderIndex(headerRow);
    const requiredFields = ["name", "school_type", "contact_name", "contact_position", "contact_phone", "contact_email"];
    const missing = requiredFields.filter((k) => idx[k] == null);

    if (missing.length) {
      previewErrors.value.push(
        `表头缺少必要列：${missing.join(", ")}。请使用“下载导入模板”生成的表头。`
      );
      previewVisible.value = true;
      return;
    }

    // 最多100条
    const limitedRows = dataRows.slice(0, 100);

    const seenInFile = new Set(); // 文件内重复检查
    const dupNames = new Set();

    const parsed = limitedRows
      .map((r, i) => {
        const rownum = i + 2; // Excel 行号（含表头）
        const get = (key) => String(r[idx[key]] ?? "").trim();

        const item = {
          __rownum: rownum,
          name: get("name"),
          school_type: get("school_type"),
          contact_name: get("contact_name"),
          contact_position: get("contact_position"),
          contact_phone: get("contact_phone"),
          contact_email: get("contact_email"),
          username: idx.username != null ? get("username") : "",
          password: idx.password != null ? get("password") : "",

          __status: "valid",      // valid | skip | invalid
          __reason: "",           // 提示原因
          __normalizedName: normalizeName(get("name")),
        };

        // 校验必填
        const errs = [];
        if (!item.name) errs.push("学校名称必填");
        if (!item.school_type) errs.push("学校类型必填");
        if (!item.contact_name) errs.push("联系人必填");
        if (!item.contact_position) errs.push("职务必填");
        if (!item.contact_phone) errs.push("电话必填");
        if (!item.contact_email) errs.push("邮箱必填");

        // school_type 校验（按你的 choices）
        if (item.school_type && !isValidSchoolType(item.school_type)) {
          errs.push("学校类型不合法");
        }

        // phone/email 基本校验
        if (item.contact_phone && !isValidPhone(item.contact_phone)) {
          errs.push("电话格式不正确");
        }
        if (item.contact_email && !isValidEmail(item.contact_email)) {
          errs.push("邮箱格式不正确");
        }

        // password 可选：如果填了，建议>=8（你规则8位）
        if (item.password && item.password.length < 8) {
          errs.push("初始密码至少 8 位");
        }

        if (errs.length) {
          item.__status = "invalid";
          item.__reason = errs.join("；");
          return item;
        }

        // 重复学校名：文件内重复
        if (item.__normalizedName) {
          if (seenInFile.has(item.__normalizedName)) {
            item.__status = "skip";
            item.__reason = "文件内学校名称重复（将跳过）";
            dupNames.add(item.name || item.__normalizedName);
            return item;
          }
          seenInFile.add(item.__normalizedName);
        }

        // 与当前列表重名（已存在）
        if (item.__normalizedName && existingNameSet.value.has(item.__normalizedName)) {
          item.__status = "skip";
          item.__reason = "系统已存在同名学校（将跳过）";
          dupNames.add(item.name || item.__normalizedName);
          return item;
        }

        return item;
      })
      .filter(Boolean);

    previewRows.value = parsed;

    // 汇总
    const total = parsed.length;
    const valid = parsed.filter((x) => x.__status === "valid").length;
    const skipDuplicate = parsed.filter((x) => x.__status === "skip").length;
    const invalid = parsed.filter((x) => x.__status === "invalid").length;

    previewSummary.value = { total, valid, skipDuplicate, invalid };
    duplicatedNames.value = Array.from(dupNames).slice(0, 50);

    previewVisible.value = true;
    ElMessage.success("解析完成，已打开预览");
  } catch (e) {
    console.error(e);
    ElMessage.error(e?.message || "解析失败");
  } finally {
    previewLoading.value = false;
  }
}

/** ======  工具函数 ====== */
function normalizeName(s) {
  return String(s || "")
    .trim()
    .replace(/\s+/g, "")
    .toLowerCase();
}

function buildHeaderIndex(headers) {
  // 支持这些表头写法（你模板里是：学校名称(name)）
  // 也兼容纯中文、纯字段名
  const find = (keys) => {
    const idx = headers.findIndex((h) => {
      const t = String(h || "").trim().toLowerCase();
      return keys.some((k) => t === k || t.includes(k));
    });
    return idx >= 0 ? idx : null;
  };

  return {
    name: find(["学校名称", "name", "(name)"]),
    school_type: find(["学校类型", "school_type", "(school_type)"]),
    contact_name: find(["联系人", "contact_name", "(contact_name)"]),
    contact_position: find(["职务", "contact_position", "(contact_position)"]),
    contact_phone: find(["联系电话", "电话", "contact_phone", "(contact_phone)"]),
    contact_email: find(["邮箱", "联系邮箱", "contact_email", "(contact_email)"]),
    username: find(["用户名", "username", "(username)"]),
    password: find(["初始密码", "密码", "password", "(password)"]),
  };
}

function isValidSchoolType(v) {
  return ["primary", "junior", "senior", "nine_year", "twelve_year"].includes(v);
}

function isValidPhone(v) {
  // 允许座机/手机号的话你可以放宽，这里先按手机号
  return /^1[3-9]\d{9}$/.test(String(v || "").trim());
}

function isValidEmail(v) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(v || "").trim());
}

function readFileAsArrayBuffer(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error("读取文件失败"));
    reader.readAsArrayBuffer(file);
  });
}

/** 关闭预览 */
function closePreview() {
  previewVisible.value = false;
}


/** 点击“开始导入” */
async function startImport() {
  // 只提交 valid 行
  const valid = previewRows.value.filter((r) => r.__status === "valid");
  if (!valid.length) {
    ElMessage.warning("没有可导入的数据");
    return;
  }

  // 后端需要 rows: [...]
  const payload = {
    rows: valid.map((r) => ({
      name: r.name,
      school_type: r.school_type,
      contact_name: r.contact_name,
      contact_position: r.contact_position,
      contact_phone: r.contact_phone,
      contact_email: r.contact_email,
      // username/password 可选：Excel 里如果有列就传，否则不传让后端生成
      username: r.username || "",
      password: r.password || "",
    })),
  };

  previewLoading.value = true;
  try {
    const { data: resp } = await apiPost(API_IMPORT, payload);
    if (!resp?.success) throw new Error(resp?.message || "导入失败");

    const rep = resp.data;

    ElMessage.success(`导入完成：成功${rep.created}，跳过${rep.skipped}，失败${rep.failed}`);

    // 可选：把后端回传的结果覆盖显示在预览表里（更直观）
    const detailMap = new Map((rep.details || []).map((d) => [d.row_index, d]));
    previewRows.value = previewRows.value.map((r, i) => {
      const d = detailMap.get(i);
      if (!d) return r;
      if (d.status === "created") {
        return { ...r, __status: "created", __reason: `已创建：${d.username}` };
      }
      if (d.status === "skipped") {
        return { ...r, __status: "skip", __reason: d.reason || "已跳过" };
      }
      return { ...r, __status: "invalid", __reason: JSON.stringify(d.reason || "失败") };
    });

    // 关闭弹窗并刷新列表（你也可以不关，留着看结果）
    previewVisible.value = false;
    await load();
  } catch (e) {
    console.error(e);
    ElMessage.error(e?.message || "导入失败");
  } finally {
    previewLoading.value = false;
  }
}

</script>


<style scoped>
/* 页面结构（你 template 里已有 class，这里补齐） */
.page {
  padding: 16px;
  background: #f5f7fa;
  min-height: 100vh;
}
.w-300 { width: 120px !important; 
flex: none !important;}

:deep(.el-date-editor.w-300) {
  width: 240px !important;
  flex: none !important;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.block {
  border-radius: 8px;
  margin-bottom: 14px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}

/* 顶部导入区（你已写好结构，这里给点样式兜底） */
.import-wrap {
  display: flex;
  gap: 16px;
  align-items: stretch;
}
.import-left { flex: 1; }
.import-right { width: 340px; }

.dropbox {
  border: 1px dashed #c0c4cc;
  border-radius: 8px;
  background: #fafafa;
  padding: 18px;
}
.drop-title { font-weight: 600; color: #303133; }
.drop-sub { margin-top: 6px; color: #909399; font-size: 12px; }

.import-actions {
  margin-top: 12px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.import-tip-title { font-weight: 600; margin-bottom: 8px; }
.import-tip { margin: 0; padding-left: 18px; color: #606266; font-size: 13px; }

/* 筛选条：一行 */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap; /* 宽度不够才换行 */
  padding: 10px 0 12px;
}

.w-220 { width: 220px; }
.w-160 { width: 160px; }

.btn-query, .btn-reset {
  white-space: nowrap;
}

/* 表格：固定右侧列 + 下拉重叠修复 */
.table {
  width: 100%;
}

/* 固定列背景/层级，避免覆盖错乱 */
:deep(.el-table__fixed-right) {
  z-index: 6;
  background: #fff;
}
:deep(.el-table__fixed-right::before) {
  background-color: #fff;
}

/* 下拉菜单弹层层级：保证不被表格盖住 */
:deep(.el-popper) {
  z-index: 3000;
}

/* 单元格样式 */
.name-cell .name {
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}
.sub {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

/* 分页 */
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

