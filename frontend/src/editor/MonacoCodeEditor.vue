<template>
  <div ref="containerRef" class="monaco-code-editor" />
</template>

<script setup lang="ts">
import "./monacoEnvironment";
import * as monaco from "monaco-editor";
import { onBeforeUnmount, onMounted, ref, watch } from "vue";

const props = withDefaults(
  defineProps<{
    modelValue: string;
    language?: string;
    height?: string;
    theme?: string;
  }>(),
  {
    language: "cpp",
    height: "520px",
    theme: "vs"
  }
);

const emit = defineEmits<{
  "update:modelValue": [value: string];
}>();

const containerRef = ref<HTMLElement | null>(null);
let editor: monaco.editor.IStandaloneCodeEditor | null = null;
let resizeObserver: ResizeObserver | null = null;

function blurEditorIfActive() {
  const container = containerRef.value;
  const activeElement = document.activeElement;
  if (container && activeElement instanceof HTMLElement && container.contains(activeElement)) {
    activeElement.blur();
  }
}

function layoutEditorIfVisible() {
  if (document.visibilityState === "visible") {
    editor?.layout();
  }
}

function handleVisibilityChange() {
  if (document.visibilityState === "hidden") {
    blurEditorIfActive();
    return;
  }
  editor?.layout();
}

onMounted(() => {
  if (!containerRef.value) {
    return;
  }

  editor = monaco.editor.create(containerRef.value, {
    value: props.modelValue,
    language: props.language,
    automaticLayout: false,
    minimap: { enabled: false },
    fontSize: 14,
    tabSize: 2,
    scrollBeyondLastLine: false,
    fixedOverflowWidgets: true,
    renderLineHighlight: "gutter",
    padding: { top: 16, bottom: 16 },
    theme: props.theme
  });

  editor.onDidChangeModelContent(() => {
    emit("update:modelValue", editor?.getValue() ?? "");
  });

  resizeObserver = new ResizeObserver(layoutEditorIfVisible);
  resizeObserver.observe(containerRef.value);
  window.addEventListener("blur", blurEditorIfActive);
  document.addEventListener("visibilitychange", handleVisibilityChange);
});

watch(
  () => props.modelValue,
  (value) => {
    if (editor && value !== editor.getValue()) {
      editor.setValue(value);
    }
  }
);

watch(
  () => props.language,
  (language) => {
    const model = editor?.getModel();
    if (model) {
      monaco.editor.setModelLanguage(model, language);
    }
  }
);

watch(
  () => props.theme,
  (theme) => {
    if (theme) {
      monaco.editor.setTheme(theme);
    }
  }
);

onBeforeUnmount(() => {
  resizeObserver?.disconnect();
  window.removeEventListener("blur", blurEditorIfActive);
  document.removeEventListener("visibilitychange", handleVisibilityChange);
  editor?.dispose();
});
</script>

<style scoped>
.monaco-code-editor {
  width: 100%;
  height: v-bind(height);
  min-height: 360px;
  border: 1px solid var(--oj-border);
  border-radius: 8px;
  overflow: hidden;
  background: #ffffff;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.45);
}
</style>
