import axios from "axios";

export const http = axios.create({
  baseURL: "/api",
  timeout: 10000,
  withCredentials: true,
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken"
});
