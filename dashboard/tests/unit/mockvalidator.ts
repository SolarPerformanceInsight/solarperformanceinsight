import APISpec from "./openapi.json";
import { APIValidator } from "@/types/validation/Validator";

const $validator = new APIValidator();

$validator.getAPISpec = jest.fn().mockResolvedValue(APISpec);

export { $validator };
