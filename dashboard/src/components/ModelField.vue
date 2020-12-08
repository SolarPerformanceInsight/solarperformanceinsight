<template>
  <div class="model-field">
    <b>{{ title }}:</b>

    <input
      v-if="inputType == 'number'"
      type="number"
      v-model.number="$parent.parameters[fieldName]"
    />
    <template v-if="inputType == 'boolean'">
      True:
      <input
        type="radio"
        :value="true"
        v-model="$parent.parameters[fieldName]"
      />
      False:
      <input
        type="radio"
        :value="false"
        v-model="$parent.parameters[fieldName]"
      />
    </template>

    <input
      v-if="inputType == 'string'"
      v-model="$parent.parameters[fieldName]"
    />

    <help :helpText="$parent.definitions.properties[fieldName].description" />
    <br />
    <span style="color: #F00;" v-if="fieldName in $parent.errors">
      {{ $parent.errors[fieldName] }}
    </span>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";
import ModelBase from "@/components/ModelBase.vue";

@Component
export default class ModelField extends Vue {
  @Prop() fieldName!: string;
  definitions!: Record<string, any>;

  get title() {
    const parent: ModelBase = this.$parent as ModelBase;
    return parent.definitions.properties[this.fieldName].title;
  }
  get inputType() {
    const parent: ModelBase = this.$parent as ModelBase;
    return parent.definitions.properties[this.fieldName].type;
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped></style>
