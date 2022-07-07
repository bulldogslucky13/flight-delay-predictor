import { FlightData, TrainingFlightData } from "../../shared/interfaces";
import { distance } from "../../utils/distance";

class KNN {
  private k: number;

  private data: TrainingFlightData[];

  constructor(k = 1, data: TrainingFlightData[]) {
    this.k = k;
    this.data = data;
  }

  private generateDistanceMap(point: FlightData) {
    const map: { index: number; distance: number; label: string }[] = [];

    let maxNeighborDistance: number | undefined;

    for (let index = 0, len = this.data.length; index < len; index++) {
      const otherPoint = this.data[index];

      const otherPointLabel = this.data[index].isDelayed; // We will define a "delay" as a duration > 0

      const currentPointDistance = distance(point, otherPoint);

      /**
       * We only want to add an item to the map if it will become a neighbor. We can keep this
       * map.length <= k by utilizing this logic.
       */
      if (!maxNeighborDistance || currentPointDistance < maxNeighborDistance) {
        // Only add an item if it's closer than the farthest of the candidates
        map.push({
          index,
          distance: currentPointDistance,
          label: otherPointLabel ? "delayed" : "on-time",
        });

        // Sort the map so the closest is first
        map.sort((a, b) => (a.distance < b.distance ? -1 : 1));

        // If the map became too long, drop the farthest item
        if (map.length > this.k) {
          map.pop();
        }

        // Update this value for the next comparison
        maxNeighborDistance = map[map.length - 1].distance;
      }
    }

    return map;
  }

  predict(point: FlightData) {
    const map = this.generateDistanceMap(point);

    /**
     * We only want up to k votes
     */
    const votes = map.slice(0, this.k);

    /**
     * Making a human-readable version of the votes with the proper counts each way.
     * e.x - { delayed: 19, on-time: 18 }
     */
    const voteCounts = votes.reduce<Record<string, number>>(
      (obj, vote) =>
        Object.assign({}, obj, {
          [vote.label]: (obj[vote.label as string] || 0) + 1,
        }),
      {}
    );

    /**
     * This puts the winning label first
     */
    const sortedVotes = Object.keys(voteCounts)
      .map((label) => ({ label, count: voteCounts[label] }))
      .sort((a, b) => (a.count > b.count ? -1 : 1));

    return {
      label: sortedVotes[0].label, // Winning label
      voteCounts,
      votes,
    };
  }
}
export default KNN;
