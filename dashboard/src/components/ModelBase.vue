<!--
Base class for Vue components to access the API spec definitions and handle
validation.
Components should implement a getter for `apiComponentName` that  returns
the string name of the schema found in the OpenAPI "components"
field. This name will be used to access the proper definitions, and as an
argument to the `validate` function. See `src/types/validator/Validator.ts`.

Validation:
  Components should implement a watch function that calls
  `this.$validator.validate(this.apiComponentName, <object>).then(this.setValidationResult)`
  where object is the system model object to validate.
-->
<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component
export default class ModelBase extends Vue {
  errors: Record<string, any> = {};
  extraErrors: Record<string, any> = {};

  get validatorInit() {
    return this.$validator.initialized;
  }
  get definitions() {
    /* Get the api definition of this object */
    return this.$validator.getComponentSpec(this.apiComponentName);
  }

  get apiComponentName(): string {
    throw new Error("apiComponentName getter not implemented.");
  }

  extraValidation() {
    // Function for adding an extra validation step. Should set this.extraErrors with a fieldname key
    // and string error message value. Implementations should clear any errors they set when valid.
    return true;
  }
  setValidationResult(validity: boolean) {
    const customValidity = this.extraValidation();
    validity = validity && customValidity;
    if (!validity) {
      const errors = this.$validator.getErrors();
      const currentErrors: Record<string, any> = {};
      if (errors) {
        errors.forEach(function(error: Record<string, any>) {
          const field = error.dataPath.split("/").pop();
          const message = error.message;
          currentErrors[field] = message;
        });
      }
      // Insert errors and priorities custom messages
      this.errors = { ...this.extraErrors, ...currentErrors };
    } else {
      this.errors = {};
    }

    this.$emit("updateValidity", validity);
  }
}
</script>
