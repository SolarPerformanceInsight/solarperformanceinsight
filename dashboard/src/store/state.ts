import { System } from "../types/System";

export const state = {
  systems: [] as Array<System>
};

export type State = typeof state;
