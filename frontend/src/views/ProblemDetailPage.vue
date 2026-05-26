<template>
  <main class="page page-stack problem-page">
    <el-skeleton v-if="loading" :rows="10" animated />

    <template v-else-if="problem">
      <header class="problem-page-head">
        <RouterLink class="page-link-back" to="/problems">← 返回题库</RouterLink>
        <div>
          <p class="page-kicker">做题</p>
          <h1 class="page-title">阅读题面、编写代码并提交判题</h1>
          <p class="page-description">阅读题目、编写代码，并在下方查看提交结果。</p>
        </div>
      </header>

      <div ref="layoutRef" class="problem-layout" :style="layoutStyle">
        <section class="page-card statement-card">
          <div class="page-card__body">
            <ProblemStatement :problem="problem" />
          </div>
        </section>

        <button
          v-if="isDesktopLayout"
          type="button"
          class="pane-resizer"
          :class="{ 'pane-resizer--active': isResizing }"
          aria-label="调整题面和代码区宽度"
          @pointerdown="startResize"
        >
          <span class="pane-resizer__handle" />
        </button>

        <section class="page-card workspace-card">
          <div class="page-card__body workspace-card__body">
            <header class="workspace-head">
              <div>
                <p class="page-kicker">代码</p>
                <h2 class="section-title">在线提交</h2>
                <p class="section-description">在这里编写代码并提交。</p>
              </div>
              <span class="workspace-draft">{{ draftStatusText }}</span>
            </header>

            <div class="editor-toolbar">
              <div class="toolbar-field">
                <span class="toolbar-label">语言</span>
                <el-select v-model="language" class="language-select" aria-label="选择语言">
                  <el-option label="C++17" value="cpp17" />
                </el-select>
              </div>

              <div class="editor-toolbar__actions">
                <el-button text @click="resetCode">恢复模板</el-button>
              </div>
            </div>

            <div class="editor-stage">
              <MonacoCodeEditor v-model="sourceCode" language="cpp" theme="vs-dark" height="620px" />
            </div>

            <div class="submit-bar">
              <div>
                <h3 class="submit-bar__title">提交代码</h3>
                <p class="submit-bar__description muted">
                  {{ user.isAuthenticated ? "判题结果将在下方显示。" : "登录后即可提交代码。" }}
                </p>
              </div>

              <el-button type="primary" size="large" :loading="submitting" @click="handlePrimaryAction">
                {{ user.isAuthenticated ? "提交代码" : "登录后提交" }}
              </el-button>
            </div>

            <JudgeStatusPanel :submission="currentSubmission" />

            <p v-if="!user.isAuthenticated" class="login-hint muted">
              登录后即可提交代码并查看结果。
            </p>
          </div>
        </section>
      </div>
    </template>

    <el-empty v-else description="题目不存在" />
  </main>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { fetchProblem, type Problem } from "../api/problems";
import { createSubmission, fetchSubmission, type Submission } from "../api/submissions";
import JudgeStatusPanel from "../components/JudgeStatusPanel.vue";
import ProblemStatement from "../components/ProblemStatement.vue";
import MonacoCodeEditor from "../editor/MonacoCodeEditor.vue";
import { useUserStore } from "../stores/user";

const DEFAULT_SOURCE_CODE = `#include <bits/stdc++.h>
using namespace std;

int main() {
  long long a, b;
  cin >> a >> b;
  cout << a + b << '\\n';
  return 0;
}
`;

const DEFAULT_SPLIT_RATIO = 0.56;
const MIN_STATEMENT_WIDTH = 340;
const MIN_WORKSPACE_WIDTH = 460;
const RESIZER_WIDTH = 18;
const DESKTOP_MEDIA_QUERY = "(min-width: 1041px)";
const SPLIT_STORAGE_KEY = "oj:problem-layout-split";

const route = useRoute();
const router = useRouter();
const user = useUserStore();

const problem = ref<Problem | null>(null);
const currentSubmission = ref<Submission | null>(null);
const loading = ref(false);
const submitting = ref(false);
const language = ref("cpp17");
const sourceCode = ref(DEFAULT_SOURCE_CODE);
const layoutRef = ref<HTMLElement | null>(null);
const splitRatio = ref(DEFAULT_SPLIT_RATIO);
const layoutWidth = ref(0);
const isDesktopLayout = ref(false);
const isResizing = ref(false);

