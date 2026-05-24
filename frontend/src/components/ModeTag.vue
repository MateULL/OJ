<template>
  <span class="mode-tag">{{ label }}</span>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  mode: string;
}>();

const label = computed(() => {
  switch (props.mode.toLowerCase()) {
    case "standard":
      return "标准判题";
    default:
      return props.mode;
  }
});
</script>

<style scoped>
.mode-tag {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 12px;
  border: 1px solid #dbe4ee;
  border-radius: 999px;
  background: #f8fafc;
  color: #475569;
  font-size: 13px;
  font-weight: 600;
}
</style>
