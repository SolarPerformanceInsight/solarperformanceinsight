import { StoredSystem } from "../types/System";

export const state = {
  systems: {} as Record<string, StoredSystem>,
  loading: true
};

export type State = typeof state;
