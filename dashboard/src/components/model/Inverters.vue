<template>
  <div class="Inverters">
    <div class="inverters-list">
      <h2>Inverters</h2>
      <button @click="addInverter()">Add Inverter</button>
      <div class="msg warning" v-if="inverters.length == 0">
        System requires at least one inverter.
      </div>
      <ul class="inverters">
        <inverter-view
          @inverter-removed="removeInverter"
          @inverter-added="addInverter"
          class="inverter"
          v-for="(inverter, index) in inverters"
          :key="index"
          :index="index"
          :parameters="inverter"
          :model="model"
        />
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";
import { Inverter } from "@/types/Inverter";
import {
  PVWattsInverterParameters,
  SandiaInverterParameters
} from "@/types/InverterParameters";
import { PVWattsLosses } from "@/types/Losses";

@Component
export default class InvertersView extends Vue {
  @Prop() inverters!: Array<Inverter>;
  @Prop() model!: string;

  addInverter(existingInverter: Inverter | null) {
    let newInverter: Inverter;
    if (existingInverter) {
      newInverter = new Inverter({
        ...existingInverter,
        name: `${existingInverter.name} copy`
      });
    } else {
      let paramClass: any = PVWattsInverterParameters;
      let lossClass: any = PVWattsLosses;
      if (this.model == "pvsyst") {
        paramClass = SandiaInverterParameters;
        lossClass = null;
      }
      newInverter = new Inverter({
        name: `Inverter ${this.inverters.length + 1}`,
        inverter_parameters: new paramClass({}),
        losses: lossClass ? new lossClass({}) : null
      });
    }
    this.inverters.push(newInverter);
  }
  removeInverter(index: number) {
    this.inverters.splice(index, 1);
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
ul {
  list-style-type: none;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
}
li.inverter {
  margin: 0.5em;
  padding: 0.5em;
  border: 1px solid #000;
  width: fit-content;
}
</style>
