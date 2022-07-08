# Flight Delay Predictor

Welcome to the Flight Delay Predictor! This is the repo for Group 8's CS5593 project.

This is a Next.JS application that predict whether or not a flight will be delayed based on a variety of sources. Don't believe me? Check it out yourself!

## Running the Program Locally

1. Install [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
2. In a terminal, navigate to your `flight-delay-predictor` folder
3. Run:

```
npm install
```

4. Download the `flights.csv` file from [kaggle](https://www.kaggle.com/datasets/usdot/flight-delays?select=flights.csv)
5. Drop this in `/server/data` and replace the file path in `/pages/api/prediction/create-prediction`'s `createReadStream` variable with the correct one for your machine
6. Run

```
npm run dev
```

7. In your browser, navigate to [localhost:3000](http://localhost:3000) and begin using the app!
