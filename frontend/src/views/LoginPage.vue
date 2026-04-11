<template>
  <main class="page auth-page">
    <section class="panel auth-panel">
      <div class="panel-body">
        <div class="auth-head">
          <h1 class="page-title">Login</h1>
          <p class="muted">Sign in to submit, track AC history, and view your heatmap.</p>
        </div>

        <el-form label-position="top" @submit.prevent="submit">
          <el-form-item label="Username">
            <el-input v-model="form.username" autocomplete="username" />
          </el-form-item>
          <el-form-item label="Password">
            <el-input v-model="form.password" type="password" show-password autocomplete="current-password" />
          </el-form-item>
          <div class="auth-actions">
            <el-button type="primary" :loading="submitting" @click="submit">Login</el-button>
            <RouterLink class="muted" :to="{ name: 'register', query: route.query }">Create account</RouterLink>
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
  password: ""
});

async function submit() {
  submitting.value = true;
  try {
    await user.login(form);
    ElMessage.success("Logged in");
    await router.push(typeof route.query.redirect === "string" ? route.query.redirect : "/me");
  } catch (error: any) {
    const message = error?.response?.data?.non_field_errors?.[0] || error?.response?.data?.detail || "Login failed.";
    ElMessage.error(message);
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
  width: min(420px, 100%);
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
