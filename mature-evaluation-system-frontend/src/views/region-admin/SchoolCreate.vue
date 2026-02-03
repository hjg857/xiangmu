<template>
  <div class="page">
    <div class="page-title">创建单个学校账号</div>

    <el-card class="block">
      <template #header>
        <div class="card-header">
          <div class="title">学校信息</div>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="110px"
        class="form"
      >
        <!-- 学校基本信息 -->
        <div class="section">
          <div class="section-title">学校基本信息</div>

          <el-form-item label="学校名称" prop="name">
            <el-input v-model="form.name" placeholder="请输入学校官方全称" />
          </el-form-item>

          <el-form-item label="学校类型" prop="school_type">
            <el-select v-model="form.school_type" placeholder="请选择学校类型" style="width: 100%">
              <el-option label="小学" value="primary" />
              <el-option label="初中" value="junior" />
              <el-option label="高中" value="senior" />
              <el-option label="九年一贯制" value="nine_year" />
              <el-option label="十二年一贯制" value="twelve_year" />
            </el-select>
          </el-form-item>

          <el-form-item label="省份">
  <el-input v-model="form.province" disabled />
</el-form-item>

<el-form-item label="城市">
  <el-input v-model="form.city" disabled />
</el-form-item>

<el-form-item label="区县">
  <el-input v-model="form.district" disabled />
  <div class="tip">该学校将自动创建在你当前管理的区域下</div>
</el-form-item>
        
        </div>

        <!-- 联系人信息 -->
        <div class="section">
          <div class="section-title">联系人信息</div>

          <el-form-item label="联系人姓名" prop="contact_name">
            <el-input v-model="form.contact_name" placeholder="负责系统的主要联系人" />
          </el-form-item>

          <el-form-item label="职务" prop="contact_position">
            <el-input v-model="form.contact_position" placeholder="请输入职务或岗位" />
          </el-form-item>

          <el-form-item label="联系电话" prop="contact_phone">
            <el-input v-model="form.contact_phone" placeholder="请填写真实联系电话" />
          </el-form-item>
        </div>

        <!-- 账号信息 -->
        <div class="section">
          <div class="section-title">账号信息</div>

          <el-form-item label="联系邮箱" prop="contact_email">
            <el-input v-model="form.contact_email" placeholder="学校联系人邮箱（必须唯一）" />
            <div class="tip">
              注意：该邮箱作为登录账号 Email，必须唯一；重复会创建失败。
            </div>
          </el-form-item>

          <el-form-item label="用户名" prop="username">
            <div class="inline">
              <el-switch v-model="form.custom_username" active-text="自定义" inactive-text="自动生成" />
              <el-input
                v-model="form.username"
                :disabled="!form.custom_username"
                placeholder="不填则由系统自动生成"
                style="flex: 1"
              />
              <el-button
                :disabled="!form.custom_username"
                @click="regenUsername"
              >
                随机生成
              </el-button>
            </div>
            <div class="tip">
              默认“自动生成”更稳：后端会按你既有规则生成 username。
            </div>
          </el-form-item>

          <el-form-item label="初始密码" prop="password">
            <div class="inline">
              <el-input v-model="form.password" show-password placeholder="至少 8 位（建议字母+数字）" />
              <el-button @click="regenPassword">重新生成</el-button>
              <el-button @click="copyPassword">复制</el-button>
            </div>
            <div class="tip">
              创建成功后你也可以在学校列表里用“修改密码”再次重置。
            </div>
          </el-form-item>
        </div>

        <!-- 操作 -->
        <div class="actions">
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            创建
          </el-button>
          <el-button :disabled="submitting" @click="handleReset">
            重置
          </el-button>
          <el-button :disabled="submitting" @click="goBack">
            返回列表
          </el-button>
        </div>
      </el-form>
    </el-card>

    <el-dialog v-model="successVisible" title="创建成功" width="520px">
      <div class="success">
        <div class="success-line">学校：{{ successInfo.name }}</div>
        <div class="success-line">用户名：{{ successInfo.username || "（由后端生成）" }}</div>
        <div class="success-line">邮箱：{{ successInfo.contact_email }}</div>
        <div class="success-line">
          初始密码：<span class="mono">{{ successInfo.password }}</span>
          <el-button link type="primary" @click="copyText(successInfo.password)">复制</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="successVisible=false">关闭</el-button>
        <el-button type="primary" @click="goBack">返回学校列表</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, nextTick } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { apiPost, apiGet } from "@/utils/api";

import { regionData, codeToText } from "element-china-area-data";
import { gatProvinces, gatChildren, gatCodeToText } from "@/utils/gat_area_patch";

const router = useRouter();

const formRef = ref(null);
const submitting = ref(false);

const successVisible = ref(false);
const successInfo = reactive({ name: "", username: "", email: "", password: "" });

