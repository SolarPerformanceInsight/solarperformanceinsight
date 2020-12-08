<!--
Single field component to render an input for schema properties defined by the
Solar Performance Insight API's OpenAPI Spec. Includes a help popup that
renders the property description at the right of the input. Safe to use in
components in the `models` directory that extend the `ModelBase` class.

WARNING : THIS COMPONENT WILL MUTATE ITS PARENTS PROPERTIES. BY UTILIZING IT
YOU ARE ALLOWING THE PROPERTIES OF YOUR COMPONENTS `parameters` FIELD TO BE
CHANGED. DO NOT USE WHEN UPSTREAM COMPONENTS ALSO USE `v-model` or `v-bind`
ON THE SAME FIELD.

This component only works for a single primitive schema property, and will not
work for properties containing nested schema. e.g. `arrays` or `inverters`

Parent components should have a Prop called `parameters` that contains an
object defined in the OpenAPI spec. This component can be used by passing the
property name to render as the `field-name` Prop.

e.g. For the PVWatts Inverter Parameter schema, the pdc0 field can be rendered
     with:

    ` <model-field field-name="pdc0">`

-->
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
