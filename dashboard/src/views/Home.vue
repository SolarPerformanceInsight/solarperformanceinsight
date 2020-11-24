<template>
  <div class="home">
    <div v-if="!$auth.loading">
      <!-- show login when not authenticated -->
      <button v-if="!$auth.isAuthenticated" @click="login">Log in</button>
      <!-- show logout when authenticated -->
      <button v-if="$auth.isAuthenticated" @click="logout">Log out</button>
    <div v-if="!$auth.isAuthenticated">
      <p>Welcome to the solarperformance insight dashboard. Other information
         about the project.
      </p>
    </div>
    <div v-if="$auth.isAuthenticated">
      <p>Successfully logged in.
      </p>
    </div>

    </div>
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
      systems: this.$store.state.systems,
    }
  }
  login(){
    this.$auth.loginWithRedirect();
  }
  logout(){
    this.$auth.logout({
	  returnTo: window.location.origin,
	});
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
