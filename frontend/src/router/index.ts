import { createRouter, createWebHistory } from "vue-router";

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
      component: () => import("../views/SubmissionListPage.vue")
    },
    {
      path: "/submissions/:id",
      name: "submission-detail",
      component: () => import("../views/SubmissionDetailPage.vue")
    },
    {
      path: "/me",
      name: "user-center",
      component: () => import("../views/UserCenterPage.vue")
    }
  ]
});

export default router;
