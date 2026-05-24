<template>
  <el-table class="oj-table" :data="results" empty-text="暂无测试点结果">
    <el-table-column prop="test_case_order" label="测试点" width="96" />
    <el-table-column label="结果" width="128">
      <template #default="{ row }">
        <VerdictTag :verdict="row.verdict" />
      </template>
    </el-table-column>
    <el-table-column label="耗时" width="128">
      <template #default="{ row }">{{ row.time_used_ms }} ms</template>
    </el-table-column>
    <el-table-column label="内存" width="140">
      <template #default="{ row }">{{ row.memory_used_kb }} KB</template>
    </el-table-column>
    <el-table-column prop="message" label="结果说明" min-width="260" />
  </el-table>
</template>

<script setup lang="ts">
import type { CaseResult } from "../api/submissions";
import VerdictTag from "./VerdictTag.vue";

defineProps<{
  results: CaseResult[];
}>();
</script>
