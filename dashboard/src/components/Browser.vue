
<template>
  <div class="db-browser">
    <button @click="show = true"> Browse Inverter Database</button>
    <input v-model="search" v-on:input="filterOptions"/>
    <div v-if="optionsLoading">
      Loading...
    </div>
    <div v-else>
     <select size=20>
       <option v-for="(op, i) in options" :key="i">{{ op }}</option>
     </select>
     <div v-if="!specLoading">
       The spec is loaded
     </div>
    </div>
  </div>
</template>
<script lang="ts">
import { Component, Prop, Vue, Watch } from "vue-property-decorator";

@Component
export default class DBBrowser extends Vue {
  @Prop() componentName!: string;
  show = false;
  optionsLoading = true;
  specLoading = true;
  options!: Array<string>;
  selectOptions: Array<string>= [];
  selection!: string;
  search!: string;
  spec: Record<string, any> = {};

  mounted() {
    console.log("browser mounted");
    this.loadOptions();
  }
  data() {
    return {
      show: false,
      options: this.options,
      selection: this.selection,
      spec: this.spec,
      search: this.search
    };
  }
  filterOptions(){
    let opts: Array<string>;
    console.log("filtering");
    this.optionsLoading = true;
    if (this.search && this.search != "") {
      opts =this.options.filter(x => x.includes(this.search));
    } else {
      opts =this.options;
    }
    this.optionsLoading = false;
    this.selectOptions = opts;
  }
  @Watch("search")
  delaySearch(){
    setTimeout(() => {
      this.filterOptions();
    }, .2)
  }
  async loadOptions() {
    const token = await this.$auth.getTokenSilently();
    const response = await fetch(
      `/api/parameters/${this.componentName.toLowerCase()}`, {
        headers: new Headers({
          Authorization: `Bearer ${token}`
        })
    });
    const optionList = await response.json()
    this.options = optionList;
    this.optionsLoading = false;
  }
  loadSpec() {
    console.log("loadspec called");
  }
  commit() {
    this.$emit("parameters-selected", this.spec);
  }
}
</script>

<style scoped>
div.help {
  display: inline-block;
  position: relative;
}
.help-wrapper {
  position: absolute;
  padding: 0.5em;
  width: 300px;
  background-color: #fff;
  border: 1px solid black;
  border-radius: 5px;
  box-shadow: 1px 1px 5px #555;
  z-index: 1;
  top: 0;
  left: 100%;
}
</style>
