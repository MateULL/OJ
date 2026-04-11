<template>
  <section class="problem-statement">
    <h1>{{ problem.title }}</h1>
    <div class="limits">
      <span>Time: {{ problem.time_limit_ms }} ms</span>
      <span>Memory: {{ problem.memory_limit_mb }} MB</span>
    </div>

    <section class="statement-section">
      <h2>Statement</h2>
      <ProblemMarkdown :source="problem.description" />
    </section>

    <ProblemSampleList
      :sample-cases="problem.sample_cases"
      :legacy-input="problem.sample_input"
      :legacy-output="problem.sample_output"
    />
  </section>
</template>

<script setup lang="ts">
import type { Problem } from "../api/problems";
import ProblemMarkdown from "./ProblemMarkdown.vue";
import ProblemSampleList from "./ProblemSampleList.vue";

defineProps<{
  problem: Problem;
}>();
</script>

<style scoped>
.problem-statement h1 {
  margin: 0 0 12px;
  font-size: 26px;
  line-height: 1.25;
}

.limits {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
  color: #59636f;
}

.statement-section {
  margin-bottom: 8px;
}

.statement-section h2 {
  margin: 0 0 14px;
  font-size: 18px;
}
</style>
