<template>
  <section class="problem-statement">
    <header class="statement-head">
      <div class="statement-head__top">
        <p class="page-kicker">题目</p>
        <span v-if="problem.is_solved" class="statement-solved">
          <el-icon><Check /></el-icon>
          已通过
        </span>
      </div>

      <div class="statement-title-row">
        <div>
          <p class="statement-id">Problem #{{ problem.display_number ?? problem.id }}</p>
          <h1>{{ problem.title }}</h1>
        </div>
        <DifficultyTag :difficulty="problem.difficulty" />
      </div>

      <div class="statement-meta">
        <ModeTag :mode="problem.judge_mode" />
        <span class="oj-pill">时间限制 {{ problem.time_limit_ms }} ms</span>
        <span class="oj-pill">内存限制 {{ problem.memory_limit_mb }} MB</span>
      </div>
    </header>

    <section class="statement-section">
      <div class="section-block__head">
        <h2 class="section-title">题目描述</h2>
        <p class="section-description">请根据题意完成程序。</p>
      </div>
      <ProblemMarkdown :source="problem.description" />
    </section>

    <ProblemSampleList
      :sample-cases="problem.sample_cases"
      :legacy-input="problem.sample_input"
      :legacy-output="problem.sample_output"
    />

    <section class="statement-section statement-info">
      <div class="section-block__head">
        <h2 class="section-title">判题信息</h2>
        <p class="section-description">提交前请留意以下限制。</p>
      </div>
      <div class="statement-info__grid">
        <article class="statement-info__card">
          <span>时间限制</span>
          <strong>{{ problem.time_limit_ms }} ms</strong>
          <p>超出限制将判为 TLE。</p>
        </article>
        <article class="statement-info__card">
          <span>内存限制</span>
          <strong>{{ problem.memory_limit_mb }} MB</strong>
          <p>超出限制将判为 MLE。</p>
        </article>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { Check } from "@element-plus/icons-vue";
import type { Problem } from "../api/problems";
import DifficultyTag from "./DifficultyTag.vue";
import ModeTag from "./ModeTag.vue";
import ProblemMarkdown from "./ProblemMarkdown.vue";
import ProblemSampleList from "./ProblemSampleList.vue";

defineProps<{
  problem: Problem;
}>();
</script>

<style scoped>
.problem-statement {
  display: grid;
  gap: 30px;
}

.statement-head {
  display: grid;
  gap: 18px;
}

.statement-head__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.statement-id {
  margin: 0 0 8px;
  color: var(--oj-muted);
  font-size: 14px;
  font-weight: 600;
}

.statement-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.statement-title-row h1 {
  margin: 0;
  font-size: 32px;
  line-height: 1.18;
}

.statement-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.statement-solved {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 28px;
  padding: 0 12px;
  border: 1px solid #ccead5;
  border-radius: 999px;
  background: #edfdf3;
  color: #15803d;
  font-size: 13px;
  font-weight: 700;
}

.statement-section {
  display: grid;
  gap: 16px;
}

.section-block__head {
  display: grid;
  gap: 2px;
}

.statement-info {
  padding-top: 6px;
  border-top: 1px solid var(--oj-border);
}

.statement-info__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.statement-info__card {
  display: grid;
  gap: 8px;
  padding: 18px;
  border: 1px solid var(--oj-border);
  border-radius: 8px;
  background: var(--oj-surface-soft);
}

.statement-info__card span {
  color: var(--oj-muted);
  font-size: 13px;
}

.statement-info__card strong {
  color: var(--oj-text);
  font-size: 20px;
  line-height: 1.2;
}

.statement-info__card p {
  margin: 0;
  color: var(--oj-text-soft);
  font-size: 14px;
}

@media (max-width: 760px) {
  .statement-head__top,
  .statement-title-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .statement-title-row h1 {
    font-size: 28px;
  }

  .statement-info__grid {
    grid-template-columns: 1fr;
  }
}
</style>
