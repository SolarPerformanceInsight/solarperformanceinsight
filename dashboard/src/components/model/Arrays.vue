<template>
  <div class="arrays">
    <div class="arrays-list">
      <h2>Arrays</h2>
      <button class="add-array" @click="addArray()" :disabled="!allFixed">
        Add Array
      </button>
      <span v-if="!allFixed" class="warning-text">
        Multiple arrays only supported for fixed tracking.
      </span>
      <div class="msg warning" v-if="pvarrays.length == 0">
        Inverter requires at least one array.
      </div>
      <ul>
        <array-view
          @array-removed="removeArray"
          @array-added="addArray"
          class="array"
          v-for="(pvarray, index) in pvarrays"
          :key="index"
          :index="index"
          :parameters="pvarray"
          :model="model"
          :allFixed="allFixed"
          :numArrays="numArrays"
        />
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";
import { PVArray } from "@/types/PVArray";
import { FixedTrackingParameters } from "@/types/Tracking";
import {
  PVWattsModuleParameters,
  PVSystModuleParameters,
  CECModuleParameters
} from "@/types/ModuleParameters";
import {
  SAPMTemperatureParameters,
  PVSystTemperatureParameters
} from "@/types/TemperatureParameters";

@Component
export default class ArraysView extends Vue {
  @Prop() pvarrays!: Array<PVArray>;
  @Prop() model!: string;

  addArray(existingArray: PVArray | null) {
    let newArray: PVArray;
    if (existingArray) {
      newArray = new PVArray({
        ...existingArray,
        name: `${existingArray.name} copy`
      });
    } else {
      let modParamClass: any = PVWattsModuleParameters;
      let tempParamClass: any = SAPMTemperatureParameters;
      if (this.model == "pvsyst") {
        modParamClass = PVSystModuleParameters;
        tempParamClass = PVSystTemperatureParameters;
      } else if (this.model == "sam") {
        modParamClass = CECModuleParameters;
        tempParamClass = PVSystTemperatureParameters;
      }

      const modParams = new modParamClass({});
      const tempParams = new tempParamClass({});
      const arrayName = `Array ${this.pvarrays.length + 1}`;
      if (
        this.pvarrays.length > 0 &&
        this.pvarrays.every(x => x.albedo === this.pvarrays[0].albedo)
      ) {
        const albedo: number = this.pvarrays[0].albedo;
        newArray = new PVArray({
          name: arrayName,
          albedo: albedo,
          module_parameters: modParams,
          temperature_model_parameters: tempParams
        });
      } else {
        newArray = new PVArray({
          name: arrayName,
          module_parameters: modParams,
          temperature_model_parameters: tempParams
        });
      }
    }
    this.pvarrays.push(newArray);
  }
  removeArray(index: number) {
    this.pvarrays.splice(index, 1);
  }
  get allFixed() {
    return this.pvarrays.reduce<boolean>((acc: boolean, arr: PVArray) => {
      return acc && FixedTrackingParameters.isInstance(arr.tracking);
    }, true);
  }
  get numArrays() {
    return this.pvarrays.length;
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