/** ✅ 合并后的 codeToText（港澳台补全） */
const codeToTextFull = { ...codeToText, ...gatCodeToText };

/** 省市区选项 */
const provinceOptions = ref([]);
const cityOptions = ref([]);
const districtOptions = ref([]);

async function initRegionLock() {
  try {
    const { res, data } = await apiGet("/api/region-admin/overview/");

    // 401/403 时给个提示
    if (!res?.ok) {
      console.warn("[initRegionLock] http not ok:", res?.status, data);
      ElMessage.error(data?.message || "获取区域信息失败，请重新登录");
      return;
    }
    if (!data?.success) {
      console.warn("[initRegionLock] api not success:", data);
      ElMessage.error(data?.message || "获取区域信息失败");
      return;
    }

    const region = data?.data?.region;
    if (!region) {
      ElMessage.error("未获取到区域信息（region为空）");
      return;
    }

    // ✅ 写入表单（你模板里禁用 input 就会直接显示）
    form.province = region.province || "";
    form.city = region.city || "";
    form.district = region.name || ""; // 注意：区县名在 region.name

    // ✅ 如果你还保留了省市区联动的 code 字段，这里清掉，避免 UI 状态冲突
    if ("provinceCode" in form) form.provinceCode = "";
    if ("cityCode" in form) form.cityCode = "";
    if ("districtCode" in form) form.districtCode = "";

    await nextTick();
    // 如果你 rules 里 province/city/district 是必填，这里主动触发一次校验（可选）
    // formRef.value?.validateField?.(["province", "city", "district"]);
  } catch (e) {
    console.error("[initRegionLock] error:", e);
    ElMessage.error("获取区域信息失败（网络或权限问题）");
  }
}

onMounted(() => {
  initRegionLock();
});

/** 初始化省份：大陆 + 港澳台 */
provinceOptions.value = [
  ...regionData.map((p) => ({
    code: p.value,
    name: p.label,
    children: p.children || [],
  })),
  ...gatProvinces.map((p) => ({
    code: p.code,
    name: p.name,
    children: [],
  })),
];

/** ===== 工具：生成密码/用户名 ===== */
function genPassword(len = 8) {
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789";
  let s = "";
  for (let i = 0; i < len; i++) s += chars[Math.floor(Math.random() * chars.length)];
  return s;
}

function genUsername() {
  // 前端只做兜底随机，不强绑定后端生成规则
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  let tail = "";
  for (let i = 0; i < 6; i++) tail += chars[Math.floor(Math.random() * chars.length)];
  return `SCH_${tail}`;
}

/** 表单 */
const form = reactive({
  name: "",
  school_type: "",

  province: "",
  city: "",
  district: "",

  provinceCode: "",
  cityCode: "",
  districtCode: "",

  contact_name: "",
  contact_position: "",
  contact_phone: "",
  contact_email: "",

  custom_username: false,
  username: "",

  password: genPassword(8),
});

/** 省变化 -> 重置市/区 + 填充市列表 + 写回 province 文本 */
function onProvinceChange(provinceCode) {
  form.cityCode = "";
  form.districtCode = "";
  cityOptions.value = [];
  districtOptions.value = [];

  form.province = codeToTextFull[provinceCode] || "";

  if (provinceCode === "810000" || provinceCode === "820000") {
    cityOptions.value = [{ code: provinceCode, name: form.province, children: [] }];
    return;
  }

  if (provinceCode === "710000") {
    const m = gatChildren["710000"] || {};
    cityOptions.value = Object.entries(m).map(([code, name]) => ({
      code,
      name,
      children: [],
    }));
    return;
  }

  const p = regionData.find((x) => x.value === provinceCode);
  cityOptions.value = (p?.children || []).map((c) => ({
    code: c.value,
    name: c.label,
    children: c.children || [],
  }));
}

function onCityChange(cityCode) {
  form.districtCode = "";
  districtOptions.value = [];

  form.city = codeToTextFull[cityCode] || "";

  if (cityCode === "810000" || cityCode === "820000") {
    const m = gatChildren[cityCode] || {};
    districtOptions.value = Object.entries(m).map(([code, name]) => ({ code, name }));
    return;
  }

  if (cityCode && cityCode.startsWith("71")) {
    const m = gatChildren[cityCode] || {};
    districtOptions.value = Object.entries(m).map(([code, name]) => ({ code, name }));
    return;
  }

  const c = cityOptions.value.find((x) => x.code === cityCode);
  districtOptions.value = (c?.children || []).map((d) => ({
    code: d.value,
    name: d.label,
  }));
}

/** 监听区县变化，回填 district 文本 */
watch(
  () => form.districtCode,
  (newCode) => {
    form.district = codeToTextFull[newCode] || "";
  }
);

/** 如果用户关闭自定义 username，则清空 username（避免误传） */
watch(
  () => form.custom_username,
  (v) => {
    if (!v) form.username = "";
  }
);

