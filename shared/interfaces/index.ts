import { z } from "zod";

const flightDataSchema = z.object({
  month: z.number(),
  day: z.number(),
  dayOfWeek: z.number(),
  scheduledDeparture: z.number(),
  originAirport: z.number(),
  destinationAirport: z.number(),
});

export type FlightData = z.infer<typeof flightDataSchema>;

export const trainingFlightDataSchema = flightDataSchema.extend({
  isDelayed: z.boolean(),
});

export type TrainingFlightData = z.infer<typeof trainingFlightDataSchema>;

export type PredictionResult = {
  label: string;
  voteCounts: {
    "on-time": number;
    delayed: number;
  };
  votes: {
    index: number;
    distance: number;
    label: string;
  }[];
};
