import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;
const LLM_API_BASE_URL = process.env.NEXT_PUBLIC_LLM_API_BASE_URL;

// Create axios instances for different base URLs
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

const llmApiClient = axios.create({
    baseURL: LLM_API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

// API wrapper functions
export const api = {
    // Generic methods for main API
    get: (url, config) => apiClient.get(url, config),
    post: (url, data, config) => apiClient.post(url, data, config),
    put: (url, data, config) => apiClient.put(url, data, config),
    patch: (url, data, config) => apiClient.patch(url, data, config),
    delete: (url, config) => apiClient.delete(url, config),
};

// LLM API wrapper
export const llmApi = {
    // Generic methods for LLM API
    get: (url, config) => llmApiClient.get(url, config),
    post: (url, data, config) => llmApiClient.post(url, data, config),
    put: (url, data, config) => llmApiClient.put(url, data, config),
    patch: (url, data, config) => llmApiClient.patch(url, data, config),
    delete: (url, config) => llmApiClient.delete(url, config),
};

export { apiClient, llmApiClient };