const problemId = computed(() => Number(route.params.id));
const draftStatusText = computed(() => "本地草稿");

let pollTimer: number | undefined;
let layoutObserver: ResizeObserver | null = null;
let mediaQueryList: MediaQueryList | null = null;
let mediaQueryListener: ((event: MediaQueryListEvent) => void) | null = null;
let dragCleanup: (() => void) | null = null;

const layoutStyle = computed(() => {
  if (!isDesktopLayout.value || !layoutWidth.value) {
    return undefined;
  }

  // 桌面端使用可拖拽的左右两栏布局，左侧题面、右侧代码区。
  const leftWidth = Math.round(layoutWidth.value * clampSplitRatio(splitRatio.value, layoutWidth.value));
  return {
    gridTemplateColumns: `${leftWidth}px ${RESIZER_WIDTH}px minmax(${MIN_WORKSPACE_WIDTH}px, 1fr)`
  };
});

function readStoredSplitRatio() {
  if (typeof window === "undefined") {
    return null;
  }

  const storedValue = Number(window.localStorage.getItem(SPLIT_STORAGE_KEY));
  if (!Number.isFinite(storedValue) || storedValue <= 0 || storedValue >= 1) {
    return null;
  }
  return storedValue;
}

function persistSplitRatio() {
  if (typeof window === "undefined" || !isDesktopLayout.value) {
    return;
  }
  window.localStorage.setItem(SPLIT_STORAGE_KEY, String(splitRatio.value));
}

function clampSplitRatio(nextRatio: number, totalWidth = layoutWidth.value) {
  if (!totalWidth) {
    return DEFAULT_SPLIT_RATIO;
  }

  // 限制分割比例，避免用户拖动后题面或编辑器区域被压得过窄。
  const minRatio = MIN_STATEMENT_WIDTH / totalWidth;
  const maxRatio = (totalWidth - MIN_WORKSPACE_WIDTH - RESIZER_WIDTH) / totalWidth;

  if (maxRatio <= minRatio) {
    return Math.max(0.5, minRatio);
  }

  return Math.min(Math.max(nextRatio, minRatio), maxRatio);
}

function updateLayoutWidth() {
  layoutWidth.value = layoutRef.value?.clientWidth ?? 0;
  if (isDesktopLayout.value && layoutWidth.value) {
    splitRatio.value = clampSplitRatio(splitRatio.value, layoutWidth.value);
  }
}

function setupLayoutObserver() {
  layoutObserver?.disconnect();
  layoutObserver = null;

  if (!layoutRef.value) {
    return;
  }

  layoutObserver = new ResizeObserver(updateLayoutWidth);
  layoutObserver.observe(layoutRef.value);
  updateLayoutWidth();
}

function applyDesktopMode(matches: boolean) {
  isDesktopLayout.value = matches;
  if (!matches) {
    stopResize();
    return;
  }

  splitRatio.value = readStoredSplitRatio() ?? splitRatio.value;
  updateLayoutWidth();
}

function startResize(event: PointerEvent) {
  if (event.button !== 0 || !isDesktopLayout.value || !layoutRef.value) {
    return;
  }

  event.preventDefault();
  const resizer = event.currentTarget instanceof HTMLElement ? event.currentTarget : null;
  resizer?.setPointerCapture(event.pointerId);
  const rect = layoutRef.value.getBoundingClientRect();
  const totalWidth = rect.width;
  if (!totalWidth) {
    return;
  }

  stopResize();
  isResizing.value = true;
  document.body.classList.add("is-resizing-problem-layout");

  // 拖拽时只更新布局比例；Monaco 编辑器自身会在组件内监听尺寸变化并重排。
  const onPointerMove = (moveEvent: PointerEvent) => {
    const nextLeft = moveEvent.clientX - rect.left;
    splitRatio.value = clampSplitRatio(nextLeft / totalWidth, totalWidth);
  };

  const finishResize = () => {
    persistSplitRatio();
    stopResize();
  };

  window.addEventListener("pointermove", onPointerMove);
  window.addEventListener("pointerup", finishResize);
  window.addEventListener("pointercancel", finishResize);

  dragCleanup = () => {
    window.removeEventListener("pointermove", onPointerMove);
    window.removeEventListener("pointerup", finishResize);
    window.removeEventListener("pointercancel", finishResize);
    if (resizer?.hasPointerCapture(event.pointerId)) {
      resizer.releasePointerCapture(event.pointerId);
    }
    document.body.classList.remove("is-resizing-problem-layout");
    isResizing.value = false;
    dragCleanup = null;
  };
}

