const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

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
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });
  
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
