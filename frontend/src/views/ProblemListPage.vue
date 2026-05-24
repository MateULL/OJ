<template>
  <main class="page page-stack">
    <section class="page-card">
      <div class="page-card__body page-card__body--spacious">
        <div class="page-head">
          <div>
            <p class="page-kicker">题库</p>
            <h1 class="page-title">在线题库</h1>
            <p class="page-description">浏览题目、搜索标题，并从这里开始做题。</p>
          </div>
        </div>

        <div class="search-row">
          <el-input
            v-model="query"
            class="search-input"
            clearable
            placeholder="搜索题目标题"
            @keyup.enter="loadProblems"
            @clear="loadProblems"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="loadProblems">搜索题目</el-button>
        </div>

        <ProblemStatsBar :items="stats" />

        <div class="table-head">
          <div>
            <h2 class="section-title">题目列表</h2>
            <p class="section-description">点击标题即可进入做题页面。</p>
          </div>
        </div>

        <el-table v-loading="loading" class="oj-table problem-table" :data="problems" empty-text="暂无题目">
          <el-table-column label="" width="72" align="center">
            <template #default="{ row }">
              <span v-if="row.is_solved" class="solved-mark" aria-label="已通过" title="已通过">
                <el-icon><Check /></el-icon>
              </span>
            </template>
          </el-table-column>
          <el-table-column label="题号" width="96">
            <template #default="{ row }">
              {{ row.display_number ?? row.id }}
            </template>
          </el-table-column>
          <el-table-column prop="title" label="标题" min-width="300">
            <template #default="{ row }">
              <RouterLink class="oj-link title-link" :to="`/problems/${row.id}`">{{ row.title }}</RouterLink>
            </template>
          </el-table-column>
          <el-table-column label="判题模式" width="150">
            <template #default="{ row }">
              <ModeTag :mode="row.judge_mode" />
            </template>
          </el-table-column>
          <el-table-column label="时间限制" width="140">
            <template #default="{ row }">{{ row.time_limit_ms }} ms</template>
          </el-table-column>
          <el-table-column label="内存限制" width="140">
            <template #default="{ row }">{{ row.memory_limit_mb }} MB</template>
          </el-table-column>
        </el-table>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { Check, Search } from "@element-plus/icons-vue";
import { computed, onMounted, ref, watch } from "vue";
import { fetchProblems, type Problem } from "../api/problems";
import ModeTag from "../components/ModeTag.vue";
import ProblemStatsBar from "../components/ProblemStatsBar.vue";
import { useUserStore } from "../stores/user";

const query = ref("");
const loading = ref(false);
const problems = ref<Problem[]>([]);
const totalProblemCount = ref(0);
const user = useUserStore();
type ProblemStatItem = {
  label: string;
  value: string | number;
  hint?: string;
};

const solvedCount = computed(() => problems.value.filter((problem) => problem.is_solved).length);
const querySummary = computed(() => (query.value.trim() ? `关键字：${query.value.trim()}` : "全部题目"));

const stats = computed<ProblemStatItem[]>(() => [
  {
    label: "题目总数",
    value: totalProblemCount.value,
    hint: "可浏览的题目数量"
  },
  {
    label: "搜索结果",
    value: problems.value.length,
    hint: querySummary.value
  },
  {
    label: "已通过",
    value: user.isAuthenticated ? solvedCount.value : "--",
    hint: user.isAuthenticated ? "你已通过的题目数量" : "登录后查看通过题数"
  },
  {
    label: "判题模式",
    value: "标准",
    hint: "题目采用标准判题"
  }
]);

async function loadProblems() {
  loading.value = true;
  try {
    const trimmedQuery = query.value.trim();
    const [filteredProblems, fullProblemList] = await Promise.all([
      fetchProblems(trimmedQuery),
      trimmedQuery ? fetchProblems() : Promise.resolve<Problem[] | null>(null)
    ]);
    problems.value = filteredProblems;
    totalProblemCount.value = fullProblemList ? fullProblemList.length : filteredProblems.length;
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
.page-card__body--spacious {
  display: grid;
  gap: 26px;
}

.page-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.search-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  max-width: 520px;
}

.table-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
}

.problem-table {
  margin-top: -6px;
}

.title-link {
  font-size: 15px;
}

.solved-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: 1px solid #cdeed5;
  border-radius: 50%;
  background: #ecfdf3;
  color: #16a34a;
}

@media (max-width: 760px) {
  .search-row {
    flex-direction: column;
    align-items: stretch;
  }

  .search-input {
    max-width: none;
  }
}
</style>
