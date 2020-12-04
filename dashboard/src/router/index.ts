/* Primary router for the dashboard. Any routes that require authentication
 * should be registered with `beforeEnter: authGuard`.
 */
import Vue from "vue";
import { RouteConfig } from "vue-router";
import SystemSpec from "../views/SystemSpec.vue";
import Systems from "../views/Systems.vue";
import HomeContent from "../views/HomeContent.vue";
import { authGuard } from "../auth/authGuard";

const routes: Array<RouteConfig> = [
  {
    path: "/",
    name: "Home",
    component: HomeContent
  },
  {
    path: "/systems",
    name: "Systems",
    component: Systems,
    beforeEnter: authGuard
  },
  {
    path: "/system/new",
    name: "Model",
    component: SystemSpec,
    beforeEnter: authGuard
  },
  {
    path: "/system/:systemId",
    name: "Update System",
    component: SystemSpec,
    props: true,
    beforeEnter: authGuard
  }
];

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes
});

export default router;
