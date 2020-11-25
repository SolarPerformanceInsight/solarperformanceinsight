<template>
  <div class="systems">
    <h1>Systems</h1>
    <router-link :to="{ name: 'Model' }">Create new System</router-link>
    <button @click="refreshSystems">Refresh System List</button><br />
    <p v-if="loading">Loading...</p>
    <ul v-if="!loading">
      <li v-if="systems.length == 0">No available systems</li>
      <li v-for="(s, index) in systems" :key="s.name">
        {{ s.name }}
        <router-link
          :to="{ name: 'Update System', params: { systemId: index } }"
        >
          Edit
        </router-link>
      </li>
    </ul>
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
