import { NextApiRequest, NextApiResponse } from "next";
import { FlightData } from "../../../shared/interfaces";
import { airportMap } from "../../../shared/airportMap";
import KNN from "../../../server/knn";
import { createPrediction } from "./create-prediction";

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  const { stream, results, failedResults } = createPrediction();
  stream
    .on("end", function () {
      console.log(failedResults);
      return res.status(200).json({ results });
    })
    .on("close", function () {
      const knn = new KNN(51, results);

      const shuffledResults = results.sort(() => 0.5 - Math.random());

      const numberOfResultsToTest = 500;
      const sampleToTest = shuffledResults.slice(0, numberOfResultsToTest);

      const numberOfTrials: number = 10;
      let correct: number = 0;
      let incorrect: number = 0;
      let totalDelayed: number = 0;
      let totalNonDelayed: number = 0;
      let totalExpectedDelayed: number = 0;
      let totalExpectedNonDelayed: number = 0;

      for (let i = 0; i < numberOfTrials; i++) {
        sampleToTest.map((s) => {
          const result = knn.predict(s);

          if (s.isDelayed) {
            totalExpectedDelayed += 1;
          } else {
            totalExpectedNonDelayed += 1;
          }

          if (result.label === "delayed") {
            totalDelayed += 1;
          } else {
            totalNonDelayed += 1;
          }

          if (result.label)
            if (
              (result.label === "delayed" && s.isDelayed) ||
              (result.label !== "delayed" && !s.isDelayed)
            ) {
              correct += 1;
              return;
            }
          incorrect += 1;
        });
      }

      const correctAverage = correct / numberOfTrials;
      const incorrectAverage = incorrect / numberOfTrials;
      const precision = correctAverage / numberOfResultsToTest;
      const recall =
        (totalDelayed / totalExpectedDelayed +
          totalNonDelayed / totalExpectedNonDelayed) /
        2;
      const fScore = 2 * ((precision * recall) / (precision + recall));

      console.log(
        `Average Correct: ${correctAverage} | Average Incorrect: ${incorrectAverage} | Precision: ${precision} | Recall: ${recall} | F-Score ${fScore}`
      );

      return res.status(200).json({
        correct: correctAverage,
        incorrect: incorrectAverage,
        precision,
        recall,
        fScore,
      });
    });
}
