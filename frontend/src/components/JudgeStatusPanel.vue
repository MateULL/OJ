<template>
  <section class="judge-status panel">
    <div class="panel-body">
      <div class="status-head">
        <div>
          <div class="muted">Submission</div>
          <strong>{{ submission ? `#${submission.id}` : "Not submitted" }}</strong>
        </div>
        <VerdictTag :verdict="submission?.final_verdict ?? statusFallback" />
      </div>

      <div v-if="submission" class="status-grid">
        <span>Status</span>
        <strong>{{ submission.status }}</strong>
        <span>Total time</span>
        <strong>{{ submission.total_time_ms }} ms</strong>
        <span>Max memory</span>
        <strong>{{ submission.max_memory_kb }} KB</strong>
      </div>

      <p v-else class="muted">Submit code to start judging.</p>
    </div>
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
</script>

<style scoped>
.judge-status {
  margin-top: 16px;
}

.status-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.status-grid {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 8px 16px;
  color: #59636f;
}

.status-grid strong {
  color: #1f2933;
}

@media (max-width: 760px) {
  .status-head {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
