/* Allows us to add the Vue global validator class without Typescript
 * complaining.
 */
import Vue from "vue"
import { APIValidator } from "./types/validation/Validator";

declare module "vue/types/vue" {
  interface Vue {
    $validator: APIValidator;
  }
}
