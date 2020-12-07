<template>
  <li>
    <b>System Name:</b>
    {{ $parent.$parent.system.name }}
    <br />
    <b>Name:</b>
    <input v-model="inverter.name" />
    <help :helpText="this.definitions.properties.name.description" />
    <br />
    <span style="color:#F00;" v-if="'name' in this.errors">
      {{ this.errors.name }}
      <br />
    </span>
    <b>Make and Model:</b>
    <input v-model="inverter.make_model" />
    <help :helpText="this.definitions.properties.make_model.description" />
    <br />
    <span style="color:#F00;" v-if="'make_model' in this.errors">
      {{ this.errors.make_model }}
      <br />
    </span>
    <b>Inverter Parameters:</b>
    <br />
    <inverter-parameters
      :parameters="inverter.inverter_parameters"
      :model="model"
    />
    <span v-if="model == 'pvwatts'">
      <b>Loss Parameters:</b>
      <br />
      <loss-parameters :parameters="inverter.losses" :model="model" />
    </span>
    <arrays-view :pvarrays="inverter.arrays" :model="model" />
    <br />
    <button @click="removeInverter">Remove Inverter</button>
    <br />
    <button @click="duplicateInverter">Duplicate Inverter</button>
  </li>
</template>

<script lang="ts">
import ModelBase from "@/components/ModelBase.vue";

import { Component, Prop, Vue, Watch } from "vue-property-decorator";
import { Inverter } from "@/types/Inverter";
import { PVWattsLosses } from "@/types/Losses";
import {
  SandiaInverterParameters,
  PVWattsInverterParameters
} from "@/types/InverterParameters";

@Component
export default class InverterView extends ModelBase {
  @Prop() inverter!: Inverter;
  @Prop() index!: number;
  @Prop() model!: string;

  @Watch("model")
  changeModel(newModel: string) {
    if (newModel == "pvsyst") {
      this.inverter.inverter_parameters = new SandiaInverterParameters({});
      this.inverter.losses = null;
    } else if (newModel == "pvwatts") {
      this.inverter.inverter_parameters = new PVWattsInverterParameters({});
      this.inverter.losses = new PVWattsLosses({});
    }
  }

  removeInverter() {
    // @ts-expect-error
    this.$parent.inverters.splice(this.index, 1);
  }
  duplicateInverter() {
    // @ts-expect-error
    this.$parent.inverters.push(new Inverter(this.inverter));
  }
  get apiComponentName() {
    return "Inverter";
  }

  @Watch("inverter", { deep: true })
  validate(newInverter: Record<string, any>) {
    const inverter = newInverter as Inverter;
    this.$validator
      .validate(this.apiComponentName, inverter)
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
li.inverter {
  margin: 0.5em;
  padding: 0.5em;
  border: 1px solid #000;
  width: fit-content;
}
</style>
