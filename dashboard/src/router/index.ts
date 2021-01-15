/* Primary router for the dashboard. Any routes that require authentication
 * should be registered with `beforeEnter: authGuard`.
 */
import Vue from "vue";
import VueRouter, { RouteConfig } from "vue-router";
import SystemSpec from "../views/SystemSpec.vue";
import Systems from "../views/Systems.vue";
import HomeContent from "../views/HomeContent.vue";
import JobHandler from "../components/jobs/JobHandler.vue";
import ComparePerformance from "../views/Compare.vue";
import CalculatePR from "../views/CalculatePR.vue";
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
  },
  {
    path: "/system/:systemId/calculate",
    name: "Calculate Performance",
    component: JobHandler,
    props: r => ({
      systemId: r.params.systemId,
      typeOfJob: "calculate"
    }),
    beforeEnter: authGuard
  },
  {
    path: "/system/:systemId/compare",
    name: "Compare Performance",
    component: JobHandler,
    props: r => ({
      systemId: r.params.systemId,
      typeOfJob: "compare"
    }),
    beforeEnter: authGuard
  },
  {
    path: "/system/:systemId/calculatepr",
    name: "Calculate Performance Ratio",
    component: JobHandler,
    props: r => ({
      systemId: r.params.systemId,
      typeOfJob: "calculatepr"
    }),
    beforeEnter: authGuard
  },
  {
    path: "/jobs/:jobId",
    name: "Job View",
    component: JobHandler,
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
