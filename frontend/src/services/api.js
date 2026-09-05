import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

export const getAnalytics = async () => {
  const response = await api.get("/analytics");
  return response.data;
};

export const getGrowth = async () => {
  const response = await api.get("/ai/growth");
  return response.data;
};

export const getOffers = async () => {
  const response = await api.get("/offers");
  return response.data;
};

export const getExperiments = async () => {
  const response = await api.get("/experiments");
  return response.data;
};

export const getAIActions = async () => {
  const response = await api.get("/ai/actions");
  return response.data;
};

export default api;