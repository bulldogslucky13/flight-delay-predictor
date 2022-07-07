import axios from "axios";
import { useCallback, useState } from "react";
import { z } from "zod";
import { requestBodySchema } from "../pages/api/prediction";
import { PredictionResult } from "../shared/interfaces";

export const useFlightPrediction = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);

  const sendPrediction = useCallback(
    async (data: z.infer<typeof requestBodySchema>) => {
      setIsLoading(true);
      setPrediction(null);
      try {
        const predictionResult = await axios.post<{ result: PredictionResult }>(
          "/api/prediction",
          data
        );
        setPrediction(predictionResult.data.result);
      } catch (error) {
        console.error("Oops! An error occured.", error);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { sendPrediction, isLoading, prediction };
};
