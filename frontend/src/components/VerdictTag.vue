<template>
  <span class="verdict-tag" :class="tagClass">{{ label }}</span>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { SubmissionStatus, Verdict } from "../api/submissions";

const props = defineProps<{
  verdict: Verdict | SubmissionStatus | "PENDING";
}>();

const label = computed(() => props.verdict ?? "PENDING");

const tagClass = computed(() => {
  switch (props.verdict) {
    case "AC":
      return "verdict-tag--success";
    case "QUEUED":
      return "verdict-tag--queued";
    case "JUDGING":
      return "verdict-tag--judging";
    case "WA":
    case "RE":
    case "TLE":
    case "MLE":
    case "OLE":
    case "CE":
    case "SE":
      return "verdict-tag--danger";
    default:
      return "verdict-tag--neutral";
  }
});
</script>

<style scoped>
.verdict-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 74px;
  min-height: 32px;
  padding: 0 12px;
  border: 1px solid transparent;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  line-height: 1;
}

.verdict-tag--success {
  border-color: #b7ebc6;
  background: #ecfdf3;
  color: #15803d;
}

.verdict-tag--queued {
  border-color: #fde68a;
  background: #fffbeb;
  color: #b45309;
}

.verdict-tag--judging {
  border-color: #bfdbfe;
  background: #eff6ff;
  color: #1d4ed8;
}

.verdict-tag--danger {
  border-color: #fecaca;
  background: #fef2f2;
  color: #b91c1c;
}

.verdict-tag--neutral {
  border-color: var(--oj-border);
  background: var(--oj-surface-soft);
  color: var(--oj-text-soft);
}
</style>