function stopResize() {
  dragCleanup?.();
}

async function loadProblem() {
  loading.value = true;
  try {
    problem.value = await fetchProblem(problemId.value);
  } finally {
    loading.value = false;
  }
}

function getDraftKey(problemValue: number, selectedLanguage: string) {
  // 草稿按“题目 + 语言”区分，切换题目时不会覆盖其他题的代码。
  return `oj:draft:${problemValue}:${selectedLanguage}`;
}

function restoreDraft() {
  if (typeof window === "undefined" || !Number.isFinite(problemId.value)) {
    sourceCode.value = DEFAULT_SOURCE_CODE;
    return;
  }

  const saved = window.localStorage.getItem(getDraftKey(problemId.value, language.value));
  sourceCode.value = saved || DEFAULT_SOURCE_CODE;
}

function resetCode() {
  sourceCode.value = DEFAULT_SOURCE_CODE;
  ElMessage.success("已恢复默认代码。");
}

async function handlePrimaryAction() {
  if (!user.isAuthenticated) {
    await router.push({
      name: "login",
      query: { redirect: route.fullPath }
    });
    return;
  }

  await submitCode();
}

async function submitCode() {
  if (!problem.value) {
    return;
  }
  submitting.value = true;
  try {
    // 前端只创建提交记录；真正的编译运行由后端 worker 异步完成。
    currentSubmission.value = await createSubmission({
      problem: problem.value.id,
      language: language.value,
      source_code: sourceCode.value
    });
    ElMessage.success("已提交，正在判题。");
    startPolling(currentSubmission.value.id);
  } catch (error: any) {
    const detail = error?.response?.data?.detail;
    if (detail === "Authentication credentials were not provided.") {
      ElMessage.error("请先登录后再提交。");
      await router.push({ name: "login", query: { redirect: route.fullPath } });
      return;
    }
    ElMessage.error(detail || "提交失败，请稍后重试。");
  } finally {
    submitting.value = false;
  }
}

function startPolling(submissionId: number) {
  stopPolling();
  // 轮询当前提交状态，worker 判完后状态会变为 FINISHED。
  pollTimer = window.setInterval(async () => {
    try {
      currentSubmission.value = await fetchSubmission(submissionId);
      if (currentSubmission.value.status === "FINISHED") {
        stopPolling();
      }
    } catch {
      stopPolling();
      ElMessage.error("获取判题结果失败，请稍后重试。");
    }
  }, 1500);
}

function stopPolling() {
  if (pollTimer !== undefined) {
    window.clearInterval(pollTimer);
    pollTimer = undefined;
  }
}

watch(
  problemId,
  async () => {
    stopPolling();
    stopResize();
    currentSubmission.value = null;
    await loadProblem();
    await nextTick();
    setupLayoutObserver();
    restoreDraft();
  },
  { immediate: true }
);

watch(language, () => {
  restoreDraft();
});

watch(sourceCode, (value) => {
  if (typeof window === "undefined" || !Number.isFinite(problemId.value)) {
    return;
  }
  window.localStorage.setItem(getDraftKey(problemId.value, language.value), value);
});

onMounted(() => {
  splitRatio.value = readStoredSplitRatio() ?? DEFAULT_SPLIT_RATIO;
  mediaQueryList = window.matchMedia(DESKTOP_MEDIA_QUERY);
  applyDesktopMode(mediaQueryList.matches);
  mediaQueryListener = (event) => applyDesktopMode(event.matches);
  mediaQueryList.addEventListener("change", mediaQueryListener);
  setupLayoutObserver();
});

onBeforeUnmount(() => {
  stopPolling();
  stopResize();
  layoutObserver?.disconnect();
  if (mediaQueryList && mediaQueryListener) {
    mediaQueryList.removeEventListener("change", mediaQueryListener);
  }
});
</script>

