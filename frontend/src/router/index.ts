import { createRouter, createWebHistory } from "vue-router";
import { pinia } from "../stores/pinia";
import { useUserStore } from "../stores/user";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/problems" },
    {
      path: "/problems",
      name: "problems",
      component: () => import("../views/ProblemListPage.vue")
    },
    {
      path: "/problems/:id",
      name: "problem-detail",
      component: () => import("../views/ProblemDetailPage.vue")
    },
    {
      path: "/submissions",
      name: "submissions",
      component: () => import("../views/SubmissionListPage.vue"),
      meta: { requiresAuth: true }
    },
    {
      path: "/submissions/:id",
      name: "submission-detail",
      component: () => import("../views/SubmissionDetailPage.vue"),
      meta: { requiresAuth: true }
    },
    {
      path: "/login",
      name: "login",
      component: () => import("../views/LoginPage.vue"),
      meta: { guestOnly: true }
    },
    {
      path: "/register",
      name: "register",
      component: () => import("../views/RegisterPage.vue"),
      meta: { guestOnly: true }
    },
    {
      path: "/me",
      name: "user-center",
      component: () => import("../views/UserCenterPage.vue"),
      meta: { requiresAuth: true }
    }
  ]
});

router.beforeEach(async (to) => {
  const user = useUserStore(pinia);
  await user.ensureLoaded();

  if (to.meta.requiresAuth && !user.isAuthenticated) {
    return {
      name: "login",
      query: { redirect: to.fullPath }
    };
  }

  if (to.meta.guestOnly && user.isAuthenticated) {
    return { name: "user-center" };
  }

  return true;
});

export default router;
