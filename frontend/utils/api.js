const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

/**
 * Normalize and resolve the API request URL adaptively.
 * Handles bases with or without '/api' and endpoints with or without '/api'.
 */
const getApiUrl = (endpoint) => {
  // Normalize base URL: strip trailing slashes
  let base = API_BASE_URL.replace(/\/+$/, '');
  
  // Normalize endpoint: ensure it starts with a single slash
  let cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  
  // Case 1: Base ends with '/api' and endpoint starts with '/api/'
  if (base.endsWith('/api') && cleanEndpoint.startsWith('/api/')) {
    return `${base}${cleanEndpoint.substring(4)}`;
  }
  
  // Case 2: Base does NOT end with '/api' and endpoint does NOT start with '/api/'
  if (!base.endsWith('/api') && !cleanEndpoint.startsWith('/api/')) {
    return `${base}/api${cleanEndpoint}`;
  }
  
  // Case 3: Matches correctly (one has '/api', one does not)
  return `${base}${cleanEndpoint}`;
};

/**
 * Retrieve the JWT auth token from localStorage if in browser environment.
 */
export const getToken = () => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('token');
  }
  return null;
};

/**
 * Store or remove the JWT auth token.
 */
export const setToken = (token) => {
  if (typeof window !== 'undefined') {
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  }
};

/**
 * Execute HTTP requests to the FastAPI backend service.
 */
async function request(endpoint, options = {}) {
  const token = getToken();
  
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  };
  
  const targetUrl = getApiUrl(endpoint);
  
  let response;
  try {
    response = await fetch(targetUrl, {
      ...options,
      headers,
    });
  } catch (netErr) {
    throw new Error('Failed to connect to the backend server. Please verify your API URL configuration or wait for the Render cloud service to wake up.');
  }
  
  if (!response.ok) {
    let errorMessage = 'An error occurred while calling the service.';
    try {
      const errJson = await response.json();
      if (errJson && errJson.detail) {
        if (typeof errJson.detail === 'string') {
          errorMessage = errJson.detail;
        } else if (Array.isArray(errJson.detail)) {
          errorMessage = errJson.detail.map(e => e.msg).join(', ');
        }
      }
    } catch (e) {
      // Fallback if not JSON
    }
    throw new Error(errorMessage);
  }
  
  return response.json();
}

export const api = {
  get: (endpoint, options = {}) => request(endpoint, { method: 'GET', ...options }),
  post: (endpoint, data, options = {}) => request(endpoint, { method: 'POST', body: JSON.stringify(data), ...options }),
  delete: (endpoint, options = {}) => request(endpoint, { method: 'DELETE', ...options }),
};
