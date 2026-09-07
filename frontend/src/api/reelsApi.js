import axiosClient from './axiosClient'

export const reelsApi = {
  list: (params) => axiosClient.get('/reels/', { params }).then(r => r.data),
  get: (id) => axiosClient.get(`/reels/${id}`).then(r => r.data),
  create: (data) => axiosClient.post('/reels/', data).then(r => r.data),
  like: (id) => axiosClient.post(`/reels/${id}/like`).then(r => r.data),
  save: (id) => axiosClient.post(`/reels/${id}/save`).then(r => r.data),
  feed: (params) => axiosClient.get('/feed/', { params }).then(r => r.data),
}
