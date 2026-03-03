import axios from "axios";

const api = axios.create({ baseURL: "/api" });

export const getSeasons = () => api.get("/seasons").then((r) => r.data);
export const getRaces = (season) => api.get(`/races?season=${season}`).then((r) => r.data);
export const getRace = (raceId) => api.get(`/races/${raceId}`).then((r) => r.data);
export const getRaceResults = (raceId) => api.get(`/races/${raceId}/results`).then((r) => r.data);
export const getFastestLaps = (raceId) => api.get(`/races/${raceId}/fastest-laps`).then((r) => r.data);
export const getLapTimes = (raceId, driverId) => {
  const q = driverId ? `?driver_id=${driverId}` : "";
  return api.get(`/races/${raceId}/lap-times${q}`).then((r) => r.data);
};
export const getTyreDegradation = (raceId) => api.get(`/races/${raceId}/tyre-degradation`).then((r) => r.data);
export const getStints = (raceId) => api.get(`/races/${raceId}/stints`).then((r) => r.data);
export const getPitStops = (raceId) => api.get(`/races/${raceId}/pit-stops`).then((r) => r.data);
export const getRacePace = (raceId) => api.get(`/races/${raceId}/race-pace`).then((r) => r.data);
export const getDriverStandings = (season) => api.get(`/standings/drivers?season=${season}`).then((r) => r.data);
export const getConstructorStandings = (season) => api.get(`/standings/constructors?season=${season}`).then((r) => r.data);
export const ingestRace = (season, round) =>
  api.post(`/ingest?season=${season}&round=${round}`).then((r) => r.data);
