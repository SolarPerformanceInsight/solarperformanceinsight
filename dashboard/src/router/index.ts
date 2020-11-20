import Vue from "vue";
import VueRouter, { RouteConfig } from "vue-router";
import Model from "../views/Model.vue";
import InverterView from "../components/Inverter.vue";

Vue.use(VueRouter);

const routes: Array<RouteConfig> = [
  {
    path: "/",
    name: "Model",
    component: Model
  }
];

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes
});

export default router;
