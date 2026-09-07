import axiosClient from './axiosClient'

export const ordersApi = {
  /**
   * Place an order from a reel.
   * @param {{ reel_id: string, food_item_id?: string, restaurant_id?: string, quantity?: number, note?: string }} data
   */
  place: (data) => axiosClient.post('/orders/', data).then(r => r.data),

  /** List all orders for the authenticated user */
  list: () => axiosClient.get('/orders/').then(r => r.data),

  /** Get a single order by ID */
  get: (id) => axiosClient.get(`/orders/${id}`).then(r => r.data),

  /** Cancel a pending order */
  cancel: (id) => axiosClient.post(`/orders/${id}/cancel`).then(r => r.data),

  /** List all incoming orders for the restaurant (restaurant accounts only) */
  restaurantOrders: () => axiosClient.get('/orders/restaurant').then(r => r.data),

  /** Update the status of an order (restaurant accounts only) */
  updateStatus: (id, newStatus) => axiosClient.patch(`/orders/${id}/status`, { status: newStatus }).then(r => r.data),
}
