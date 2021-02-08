<template>
  <div class="csv-preview">
    <b>CSV Preview</b>
    <p>
      Below are the first 5 rows of data from your csv, with the variable each
      column is mapped to in the
      <i>Mapped Variable</i>
      row.
    </p>
    <div class="table-container">
      <table
        class="striped-table csv-mapping-preview"
        :style="`--numCol: ` + numCol"
      >
        <thead>
          <tr>
            <th><b>CSV Headers</b></th>
            <th
              v-for="(header, i) of headers"
              :key="i"
              v-bind:class="{
                hovered: currentlySelected == header,
                mapped: mapping[header]
              }"
            >
              {{ header }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><b>Mapped Variable</b></td>
            <td
              v-for="(col, j) of headers"
              :key="j"
              v-bind:class="{
                hovered: currentlySelected == col,
                mapped: mapping[col],
                'warning-text': !mapping[col]
              }"
            >
              {{ mapping[col] ? displayName(mapping[col]) : `Not Mapped` }}
            </td>
          </tr>
          <tr v-for="(row, i) of csvData" :key="i">
            <td>
              <b>Data Row {{ i + 1 }}</b>
            </td>
            <td
              v-for="(col, j) of headers"
              :key="j"
              v-bind:class="{
                hovered: currentlySelected == col,
                mapped: mapping[col]
              }"
            >
              {{ row[col] }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop, Watch } from "vue-property-decorator";
import { variableDisplayNames } from "@/utils/displayNames";

@Component
export default class CSVPreview extends Vue {
  @Prop() mapping!: Record<string, string>;
  @Prop() currentlySelected!: string;
  @Prop() headers!: Array<string>;
  @Prop() csvData!: Array<Record<string, any>>;

  get numCol() {
    return this.headers.length + 1;
  }
  @Watch("mapping", { deep: true })
  rerender() {
    this.$forceUpdate();
  }
  displayName(variable: string) {
    // @ts-expect-error
    return variableDisplayNames[variable];
  }
}
</script>
<style scoped="true">
th.hovered,
td.hovered {
  background: yellow;
}
th.mapped {
  background: #aaa;
}
td.mapped {
  background: #ddd;
}
th.mapped,
td.mapped {
  border-left: 1px solid black;
  border-right: 1px solid black !important;
}
.table-container {
  width: 100%;
  overflow-x: scroll;
}
</style>
