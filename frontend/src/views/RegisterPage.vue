<template>
  <main class="page auth-page">
    <section class="panel auth-panel">
      <div class="panel-body">
        <div class="auth-head">
          <h1 class="page-title">Register</h1>
          <p class="muted">Create a local account for submissions, solved marks, and AC check-ins.</p>
        </div>

        <el-form label-position="top" @submit.prevent="submit">
          <el-form-item label="Username">
            <el-input v-model="form.username" autocomplete="username" />
          </el-form-item>
          <el-form-item label="Password">
            <el-input v-model="form.password" type="password" show-password autocomplete="new-password" />
          </el-form-item>
          <el-form-item label="Confirm Password">
            <el-input
              v-model="form.confirm_password"
              type="password"
              show-password
              autocomplete="new-password"
            />
          </el-form-item>
          <div class="auth-actions">
            <el-button type="primary" :loading="submitting" @click="submit">Create account</el-button>
            <RouterLink class="muted" :to="{ name: 'login', query: route.query }">Back to login</RouterLink>
          </div>
        </el-form>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useUserStore } from "../stores/user";

const route = useRoute();
const router = useRouter();
const user = useUserStore();
const submitting = ref(false);
const form = reactive({
  username: "",
  password: "",
  confirm_password: ""
});

function flattenError(value: unknown): string {
  if (Array.isArray(value)) {
    return value[0] ?? "Register failed.";
  }
  if (typeof value === "string") {
    return value;
  }
  if (value && typeof value === "object") {
    const firstValue = Object.values(value as Record<string, unknown>)[0];
    return flattenError(firstValue);
  }
  return "Register failed.";
}

async function submit() {
  submitting.value = true;
  try {
    await user.register(form);
    ElMessage.success("Account created");
    await router.push(typeof route.query.redirect === "string" ? route.query.redirect : "/me");
  } catch (error: any) {
    ElMessage.error(flattenError(error?.response?.data));
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
}

.auth-panel {
  width: min(460px, 100%);
}

.auth-head {
  margin-bottom: 18px;
}

.auth-head p {
  margin: 0;
}

.auth-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
</style>
