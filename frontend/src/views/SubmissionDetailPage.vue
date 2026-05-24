<template>
  <main class="page page-stack">
    <el-skeleton v-if="loading" :rows="8" animated />
    <template v-else-if="submission">
      <section class="page-card">
        <div class="page-card__body submission-summary">
          <div>
            <p class="page-kicker">提交详情</p>
            <h1 class="page-title">提交 #{{ submission.id }}</h1>
            <p class="page-description">{{ submission.problem_title }} &middot; {{ submission.language }}</p>
          </div>
          <VerdictTag :verdict="submission.final_verdict ?? submission.status" />
        </div>
      </section>

      <section class="page-card">
        <div class="page-card__body">
          <div class="section-block__head">
            <h2 class="section-title">结果摘要</h2>
            <p class="section-description">查看本次提交的判题结果。</p>
          </div>

          <div class="summary-grid">
            <div class="summary-item">
              <span>最终结果</span>
              <strong>{{ submission.final_verdict ?? "-" }}</strong>
            </div>
            <div class="summary-item">
              <span>状态</span>
              <strong>{{ submission.status }}</strong>
            </div>
            <div class="summary-item">
              <span>总耗时</span>
              <strong>{{ submission.total_time_ms }} ms</strong>
            </div>
            <div class="summary-item">
              <span>最大内存</span>
              <strong>{{ submission.max_memory_kb }} KB</strong>
            </div>
            <div class="summary-item">
              <span>提交时间</span>
              <strong>{{ formatDate(submission.submitted_at) }}</strong>
            </div>
            <div class="summary-item">
              <span>判题时间</span>
              <strong>{{ submission.judged_at ? formatDate(submission.judged_at) : "-" }}</strong>
            </div>
          </div>
        </div>
      </section>

      <section v-if="submission.final_verdict === 'CE'" class="page-card">
        <div class="page-card__body">
          <div class="section-block__head">
            <h2 class="section-title">编译日志</h2>
            <p class="section-description">编译失败详情如下。</p>
          </div>
          <pre>{{ submission.compile_log || "暂无编译日志。" }}</pre>
        </div>
      </section>

      <section class="page-card">
        <div class="page-card__body">
          <div class="section-block__head">
            <h2 class="section-title">测试点结果</h2>
            <p class="section-description">查看每个测试点的结果。</p>
          </div>
          <CaseResultTable :results="submission.case_results ?? []" />
        </div>
      </section>
    </template>
    <el-empty v-else description="提交不存在" />
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
      ElMessage.error("加载失败，请稍后重试。");
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
.submission-summary {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.submission-summary .page-title {
  font-size: 30px;
}

.section-block__head {
  display: grid;
  gap: 2px;
  margin-bottom: 16px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.summary-item {
  display: grid;
  gap: 8px;
  padding: 16px;
  border: 1px solid var(--oj-border);
  border-radius: 8px;
  background: var(--oj-surface-soft);
}

.summary-item span {
  color: var(--oj-muted);
  font-size: 13px;
}

.summary-item strong {
  color: var(--oj-text);
  font-size: 16px;
}

@media (max-width: 900px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .submission-summary {
    flex-direction: column;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
