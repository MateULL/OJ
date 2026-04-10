<template>
  <section class="problem-statement">
    <h1>{{ problem.title }}</h1>
    <div class="limits">
      <span>Time: {{ problem.time_limit_ms }} ms</span>
      <span>Memory: {{ problem.memory_limit_mb }} MB</span>
    </div>
    <article class="description">{{ problem.description }}</article>

    <div class="sample-grid">
      <div>
        <h2>Sample Input</h2>
        <pre>{{ problem.sample_input || "No sample input." }}</pre>
      </div>
      <div>
        <h2>Sample Output</h2>
        <pre>{{ problem.sample_output || "No sample output." }}</pre>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { Problem } from "../api/problems";

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

.description {
  margin-bottom: 24px;
  white-space: pre-wrap;
}

.sample-grid {
  display: grid;
  gap: 16px;
}

.sample-grid h2 {
  margin: 0 0 8px;
  font-size: 16px;
}
</style>
