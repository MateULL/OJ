<template>
  <article class="problem-markdown" v-html="sanitizedHtml" />
</template>

<script setup lang="ts">
import DOMPurify from "dompurify";
import MarkdownIt from "markdown-it";
import { computed } from "vue";

const props = defineProps<{
  source?: string;
}>();

const markdown = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true
});

const sanitizedHtml = computed(() => {
  const source = props.source?.trim() || "暂无题面内容。";
  return DOMPurify.sanitize(markdown.render(source));
});
</script>

<style scoped>
.problem-markdown {
  color: var(--oj-text);
  font-size: 15px;
  line-height: 1.9;
}

.problem-markdown :deep(h1),
.problem-markdown :deep(h2),
.problem-markdown :deep(h3) {
  margin: 30px 0 14px;
  color: var(--oj-text);
  line-height: 1.28;
}

.problem-markdown :deep(h1) {
  font-size: 24px;
}

.problem-markdown :deep(h2) {
  font-size: 21px;
}

.problem-markdown :deep(h3) {
  font-size: 18px;
}

.problem-markdown :deep(p),
.problem-markdown :deep(ul),
.problem-markdown :deep(ol),
.problem-markdown :deep(blockquote),
.problem-markdown :deep(table) {
  margin: 0 0 18px;
}

.problem-markdown :deep(ul),
.problem-markdown :deep(ol) {
  padding-left: 24px;
}

.problem-markdown :deep(li + li) {
  margin-top: 6px;
}

.problem-markdown :deep(code) {
  padding: 2px 6px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #f8fafc;
  color: #0f172a;
  font-family: Consolas, "Courier New", monospace;
  font-size: 0.94em;
}

.problem-markdown :deep(pre) {
  margin: 0 0 18px;
  padding: 16px 18px;
  border: 1px solid var(--oj-border);
  border-radius: 8px;
  background: #f8fafc;
  color: #0f172a;
  overflow-x: auto;
}

.problem-markdown :deep(pre code) {
  padding: 0;
  border: 0;
  background: transparent;
  color: inherit;
}

.problem-markdown :deep(blockquote) {
  padding: 12px 16px;
  border-left: 3px solid #93c5fd;
  border-radius: 0 8px 8px 0;
  background: #eff6ff;
  color: #334155;
}

.problem-markdown :deep(a) {
  color: var(--oj-link);
  font-weight: 600;
}

.problem-markdown :deep(table) {
  width: 100%;
  border-collapse: collapse;
}

.problem-markdown :deep(th),
.problem-markdown :deep(td) {
  padding: 10px 12px;
  border: 1px solid var(--oj-border);
  text-align: left;
}

.problem-markdown :deep(th) {
  background: var(--oj-surface-soft);
}
</style>
