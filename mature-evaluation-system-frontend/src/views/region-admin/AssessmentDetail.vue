<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div>评估详情</div>
          <div style="display:flex;gap:8px;">
            <el-button @click="goBack">返回列表</el-button>
            <el-button @click="load" :loading="loading">刷新</el-button>
          </div>
        </div>
      </template>

      <el-skeleton :loading="loading" animated>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="评估ID">{{ detail.id }}</el-descriptions-item>
          <el-descriptions-item label="学校">{{ detail.school?.name }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ detail.status }}</el-descriptions-item>
          <el-descriptions-item label="等级">{{ detail.maturity_level || '-' }}</el-descriptions-item>
          <el-descriptions-item label="总分">{{ detail.scores?.total_score ?? '-' }}</el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ detail.times?.completed_at || '-' }}</el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">各维度得分</el-divider>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="素养">{{ detail.scores?.literacy_score ?? '-' }}</el-descriptions-item>
          <el-descriptions-item label="制度">{{ detail.scores?.institution_score ?? '-' }}</el-descriptions-item>
          <el-descriptions-item label="行为">{{ detail.scores?.behavior_score ?? '-' }}</el-descriptions-item>
          <el-descriptions-item label="资产">{{ detail.scores?.asset_score ?? '-' }}</el-descriptions-item>
          <el-descriptions-item label="技术">{{ detail.scores?.technology_score ?? '-' }}</el-descriptions-item>
          <el-descriptions-item label="总分">{{ detail.scores?.total_score ?? '-' }}</el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">制度 / 行为 / 资产 / 技术 原始数据</el-divider>

        <el-collapse>
          <el-collapse-item title="制度（Institution）" name="i">
            <pre class="json">{{ pretty(detail.institution) }}</pre>
          </el-collapse-item>
          <el-collapse-item title="行为（Behavior）" name="b">
            <pre class="json">{{ pretty(detail.behavior) }}</pre>
          </el-collapse-item>
          <el-collapse-item title="资产（Asset）" name="a">
            <pre class="json">{{ pretty(detail.asset) }}</pre>
          </el-collapse-item>
          <el-collapse-item title="技术（Technology）" name="t">
            <pre class="json">{{ pretty(detail.technology) }}</pre>
          </el-collapse-item>
        </el-collapse>
      </el-skeleton>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { apiGet } from "@/utils/api";

const route = useRoute();
const router = useRouter();
const loading = ref(false);

const detail = reactive({
  id: null,
  school: null,
  status: "",
  maturity_level: "",
  scores: {},
  report: {},
  times: {},
  institution: null,
  behavior: null,
  asset: null,
  technology: null
});

function pretty(obj) {
  if (!obj) return "{}";
  return JSON.stringify(obj, null, 2);
}

function goBack() {
  router.push("/region-admin/assessments");
}

async function load() {
  const id = route.params.id;
  if (!id) return;

  loading.value = true;
  try {
    const { data: resp } = await apiGet(`/api/region-admin/assessments/${id}/`);
    if (!resp.success) throw new Error(resp.message || "加载失败");

    // 你的返回是 data 直接是详情结构（不是 data.assessment）
    const d = resp.data || {};
    Object.keys(detail).forEach(k => (detail[k] = d[k] ?? detail[k]));
  } catch (e) {
    ElMessage.error(e.message || "加载失败");
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<style scoped>
.json {
  background: #0b1020;
  color: #d6e7ff;
  padding: 12px;
  border-radius: 8px;
  overflow: auto;
  font-size: 12px;
  line-height: 1.4;
}
</style>
