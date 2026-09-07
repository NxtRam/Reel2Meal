import axiosClient from './axiosClient'

export const menuApi = {
  getByReel: (reelId) => axiosClient.get(`/menu/reel/${reelId}`).then(r => r.data),
  getItem: (itemId) => axiosClient.get(`/menu/item/${itemId}`).then(r => r.data),
}
