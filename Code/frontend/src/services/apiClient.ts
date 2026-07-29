import axios from "axios";

/**
 * Shared Axios instance.
 *
 * Per 08_Frontend_Architecture.md Section 9, components never call Axios
 * directly — they go through a service module, which uses this client.
 */
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true, // sends the Django session cookie
  headers: {
    "Content-Type": "application/json",
  },
});

export default apiClient;
