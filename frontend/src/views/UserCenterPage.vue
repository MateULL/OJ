<template>
  <main class="page">
    <h1 class="page-title">User Center</h1>
    <section class="panel">
      <div class="panel-body">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="User ID">{{ user.id ?? "-" }}</el-descriptions-item>
          <el-descriptions-item label="Username">{{ user.username || "Loading" }}</el-descriptions-item>
          <el-descriptions-item label="Mode">
            {{ user.isDemo ? "Demo user for first-stage local flow" : "Authenticated user" }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useUserStore } from "../stores/user";

const user = useUserStore();

onMounted(() => {
  user.loadMe();
});
</script>
