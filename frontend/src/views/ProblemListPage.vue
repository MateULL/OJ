<template>
  <main class="page">
    <div class="toolbar">
      <h1 class="page-title">Problems</h1>
      <el-input
        v-model="query"
        class="search-input"
        clearable
        placeholder="Search by title"
        @keyup.enter="loadProblems"
        @clear="loadProblems"
      >
        <template #append>
          <el-button @click="loadProblems">Search</el-button>
        </template>
      </el-input>
    </div>

    <section class="panel">
      <el-table v-loading="loading" :data="problems" empty-text="No problems yet">
        <el-table-column label="" width="60" align="center">
          <template #default="{ row }">
            <span v-if="row.is_solved" class="solved-mark" aria-label="Solved" title="Solved">&#10003;</span>
          </template>
        </el-table-column>
        <el-table-column prop="id" label="#" width="80" />
        <el-table-column prop="title" label="Title" min-width="240">
          <template #default="{ row }">
            <RouterLink class="problem-link" :to="`/problems/${row.id}`">{{ row.title }}</RouterLink>
          </template>
        </el-table-column>
        <el-table-column prop="time_limit_ms" label="Time" width="120">
          <template #default="{ row }">{{ row.time_limit_ms }} ms</template>
        </el-table-column>
        <el-table-column prop="memory_limit_mb" label="Memory" width="120">
          <template #default="{ row }">{{ row.memory_limit_mb }} MB</template>
        </el-table-column>
        <el-table-column prop="judge_mode" label="Mode" width="120" />
      </el-table>
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { fetchProblems, type Problem } from "../api/problems";
import { useUserStore } from "../stores/user";

const query = ref("");
const loading = ref(false);
const problems = ref<Problem[]>([]);
const user = useUserStore();

async function loadProblems() {
  loading.value = true;
  try {
    problems.value = await fetchProblems(query.value);
  } finally {
    loading.value = false;
  }
}

onMounted(loadProblems);

watch(
  () => user.isAuthenticated,
  () => {
    void loadProblems();
  }
);
</script>

<style scoped>
.search-input {
  max-width: 360px;
}

.problem-link {
  color: #0f766e;
  font-weight: 700;
}

.solved-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  color: #15803d;
  font-weight: 800;
  background: #e8f7ec;
}
</style>
