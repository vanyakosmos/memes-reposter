const LOCAL_STORAGE_KEY = 'jwt';

export function getToken() {
  return window.localStorage.getItem(LOCAL_STORAGE_KEY);
}

export function setToken(token) {
  return window.localStorage.setItem(LOCAL_STORAGE_KEY, token);
}

export function removeToken() {
  return window.localStorage.removeItem(LOCAL_STORAGE_KEY);
}
