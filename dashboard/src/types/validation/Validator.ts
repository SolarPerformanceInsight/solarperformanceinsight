import Ajv from "ajv";

const apiUrl = "http://localhost:8888";

export class APIValidator {
  ajv: any;
  components: Record<string, any>;
  initialized: boolean;

  constructor() {
    this.ajv = new Ajv({
      keywords: ["openapi", "info", "paths", "components", "tags"],
      allErrors: true
    });
    this.components = {};
    this.initialized = false;
  }

  async init() {
    const spec = await this.getAPISpec();
    this.components = spec.components.schemas;
    this.ajv.addSchema(spec, "spi");
    this.initialized = true;
  }

  async getAPISpec() {
    return fetch(`${apiUrl}/openapi.json`).then(response => response.json());
  }

  getComponentSpec(componentName: string) {
    if (componentName in this.components) {
      return this.components[componentName];
    }
  }

  async validate(componentName: string, data: Record<string, any>) {
    console.log(this.getComponentSpec(componentName));
    const res = this.ajv.validate(
      { $ref: `spi#/components/schemas/${componentName}` },
      data
    );
    return res;
  }

  getErrors() {
    return this.ajv.errors;
  }
}
