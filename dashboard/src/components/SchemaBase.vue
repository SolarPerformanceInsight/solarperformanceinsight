/* Base class for Vue components to access the API spec definitions and handle.
 * validation. Components should implement a getter for apiComponentName that
 * returns the string name of the schema found in the OpenAPI "components"
 * field.
 * 
 */
<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";

  @Component
  export default class SchemaBase extends Vue {
    errors: Record<string, any> = {};

    get definitions() {
      /* Get the api definition of this object */
      return this.$validator.getComponentSpec(this.apiComponentName);
    }

    get apiComponentName(): string {
      throw new Error('apiComponentName getter not implemented.');
    }

    setValidationResult(validity: boolean) {
      if (!validity) {
        const errors = this.$validator.getErrors();
        const currentErrors: Record<string, any> = {};
        errors.forEach(function(error: Record<string, any>) {
          const field = error.dataPath.split("/").pop();
          const message = error.message;
          currentErrors[field] = message;
        });
        this.errors = currentErrors;
      } else {
        this.errors = {};
      }
    }
  }
</script>
