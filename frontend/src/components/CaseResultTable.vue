<template>
  <el-table :data="results" border empty-text="暂无测试点结果">
    <el-table-column prop="test_case_order" label="#" width="80" />
    <el-table-column label="Verdict" width="120">
      <template #default="{ row }">
        <VerdictTag :verdict="row.verdict" />
      </template>
    </el-table-column>
    <el-table-column prop="time_used_ms" label="Time" width="120">
      <template #default="{ row }">{{ row.time_used_ms }} ms</template>
    </el-table-column>
    <el-table-column prop="memory_used_kb" label="Memory" width="140">
      <template #default="{ row }">{{ row.memory_used_kb }} KB</template>
    </el-table-column>
    <el-table-column prop="message" label="Message" min-width="220" />
  </el-table>
</template>

<script setup lang="ts">
import type { CaseResult } from "../api/submissions";
import VerdictTag from "./VerdictTag.vue";

defineProps<{
  results: CaseResult[];
}>();
</script>
