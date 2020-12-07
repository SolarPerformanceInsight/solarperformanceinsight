<template>
  <div class="model-field">
    <b>{{ title }}:</b>
    <input v-if="inputType == 'number'" type="number" v-model.number="$parent.parameters[fieldName]" />
    <input v-if="inputType != 'number'" v-model="$parent.parameters[fieldName]" />
    <help :helpText="$parent.definitions.properties[fieldName].description" />
    <br />
    <span style="color: #F00;" v-if="fieldName in $parent.errors">
      {{ $parent.errors[fieldName] }}
    </span>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";

@Component
export default class ModelField extends Vue{
  @Prop() title!: string;
  @Prop() inputType?: string;
  @Prop() fieldName!: string;
  //@Prop() parameters!: Record<string, any>;
  //@Prop() errors!: Record<string, any>;
  //@Prop() definitions!: Record<string, any>;

}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
