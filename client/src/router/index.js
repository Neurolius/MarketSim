import { createRouter, createWebHistory } from "vue-router";
import LoginPage from "../views/LoginPage.vue";
import DashboardPage from "../views/DashboardPage.vue";
import PortfoliosListPage from "../views/PortfoliosListPage.vue";
import InstrumentsListPage from "../views/InstrumentsListPage.vue";
import ProfilePage from "../views/ProfilePage.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "login",
      component: LoginPage,
    },
    {
      path: "/dashboard",
      name: "dashboard",
      component: DashboardPage,
    },
    {
      path: "/portfolios",
      name: "portfolios",
      component: PortfoliosListPage,
    },
    {
      path: "/instruments",
      name: "instruments",
      component: InstrumentsListPage,
    },
    {
      path: "/profile",
      name: "profile",
      component: ProfilePage,
    },
  ],
});

export default router;
