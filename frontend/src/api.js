const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1'

export async function api(path, options = {}) {
  const token = localStorage.getItem('accessToken')
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })
  const data = response.status === 204 ? null : await response.json()
  if (!response.ok) {
    const errors = Object.values(data || {}).flatMap(value =>
      Array.isArray(value) ? value : typeof value === 'object' && value !== null ? Object.values(value) : [value]
    ).filter(Boolean)
    throw new Error(data?.detail || data?.error || errors.join(' ') || 'Request failed')
  }
  return data
}

export async function login(email, password) {
  const data = await api('/token/', { method: 'POST', body: JSON.stringify({ email, password }) })
  localStorage.setItem('accessToken', data.access)
  localStorage.setItem('refreshToken', data.refresh)
  return data
}

export async function register(email, username, password) {
  return api('/register/', {
    method: 'POST',
    body: JSON.stringify({ email, username, password }),
  })
}

export function logout() {
  localStorage.removeItem('accessToken')
  localStorage.removeItem('refreshToken')
}
