<template>
  <main class="page auth-page">
    <section class="page-card auth-panel">
      <div class="page-card__body">
        <div class="auth-head">
          <p class="page-kicker">账号登录</p>
          <h1 class="page-title">登录系统</h1>
          <p class="page-description">登录后可以提交代码、查看已通过标识和 AC 打卡热力图。</p>
        </div>

        <el-form label-position="top" @submit.prevent="submit">
          <el-form-item label="用户名">
            <el-input v-model="form.username" autocomplete="username" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.password" type="password" show-password autocomplete="current-password" />
          </el-form-item>
          <div class="auth-actions">
            <el-button type="primary" :loading="submitting" @click="submit">登录</el-button>
            <RouterLink class="oj-link" :to="{ name: 'register', query: route.query }">没有账号？去注册</RouterLink>
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
    ElMessage.success("登录成功");
    await router.push(typeof route.query.redirect === "string" ? route.query.redirect : "/me");
  } catch (error: any) {
    const message = error?.response?.data?.non_field_errors?.[0] || error?.response?.data?.detail || "登录失败。";
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
  width: min(520px, 100%);
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
