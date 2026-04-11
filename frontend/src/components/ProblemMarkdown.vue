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
  const source = props.source?.trim() || "No problem statement yet.";
  return DOMPurify.sanitize(markdown.render(source));
});
</script>

<style scoped>
.problem-markdown {
  color: #1f2933;
  line-height: 1.7;
}

.problem-markdown :deep(h1),
.problem-markdown :deep(h2),
.problem-markdown :deep(h3) {
  margin: 24px 0 12px;
  color: #111827;
  line-height: 1.3;
}

.problem-markdown :deep(h1) {
  font-size: 24px;
}

.problem-markdown :deep(h2) {
  font-size: 20px;
}

.problem-markdown :deep(h3) {
  font-size: 18px;
}

.problem-markdown :deep(p),
.problem-markdown :deep(ul),
.problem-markdown :deep(ol),
.problem-markdown :deep(blockquote) {
  margin: 0 0 14px;
}

.problem-markdown :deep(ul),
.problem-markdown :deep(ol) {
  padding-left: 22px;
}

.problem-markdown :deep(code) {
  padding: 1px 5px;
  border-radius: 4px;
  background: #f2f5f8;
  font-family: Consolas, "Courier New", monospace;
  font-size: 0.95em;
}

.problem-markdown :deep(pre) {
  margin: 0 0 14px;
  padding: 14px;
  border-radius: 8px;
  background: #0f172a;
  color: #e2e8f0;
  overflow-x: auto;
}

.problem-markdown :deep(pre code) {
  padding: 0;
  background: transparent;
  color: inherit;
}

.problem-markdown :deep(blockquote) {
  padding-left: 12px;
  border-left: 3px solid #cbd5e1;
  color: #475569;
}

.problem-markdown :deep(a) {
  color: #0f766e;
}

.problem-markdown :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 14px;
}

.problem-markdown :deep(th),
.problem-markdown :deep(td) {
  padding: 8px 10px;
  border: 1px solid #d9dee7;
  text-align: left;
}
</style>
