<template>
  <main class="page auth-page">
    <section class="page-card auth-panel">
      <div class="page-card__body">
        <div class="auth-head">
          <p class="page-kicker">账号注册</p>
          <h1 class="page-title">创建新账号</h1>
          <p class="page-description">注册成功后会自动登录，随后即可进入题库并开始提交代码。</p>
        </div>

        <el-form label-position="top" @submit.prevent="submit">
          <el-form-item label="用户名">
            <el-input v-model="form.username" autocomplete="username" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.password" type="password" show-password autocomplete="new-password" />
          </el-form-item>
          <el-form-item label="确认密码">
            <el-input
              v-model="form.confirm_password"
              type="password"
              show-password
              autocomplete="new-password"
            />
          </el-form-item>
          <div class="auth-actions">
            <el-button type="primary" :loading="submitting" @click="submit">创建账号</el-button>
            <RouterLink class="oj-link" :to="{ name: 'login', query: route.query }">已有账号？去登录</RouterLink>
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
    return value[0] ?? "注册失败。";
  }
  if (typeof value === "string") {
    return value;
  }
  if (value && typeof value === "object") {
    const firstValue = Object.values(value as Record<string, unknown>)[0];
    return flattenError(firstValue);
  }
  return "注册失败。";
}

async function submit() {
  submitting.value = true;
  try {
    await user.register(form);
    ElMessage.success("账号创建成功");
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
  width: min(560px, 100%);
}

.auth-head {
  margin-bottom: 20px;
}

.auth-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

@media (max-width: 760px) {
  .auth-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
