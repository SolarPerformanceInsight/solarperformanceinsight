<template>
  <li>
    <b>Inverter Name:</b>
    {{ $parent.$parent.inverter.name }}
    <br />
    <b>Name:</b>
    <input v-model="pvarray.name" />
    <help :helpText="this.definitions.properties.name.description" />
    <br />
    <span style="color:#F00;" v-if="'name' in this.errors">
      {{ this.errors.name }}
      <br />
    </span>
    <b>Make and Model:</b>
    <input v-model="pvarray.make_model" />
    <help :helpText="this.definitions.properties.make_model.description" />
    <br />
    <span style="color:#F00;" v-if="'make_model' in this.errors">
      {{ this.errors.make_model }}
      <br />
    </span>
    <b>Tracking:</b>
    <input
      v-model="tracking"
      type="radio"
      v-on:change="changeTracking"
      value="fixed"
    />
    Fixed
    <input
      v-model="tracking"
      type="radio"
      v-on:change="changeTracking"
      value="singleAxis"
    />
    Single Axis
    <tracking-parameters :tracking="tracking" :parameters="pvarray.tracking" />
    <b>Temperature Model Parameters:</b>
    <br />
    <temperature-parameters
      :model="model"
      :parameters="pvarray.temperature_model_parameters"
    />
    <b>Module Parameters:</b>
    <br />
    <module-parameters :parameters="pvarray.module_parameters" :model="model" />
    <button @click="removeArray">Remove Array</button>
    <br />
    <button @click="duplicateArray">Duplicate Array</button>
  </li>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from "vue-property-decorator";
import { PVArray } from "@/types/PVArray";
import {
  PVSystModuleParameters,
  PVWattsModuleParameters
} from "@/types/ModuleParameters";

import {
  PVSystTemperatureParameters,
  SAPMTemperatureParameters
} from "@/types/TemperatureParameters";

import {
  FixedTrackingParameters,
  SingleAxisTrackingParameters
} from "@/types/Tracking";

import ModelBase from "@/components/ModelBase.vue";

interface HTMLInputEvent extends Event {
  target: HTMLInputElement & EventTarget;
}

@Component
export default class ArrayView extends ModelBase {
  @Prop() pvarray!: PVArray;
  @Prop() index!: number;
  @Prop() model!: string;
  tracking!: string;

  data() {
    return {
      tracking: this.inferTracking()
    };
  }
  created() {
    this.tracking = this.inferTracking();
  }
  inferTracking() {
    if (FixedTrackingParameters.isInstance(this.pvarray.tracking)) {
      return "fixed";
    } else {
      return "singleAxis";
    }
  }
  @Watch("model")
  changeModel(newModel: string) {
    if (newModel == "pvsyst") {
      this.pvarray.module_parameters = new PVSystModuleParameters({});
      this.pvarray.temperature_model_parameters = new PVSystTemperatureParameters(
        {}
      );
    } else if (newModel == "pvwatts") {
      this.pvarray.module_parameters = new PVWattsModuleParameters({});
      this.pvarray.temperature_model_parameters = new SAPMTemperatureParameters(
        {}
      );
    }
  }

  changeTracking(e: HTMLInputEvent) {
    const tracking = e.target.value;
    if (tracking == "fixed") {
      this.pvarray.tracking = new FixedTrackingParameters({});
    } else {
      this.pvarray.tracking = new SingleAxisTrackingParameters({});
    }
  }
  @Watch("pvarray.tracking")
  ensureTracking() {
    // Ensure tracking stays consistent when the tracking parameters change
    // commonly fired an array is removed, so tha the component updates with
    // the new object. This does not trigger when fields on the tracking
    // object are changed.
    this.tracking = this.inferTracking();
  }

  removeArray() {
    // @ts-expect-error
    this.$parent.pvarrays.splice(this.index, 1);
  }
  duplicateArray() {
    // @ts-expect-error
    this.$parent.pvarrays.push(new PVArray(this.pvarray));
  }
  get apiComponentName() {
    return "PVArray";
  }

  @Watch("pvarray", { deep: true })
  validate(newArray: Record<string, any>) {
    const arr = newArray as PVArray;
    this.$validator
      .validate(this.apiComponentName, arr)
      .then(this.setValidationResult);
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
ul {
  list-style-type: none;
  padding: 0;
}
li.array {
  margin: 0.5em;
  padding: 0.5em;
  border: 1px solid #000;
  width: fit-content;
}
</style>
