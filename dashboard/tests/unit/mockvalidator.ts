import APISpec from "./openapi.json";
import { APIValidator } from "@/types/validation/Validator";

APIValidator.prototype.getAPISpec = jest.fn().mockResolvedValue(APISpec);

const $validator = new APIValidator();

export { $validator };
