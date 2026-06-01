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
        <el-table-column prop="index" label="序号" width="70" />
        <el-table-column prop="name" label="学校名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="school_type_display" label="学校类型" width="130" />
        <el-table-column prop="contact_name" label="负责人" width="110" />
        <el-table-column prop="contact_position" label="职务" width="140" show-overflow-tooltip />
        <el-table-column prop="contact_phone" label="联系电话" width="140" />
        <el-table-column prop="contact_email" label="邮箱" min-width="180" show-overflow-tooltip />
        <el-table-column prop="username" label="登录用户名" min-width="140" show-overflow-tooltip />
        <el-table-column prop="password" label="登录密码" min-width="120" show-overflow-tooltip />

        <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag
            v-if="row.__status === 'created'"
            type="success"
          >
            已创建
          </el-tag>

          <el-tag
            v-else-if="row.__status === 'valid'"
            type="success"
          >
            可导入
          </el-tag>

          <el-tag
            v-else-if="row.__status === 'skip'"
            type="warning"
          >
            将跳过
          </el-tag>

          <el-tag
            v-else
            type="danger"
          >
            无效
          </el-tag>
        </template>
      </el-table-column>
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
            <li>所有填报信息必须真实有效、准确无误，严格对照表格填报要求及标准示例规范填写；</li>
            <li>不能对模板字段、表头、列序及格式进行任何修改，以确保数据能够正常导入系统；</li>
            <li>填报完成后需逐项核对校验，排查错填、漏填、格式错乱等问题，确认无误后再提交。</li>
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
  <el-table-column prop="id" label="ID" width="70" align="center" />

  <el-table-column label="学校名称" min-width="170" show-overflow-tooltip>
    <template #default="{ row }">
      <div class="name-cell">
        <div class="name">{{ row.name }}</div>
        <div class="sub">账号：{{ row.username || row.account || row.user?.username || "-" }}</div>
      </div>
    </template>
  </el-table-column>

  <el-table-column label="学校类型" width="100" align="center">
    <template #default="{ row }">
      {{ schoolTypeLabel(row.school_type) }}
    </template>
  </el-table-column>

  <el-table-column label="所在地" min-width="150" show-overflow-tooltip align="center">
    <template #default="{ row }">
      {{ formatLocation(row) }}
    </template>
  </el-table-column>

  <el-table-column label="联系人" width="130" align="center">
    <template #default="{ row }">
      <div class="contact-cell">
        <div>{{ row.contact_name || "-" }}</div>
        <div class="sub">{{ row.contact_phone || "-" }}</div>
      </div>
    </template>
  </el-table-column>

  <el-table-column label="邮箱" min-width="190" show-overflow-tooltip align="center">
    <template #default="{ row }">
      {{ row.contact_email || "-" }}
    </template>
  </el-table-column>

  <el-table-column label="申请状态" width="110" align="center">
    <template #default="{ row }">
      <el-tag :type="applyTagType(row.apply_status || row.status)">
        {{ applyStatusLabel(row.apply_status || row.status) }}
      </el-tag>
    </template>
  </el-table-column>

  <el-table-column label="申请时间" width="165" align="center">
    <template #default="{ row }">
      {{ formatDateTime(row.created_at || row.applied_at) }}
    </template>
  </el-table-column>

  <el-table-column label="操作" width="100" fixed="right" align="center">
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
import * as XLSX from "xlsx-js-style";

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
  const rows = [
    [
      "序号",
      "学校名称",
      "学校类型",
      "负责人",
      "职务",
      "联系电话",
      "邮箱",
      "登录用户名",
      "登录密码",
    ],
    [
      "填报说明",
      "填写学校官方完整全称",
      "仅限选择：小学、初中、高中、九年一贯制、十二年一贯制",
      "填写各学校负责人姓名",
      "填写负责人岗位职务",
      "填写负责人有效联系电话",
      "填写负责人有效邮箱",
      "学校全称大写首字母组合，无特殊字符",
      "8位字符（数字或字母组合）",
    ],
    [
      "填报示例",
      "徐州市泉山实验小学",
      "小学",
      "易XX",
      "信息中心主任",
      "18864471307",
      "204142312@gq.com",
      "XZQSSYXX",
      "QSSYXX11",
    ],
    [
      "① 所有填报信息必须真实有效、准确无误，严格对照表格填报要求及标准示例规范填写；\n② 不能对模板字段、表头、列序及格式进行任何修改，以确保数据能够正常导入系统；\n③ 填报完成后需逐项核对校验，排查错填、漏填、格式错乱等问题，确认无误后再提交。",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
    ],
  ]

  // 第5行开始预留正式填写区域
  for (let i = 1; i <= 100; i++) {
    rows.push([i, "", "", "", "", "", "", "", ""])
  }

  const ws = XLSX.utils.aoa_to_sheet(rows)

  // 合并第4行说明区域
  ws["!merges"] = [
    {
      s: { r: 3, c: 0 },
      e: { r: 3, c: 8 },
    },
  ]

  // 列宽
  ws["!cols"] = [
    { wch: 8 },
    { wch: 28 },
    { wch: 30 },
    { wch: 18 },
    { wch: 18 },
    { wch: 18 },
    { wch: 26 },
    { wch: 24 },
    { wch: 20 },
  ]

  // 行高
  ws["!rows"] = [
    { hpt: 28 },
    { hpt: 44 },
    { hpt: 26 },
    { hpt: 60 },
  ]

  const borderStyle = {
    top: { style: "thin", color: { rgb: "000000" } },
    bottom: { style: "thin", color: { rgb: "000000" } },
    left: { style: "thin", color: { rgb: "000000" } },
    right: { style: "thin", color: { rgb: "000000" } },
  }

  const headerStyle = {
    font: {
      name: "宋体",
      bold: true,
      color: { rgb: "FFFFFF" },
      sz: 12,
    },
    fill: {
      fgColor: { rgb: "305496" },
    },
    alignment: {
      horizontal: "center",
      vertical: "center",
      wrapText: true,
    },
    border: borderStyle,
  }

  const noteStyle = {
    font: {
      name: "宋体",
      color: { rgb: "000000" },
      sz: 11,
    },
    fill: {
      fgColor: { rgb: "D9E2F3" },
    },
    alignment: {
      horizontal: "center",
      vertical: "center",
      wrapText: true,
    },
    border: borderStyle,
  }

  const exampleStyle = {
    font: {
      name: "宋体",
      color: { rgb: "000000" },
      sz: 11,
    },
    fill: {
      fgColor: { rgb: "D9E2F3" },
    },
    alignment: {
      horizontal: "center",
      vertical: "center",
      wrapText: true,
    },
    border: borderStyle,
  }

  const mergedNoteStyle = {
    font: {
      name: "宋体",
      color: { rgb: "000000" },
      sz: 11,
    },
    fill: {
      fgColor: { rgb: "D9E2F3" },
    },
    alignment: {
      horizontal: "left",
      vertical: "center",
      wrapText: true,
    },
    border: borderStyle,
  }

  const emptyStyle = {
    font: {
      name: "宋体",
      color: { rgb: "000000" },
      sz: 11,
    },
    alignment: {
      horizontal: "center",
      vertical: "center",
      wrapText: true,
    },
    border: borderStyle,
  }

  // 设置前4行样式
  for (let r = 0; r <= 3; r++) {
    for (let c = 0; c <= 8; c++) {
      const cellRef = XLSX.utils.encode_cell({ r, c })

      if (!ws[cellRef]) {
        ws[cellRef] = { t: "s", v: "" }
      }

      if (r === 0) {
        ws[cellRef].s = headerStyle
      } else if (r === 1) {
        ws[cellRef].s = noteStyle
      } else if (r === 2) {
        ws[cellRef].s = exampleStyle
      } else if (r === 3) {
        ws[cellRef].s = mergedNoteStyle
      }
    }
  }

  // 设置第5行以后空白填写区域样式
  for (let r = 4; r < rows.length; r++) {
    for (let c = 0; c <= 8; c++) {
      const cellRef = XLSX.utils.encode_cell({ r, c })

      if (!ws[cellRef]) {
        ws[cellRef] = { t: "s", v: "" }
      }

      ws[cellRef].s = emptyStyle
    }
  }

  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, "学校账号导入模板")

  XLSX.writeFile(wb, "学校账号导入模板.xlsx")
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

    const aoa = XLSX.utils.sheet_to_json(ws, { header: 1, defval: "" });

    if (!aoa || aoa.length < 5) {
      throw new Error("Excel格式不正确：第5行开始才是正式数据，请使用新版导入模板");
    }

    const headerRow = (aoa[0] || []).map((x) => String(x || "").trim());
    const idx = buildHeaderIndex(headerRow);

    const requiredFields = [
      "index",
      "name",
      "school_type",
      "contact_name",
      "contact_position",
      "contact_phone",
      "contact_email",
      "username",
      "password",
    ];

    const missing = requiredFields.filter((k) => idx[k] == null);

    if (missing.length) {
      previewErrors.value.push(
        `表头缺少必要列：${missing.join("、")}。请使用新版“学校账号导入模板”。`
      );
      previewVisible.value = true;
      return;
    }

    // 第2、3、4行为说明和示例，不参与导入
    // 第5行开始才是正式数据
    // 注意：模板第5行以后 A列有序号，所以不能只判断整行是否为空；
    // 要判断 B-I 列是否有实际填写内容。
    const dataRows = aoa.slice(4).filter((row) => {
      const meaningfulCells = row.slice(1, 9);
      return meaningfulCells.some((cell) => String(cell || "").trim() !== "");
    });

    const limitedRows = dataRows.slice(0, 100);

    const seenNameInFile = new Set();
    const seenEmailInFile = new Set();
    const seenUsernameInFile = new Set();
    const dupNames = new Set();

    const parsed = limitedRows.map((r, i) => {
      const rownum = i + 5;
      const get = (key) => String(r[idx[key]] ?? "").trim();

      const schoolTypeText = get("school_type");
      const schoolTypeValue = normalizeSchoolType(schoolTypeText);

      const item = {
        __rownum: rownum,
        index: get("index"),
        name: get("name"),
        school_type: schoolTypeValue,
        school_type_display: schoolTypeText,
        contact_name: get("contact_name"),
        contact_position: get("contact_position"),
        contact_phone: get("contact_phone"),
        contact_email: get("contact_email"),
        username: get("username"),
        password: get("password"),

        __status: "valid",
        __reason: "",
        __normalizedName: normalizeName(get("name")),
      };

      const errs = [];

      if (!item.index) errs.push("序号必填");
      if (!item.name) errs.push("学校名称必填");
      if (!item.school_type_display) errs.push("学校类型必填");
      if (!item.school_type) errs.push("学校类型不合法");
      if (!item.contact_name) errs.push("负责人必填");
      if (!item.contact_position) errs.push("职务必填");
      if (!item.contact_phone) errs.push("联系电话必填");
      if (!item.contact_email) errs.push("邮箱必填");
      if (!item.username) errs.push("登录用户名必填");
      if (!item.password) errs.push("登录密码必填");

      if (item.contact_phone && !isValidPhone(item.contact_phone)) {
        errs.push("联系电话格式不正确");
      }

      if (item.contact_email && !isValidEmail(item.contact_email)) {
        errs.push("邮箱格式不正确");
      }

      if (item.username && !/^[A-Za-z0-9]+$/.test(item.username)) {
        errs.push("登录用户名只能包含数字或字母，不能包含特殊字符");
      }

      if (item.password && !/^[A-Za-z0-9]{8}$/.test(item.password)) {
        errs.push("登录密码必须为8位数字或字母组合");
      }

      const normalizedEmail = item.contact_email.toLowerCase();
      const normalizedUsername = item.username.toLowerCase();

      if (item.__normalizedName) {
        if (seenNameInFile.has(item.__normalizedName)) {
          errs.push("文件内学校名称重复");
          dupNames.add(item.name || item.__normalizedName);
        }
        seenNameInFile.add(item.__normalizedName);
      }

      if (normalizedEmail) {
        if (seenEmailInFile.has(normalizedEmail)) {
          errs.push("文件内邮箱重复");
        }
        seenEmailInFile.add(normalizedEmail);
      }

      if (normalizedUsername) {
        if (seenUsernameInFile.has(normalizedUsername)) {
          errs.push("文件内登录用户名重复");
        }
        seenUsernameInFile.add(normalizedUsername);
      }

      if (item.__normalizedName && existingNameSet.value.has(item.__normalizedName)) {
        item.__status = "skip";
        item.__reason = "系统已存在同名学校（将跳过）";
        dupNames.add(item.name || item.__normalizedName);
        return item;
      }

      if (errs.length) {
        item.__status = "invalid";
        item.__reason = errs.join("；");
      }

      return item;
    });

    previewRows.value = parsed;

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
  const normalizeHeader = (value) => {
    return String(value || "")
      .trim()
      .replace(/\s+/g, "")
      .replace(/[()（）]/g, "")
      .toLowerCase()
  }

  const normalizedHeaders = headers.map(normalizeHeader)

  const findByNames = (names) => {
    const normalizedNames = names.map(normalizeHeader)

    const idx = normalizedHeaders.findIndex((header) => {
      return normalizedNames.some((name) => header === name || header.includes(name))
    })

    return idx >= 0 ? idx : null
  }

  return {
    index: findByNames(["序号", "序列号", "编号", "no", "no."]),
    name: findByNames(["学校名称", "学校全称"]),
    school_type: findByNames(["学校类型", "办学类型"]),
    contact_name: findByNames(["负责人", "联系人", "联系人姓名"]),
    contact_position: findByNames(["职务", "岗位", "负责人职务"]),
    contact_phone: findByNames(["联系电话", "电话", "手机号码", "手机号"]),
    contact_email: findByNames(["邮箱", "联系邮箱", "电子邮箱"]),
    username: findByNames(["登录用户名", "用户名", "账号", "登录账号"]),
    password: findByNames(["登录密码", "初始密码", "密码"]),
  }
}

