<template>
  <div class="api-errors">
    <ul>
      <li v-for="(error, i) of errorFields" :key="i" class="warning-text">
        <b>{{ error.field }}:</b>
        {{ error.message }}
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";

type APIError = {
  loc: Array<string>;
  msg: string;
  type: string;
};

type renderableError = {
  field: string;
  message: string;
};

@Component
export default class APIErrors extends Vue {
  @Prop() errors!: Array<APIError>;
  // fields, if supplied will limit the fields that errors are produced for.
  @Prop() fields!: Array<string>;

  get errorFields(): Array<renderableError> {
    let errors = this.errors.map((error: APIError) => {
      return {
        field: this.terminalLoc(error.loc),
        message: error.msg
      };
    });
    if (this.fields && this.fields.length) {
      errors = errors.filter((error: renderableError) => {
        return this.fields.includes(error.field);
      });
    }
    return errors;
  }
  terminalLoc(locArray: Array<string>) {
    let loc = locArray[0];
    for (let i = 1; i < locArray.length; i++) {
      if (locArray[i] != "__root__") {
        loc = locArray[i];
      } else {
        break;
      }
    }
    return loc;
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped></style>
