import { System } from "../types/System";

export const state = {
  systems: {} as Record<string, System>,
  loading: true
};

export type State = typeof state;
