<template>
  <section class="sample-list">
    <div class="section-head">
      <div>
        <h2 class="section-title">样例</h2>
        <p class="section-description">通过样例理解输入与输出格式。</p>
      </div>
      <span v-if="normalizedSamples.length" class="muted">{{ normalizedSamples.length }} 组样例</span>
    </div>

    <div v-if="normalizedSamples.length" class="sample-stack">
      <article v-for="sample in normalizedSamples" :key="sample.id" class="sample-item">
        <div class="sample-item__head">
          <!-- <h3>{{ showMultiLabels ? `样例 ${sample.sort_order}` : "样例" }}</h3> -->
        </div>
        <div class="sample-grid">
          <div class="sample-panel">
            <h4>{{ showMultiLabels ? "输入" : "输入" }}</h4>
            <pre>{{ sample.input_text || "暂无样例输入。" }}</pre>
          </div>
          <div class="sample-panel">
            <h4>{{ showMultiLabels ? "输出" : "输出" }}</h4>
            <pre>{{ sample.output_text || "暂无样例输出。" }}</pre>
          </div>
        </div>
      </article>
    </div>

    <p v-else class="muted">暂无样例数据。</p>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { ProblemSampleCase } from "../api/problems";

const props = withDefaults(
  defineProps<{
    sampleCases?: ProblemSampleCase[];
    legacyInput?: string;
    legacyOutput?: string;
  }>(),
  {
    sampleCases: () => [],
    legacyInput: "",
    legacyOutput: ""
  }
);

const normalizedSamples = computed<ProblemSampleCase[]>(() => {
  if (props.sampleCases.length > 0) {
    return [...props.sampleCases].sort((left, right) => left.sort_order - right.sort_order);
  }

  if (!props.legacyInput && !props.legacyOutput) {
    return [];
  }

  return [
    {
      id: 0,
      sort_order: 1,
      input_text: props.legacyInput || "",
      output_text: props.legacyOutput || ""
    }
  ];
});

const showMultiLabels = computed(() => normalizedSamples.value.length > 1);
</script>

<style scoped>
.sample-list {
  display: grid;
  gap: 18px;
}

.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.sample-stack {
  display: grid;
  gap: 16px;
}

.sample-item {
  display: grid;
  gap: 14px;
  padding: 20px;
  border: 1px solid var(--oj-border);
  border-radius: 8px;
  background: #fbfdff;
}

.sample-item__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.sample-item__head h3 {
  margin: 0;
  font-size: 16px;
  line-height: 1.3;
}

.sample-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.sample-panel {
  display: grid;
  gap: 8px;
}

.sample-panel h4 {
  margin: 0;
  color: var(--oj-text-soft);
  font-size: 14px;
  font-weight: 700;
}

.sample-panel pre {
  min-height: 96px;
  background: var(--oj-surface-soft);
}

@media (max-width: 760px) {
  .section-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .sample-grid {
    grid-template-columns: 1fr;
  }
}
</style>
