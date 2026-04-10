<template>
  <main class="page">
    <el-skeleton v-if="loading" :rows="8" animated />
    <div v-else-if="problem" class="problem-layout">
      <section class="panel panel-body statement-panel">
        <ProblemStatement :problem="problem" />
      </section>

      <section class="solve-panel">
        <div class="editor-toolbar">
          <el-select v-model="language" class="language-select" aria-label="Language">
            <el-option label="C++17" value="cpp17" />
          </el-select>
          <el-button type="primary" :loading="submitting" @click="submitCode">Submit</el-button>
        </div>

        <JudgeStatusPanel :submission="currentSubmission" />
        <MonacoCodeEditor v-model="sourceCode" language="cpp" height="520px" />
      </section>
    </div>
    <el-empty v-else description="Problem not found" />
  </main>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { onBeforeUnmount, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { fetchProblem, type Problem } from "../api/problems";
import { createSubmission, fetchSubmission, type Submission } from "../api/submissions";
import JudgeStatusPanel from "../components/JudgeStatusPanel.vue";
import ProblemStatement from "../components/ProblemStatement.vue";
import MonacoCodeEditor from "../editor/MonacoCodeEditor.vue";

const route = useRoute();
const problem = ref<Problem | null>(null);
const currentSubmission = ref<Submission | null>(null);
const loading = ref(false);
const submitting = ref(false);
const language = ref("cpp17");
const sourceCode = ref(`#include <bits/stdc++.h>
using namespace std;

int main() {
  long long a, b;
  cin >> a >> b;
  cout << a + b << '\\n';
  return 0;
}
`);

let pollTimer: number | undefined;

async function loadProblem() {
  loading.value = true;
  try {
    problem.value = await fetchProblem(Number(route.params.id));
  } finally {
    loading.value = false;
  }
}

async function submitCode() {
  if (!problem.value) {
    return;
  }
  submitting.value = true;
  try {
    currentSubmission.value = await createSubmission({
      problem: problem.value.id,
      language: language.value,
      source_code: sourceCode.value
    });
    ElMessage.success("Submission queued");
    startPolling(currentSubmission.value.id);
  } catch {
    ElMessage.error("Submit failed. Please check CSRF/session or backend logs.");
  } finally {
    submitting.value = false;
  }
}

function startPolling(submissionId: number) {
  stopPolling();
  pollTimer = window.setInterval(async () => {
    try {
      currentSubmission.value = await fetchSubmission(submissionId);
      if (currentSubmission.value.status === "FINISHED") {
        stopPolling();
      }
    } catch {
      stopPolling();
      ElMessage.error("Failed to refresh judge status.");
    }
  }, 1500);
}

function stopPolling() {
  if (pollTimer !== undefined) {
    window.clearInterval(pollTimer);
    pollTimer = undefined;
  }
}

onMounted(loadProblem);
onBeforeUnmount(stopPolling);
</script>

<style scoped>
.problem-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(420px, 1fr);
  gap: 18px;
  align-items: start;
}

.statement-panel {
  min-height: 680px;
}

.solve-panel {
  min-width: 0;
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.language-select {
  width: 160px;
}

@media (max-width: 980px) {
  .problem-layout {
    grid-template-columns: 1fr;
  }

  .statement-panel {
    min-height: auto;
  }
}

@media (max-width: 760px) {
  .editor-toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .language-select {
    width: 100%;
  }
}
</style>
