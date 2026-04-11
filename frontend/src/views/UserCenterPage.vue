<template>
  <main class="page">
    <div class="toolbar">
      <h1 class="page-title">User Center</h1>
      <div class="month-toolbar">
        <el-button @click="moveMonth(-1)">Previous</el-button>
        <strong>{{ monthLabel }}</strong>
        <el-button @click="moveMonth(1)">Next</el-button>
      </div>
    </div>

    <section class="panel">
      <div class="panel-body">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="User ID">{{ user.id ?? "-" }}</el-descriptions-item>
          <el-descriptions-item label="Username">{{ user.username }}</el-descriptions-item>
          <el-descriptions-item label="Authenticated">Yes</el-descriptions-item>
        </el-descriptions>
      </div>
    </section>

    <section class="panel heatmap-panel">
      <div class="panel-body">
        <div class="heatmap-head">
          <div>
            <h2>AC Check-ins</h2>
            <p class="muted">{{ checkins.active_days }} active day{{ checkins.active_days === 1 ? "" : "s" }} this month</p>
          </div>
        </div>
        <CheckinHeatmap :month="monthKey" :values="checkins.values" />
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { computed, onMounted, ref } from "vue";
import type { CheckinResponse } from "../api/users";
import { fetchCheckins } from "../api/users";
import CheckinHeatmap from "../components/CheckinHeatmap.vue";
import { useUserStore } from "../stores/user";

const user = useUserStore();
const now = new Date();
const currentMonth = ref(new Date(now.getFullYear(), now.getMonth(), 1));
const checkins = ref<CheckinResponse>({
  month: "",
  active_days: 0,
  values: []
});

const monthKey = computed(() => {
  const year = currentMonth.value.getFullYear();
  const month = `${currentMonth.value.getMonth() + 1}`.padStart(2, "0");
  return `${year}-${month}`;
});

const monthLabel = computed(() =>
  currentMonth.value.toLocaleDateString(undefined, { year: "numeric", month: "long" })
);

async function loadCheckins() {
  try {
    checkins.value = await fetchCheckins(monthKey.value);
  } catch {
    ElMessage.error("Failed to load check-in heatmap.");
  }
}

function moveMonth(offset: number) {
  const next = new Date(currentMonth.value);
  next.setMonth(next.getMonth() + offset);
  next.setDate(1);
  currentMonth.value = next;
  void loadCheckins();
}

onMounted(async () => {
  await user.ensureLoaded();
  await loadCheckins();
});
</script>

<style scoped>
.month-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.heatmap-panel {
  margin-top: 16px;
}

.heatmap-head {
  margin-bottom: 12px;
}

.heatmap-head h2,
.heatmap-head p {
  margin: 0;
}
</style>
