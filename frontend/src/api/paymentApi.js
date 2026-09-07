import axiosClient from './axiosClient'

/**
 * paymentApi.js — Two-step Razorpay checkout API calls.
 *
 * Step 1: createOrder(data)
 *   POST /api/v1/payments/create-order
 *   Returns { razorpay_order_id, amount_paise, key_id, our_order_id, ... }
 *
 * Step 2: verifyPayment(data)
 *   POST /api/v1/payments/verify
 *   Returns { success, our_order_id, payment_status, message }
 *
 * On failure: reportFailure(orderId)
 *   POST /api/v1/payments/{orderId}/failure
 */

export const paymentApi = {
  /**
   * Create a Razorpay order.
   * @param {{ reel_id: string, quantity: number, food_item_id?: string, note?: string }} data
   */
  createOrder: (data) =>
    axiosClient.post('/payments/create-order', data).then((r) => r.data),

  /**
   * Verify Razorpay payment signature after checkout.
   * @param {{ our_order_id: string, razorpay_order_id: string, razorpay_payment_id: string, razorpay_signature: string }} data
   */
  verifyPayment: (data) =>
    axiosClient.post('/payments/verify', data).then((r) => r.data),

  /**
   * Report that the user cancelled / dismissed the Razorpay popup.
   * @param {string} orderId — our internal Order.id
   */
  reportFailure: (orderId) =>
    axiosClient.post(`/payments/${orderId}/failure`).catch(() => {}), // best-effort
}
