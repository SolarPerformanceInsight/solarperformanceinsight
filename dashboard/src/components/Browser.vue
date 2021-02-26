<template>
  <div class="db-browser">
    <input v-model="search" v-on:keyup.enter="filterOptions" />
    <button class="search" @click="filterOptions">Search</button>
    <button class="search-reset" @click="resetSearch">Reset Search</button>
    <button class="cancel" @click="cancel">Cancel</button>
    <div v-if="optionsLoading">
      Loading database...
    </div>
    <div v-else>
      <select size="20" v-model="selection" @change="loadSpec">
        <option v-for="(op, i) in selectOptions" :key="i">{{ op }}</option>
      </select>
      <div v-if="specLoading">
        Loading parameters...
      </div>
      <template v-else>
        <div v-if="this.spec">
          Parameters for Inverter :
          <b>{{ this.selection }}</b>
          <br />
          <ul class="parameter-summary">
            <li v-for="(v, k) in spec" :key="k">
              <b>{{ k }}:</b>
              {{ v }}
            </li>
          </ul>
          <button class="commit" @click="commit">Use these parameters</button>
        </div>
        <div v-else>
          Please make a selection.
        </div>
      </template>
    </div>
  </div>
</template>
<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";

@Component
export default class DBBrowser extends Vue {
  @Prop() componentName!: string;
  optionsLoading = true;
  specLoading = false;
  options!: Array<string>;
  selectOptions: Array<string> = [];
  selection!: string;
  search!: string;
  spec: Record<string, any> = {};
  timeoutId!: number | null;

  mounted() {
    this.loadOptions();
  }
  data() {
    return {
      show: false,
      options: this.options,
      selectOptions: this.options,
      selection: this.selection,
      spec: this.spec,
      search: this.search,
      timeoutId: null
    };
  }
  async setFilteredOptions() {
    let opts: Array<string>;
    if (this.search && this.search != "") {
      // split the search term on spaces and make lowercase
      const searchTerms = this.search
        .toLowerCase()
        .replace(/_/g, " ")
        .split(" ")
        .filter(x => x != "");

      // filter for options that contain all of the separated search terms
      opts = this.options.filter(x => {
        const lowerName = x.toLowerCase().replace(/_/g, " ");
        return searchTerms.reduce<boolean>((acc: boolean, y: string) => {
          return acc && lowerName.includes(y);
        }, true);
      });
    } else {
      opts = this.options;
    }
    return opts;
  }
  resetSearch() {
    this.search = "",
    this.filterOptions();
  }
  filterOptions() {
    this.optionsLoading = true;
    this.setFilteredOptions().then(opts => {
      this.selectOptions = opts;
      this.optionsLoading = false;
    });
  }
  async loadOptions() {
    const response = await fetch(
      `/api/parameters/${this.componentName.toLowerCase()}`
    );
    const optionList = await response.json();
    this.options = optionList;
    this.selectOptions = optionList;
    this.optionsLoading = false;
  }
  async fetchSpec() {
    const response = await fetch(
      `/api/parameters/${this.componentName.toLowerCase()}/${this.selection}`
    );
    const optionList = await response.json();
    return optionList;
  }
  loadSpec() {
    this.specLoading = true;
    this.fetchSpec().then(spec => {
      this.spec = spec;
      this.specLoading = false;
    });
  }
  commit() {
    this.$emit("parameters-selected", {
      parameters: this.spec,
      name: this.selection
    });
  }
  cancel() {
    this.$emit("cancel-selection");
  }
}
</script>

<style scoped>
div.db-browser {
  position: absolute;
  z-index: 10;
  background-color: white;
  border: solid 1px #333;
  padding: 1em;
}
.search-box {
  width: 350px;
}
</style>
