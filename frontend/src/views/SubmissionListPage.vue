<template>
  <main class="page page-stack">
    <section class="page-card">
      <div class="page-card__body list-head">
        <div>
          <p class="page-kicker">提交记录</p>
          <h1 class="page-title">我的提交</h1>
          <p class="page-description">查看最近提交、判题结果与基础资源消耗。</p>
        </div>
        <el-button @click="loadSubmissions">刷新列表</el-button>
      </div>
    </section>

    <section class="page-card">
      <div class="page-card__body">
        <el-table v-loading="loading" class="oj-table" :data="submissions" empty-text="暂无提交记录">
          <el-table-column prop="id" label="编号" width="88" />
          <el-table-column prop="problem_title" label="题目" min-width="240" />
          <el-table-column prop="language" label="语言" width="120" />
          <el-table-column label="结果" width="130">
            <template #default="{ row }">
              <VerdictTag :verdict="row.final_verdict ?? row.status" />
            </template>
          </el-table-column>
          <el-table-column label="耗时" width="120">
            <template #default="{ row }">{{ row.total_time_ms }} ms</template>
          </el-table-column>
          <el-table-column label="提交时间" min-width="200">
            <template #default="{ row }">{{ formatDate(row.submitted_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <RouterLink class="oj-link" :to="`/submissions/${row.id}`">查看详情</RouterLink>
            </template>
          </el-table-column>
        </el-table>
      </div>
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

<style scoped>
.list-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

@media (max-width: 760px) {
  .list-head {
    flex-direction: column;
  }
}
</style>
