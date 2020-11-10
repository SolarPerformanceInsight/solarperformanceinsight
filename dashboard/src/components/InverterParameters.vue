<template>
  <div class="inverter-parameters">
    <b>Parameter source: </b>
    <select v-model="parameterSource" name="parameter-source">
      <option>User Supplied</option>
      <option>Browse Database</option> </select
    ><br />
    <!-- If user selects something other than User Supplied, display the
         list of inverters from the db. This should probably be it's own
         component with some search functionality built in
     -->
    <div v-if="parameterSource !== 'User Supplied'">
      <b>Select an Inverter: </b>
      <select @change="loadInverter" name="inverter-list">
        <option v-for="p in parameterOptions" :key="p">{{ p }}</option> </select
      ><br />
    </div>
    <div v-if="model == 'pvsyst'">
      <b>AC Power Rating: </b><input v-model="parameters.Paco" /><br />
      <b>DC Power Rating: </b><input v-model="parameters.Pdco" /><br />
      <b>Vdco: </b><input v-model="parameters.Vdco" /><br />
      <b>Pso: </b><input v-model="parameters.Pso" /><br />
      <b>C0: </b><input v-model="parameters.C0" /><br />
      <b>C1: </b><input v-model="parameters.C1" /><br />
      <b>C2: </b><input v-model="parameters.C2" /><br />
      <b>C3: </b><input v-model="parameters.C3" /><br />
      <b>Pnt: </b><input v-model="parameters.Pnt" /><br />
    </div>
    <div v-if="model == 'pvwatts'">
      <b>Param 1: </b><input v-model="parameters.param_1" /><br />
      <b>Param 2: </b><input v-model="parameters.param_2" /><br />
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";
import ArraysView from "@/components/Arrays.vue";
import {
  PVSystInverterParameters,
  PVWattsInverterParameters
} from "@/types/InverterParameters";

Vue.component("arrays-view", ArraysView);
@Component
export default class InverterParametersView extends Vue {
  // extend acceptable types for InverterParameters to include a PVWatts class
  @Prop() parameters!: PVSystInverterParameters | PVWattsInverterParameters;
  @Prop() model!: string;
  @Prop({ default: null }) selectedInverter!: string;

  data() {
    return {
      parameterSource: "User Supplied"
    };
  }

  loadInverter(event: any) {
    // TODO: load inverter from correct source based on selected model.
    console.log(event.target.value);
  }

  get parameterOptions() {
    // Return a list of parameter options based on currently selected model
    if (this.model == "pvsyst") {
      return ["PVSystInverter_0", "PVSystInverter_1"];
    } else if (this.model == "pvwatts") {
      return ["PVWattsInverter_0", "PVWattsInverter_1"];
    } else {
      return [];
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
div.inverter-parameters {
  margin: 0.5em;
  padding: 0.5em;
  border: 1px solid #000;
  width: fit-content;
}
</style>
