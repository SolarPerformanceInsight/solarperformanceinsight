<template>
  <li>
    <model-field
      :parameters="parameters"
      :errors="errors"
      :definitions="definitions"
      field-name="name"
    />
    <model-field
      :parameters="parameters"
      :errors="errors"
      :definitions="definitions"
      field-name="albedo"
    />
    <model-field
      :parameters="parameters"
      :errors="errors"
      :definitions="definitions"
      field-name="modules_per_string"
    />
    <model-field
      :parameters="parameters"
      :errors="errors"
      :definitions="definitions"
      field-name="strings"
    />
    <b>Tracking:</b>
    <input
      v-model="tracking"
      class="fixed_tracking"
      type="radio"
      v-on:change="changeTracking"
      value="fixed"
    />
    Fixed
    <input
      :disabled="numArrays > 1"
      v-model="tracking"
      class="single_axis_tracking"
      type="radio"
      v-on:change="changeTracking"
      value="singleAxis"
    />
    Single Axis
    <span v-if="numArrays > 1" class="warning-text">
      Only supported for single array inverter.
    </span>
    <tracking-parameters
      :tracking="tracking"
      :parameters="parameters.tracking"
    />
    <br />
    <model-field
      :parameters="parameters"
      :errors="errors"
      :definitions="definitions"
      field-name="make_model"
    />
    <b>Module Parameters:</b>
    <br />
    <module-parameters
      :parameters="parameters.module_parameters"
      :model="model"
    />
    <b>Temperature Model Parameters:</b>
    <temperature-parameters
      :model="model"
      :parameters="parameters.temperature_model_parameters"
    />

    <button class="remove-array" @click="removeArray">Remove Array</button>
    <br />
    <button
      class="duplicate-array"
      @click="duplicateArray"
      :disabled="!allFixed"
    >
      Duplicate Array
    </button>
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
  @Prop() parameters!: PVArray;
  @Prop() index!: number;
  @Prop() model!: string;
  @Prop() allFixed!: boolean;
  @Prop() numArrays!: number;

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
    if (FixedTrackingParameters.isInstance(this.parameters.tracking)) {
      return "fixed";
    } else {
      return "singleAxis";
    }
  }
  @Watch("model")
  changeModel(newModel: string) {
    if (newModel == "pvsyst") {
      this.parameters.module_parameters = new PVSystModuleParameters({});
      this.parameters.temperature_model_parameters = new PVSystTemperatureParameters(
        {}
      );
    } else if (newModel == "pvwatts") {
      this.parameters.module_parameters = new PVWattsModuleParameters({});
      this.parameters.temperature_model_parameters = new SAPMTemperatureParameters(
        {}
      );
    }
  }

  changeTracking(e: HTMLInputEvent) {
    const tracking = e.target.value;
    if (tracking == "fixed") {
      this.parameters.tracking = new FixedTrackingParameters({});
    } else {
      this.parameters.tracking = new SingleAxisTrackingParameters({});
    }
  }
  @Watch("parameters.tracking")
  ensureTracking() {
    // Ensure tracking stays consistent when the tracking parameters change
    // commonly fired an array is removed, so tha the component updates with
    // the new object. This does not trigger when fields on the tracking
    // object are changed.
    this.tracking = this.inferTracking();
  }

  removeArray() {
    this.$emit("array-removed", this.index);
  }
  duplicateArray() {
    this.$emit("array-added", this.parameters);
  }
  get apiComponentName() {
    return "PVArray";
  }

  @Watch("parameters", { deep: true })
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
