<template>
  <div class="system" v-if="validatorInit">
    <div v-if="exists" class="model-field">
      <b>Name:</b>
      <span>{{ parameters.name }}</span>
    </div>
    <model-field
      v-if="!exists"
      :parameters="parameters"
      :errors="errors"
      :definitions="definitions"
      field-name="name"
    />
    <model-field
      :parameters="parameters"
      :errors="errors"
      :definitions="definitions"
      field-name="latitude"
    />
    <model-field
      :parameters="parameters"
      :errors="errors"
      :definitions="definitions"
      field-name="longitude"
    />
    <model-field
      @change="elevationError = null"
      :parameters="parameters"
      :errors="errors"
      :definitions="definitions"
      field-name="elevation"
    >
      <button
        class="elevation-button"
        :disabled="!locationValid"
        @click="lookupElevation"
      >
        Look Up Elevation
      </button>
    </model-field>
    <span class="warning-text" v-if="elevationError">{{ elevationError }}</span>
    <inverters-view :inverters="parameters.inverters" :model="model" />
  </div>
</template>

<script lang="ts">
import ModelBase from "@/components/ModelBase.vue";

import { Component, Prop, Watch } from "vue-property-decorator";
import { System, StoredSystem } from "@/types/System";

import { getElevation } from "@/utils/elevation";
import { resetIndex } from "@/utils/fieldIndex";

@Component
export default class SystemView extends ModelBase {
  @Prop({ default: false }) exists!: boolean;
  @Prop() parameters!: System;
  @Prop() model!: string;
  elevationError!: string | null;

  data() {
    return {
      elevationError: null
    };
  }
  mounted() {
    // reset the value used for producing unique field ids
    resetIndex();
  }
  get apiComponentName() {
    return "PVSystem";
  }
  @Watch("parameters", { deep: true })
  validate(newSystem: Record<string, any>) {
    const system = newSystem as System;
    this.$validator
      .validate(this.apiComponentName, system)
      .then(this.setValidationResult);
  }
  get locationValid() {
    return !("latitude" in this.errors) && !("longitude" in this.errors);
  }
  lookupElevation() {
    /* istanbul ignore next */
    getElevation(this.parameters.latitude, this.parameters.longitude)
      .then((elevation: number) => {
        this.parameters.elevation = elevation;
        this.elevationError = null;
      })
      .catch(() => {
        this.elevationError =
          "Elevation information could not be found. Lookup service is only available for sites in the United States.";
        this.validate(this.parameters);
      });
  }
  extraValidation() {
    let valid = true;
    if (!this.exists) {
      const existingSystems = Object.values(this.$store.state.systems).map(
        // @ts-expect-error
        (stored: StoredSystem) => {
          return stored.definition.name;
        }
      );
      if (existingSystems.includes(this.parameters.name)) {
        this.extraErrors[
          "name"
        ] = `System with name "${this.parameters.name}" already exists.`;
        valid = false;
      }
      delete this.extraErrors["name"];
    }
    return valid;
  }
}
</script>

<style scoped>
div {
  text-align: left;
}
.elevation-button {
  margin: 0 0.25em;
}
</style>
