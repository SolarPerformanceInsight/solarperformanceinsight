import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import * as Sentry from "@sentry/browser";
import { Vue as VueIntegration } from "@sentry/integrations";

Vue.config.productionTip = false;

Sentry.init({
  dsn: process.env.VUE_APP_SENTRY_DSN,
  integrations: [new VueIntegration({ Vue })],
  // eslint-disable-next-line no-unused-vars
  beforeSend(event, hint) {
    // Check if it is an exception, and if so, show the report dialog
    if (event.exception) {
      Sentry.showReportDialog({ eventId: event.event_id });
    }
    return event;
  }
});

new Vue({
  router,
  render: h => h(App)
}).$mount("#app");
