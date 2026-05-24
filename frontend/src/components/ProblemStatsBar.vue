<template>
  <section class="stats-bar" aria-label="题库统计">
    <article v-for="item in items" :key="item.label" class="stats-item">
      <span class="stats-item__label">{{ item.label }}</span>
      <strong class="stats-item__value">{{ item.value }}</strong>
      <span v-if="item.hint" class="stats-item__hint">{{ item.hint }}</span>
    </article>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  items: Array<{
    label: string;
    value: string | number;
    hint?: string;
  }>;
}>();
</script>

<style scoped>
.stats-bar {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0;
  border-top: 1px solid var(--oj-border);
  border-bottom: 1px solid var(--oj-border);
}

.stats-item {
  display: grid;
  gap: 6px;
  padding: 18px 16px;
}

.stats-item + .stats-item {
  border-left: 1px solid var(--oj-border);
}

.stats-item__label {
  color: var(--oj-muted);
  font-size: 13px;
}

.stats-item__value {
  color: var(--oj-text);
  font-size: 24px;
  font-weight: 700;
  line-height: 1.1;
}

.stats-item__hint {
  color: var(--oj-muted);
  font-size: 13px;
  line-height: 1.4;
}

@media (max-width: 900px) {
  .stats-bar {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .stats-item:nth-child(2n + 1) {
    border-left: 0;
  }

  .stats-item:nth-child(n + 3) {
    border-top: 1px solid var(--oj-border);
  }
}

@media (max-width: 560px) {
  .stats-bar {
    grid-template-columns: 1fr;
  }

  .stats-item + .stats-item {
    border-left: 0;
    border-top: 1px solid var(--oj-border);
  }
}
</style>
