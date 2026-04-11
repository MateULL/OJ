<template>
  <el-container class="app-shell">
    <el-header class="app-header">
      <RouterLink class="brand" to="/problems">Minimal OJ</RouterLink>
      <nav class="nav-links">
        <RouterLink to="/problems">Problems</RouterLink>
        <RouterLink v-if="user.isAuthenticated" to="/submissions">
          <span class="wide-label">Submissions</span>
          <span class="narrow-label">Subs</span>
        </RouterLink>
        <RouterLink v-if="user.isAuthenticated" to="/me">Me</RouterLink>
        <RouterLink v-if="!user.isAuthenticated" to="/login">Login</RouterLink>
        <RouterLink v-if="!user.isAuthenticated" to="/register">Register</RouterLink>
        <button v-if="user.isAuthenticated" class="logout-button" type="button" @click="handleLogout">Logout</button>
      </nav>
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
    ElMessage.success("Logged out");
    await router.push("/problems");
  } catch {
    ElMessage.error("Logout failed.");
  }
}
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 58px;
  border-bottom: 1px solid #d9dee7;
  background: #ffffff;
}

.brand {
  font-size: 18px;
  font-weight: 700;
  color: #0f766e;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 18px;
  color: #59636f;
  font-size: 14px;
}

.logout-button {
  padding: 0;
  border: 0;
  background: transparent;
  color: inherit;
  font: inherit;
  cursor: pointer;
}

.logout-button:hover,
.nav-links a.router-link-active {
  color: #0f766e;
  font-weight: 700;
}

.narrow-label {
  display: none;
}

.app-main {
  padding: 0;
}

@media (max-width: 520px) {
  .app-header {
    align-items: flex-start;
    flex-direction: column;
    justify-content: center;
    gap: 8px;
    height: auto;
    min-height: 76px;
    padding: 10px 12px;
  }

  .brand {
    font-size: 16px;
  }

  .nav-links {
    flex-wrap: wrap;
    justify-content: flex-start;
    width: 100%;
    gap: 14px;
    font-size: 12px;
  }

  .wide-label {
    display: none;
  }

  .narrow-label {
    display: inline;
  }
}
</style>
