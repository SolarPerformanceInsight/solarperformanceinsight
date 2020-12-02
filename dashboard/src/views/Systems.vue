<template>
  <div class="systems">
    <h1>Systems</h1>
    <router-link :to="{ name: 'Model' }">Create new System</router-link>
    <button @click="refreshSystems">Refresh System List</button>
    <br />
    <p v-if="loading">Loading...</p>

    <div v-if="!loading" class="container">
      <ul class="grid">
        <li>
          <span class="system-cell"><b>Name</b></span>
          <span class="system-cell"><b>Latitude</b></span>
          <span class="system-cell"><b>Longitude</b></span>
        </li>
        <li v-if="systems.length == 0">No available systems</li>
        <li v-for="(system, uuid) in systems" :key="uuid">
          <span class="system-cell system-name">
            <b>{{ system.name }}</b>
          </span>
          <span class="system-cell latitude">{{ system.latitude }}</span>
          <span class="system-cell longitude">{{ system.longitude }}</span>
          <span class="system-cell">
            <router-link
              :to="{ name: 'Update System', params: { systemId: uuid } }"
            >
              Edit
            </router-link>
          </span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component
export default class Systems extends Vue {
  data() {
    return {
      loading: false,
      response: ""
    };
  }
  created() {
    this.refreshSystems();
  }
  refreshSystems() {
    this.$store.dispatch("fetchSystems");
  }
  get systems() {
    // computed property returns the list of systems
    return this.$store.state.systems;
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
  width: fit-content;
}
li {
  width: 100%;
  margin: 0 10px;
  border-bottom: 1px solid black;
  margin-bottom: 0.5em;
}
span.system-cell {
  display: inline-block;
  width: 150px;
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
