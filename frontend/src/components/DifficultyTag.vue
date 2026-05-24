<template>
  <span class="difficulty-tag" :class="`difficulty-tag--${tone}`">{{ label }}</span>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  difficulty?: string;
}>();

const normalizedDifficulty = computed(() => (props.difficulty || "").toLowerCase());

const tone = computed(() => {
  switch (normalizedDifficulty.value) {
    case "easy":
      return "easy";
    case "medium":
      return "medium";
    case "hard":
      return "hard";
    default:
      return "neutral";
  }
});

const label = computed(() => {
  switch (normalizedDifficulty.value) {
    case "easy":
      return "简单";
    case "medium":
      return "中等";
    case "hard":
      return "困难";
    default:
      return "未分级";
  }
});
</script>

<style scoped>
.difficulty-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 28px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid transparent;
  font-size: 13px;
  font-weight: 700;
}

.difficulty-tag--easy {
  border-color: #bbf7d0;
  background: #f0fdf4;
  color: #15803d;
}

.difficulty-tag--medium {
  border-color: #fde68a;
  background: #fffbeb;
  color: #b45309;
}

.difficulty-tag--hard {
  border-color: #fecaca;
  background: #fef2f2;
  color: #dc2626;
}

.difficulty-tag--neutral {
  border-color: var(--oj-border);
  background: var(--oj-surface-soft);
  color: var(--oj-text-soft);
}
</style>
