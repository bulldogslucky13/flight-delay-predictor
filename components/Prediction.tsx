import { Field, Form, Formik } from "formik";
import { useFlightPrediction } from "../hooks/useFlightPrediction";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { getCurrentFormattedTime } from "../utils/getCurrentFormattedTime";

const colorMap: Record<string, string> = {
  "on-time": "text-green-600",
  delayed: "text-red-600",
  loading: "",
};

export const Prediction = () => {
  const { sendPrediction, isLoading, prediction } = useFlightPrediction();

  return (
    <Formik
      initialValues={{
        originAirport: "",
        destinationAirport: "",
        departureDate: new Date(),
        scheduledDepartureTime: getCurrentFormattedTime(),
      }}
      onSubmit={(values) => {
        console.log(values);
        sendPrediction({
          destinationAirport: values.destinationAirport,
          originAirport: values.originAirport,
          day: values.departureDate.getDate(),
          dayOfWeek: values.departureDate.getDay(),
          month: values.departureDate.getMonth(),
          scheduledDeparture: Number(values.scheduledDepartureTime),
        });
      }}
    >
      {({ handleSubmit, setFieldValue, values }) => (
        <Form>
          <div className="bg-slate-300 px-10 py-8 round-lg">
            <h1 className="text-lg font-bold">Flight Delay Predictor</h1>
            <div className="flex flex-row">
              <div className="flex flex-col w-full">
                <label htmlFor="originAirport">Departure Airport</label>
                <Field
                  id="originAirport"
                  name="originAirport"
                  className="rounded-md flex-grow"
                  type="text"
                  as="input"
                />
              </div>
              <div className="flex flex-col pl-2">
                <label htmlFor="destinationAirport">Arrival Airport</label>
                <Field
                  as="input"
                  id="destinationAirport"
                  name="destinationAirport"
                  className="rounded-md flex-grow"
                  type="text"
                />
              </div>
            </div>
            <div className="flex flex-row pt-2">
              <div className="flex flex-col">
                <label htmlFor="departureDate">Departure Date</label>
                <DatePicker
                  id="departureDate"
                  selected={values.departureDate}
                  inline
                  onChange={(newDate: Date | null) => {
                    if (!newDate) return;
                    setFieldValue("departureDate", newDate);
                  }}
                />
                ;
              </div>
              <div className="flex flex-col pl-2">
                <label htmlFor="scheduledDepartureTime">Departure Time</label>
                <Field
                  as="input"
                  id="scheduledDepartureTime"
                  name="scheduledDepartureTime"
                  type="string"
                  className="rounded-md"
                />
              </div>
            </div>
            <div className="flex items-center pt-4 flex-col">
              <p className="font-semibold text-slate-700">
                Will this flight be delayed?
              </p>

              {!prediction && isLoading ? (
                <p className="uppercase font-bold">Predicting...</p>
              ) : null}

              {prediction ? (
                <>
                  <p
                    className={`${
                      colorMap[prediction?.label ?? ""] ?? ""
                    } uppercase font-bold`}
                  >
                    {prediction && prediction.label ? prediction.label : null}
                  </p>
                  <p>
                    On-Time: {prediction?.voteCounts["on-time"]} / Delayed:{" "}
                    {prediction?.voteCounts["delayed"]}
                  </p>
                </>
              ) : null}
            </div>
            <div className="flex justify-end pt-8">
              <button
                className="border-2 px-2 py-1 rounded-lg bg-white hover:bg-slate-50 hover:transition-colors 50ms"
                onClick={() => handleSubmit()}
                disabled={isLoading}
              >
                Predict
              </button>
            </div>
          </div>
        </Form>
      )}
    </Formik>
  );
};
