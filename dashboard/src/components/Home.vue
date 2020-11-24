<template>
  <div class="model">
    <h1>All Dem Systems</h1>
    <router-link :to="{name: 'Model'}">Create new System</router-link>
    <ul>
      <li v-for="(s, index) in systems" :key="s.name">
        {{ s.name }}
        <router-link :to="{name: 'Update System', params: {systemId: index}}">
          Edit
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

import { System } from "@/types/System";
import { modelSpecs } from "@/types/ModelSpecification";
import  DemoSystems from "@/types/demo/systems";


@Component
export default class Home extends Vue {
  data(){
    return {
      systems: DemoSystems,
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  margin: 0 10px;
}
a {
  color: #42b983;
}
div.advanced-model-params {
  border: 1px solid black;
  padding: 0.5em;
  width: fit-content;
}
</style>
