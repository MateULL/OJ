<template>
  <MainLayout />
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import MainLayout from "./layouts/MainLayout.vue";
import { ensureCsrfCookie } from "./api/auth";
import { useUserStore } from "./stores/user";

const user = useUserStore();

onMounted(async () => {
  await ensureCsrfCookie();
  await user.ensureLoaded();
});
</script>
