<template>
  <div class="home-content">
    <div v-if="!$auth.isAuthenticated" class="unauth-home">
      <p>
        Welcome to the solarperformance insight dashboard. Other information
        about the project.
      </p>
    </div>
    <div v-if="$auth.isAuthenticated" class="auth-home">
      <p>
        Successfully logged in.
      </p>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component
export default class HomeContent extends Vue {}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped></style>
