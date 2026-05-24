<template>
  <section class="judge-status">
    <div class="status-head">
      <div>
        <p class="page-kicker">判题结果</p>
        <h3>{{ headline }}</h3>
        <p v-if="submission" class="submission-id muted">提交 #{{ submission.id }}</p>
      </div>
      <VerdictTag :verdict="submission?.final_verdict ?? statusFallback" />
    </div>

    <div v-if="submission" class="status-grid">
      <div class="status-item">
        <span>当前状态</span>
        <strong>{{ submission.status }}</strong>
      </div>
      <div class="status-item">
        <span>最终结果</span>
        <strong>{{ submission.final_verdict || "--" }}</strong>
      </div>
      <div class="status-item">
        <span>总耗时</span>
        <strong>{{ submission.total_time_ms }} ms</strong>
      </div>
      <div class="status-item">
        <span>最大内存</span>
        <strong>{{ submission.max_memory_kb }} KB</strong>
      </div>
      <div class="status-item">
        <span>提交时间</span>
        <strong>{{ formatDate(submission.submitted_at) }}</strong>
      </div>
      <div class="status-item">
        <span>判题完成</span>
        <strong>{{ submission.judged_at ? formatDate(submission.judged_at) : "--" }}</strong>
      </div>
    </div>

    <p v-else class="muted">提交后可在这里查看判题结果。</p>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { Submission } from "../api/submissions";
import VerdictTag from "./VerdictTag.vue";

const props = defineProps<{
  submission: Submission | null;
}>();

const statusFallback = computed(() => {
  if (!props.submission) {
    return "PENDING";
  }
  return props.submission.status === "FINISHED" ? "PENDING" : props.submission.status;
});

const headline = computed(() => {
  if (!props.submission) {
    return "尚未提交";
  }
  if (props.submission.status === "QUEUED") {
    return "正在排队，等待判题";
  }
  if (props.submission.status === "JUDGING") {
    return "判题中，请稍候";
  }
  return props.submission.final_verdict ? `判题完成：${props.submission.final_verdict}` : "判题完成";
});

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}
</script>

<style scoped>
.judge-status {
  display: grid;
  gap: 18px;
  padding: 20px;
  border: 1px solid var(--oj-border);
  border-radius: 8px;
  background: #f8fafc;
}

.status-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.status-head h3 {
  margin: 0;
  font-size: 20px;
  line-height: 1.3;
}

.submission-id {
  margin: 8px 0 0;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.status-item {
  display: grid;
  gap: 6px;
  padding: 14px;
  border: 1px solid var(--oj-border);
  border-radius: 8px;
  background: var(--oj-surface);
}

.status-item span {
  color: var(--oj-muted);
  font-size: 13px;
}

.status-item strong {
  color: var(--oj-text);
  font-size: 15px;
  line-height: 1.4;
}

@media (max-width: 760px) {
  .status-head {
    flex-direction: column;
  }

  .status-grid {
    grid-template-columns: 1fr;
  }
}
</style>
