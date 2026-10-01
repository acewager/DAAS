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

/**
 * Django session authentication enforces CSRF on unsafe methods. The
 * csrftoken cookie is seeded by GET /auth/csrf/ at application start
 * (AuthContext); send its value as the X-CSRFToken header the backend checks.
 */
apiClient.interceptors.request.use((config) => {
  if (config.method && ["post", "put", "patch", "delete"].includes(config.method)) {
    const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    if (match) {
      config.headers.set("X-CSRFToken", decodeURIComponent(match[1]));
    }
  }
  return config;
});

export default apiClient;
