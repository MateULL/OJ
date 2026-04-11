<template>
  <main class="page">
    <el-skeleton v-if="loading" :rows="6" animated />
    <template v-else-if="submission">
      <div class="detail-head">
        <div>
          <h1 class="page-title">Submission #{{ submission.id }}</h1>
          <p class="muted">{{ submission.problem_title }} · {{ submission.language }}</p>
        </div>
        <VerdictTag :verdict="submission.final_verdict ?? submission.status" />
      </div>

      <section class="panel">
        <div class="panel-body metrics">
          <span>Final verdict</span>
          <strong>{{ submission.final_verdict ?? "-" }}</strong>
          <span>Status</span>
          <strong>{{ submission.status }}</strong>
          <span>Total time</span>
          <strong>{{ submission.total_time_ms }} ms</strong>
          <span>Max memory</span>
          <strong>{{ submission.max_memory_kb }} KB</strong>
          <span>Submitted</span>
          <strong>{{ formatDate(submission.submitted_at) }}</strong>
          <span>Judged</span>
          <strong>{{ submission.judged_at ? formatDate(submission.judged_at) : "-" }}</strong>
        </div>
      </section>

      <section v-if="submission.final_verdict === 'CE'" class="panel log-panel">
        <div class="panel-body">
          <h2>Compile Log</h2>
          <pre>{{ submission.compile_log || "No compile log." }}</pre>
        </div>
      </section>

      <section class="panel result-panel">
        <div class="panel-body">
          <h2>Case Results</h2>
          <CaseResultTable :results="submission.case_results ?? []" />
        </div>
      </section>
    </template>
    <el-empty v-else description="Submission not found" />
  </main>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { onBeforeUnmount, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { fetchSubmission, type Submission } from "../api/submissions";
import CaseResultTable from "../components/CaseResultTable.vue";
import VerdictTag from "../components/VerdictTag.vue";

const route = useRoute();
const loading = ref(false);
const submission = ref<Submission | null>(null);
let pollTimer: number | undefined;

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}

async function loadSubmission() {
  loading.value = true;
  try {
    submission.value = await fetchSubmission(Number(route.params.id));
    if (submission.value.status !== "FINISHED") {
      startPolling();
    }
  } finally {
    loading.value = false;
  }
}

function startPolling() {
  stopPolling();
  pollTimer = window.setInterval(async () => {
    try {
      submission.value = await fetchSubmission(Number(route.params.id));
    } catch {
      stopPolling();
      ElMessage.error("Failed to refresh submission details.");
      return;
    }

    if (submission.value.status === "FINISHED") {
      stopPolling();
    }
  }, 1500);
}

function stopPolling() {
  if (pollTimer !== undefined) {
    window.clearInterval(pollTimer);
    pollTimer = undefined;
  }
}

onMounted(loadSubmission);
onBeforeUnmount(stopPolling);
</script>

<style scoped>
.detail-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.detail-head p {
  margin: 0;
}

.metrics {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 10px 18px;
}

.metrics span {
  color: #59636f;
}

.log-panel,
.result-panel {
  margin-top: 16px;
}

.panel-body h2 {
  margin: 0 0 12px;
  font-size: 18px;
}

@media (max-width: 760px) {
  .detail-head {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
