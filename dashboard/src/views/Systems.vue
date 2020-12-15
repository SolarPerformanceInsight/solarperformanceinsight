<template>
  <div class="systems">
    <h1>Systems</h1>
    <router-link :to="{ name: 'Model' }">Create new System</router-link>
    <br />
    <p v-if="loading">Loading...</p>

    <div v-if="!loading" class="container">
      <ul class="grid">
        <li>
          <span class="system-cell"><b>Name</b></span>
        </li>
        <li v-if="systems.length == 0">No available systems</li>
        <li v-for="(system, uuid) in systems" :key="uuid">
          <span class="system-cell system-name">
            <b>{{ system.definition.name }}</b>
          </span>
          <span class="system-cell small">
            <router-link
              :to="{ name: 'Update System', params: { systemId: uuid } }"
            >
              Edit
            </router-link>
          </span>
          <span class="system-cell small">
            <a role="button" @click="displayDeleteDialog(system)">Delete</a>
          </span>
          <span class="system-cell"><button>Predict Performance</button></span>
          <span class="system-cell"><button>Compare Performance</button></span>
          <span class="system-cell"><button>Calculate PR</button></span>
        </li>
      </ul>
    </div>
    <transition name="fade">
      <div v-if="showDeleteDialog" id="delete-dialog">
        <div class="modal-block">
          <p>
            Are you sure you want to delete the system
            {{ selectedSystem.definition.name }}?
          </p>
          <button @click="deleteSystem">Yes</button>
          <button @click="showDeleteDialog = false">Cancel</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { StoredSystem } from "@/types/System";
@Component
export default class Systems extends Vue {
  showDeleteDialog = false;
  selectedSystem: StoredSystem | null = null;

  data() {
    return {
      showDeleteDialog: this.showDeleteDialog,
      selectedSystem: this.selectedSystem,
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
  displayDeleteDialog(system: StoredSystem) {
    this.selectedSystem = system;
    this.showDeleteDialog = true;
  }
  async sendDeleteRequest(system_id: string) {
    const token = await this.$auth.getTokenSilently();
    const response = await fetch(`/api/systems/${system_id}`, {
      headers: new Headers({
        Authorization: `Bearer ${token}`
      }),
      method: "delete"
    });
    return response;
  }
  deleteSystem() {
    if (this.selectedSystem) {
      this.sendDeleteRequest(this.selectedSystem.object_id).then(response => {
        if (response.ok) {
          this.refreshSystems();
        } else {
          console.log(`Failed to delete with code ${response.status}`);
        }
      });
    }
    this.showDeleteDialog = false;
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
  min-width: 125px;
  width: 18vw;
}
span.system-cell.small {
  min-width: 75px;
  width: fit-content;
}
a {
  color: #42b983;
}
div.advanced-model-params {
  border: 1px solid black;
  padding: 0.5em;
  width: fit-content;
}
#delete-dialog {
  position: fixed;
  top: 0;
  left: 0;
  height: 100%;
  width: 100%;
  display: block;
  background-color: rgba(0, 0, 0, 0.5);
}
#delete-dialog .modal-block {
  width: 500px;
  margin: 25% auto;
  padding: 2em;
  border: 1px solid #000;
  background-color: #fff;
}
#delete-dialog button {
  display: inline-block;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}
</style>