<style scoped>
.problem-page {
  gap: 18px;
}

.problem-page-head {
  display: grid;
  gap: 14px;
}

.problem-layout {
  display: grid;
  grid-template-columns: minmax(340px, 0.95fr) 18px minmax(460px, 1.15fr);
  align-items: stretch;
}

.statement-card,
.workspace-card {
  min-width: 0;
  height: 100%;
  overflow: hidden;
}

.statement-card,
.workspace-card,
.pane-resizer {
  align-self: stretch;
}

.statement-card > .page-card__body,
.workspace-card__body {
  height: 100%;
}

.workspace-card__body {
  display: grid;
  gap: 20px;
}

.statement-card > .page-card__body > *,
.workspace-card__body > * {
  min-width: 0;
  max-width: 100%;
}

.workspace-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  min-width: 0;
}

.workspace-draft {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 12px;
  border: 1px solid var(--oj-border);
  border-radius: 999px;
  background: var(--oj-surface-soft);
  color: var(--oj-text-soft);
  font-size: 13px;
  font-weight: 600;
  max-width: 100%;
  white-space: normal;
}

.editor-toolbar {
  display: flex;
  align-items: end;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  min-width: 0;
}

.toolbar-field {
  display: grid;
  gap: 8px;
  min-width: 0;
}

.toolbar-label {
  color: var(--oj-muted);
  font-size: 13px;
  font-weight: 600;
}

.language-select {
  width: 180px;
}

.editor-toolbar__actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
  min-width: 0;
}

.editor-stage {
  padding: 10px;
  border: 1px solid var(--oj-code-border);
  border-radius: 8px;
  background: linear-gradient(180deg, var(--oj-code-surface-soft) 0%, var(--oj-code-surface) 100%);
  min-width: 0;
  overflow: hidden;
}

.submit-bar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  padding: 18px 20px;
  border: 1px solid var(--oj-border);
  border-radius: 8px;
  background: var(--oj-surface-soft);
  min-width: 0;
}

.workspace-head > div,
.submit-bar > div {
  flex: 1 1 240px;
  min-width: 0;
}

.submit-bar__title {
  margin: 0;
  color: var(--oj-text);
  font-size: 18px;
  line-height: 1.3;
}

.submit-bar__description {
  margin: 8px 0 0;
  font-size: 14px;
}

.login-hint {
  margin: -4px 0 0;
  font-size: 14px;
  min-width: 0;
}

.submit-bar :deep(.el-button) {
  flex-shrink: 0;
}

.pane-resizer {
  position: relative;
  border: 0;
  background: transparent;
  cursor: col-resize;
  padding: 0;
  touch-action: none;
  min-height: 100%;
  z-index: 2;
}

.pane-resizer::before {
  content: "";
  position: absolute;
  top: 18px;
  bottom: 18px;
  left: 50%;
  width: 1px;
  transform: translateX(-50%);
  background: #d1d5db;
  transition: background-color 0.18s ease;
}

.pane-resizer__handle {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 10px;
  height: 58px;
  transform: translate(-50%, -50%);
  border: 1px solid #dbe2ea;
  border-radius: 999px;
  background: #ffffff;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
}

.pane-resizer__handle::before {
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  width: 2px;
  height: 26px;
  transform: translate(-50%, -50%);
  border-radius: 999px;
  background: #cbd5e1;
  box-shadow: -3px 0 0 #cbd5e1, 3px 0 0 #cbd5e1;
}

.pane-resizer:hover::before,
.pane-resizer--active::before {
  background: #60a5fa;
}

.pane-resizer:hover .pane-resizer__handle,
.pane-resizer--active .pane-resizer__handle {
  border-color: #bfdbfe;
  background: #eff6ff;
}

@media (max-width: 1040px) {
  .problem-layout {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}

@media (max-width: 760px) {
  .workspace-head,
  .editor-toolbar,
  .submit-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .language-select {
    width: 100%;
  }

  .editor-toolbar__actions {
    justify-content: space-between;
  }
}

:global(body.is-resizing-problem-layout) {
  cursor: col-resize;
  user-select: none;
}
</style>
