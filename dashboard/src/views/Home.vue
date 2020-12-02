<!-- Wrapper component displays login/logout buttons, and conditionally build
     the header menu based on whether the user is authenticated or not.
-->
<template>
  <div class="home">
    <div v-if="!$auth.loading">
      <div id="site-header">
        <div id="nav">
          <!-- Always display home link -->
          <router-link to="/">
          Home
          </router-link>

          <!-- Router links to dispalay for authenticated users go in this
               span -->
          <span  v-if="$auth.isAuthenticated">
          <router-link v-if="$auth.isAuthenticated" to="/systems">
          Systems
          </router-link>
          </span>
        </div>
        <div id="account-menu">
          <!-- show login when not authenticated -->
          <button v-if="!$auth.isAuthenticated" @click="login">Log in</button>
          <!-- show logout when authenticated -->
          <button v-if="$auth.isAuthenticated" @click="logout">Log out</button>
        </div>
      </div>
      <div class="body">
        <router-view />
      </div>
    </div>
    <div id="site-footer">
      <div class="project-link">
        <a href="https://solarperformanceinsight.org">Solar Performance Insight</a>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component
export default class Home extends Vue {
  data() {
    return {
      systems: this.$store.state.systems
    };
  }
  login() {
    this.$auth.loginWithRedirect();
  }
  logout() {
    this.$auth.logout({
      returnTo: window.location.origin
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

#site-header, #site-footer{
  display: flex;
}
#site-header {
  border-bottom: 1px solid black;
  margin-bottom: 1em;
}
#site-footer {
  border-top: 1px solid black;
  margin-top: 1em;
}

#nav, #account-menu {
  padding: 30px;
  display: inline-flex;
}

#account-menu {
  margin-left: auto;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
}

#nav a.router-link-exact-active {
  color: #42b983;
}
#nav a.router-link-active {
  margin-right: 1em;
}
.project-link {
  padding: 30px;
}
</style>
