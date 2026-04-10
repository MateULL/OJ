<template>
  <el-container class="app-shell">
    <el-header class="app-header">
      <RouterLink class="brand" to="/problems">Minimal OJ</RouterLink>
      <nav class="nav-links">
        <RouterLink to="/problems">Problems</RouterLink>
        <RouterLink to="/submissions">
          <span class="wide-label">Submissions</span>
          <span class="narrow-label">Subs</span>
        </RouterLink>
        <RouterLink to="/me">Me</RouterLink>
      </nav>
    </el-header>
    <el-main class="app-main">
      <RouterView />
    </el-main>
  </el-container>
</template>

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
  gap: 18px;
  color: #59636f;
  font-size: 14px;
}

.narrow-label {
  display: none;
}

.nav-links a.router-link-active {
  color: #0f766e;
  font-weight: 700;
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
