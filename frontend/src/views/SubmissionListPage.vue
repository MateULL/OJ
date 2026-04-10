<template>
  <main class="page">
    <div class="toolbar">
      <h1 class="page-title">Submissions</h1>
      <el-button @click="loadSubmissions">Refresh</el-button>
    </div>

    <section class="panel">
      <el-table v-loading="loading" :data="submissions" empty-text="No submissions yet">
        <el-table-column prop="id" label="#" width="80" />
        <el-table-column prop="problem_title" label="Problem" min-width="220" />
        <el-table-column prop="language" label="Language" width="120" />
        <el-table-column label="Verdict" width="130">
          <template #default="{ row }">
            <VerdictTag :verdict="row.final_verdict ?? row.status" />
          </template>
        </el-table-column>
        <el-table-column prop="total_time_ms" label="Time" width="120">
          <template #default="{ row }">{{ row.total_time_ms }} ms</template>
        </el-table-column>
        <el-table-column prop="submitted_at" label="Submitted At" min-width="190">
          <template #default="{ row }">{{ formatDate(row.submitted_at) }}</template>
        </el-table-column>
        <el-table-column label="Action" width="120">
          <template #default="{ row }">
            <RouterLink :to="`/submissions/${row.id}`">Detail</RouterLink>
          </template>
        </el-table-column>
      </el-table>
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { fetchSubmissions, type Submission } from "../api/submissions";
import VerdictTag from "../components/VerdictTag.vue";

const loading = ref(false);
const submissions = ref<Submission[]>([]);

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}

async function loadSubmissions() {
  loading.value = true;
  try {
    submissions.value = await fetchSubmissions();
  } finally {
    loading.value = false;
  }
}

onMounted(loadSubmissions);
</script>
