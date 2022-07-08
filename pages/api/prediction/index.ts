import { NextApiRequest, NextApiResponse } from "next";
import { z } from "zod";
import { FlightData, TrainingFlightData } from "../../../shared/interfaces";
import { airportMap } from "../../../shared/airportMap";
import KNN from "../../../server/knn";
import { createPrediction } from "./create-prediction";

export const requestBodySchema = z.object({
  originAirport: z.string().length(3),
  destinationAirport: z.string().length(3),
  day: z.number(),
  dayOfWeek: z.number(),
  month: z.number(),
  scheduledDeparture: z.number(),
});

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  const limit = 10000;

  const parsedBody = requestBodySchema.safeParse(req.body);

  if (!parsedBody.success) {
    return res.status(400).json({ error: parsedBody.error });
  }

  const bodyFlightData: FlightData = {
    ...parsedBody.data,
    originAirport: airportMap[parsedBody.data.originAirport],
    destinationAirport: airportMap[parsedBody.data.destinationAirport],
  };

  const { stream, results, failedResults } = createPrediction(limit);
  stream
    .on("end", function () {
      console.log(failedResults);
      return res.status(200).json({ results });
    })
    .on("close", function () {
      const knn = new KNN(51, results); // Trial and error was done to maximize precision
      const result = knn.predict(bodyFlightData);

      return res.status(200).json({ result });
    });
}
