<template>
  <div class="loss-parameters">
    <div v-if="model == 'pvwatts'">
      <b>soiling:</b>
      <input type="number" v-model.number="parameters.soiling" />
      <help :helpText="this.definitions.properties.soiling.description" />
      <br />
      <span style="color: #F00;" v-if="'soiling' in this.errors">
        {{ this.errors.soiling }}
        <br />
      </span>
      <b>shading:</b>
      <input type="number" v-model.number="parameters.shading" />
      <help :helpText="this.definitions.properties.shading.description" />
      <br />
      <span style="color: #F00;" v-if="'shading' in this.errors">
        {{ this.errors.shading }}
        <br />
      </span>
      <b>snow:</b>
      <input type="number" v-model.number="parameters.snow" />
      <help :helpText="this.definitions.properties.snow.description" />
      <br />
      <span style="color: #F00;" v-if="'snow' in this.errors">
        {{ this.errors.snow }}
        <br />
      </span>
      <b>mismath:</b>
      <input type="number" v-model.number="parameters.mismatch" />
      <help :helpText="this.definitions.properties.mismatch.description" />
      <br />
      <span style="color: #F00;" v-if="'mismatch' in this.errors">
        {{ this.errors.mismatch }}
        <br />
      </span>
      <b>wiring:</b>
      <input type="number" v-model.number="parameters.wiring" />
      <help :helpText="this.definitions.properties.wiring.description" />
      <br />
      <span style="color: #F00;" v-if="'wiring' in this.errors">
        {{ this.errors.wiring }}
        <br />
      </span>
      <b>connections:</b>
      <input type="number" v-model.number="parameters.connections" />
      <help :helpText="this.definitions.properties.connections.description" />
      <br />
      <span style="color: #F00;" v-if="'connections' in this.errors">
        {{ this.errors.connections }}
        <br />
      </span>
      <b>lid:</b>
      <input type="number" v-model.number="parameters.lid" />
      <help :helpText="this.definitions.properties.lid.description" />
      <br />
      <span style="color: #F00;" v-if="'lid' in this.errors">
        {{ this.errors.lid }}
        <br />
      </span>
      <b>nameplate rating:</b>
      <input type="number" v-model.number="parameters.nameplate_rating" />
      <help
        :helpText="this.definitions.properties.nameplate_rating.description"
      />
      <br />
      <span style="color: #F00;" v-if="'nameplate_rating' in this.errors">
        {{ this.errors.nameplate_rating }}
        <br />
      </span>
      <b>age:</b>
      <input type="number" v-model.number="parameters.age" />
      <help :helpText="this.definitions.properties.age.description" />
      <br />
      <span style="color: #F00;" v-if="'age' in this.errors">
        {{ this.errors.age }}
        <br />
      </span>
      <b>availability:</b>
      <input type="number" v-model.number="parameters.availability" />
      <help :helpText="this.definitions.properties.availability.description" />
      <br />
      <span style="color: #F00;" v-if="'availability' in this.errors">
        {{ this.errors.availability }}
        <br />
      </span>
    </div>
  </div>
</template>

<script lang="ts">
import SchemaBase from "@/components/SchemaBase.vue";
import { Component, Prop, Vue, Watch } from "vue-property-decorator";

import HelpPopup from "@/components/Help.vue";

// Update with many classes of inverter parameters to check for type before
// choosing a display.
import { PVWattsLosses } from "@/types/Losses";

Vue.component("help", HelpPopup);

@Component
export default class LossParametersView extends SchemaBase {
  @Prop() parameters!: PVWattsLosses | null;

  @Prop() model!: string;
  errors: Record<string, any> = {};

  get apiComponentName() {
    return "PVWattsLosses";
  }
  @Watch("parameters", { deep: true })
  validate(newParams: Record<string, any>) {
    if (this.model == "pvwatts") {
      this.$validator
        .validate(this.apiComponentName, newParams as PVWattsLosses)
        .then(this.setValidationResult);
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
ul {
  list-style-type: none;
  padding: 0;
}
div.loss-parameters {
  margin: 0.5em;
  padding: 0.5em;
  border: 1px solid #000;
  width: fit-content;
}
</style>
