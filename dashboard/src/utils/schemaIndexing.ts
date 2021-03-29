import { System } from "@/types/System";

export function indexSystemFromSchemaPath(
  system: System,
  schemaPath: Array<string> | string
) {
  let indices: Array<string>;
  let component: any;

  if (!Array.isArray(schemaPath)) {
    indices = schemaPath.split("/");
  } else {
    indices = [...schemaPath];
  }
  if (indices[0] == "") {
    // Pop an empty string, which can occur when "" or "/" is passed
    indices.shift();
  }
  if (!indices.length) {
    throw new Error("Invalid System Index: Empty");
  }
  component = system;

  // Pull first index, so the "" that exists for the root component does not
  // fail, and when we have a valid non-falsy index we'll traverse the system
  // as expected.
  // @ts-expect-error
  let index: string | number = indices.shift();

  while (index) {
    try {
      component = component[index];
    } catch (error) {
      // Handle if index does not exist in component, should only occur if system
      // parameter is null/undefined
      throw new error("invalid system index");
    }
    // If value is null/undefined index was invalid
    if (component == null) {
      throw new Error("Invalid System Index");
    }
    // @ts-expect-error
    index = indices.shift();
  }
  return component;
}
