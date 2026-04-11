<template>
  <section class="sample-list">
    <div class="section-head">
      <h2>Samples</h2>
      <span class="muted">{{ normalizedSamples.length }} sample{{ normalizedSamples.length === 1 ? "" : "s" }}</span>
    </div>

    <div v-if="normalizedSamples.length" class="sample-stack">
      <article v-for="sample in normalizedSamples" :key="sample.id" class="sample-item">
        <h3 v-if="showMultiLabels">Sample {{ sample.sort_order }}</h3>
        <div class="sample-grid">
          <div>
            <h4>{{ showMultiLabels ? "Input" : "Sample Input" }}</h4>
            <pre>{{ sample.input_text || "No sample input." }}</pre>
          </div>
          <div>
            <h4>{{ showMultiLabels ? "Output" : "Sample Output" }}</h4>
            <pre>{{ sample.output_text || "No sample output." }}</pre>
          </div>
        </div>
      </article>
    </div>

    <p v-else class="muted">No sample cases yet.</p>
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
  margin-top: 28px;
}

.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.section-head h2,
.sample-item h3,
.sample-grid h4 {
  margin: 0;
}

.sample-stack {
  display: grid;
  gap: 16px;
}

.sample-item {
  padding: 16px;
  border: 1px solid #d9dee7;
  border-radius: 8px;
  background: #fbfcfe;
}

.sample-item h3 {
  margin-bottom: 12px;
  font-size: 17px;
}

.sample-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.sample-grid h4 {
  margin-bottom: 8px;
  font-size: 14px;
  color: #59636f;
}

.sample-grid pre {
  min-height: 88px;
  margin: 0;
  padding: 12px;
  border-radius: 8px;
  background: #0f172a;
  color: #e2e8f0;
  overflow-x: auto;
}

@media (max-width: 760px) {
  .sample-grid {
    grid-template-columns: 1fr;
  }
}
</style>
