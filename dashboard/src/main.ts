import Vue from "vue";
import Vuex from "vuex";
import App from "./App.vue";
import router from "./router";
import * as Sentry from "@sentry/browser";
import { Vue as VueIntegration } from "@sentry/integrations";
import { APIValidator } from "./types/validation/Validator";
import { spiStore } from "./store/store";

// Auth0 configuration
import { domain, clientId, audience } from "../auth_config.json";
import { Auth0Plugin } from "./auth/auth";

import "./assets/css/styles.css";

Vue.use(Auth0Plugin, {
  domain,
  clientId,
  audience,
  onredirectCallback: (appState: { targetUrl: string }) => {
    router.push(
      appState && appState.targetUrl
        ? appState.targetUrl
        : window.location.pathname
    );
  }
});

if (process.env.NODE_ENV == "production") {
  Sentry.init({
    dsn:
      "https://624f863de69b4b1dabddc48e04329c5e@o481024.ingest.sentry.io/5528970",
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
}

Vue.config.productionTip = false;

/* Instantiate a validator object and make it globally available via the
 * this.$validator.
 */
const validator = new APIValidator();
validator.init();
Vue.prototype.$validator = validator;

Vue.use(Vuex);
const store = new Vuex.Store(spiStore);

new Vue({
  router,
  render: h => h(App),
  store
}).$mount("#app");
