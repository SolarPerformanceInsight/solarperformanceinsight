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

Parent components should v-bind `parameters`, `definitions`, and `errors` and
pass the name of the property to render as the `fieldName` prop.

e.g. For the PVWatts Inverter Parameter schema, the pdc0 field can be rendered
     with:

    <model-field
      :parameters="parameters"
      :definitions="definitions"
      :errors="errors"
      field-name="pdc0">`

-->
<template>
  <div class="model-field">
    <label class="field_label" :id="titleId">{{ title }}:</label>

    <input
      @change="emitChange"
      v-if="inputType == 'number'"
      type="number"
      :id="fieldId"
      :aria-labelledby="titleId"
      :aria-describedby="helpId"
      step="any"
      v-model.number="parameters[fieldName]"
    />
    <input
      @change="emitChange"
      v-if="inputType == 'integer'"
      :id="fieldId"
      :aria-labelledby="titleId"
      :aria-describedby="helpId"
      type="number"
      v-model.number="parameters[fieldName]"
    />
    <template v-if="inputType == 'boolean'">
      <label>
        True:
        <input
          @change="emitChange"
          type="radio"
          :id="fieldId + '_true'"
          :value="true"
          v-model="parameters[fieldName]"
          :aria-describedby="helpId"
        />
      </label>
      <label>
        False:
        <input
          @change="emitChange"
          type="radio"
          :id="fieldId + '_false'"
          :value="false"
          v-model="parameters[fieldName]"
          :aria-describedby="helpId"
        />
      </label>
    </template>

    <input
      @change="emitChange"
      v-if="inputType == 'string'"
      :id="fieldId"
      :aria-labelledby="titleId"
      :aria-describedby="helpId"
      v-model="parameters[fieldName]"
    />
    <slot></slot>
    <help
      :helpText="definitions.properties[fieldName].description"
      :tagId="helpId"
    />
    <br />
    <span class="errors" style="color: #F00;" v-if="fieldName in errors">
      {{ errors[fieldName] }}
    </span>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";
import { getIndex } from "@/utils/fieldIndex";

@Component
export default class ModelField extends Vue {
  @Prop() fieldName!: string;
  @Prop() parameters!: Record<string, any>;
  @Prop() definitions!: Record<string, any>;
  @Prop() errors!: Record<string, any>;
  fieldIndex!: number;

  data() {
    return {
      fieldIndex: getIndex()
    };
  }

  get title() {
    return this.definitions.properties[this.fieldName].title;
  }
  get inputType() {
    return this.definitions.properties[this.fieldName].type;
  }
  get fieldId() {
    return `field_${this.fieldIndex}`;
  }
  get titleId() {
    return `${this.fieldId}_title`;
  }
  get helpId() {
    return `${this.fieldId}_help`;
  }
  emitChange(event: any) {
    this.$emit("change", event);
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped></style>
