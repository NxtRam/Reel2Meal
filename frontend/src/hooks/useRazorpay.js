import { useState, useEffect, useCallback } from 'react'

const RAZORPAY_SCRIPT_URL = 'https://checkout.razorpay.com/v1/checkout.js'

/**
 * useRazorpay — dynamically loads the Razorpay checkout script
 * and exposes an `openCheckout` function.
 *
 * Usage:
 *   const { ready, openCheckout } = useRazorpay()
 *
 *   openCheckout({
 *     key:          'rzp_test_...',
 *     order_id:     'order_XXXX',
 *     amount:       29900,           // paise
 *     currency:     'INR',
 *     name:         'Reel2Meal',
 *     description:  '2x Neapolitan Pizza',
 *     prefill:      { name: 'Ram', email: 'ram@example.com' },
 *     theme:        { color: '#ff6b35' },
 *     handler:      (response) => { ... },    // success callback
 *     modal:        { ondismiss: () => { ... } },
 *   })
 */
export function useRazorpay() {
  const [ready, setReady] = useState(false)

  useEffect(() => {
    // If already loaded (e.g. hot-reload), skip
    if (window.Razorpay) {
      setReady(true)
      return
    }

    const script = document.createElement('script')
    script.src = RAZORPAY_SCRIPT_URL
    script.async = true
    script.onload = () => setReady(true)
    script.onerror = () => console.error('Failed to load Razorpay checkout script')
    document.body.appendChild(script)

    return () => {
      // Don't remove the script on unmount — it's needed globally
    }
  }, [])

  const openCheckout = useCallback(
    (options) => {
      if (!ready || !window.Razorpay) {
        console.error('Razorpay script not loaded yet')
        return
      }
      const rzp = new window.Razorpay(options)
      rzp.open()
    },
    [ready]
  )

  return { ready, openCheckout }
}
