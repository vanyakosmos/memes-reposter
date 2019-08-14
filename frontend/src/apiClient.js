import axios from 'axios'
import { getToken, removeToken, setToken } from "src/jwt"

const baseURL = process.env.GATSBY_API_URL;
const client = axios.create({ baseURL });

client.interceptors.request.use(
  function(config) {
    const token = getToken();
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  function(error) {
    return Promise.reject(error);
  },
);

export async function authObtain(username, password) {
  const res = await client.post(`auth/obtain/`, { username, password })
  const token = res.data.token;
  setToken(token)
  return token;
}

export async function authRefresh(token) {
  if (!token) {
    removeToken()
    throw "invalid token"
  }
  const res = await client.post(`auth/refresh/`, { token })
  const newToken = res.data.token;
  setToken(newToken)
  return newToken;
}

export async function authVerify(token) {
  const res = await client.post(`auth/verify/`, { token })
  const newToken = res.data.token;
  if (token === newToken) {
    setToken(newToken)
    return newToken
  }
  return null
}

export async function getRedditPosts(subreddit, ordering) {
  console.log('getRedditPosts')
  const res = await client.get(`reddit/posts/`, {
    params: { ordering, subreddit_name: subreddit },
  })
  console.log('getRedditPosts', res.data)
  return res.data.results;
}