/** 校验 */
function validatePhone(rule, value, callback) {
  if (!value) callback(new Error("请输入联系电话"));
  else if (!/^1[3-9]\d{9}$/.test(value)) callback(new Error("请输入有效的手机号码"));
  else callback();
}

function validateEmail(rule, value, callback) {
  if (!value) callback(new Error("请输入邮箱"));
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) callback(new Error("请输入有效的邮箱地址"));
  else callback();
}

/** ✅ 自定义用户名时必须填写 */
function validateUsername(rule, value, callback) {
  if (!form.custom_username) return callback();
  if (!value || !String(value).trim()) return callback(new Error("已选择自定义，请填写用户名"));
  return callback();
}

const rules = {
  name: [{ required: true, message: "请输入学校名称", trigger: "blur" }],
  school_type: [{ required: true, message: "请选择学校类型", trigger: "change" }],

  province: [{ required: true, message: "省份未加载，请刷新页面", trigger: "blur" }],
  city: [{ required: true, message: "城市未加载，请刷新页面", trigger: "blur" }],
  district: [{ required: true, message: "区县未加载，请刷新页面", trigger: "blur" }],

  contact_name: [{ required: true, message: "请输入联系人姓名", trigger: "blur" }],
  contact_position: [{ required: true, message: "请输入职务", trigger: "blur" }],
  contact_phone: [{ required: true, validator: validatePhone, trigger: "blur" }],
  contact_email: [{ required: true, validator: validateEmail, trigger: "blur" }],

  // ✅ 对齐后端：min_length = 8
  password: [
    { required: true, message: "请设置初始密码", trigger: "blur" },
    { min: 8, message: "密码不少于 8 位", trigger: "blur" },
  ],

  username: [{ validator: validateUsername, trigger: "blur" }],
};

function regenPassword() {
  form.password = genPassword(8);
  ElMessage.success("已生成新密码");
}

function regenUsername() {
  form.username = genUsername();
  ElMessage.success("已生成随机用户名");
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(String(text || ""));
    ElMessage.success("已复制");
  } catch (e) {
    ElMessage.warning("复制失败，请手动复制");
  }
}

function copyPassword() {
  copyText(form.password);
}

/** 提交 */
async function handleSubmit() {
  if (!formRef.value) return;

  await formRef.value.validate(async (valid) => {
    if (!valid) return;

    submitting.value = true;
    try {
      // ✅ payload 严格对齐 RegionAdminCreateSchoolSerializer
      const payload = {
        password: form.password,

        name: form.name,
        school_type: form.school_type,
        province: form.province,
        city: form.city,
        district: form.district,

        contact_name: form.contact_name,
        contact_position: form.contact_position,
        contact_phone: form.contact_phone,
        contact_email: form.contact_email,
      };

      // username：只有勾选自定义且非空才传
      if (form.custom_username && form.username && form.username.trim()) {
        payload.username = form.username.trim();
      }

      const { data: resp } = await apiPost("/api/region-admin/schools/create/", payload);

      if (!resp?.success) {
        throw new Error(resp?.message || "创建失败");
      }

      successInfo.name = form.name;
      successInfo.username = resp.data?.username || payload.username || "";
      successInfo.contact_email = resp.data?.contact_email || payload.contact_email || form.contact_email;
      successInfo.password = form.password;

      ElMessage.success("创建成功");
      successVisible.value = true;
    } catch (e) {
      console.error(e);

      // ✅ 你之前遇到的 500 + HTML (IntegrityError) 常见原因：email/username 唯一约束冲突
      const msg = e?.message || "";
      if (msg.includes("非JSON") || msg.includes("Unexpected token '<'") || msg.includes("500")) {
        ElMessage.error("创建失败：后端 500（常见原因：登录邮箱或用户名重复）");
      } else {
        ElMessage.error(msg || "创建失败");
      }
    } finally {
      submitting.value = false;
    }
  });
}

function handleReset() {
  if (!formRef.value) return;

  formRef.value.resetFields();
  form.provinceCode = "";
  form.cityCode = "";
  form.districtCode = "";
  cityOptions.value = [];
  districtOptions.value = [];

  form.custom_username = false;
  form.username = "";
  form.password = genPassword(8);
}

function goBack() {
  router.push("/region-admin/schools");
}
</script>

<style scoped>
.page {
  padding: 16px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.block {
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
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

.form {
  max-width: 820px;
}

.section {
  padding: 10px 6px 2px;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 12px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin: 6px 0 12px;
  padding-left: 10px;
  border-left: 3px solid #409eff;
}

.inline {
  display: flex;
  gap: 10px;
  align-items: center;
  width: 100%;
}

.tip {
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

.actions {
  padding-top: 8px;
  display: flex;
  gap: 12px;
}

.success {
  padding: 4px 0;
}
.success-line {
  margin: 8px 0;
  color: #303133;
}
.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}
</style>
