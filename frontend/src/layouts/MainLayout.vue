<template>
  <el-container class="app-shell">
    <el-header class="app-header">
      <div class="app-header__inner">
        <RouterLink class="brand" to="/problems">OJ 判题系统</RouterLink>

        <nav class="nav-links" aria-label="主导航">
          <RouterLink to="/problems">题库</RouterLink>
          <RouterLink v-if="user.isAuthenticated" to="/submissions">提交记录</RouterLink>
          <RouterLink v-if="user.isAuthenticated" to="/me">个人中心</RouterLink>
          <RouterLink v-if="!user.isAuthenticated" to="/login">登录</RouterLink>
          <RouterLink v-if="!user.isAuthenticated" to="/register">注册</RouterLink>
        </nav>

        <div class="header-actions">
          <span v-if="user.isAuthenticated" class="user-chip">{{ user.username }}</span>
          <button v-if="user.isAuthenticated" class="logout-button" type="button" @click="handleLogout">退出</button>
        </div>
      </div>
    </el-header>

    <el-main class="app-main">
      <RouterView />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { useRouter } from "vue-router";
import { useUserStore } from "../stores/user";

const router = useRouter();
const user = useUserStore();

async function handleLogout() {
  try {
    await user.logout();
    ElMessage.success("已退出登录");
    await router.push("/problems");
  } catch {
    ElMessage.error("退出失败，请稍后重试。");
  }
}
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
}

.app-header {
  padding: 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  background: var(--oj-nav);
}

.app-header__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  width: min(1180px, calc(100% - 32px));
  min-height: 64px;
  margin: 0 auto;
}

.brand {
  color: #f8fafc;
  font-size: 20px;
  font-weight: 700;
  white-space: nowrap;
}

.nav-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.nav-links a,
.logout-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 38px;
  padding: 0 14px;
  border-radius: 8px;
  color: #d1d5db;
  font-size: 14px;
  font-weight: 600;
  transition: background-color 0.18s ease, color 0.18s ease;
}

.nav-links a:hover,
.logout-button:hover {
  background: var(--oj-nav-hover);
  color: #ffffff;
}

.nav-links a.router-link-active {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.header-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  min-width: 0;
}

.user-chip {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0 12px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  color: #e5e7eb;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}

.logout-button {
  border: 0;
  background: transparent;
  cursor: pointer;
}

.app-main {
  padding: 0;
  background: var(--oj-bg);
}

@media (max-width: 760px) {
  .app-header__inner {
    flex-wrap: wrap;
    width: min(100% - 20px, 1180px);
    padding: 12px 0;
  }

  .brand {
    font-size: 18px;
  }

  .nav-links {
    order: 3;
    justify-content: flex-start;
    width: 100%;
    flex-wrap: wrap;
  }

  .header-actions {
    margin-left: auto;
  }
}
</style>
