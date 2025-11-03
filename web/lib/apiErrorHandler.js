/**
 * Global API Error Handler
 * Provides friendly error messages for common API errors
 */

export class ApiError extends Error {
    constructor(message, status, data) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.data = data;
    }
}

/**
 * Get a friendly error message based on the error response
 */
export function getFriendlyErrorMessage(error, response, data) {
    // Check for network errors
    if (!response) {
        if (error.message === 'Failed to fetch') {
            return 'Unable to connect to the server. Please check your internet connection.';
        }
        return 'Network error. Please try again.';
    }

    const status = response.status || data?.status;

    // Handle specific status codes
    switch (status) {
        case 400:
            return data?.message || 'Invalid request. Please check your input.';

        case 401:
            return data?.message || 'Session expired. Please login again.';

        case 403:
            return 'Access denied. You do not have permission to perform this action.';

        case 404:
            return 'The requested resource was not found. Please contact support if this persists.';

        case 429:
            return 'Too many requests. Please wait a moment and try again.';

        case 500:
            return data?.message || 'Server error. Please try again later.';

        case 502:
        case 503:
        case 504:
            return 'The server is temporarily unavailable. Please try again in a few moments.';

        default:
            return data?.message || data?.error || 'Something went wrong. Please try again.';
    }
}

/**
 * Handle fetch response and throw appropriate errors
 * @param {Response} response - Fetch API response
 * @param {string} context - Context for the error (e.g., 'sending message', 'login')
 * @returns {Promise<any>} - Parsed response data
 */
export async function handleApiResponse(response, context = 'processing your request') {
    let data;

    try {
        data = await response.json();
    } catch (e) {
        // If response is not JSON
        if (!response.ok) {
            const message = getFriendlyErrorMessage(null, response, {});
            throw new ApiError(message, response.status, null);
        }
        return null;
    }

    // Check for 401 in both HTTP status and response body
    if (response.status === 401 || data?.status === 401) {
        const message = data?.message || 'Your session has expired. Please login again.';
        throw new ApiError(message, 401, data);
    }

    // Handle other error responses
    // Check HTTP status first, then data.status for API-level errors
    if (!response.ok) {
        const message = getFriendlyErrorMessage(null, response, data);
        throw new ApiError(message, response.status, data);
    }

    // Check for API-level errors in data.status (but allow 200-299)
    if (data?.status && (data.status < 200 || data.status >= 400)) {
        const message = getFriendlyErrorMessage(null, response, data);
        throw new ApiError(message, data.status, data);
    }

    return data;
}

/**
 * Wrapper for fetch with automatic error handling
 * @param {string} url - The URL to fetch
 * @param {object} options - Fetch options
 * @param {string} context - Context for error messages
 * @returns {Promise<any>} - Response data
 */
export async function apiFetch(url, options = {}, context = 'processing your request') {
    try {
        const response = await fetch(url, options);
        return await handleApiResponse(response, context);
    } catch (error) {
        // If it's already an ApiError, re-throw it
        if (error instanceof ApiError) {
            throw error;
        }

        // Handle network errors
        const message = getFriendlyErrorMessage(error, null, null);
        throw new ApiError(message, null, null);
    }
}

/**
 * Log error for debugging while showing friendly message to user
 */
export function logAndGetUserMessage(error, context = '') {
    console.error(`API Error${context ? ` (${context})` : ''}:`, {
        message: error.message,
        status: error.status,
        data: error.data,
        stack: error.stack
    });

    // Return user-friendly message
    if (error instanceof ApiError) {
        return error.message;
    }

    return getFriendlyErrorMessage(error, null, null);
}