function normalizeSchoolType(v) {
  const text = String(v || "").trim();

  const map = {
    小学: "primary",
    初中: "junior",
    高中: "senior",
    九年一贯制: "nine_year",
    十二年一贯制: "twelve_year",

    primary: "primary",
    junior: "junior",
    senior: "senior",
    nine_year: "nine_year",
    twelve_year: "twelve_year",
  };

  return map[text] || "";
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

function formatImportReason(reason) {
  if (!reason) {
    return "导入失败"
  }

  if (typeof reason === "string") {
    return reason
  }

  if (Array.isArray(reason)) {
    return reason.join("；")
  }

  if (typeof reason === "object") {
    const messages = []

    Object.entries(reason).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        messages.push(`${key}：${value.join("；")}`)
      } else if (typeof value === "string") {
        messages.push(`${key}：${value}`)
      } else {
        messages.push(`${key}：${JSON.stringify(value)}`)
      }
    })

    return messages.join("；") || "导入失败"
  }

  return String(reason)
}


/** 点击“开始导入” */
async function startImport() {
  const validRows = previewRows.value.filter((r) => r.__status === "valid")

  if (!validRows.length) {
    ElMessage.warning("没有可导入的数据")
    return
  }

  const payload = {
    rows: validRows.map((r) => ({
      name: r.name,
      school_type: r.school_type,
      contact_name: r.contact_name,
      contact_position: r.contact_position,
      contact_phone: r.contact_phone,
      contact_email: r.contact_email,
      username: r.username,
      password: r.password,
    })),
  }

  previewLoading.value = true

  try {
    const { data: resp } = await apiPost(API_IMPORT, payload)

    if (!resp?.success) {
      throw new Error(resp?.message || "导入失败")
    }

    const rep = resp.data || {
      created: 0,
      skipped: 0,
      failed: 0,
      details: [],
    }

    /**
     * 后端返回的 row_index 是 validRows 的下标，
     * 不是 previewRows 的下标。
     * 所以这里先用 validRows[row_index].__rownum 找回原始 Excel 行号。
     */
    const detailByExcelRow = new Map()

    ;(rep.details || []).forEach((detail) => {
      const validRow = validRows[detail.row_index]

      if (validRow) {
        detailByExcelRow.set(validRow.__rownum, detail)
      }
    })

    previewRows.value = previewRows.value.map((row) => {
      const detail = detailByExcelRow.get(row.__rownum)

      if (!detail) {
        return row
      }

      if (detail.status === "created") {
        return {
          ...row,
          __status: "created",
          __reason: `已创建，用户名：${detail.username || row.username}`,
        }
      }

      if (detail.status === "skipped") {
        return {
          ...row,
          __status: "skip",
          __reason: detail.reason || "已跳过",
        }
      }

      return {
        ...row,
        __status: "invalid",
        __reason: formatImportReason(detail.reason),
      }
    })

    previewSummary.value = {
      total: previewRows.value.length,
      valid: previewRows.value.filter((x) => x.__status === "valid").length,
      skipDuplicate: previewRows.value.filter((x) => x.__status === "skip").length,
      invalid: previewRows.value.filter((x) => x.__status === "invalid").length,
    }

    ElMessage.success(
      `导入完成：成功${rep.created || 0}，跳过${rep.skipped || 0}，失败${rep.failed || 0}`
    )

    await load()
  } catch (e) {
    console.error(e)
    ElMessage.error(e?.message || "导入失败")
  } finally {
    previewLoading.value = false
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

/* 表格整体更紧凑 */
.table {
  width: 100%;
  font-size: 13px;
}

/* 表头和单元格上下间距压缩 */
.table :deep(.el-table__cell) {
  padding: 6px 0 !important;
}

/* 单元格内部左右留白统一 */
.table :deep(.cell) {
  padding: 0 8px !important;
  line-height: 18px;
}

/* 表头文字居中，间距统一 */
.table :deep(.el-table__header .cell) {
  text-align: center;
  font-weight: 600;
}

/* 表格内容垂直居中 */
.table :deep(.el-table__body .el-table__cell) {
  vertical-align: middle;
}

/* 压缩两行内容的行距 */
.name-cell .name,
.contact-cell > div:first-child {
  font-weight: 600;
  color: #303133;
  line-height: 18px;
}

.sub {
  font-size: 12px;
  color: #909399;
  margin-top: 1px;
  line-height: 16px;
}

/* 状态标签稍微变小，避免撑高行 */
.table :deep(.el-tag) {
  height: 22px;
  line-height: 20px;
  padding: 0 8px;
  font-size: 12px;
}

/* 操作按钮压缩 */
.table :deep(.el-button--small) {
  height: 24px;
  padding: 4px 10px;
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
  line-height: 18px;
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

