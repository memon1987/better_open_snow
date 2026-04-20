import resorts from "../resorts.seed.json";

export type ResortPass = "epic" | "ikon";

export interface ResortSeed {
  resort_id: string;
  name: string;
  pass: ResortPass;
  state: string;
  base_lat: number;
  base_lon: number;
  base_elevation_ft: number;
  summit_elevation_ft: number;
  snotel_triplet: string;
  timezone: string;
}

export const RESORTS: readonly ResortSeed[] = resorts as ResortSeed[];
