import axiosClient from './axiosClient'

export const authApi = {
  register: (data) => axiosClient.post('/auth/register', data).then(r => r.data),
  registerRestaurant: (data) => axiosClient.post('/auth/register/restaurant', data).then(r => r.data),
  login: (data) => axiosClient.post('/auth/login', data).then(r => r.data),
  me: () => axiosClient.get('/auth/me').then(r => r.data),
}
