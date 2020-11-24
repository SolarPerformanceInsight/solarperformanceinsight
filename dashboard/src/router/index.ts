import Vue from "vue";
import VueRouter, { RouteConfig } from "vue-router";
import Model from "../views/Model.vue";
import Home from "../views/Home.vue";


Vue.use(VueRouter);

const routes: Array<RouteConfig> = [
  {
    path: "/",
    name: "Systems",
    component: Home
  },
  {
    path: "/system",
    name: "Model",
    component: Model
  },
  {
    path: "/system/:systemId",
    name: "Update System",
    component: Model,
    props: true
  },
];

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes
});

export default router;
