import Vue from "vue";
import VueRouter from "vue-router";
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

// Import all components for global registration
import ArrayView from "@/components/model/Array.vue";
import ArraysView from "@/components/model/Arrays.vue";
import DBBrowser from "@/components/Browser.vue";
import FileUpload from "@/components/FileUpload.vue";
import HelpPopup from "@/components/Help.vue";
import Home from "@/views/Home.vue";
import InverterView from "@/components/model/Inverter.vue";
import InvertersView from "@/components/model/Inverters.vue";
import InverterParametersView from "@/components/model/InverterParameters.vue";
import LossParametersView from "@/components/model/LossParameters.vue";
import ModelField from "@/components/ModelField.vue";
import ModuleParametersView from "@/components/model/ModuleParameters.vue";
import TemperatureParametersView from "@/components/model/TemperatureParameters.vue";
import TrackingParametersView from "@/components/model/TrackingParameters.vue";
import SystemView from "@/components/model/System.vue";
import WeatherUpload from "@/components/jobs/WeatherUpload.vue";
import WeatherCSVMapper from "@/components/jobs/WeatherCSVMapper.vue";

import "./assets/css/styles.css";

Vue.use(VueRouter);

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

// Register components globally.
Vue.component("array-view", ArrayView);
Vue.component("arrays-view", ArraysView);
Vue.component("db-browser", DBBrowser);
Vue.component("file-upload", FileUpload);
Vue.component("help", HelpPopup);
Vue.component("home", Home);
Vue.component("inverter-view", InverterView);
Vue.component("inverters-view", InvertersView);
Vue.component("inverter-parameters", InverterParametersView);
Vue.component("loss-parameters", LossParametersView);
Vue.component("model-field", ModelField);
Vue.component("module-parameters", ModuleParametersView);
Vue.component("tracking-parameters", TrackingParametersView);
Vue.component("temperature-parameters", TemperatureParametersView);
Vue.component("system-view", SystemView);
Vue.component("weather-upload", WeatherUpload);
Vue.component("weather-csv-mapper", WeatherCSVMapper);

new Vue({
  router,
  render: h => h(App),
  store
}).$mount("#app");
