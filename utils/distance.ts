import { FlightData } from "../shared/interfaces";

export function distance(a: FlightData, b: FlightData) {
  let sum = 0;
  for (let i = 0; i < Object.values(a).length; i++) {
    sum += Object.values(a)[i] - Object.values(b)[i];
  }
  return Math.sqrt(sum);
}
