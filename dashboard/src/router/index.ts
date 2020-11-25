import Vue from "vue";
import VueRouter, { RouteConfig } from "vue-router";
import Model from "../views/Model.vue";
import Systems from "../views/Systems.vue";
import Home from "../views/Home.vue";
import { authGuard } from "../auth/authGuard";

Vue.use(VueRouter);

const routes: Array<RouteConfig> = [
  {
    path: "/",
    name: "Home",
    component: Home
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
    component: Model,
    beforeEnter: authGuard
  },
  {
    path: "/system/:systemId",
    name: "Update System",
    component: Model,
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
