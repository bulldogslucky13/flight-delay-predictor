import fs from "fs";
import csv from "csv-parser";
import { z } from "zod";
import { airportMap } from "../../../shared/airportMap";
import {
  TrainingFlightData,
  trainingFlightDataSchema,
} from "../../../shared/interfaces";

type RawTrainingFlightData = {
  ORIGIN_AIRPORT: string;
  DESTINATION_AIRPORT: string;
  DEPARTURE_DELAY?: string;
  DAY: string;
  DAY_OF_WEEK: string;
  MONTH: string;
  SCHEDULED_DEPARTURE: string;
};

function isRowTrainingFlightData(data: unknown): data is RawTrainingFlightData {
  return !!(
    typeof (data as RawTrainingFlightData)?.ORIGIN_AIRPORT === "string" &&
    typeof (data as RawTrainingFlightData)?.DESTINATION_AIRPORT === "string" &&
    typeof (data as RawTrainingFlightData)?.DEPARTURE_DELAY === "string" &&
    typeof (data as RawTrainingFlightData)?.DAY === "string" &&
    typeof (data as RawTrainingFlightData)?.DAY_OF_WEEK === "string" &&
    typeof (data as RawTrainingFlightData)?.MONTH === "string" &&
    typeof (data as RawTrainingFlightData)?.SCHEDULED_DEPARTURE === "string"
  );
}

export function createPrediction(limit: number = 10000) {
  const results: TrainingFlightData[] = [];
  const failedResults: string[] = [];

  const stream = fs
    .createReadStream(
      "/Users/cameronbristol/Desktop/OU/CS5593/flight-delay-predictor/server/data/flights.csv"
    )
    .pipe(csv())
    .on("data", function (row) {
      const shouldTakeValue = Math.floor(Math.random() * 20);
      if (!shouldTakeValue) return; // This means we have a 1/20 chance of picking the item

      const formatItem = z.preprocess((item) => {
        if (!isRowTrainingFlightData(item)) {
          return;
        }

        const {
          ORIGIN_AIRPORT,
          DEPARTURE_DELAY,
          DESTINATION_AIRPORT,
          DAY,
          DAY_OF_WEEK,
          MONTH,
          SCHEDULED_DEPARTURE,
        } = item;

        const trainingFlightData: TrainingFlightData = {
          originAirport: airportMap[ORIGIN_AIRPORT],
          destinationAirport: airportMap[DESTINATION_AIRPORT],
          isDelayed: !!(DEPARTURE_DELAY && Number(DEPARTURE_DELAY) > 0),
          day: Number(DAY),
          dayOfWeek: Number(DAY_OF_WEEK),
          month: Number(MONTH),
          scheduledDeparture: Number(SCHEDULED_DEPARTURE),
        };
        return trainingFlightData;
      }, trainingFlightDataSchema);

      try {
        const formattedItem = formatItem.safeParse(row);
        if (!formattedItem.success) {
          console.error("Failure!", row);
          failedResults.push(row.toString());
        } else {
          results.push(formattedItem.data);
        }
      } catch (error) {
        console.error("Failure!", row, error);
        stream.destroy();
      }

      if (results.length >= limit) {
        stream.destroy();
      }
    });

  return { stream, results, failedResults };
}
