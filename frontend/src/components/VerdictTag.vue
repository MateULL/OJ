<template>
  <el-tag :type="tagType" effect="light" round>{{ label }}</el-tag>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { SubmissionStatus, Verdict } from "../api/submissions";

const props = defineProps<{
  verdict: Verdict | SubmissionStatus | "PENDING";
}>();

const label = computed(() => props.verdict ?? "PENDING");

const tagType = computed(() => {
  switch (props.verdict) {
    case "AC":
      return "success";
    case "WA":
    case "RE":
    case "TLE":
    case "MLE":
    case "OLE":
    case "CE":
    case "SE":
      return "danger";
    default:
      return "info";
  }
});
</script>
