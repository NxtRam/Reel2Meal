import { useEffect, useRef, useState } from 'react'
import 'leaflet/dist/leaflet.css'

/**
 * DeliveryMapModal
 * Shows a live delivery tracking map:
 *   🍽️ Restaurant  — green pin (origin)
 *   🏠 Customer   — blue pin (destination = browser geolocation)
 *   🛵 Rider      — animated orange marker that moves along the route
 */

const RIDER_STEPS = 60          // animation steps along the route
const STEP_INTERVAL_MS = 1200   // ms per step

function lerp(a, b, t) { return a + (b - a) * t }

export default function DeliveryMapModal({ order, onClose }) {
  const mapRef      = useRef(null)
  const mapInstance = useRef(null)
  const riderMarker = useRef(null)
  const stepRef     = useRef(0)
  const timerRef    = useRef(null)

  const [customerPos, setCustomerPos] = useState(null)
  const [eta, setEta]                 = useState(null)

  const restLat  = order.restaurant_lat  ?? 12.9716
  const restLng  = order.restaurant_lng  ?? 77.5946
  const restName = order.restaurant_name ?? 'Restaurant'

  // ── Get customer location ──────────────────────────────────────────────────
  useEffect(() => {
    if (!navigator.geolocation) {
      setCustomerPos({ lat: restLat + 0.027, lng: restLng + 0.027 })
      return
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => setCustomerPos({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      () => setCustomerPos({ lat: restLat + 0.027, lng: restLng + 0.027 }),
      { timeout: 6000 }
    )
  }, [])

  // ── Build map once customer position is known ─────────────────────────────
  useEffect(() => {
    if (!customerPos || !mapRef.current || mapInstance.current) return

    import('leaflet').then((L) => {
      delete L.Icon.Default.prototype._getIconUrl
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
        iconUrl:       'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
        shadowUrl:     'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
      })

      const midLat = (restLat + customerPos.lat) / 2
      const midLng = (restLng + customerPos.lng) / 2

      const map = L.map(mapRef.current, { zoomControl: false }).setView([midLat, midLng], 13)
      mapInstance.current = map

      // Dark map tiles
      L.tileLayer(
        'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        { attribution: '© OpenStreetMap © CARTO', maxZoom: 19 }
      ).addTo(map)

      L.control.zoom({ position: 'bottomright' }).addTo(map)

      // Restaurant marker (green)
      const restIcon = L.divIcon({
        html: `<div style="background:#22c55e;width:38px;height:38px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);border:3px solid #fff;box-shadow:0 2px 10px rgba(0,0,0,.6)"><span style="transform:rotate(45deg);display:block;text-align:center;line-height:32px;font-size:17px">🍽️</span></div>`,
        className: '',
        iconSize: [38, 38],
        iconAnchor: [19, 38],
      })
      L.marker([restLat, restLng], { icon: restIcon })
        .addTo(map)
        .bindPopup(`<b>${restName}</b><br>Your order is here!`)

      // Customer marker (blue)
      const custIcon = L.divIcon({
        html: `<div style="background:#3b82f6;width:34px;height:34px;border-radius:50%;border:3px solid #fff;box-shadow:0 2px 10px rgba(0,0,0,.6);display:flex;align-items:center;justify-content:center;font-size:17px">🏠</div>`,
        className: '',
        iconSize: [34, 34],
        iconAnchor: [17, 17],
      })
      L.marker([customerPos.lat, customerPos.lng], { icon: custIcon })
        .addTo(map)
        .bindPopup('<b>Your Location</b><br>Delivery destination')

      // Route polyline
      const routeLine = L.polyline(
        [[restLat, restLng], [customerPos.lat, customerPos.lng]],
        { color: '#f97316', weight: 4, dashArray: '10 8', opacity: 0.9 }
      ).addTo(map)

      map.fitBounds(routeLine.getBounds(), { padding: [52, 52] })

      // Rider marker
      const riderIcon = L.divIcon({
        html: `<div style="background:#f97316;width:42px;height:42px;border-radius:50%;border:3px solid #fff;box-shadow:0 2px 14px rgba(249,115,22,.7);display:flex;align-items:center;justify-content:center;font-size:21px">🛵</div>`,
        className: '',
        iconSize: [42, 42],
        iconAnchor: [21, 21],
      })
      riderMarker.current = L.marker([restLat, restLng], { icon: riderIcon, zIndexOffset: 1000 })
        .addTo(map)
        .bindPopup('<b>Your Delivery Rider</b><br>On the way! 🚀')

      // ETA
      const dist = Math.sqrt(
        Math.pow((customerPos.lat - restLat) * 111, 2) +
        Math.pow((customerPos.lng - restLng) * 111, 2)
      )
      setEta(Math.max(5, Math.round(dist * 3)))

      // Animate rider
      stepRef.current = 0
      timerRef.current = setInterval(() => {
        stepRef.current += 1
        if (stepRef.current > RIDER_STEPS) { clearInterval(timerRef.current); return }
        const t = stepRef.current / RIDER_STEPS
        riderMarker.current.setLatLng([
          lerp(restLat, customerPos.lat, t),
          lerp(restLng, customerPos.lng, t),
        ])
      }, STEP_INTERVAL_MS)
    })

    return () => {
      clearInterval(timerRef.current)
      if (mapInstance.current) { mapInstance.current.remove(); mapInstance.current = null }
    }
  }, [customerPos])

  return (
    <div className="fixed inset-0 z-50 flex flex-col bg-black">
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3 bg-black/90 backdrop-blur-md border-b border-white/10 shrink-0">
        <button
          onClick={onClose}
          className="w-9 h-9 rounded-full bg-white/10 flex items-center justify-center text-white hover:bg-white/20 transition"
        >✕</button>
        <div className="flex-1">
          <p className="text-white font-bold text-sm">🛵 Live Delivery Tracking</p>
          <p className="text-white/50 text-xs">Order #{order.id.slice(0, 8).toUpperCase()}</p>
        </div>
        {eta && (
          <div className="bg-orange-500/20 border border-orange-500/40 rounded-xl px-3 py-1.5 text-right">
            <p className="text-orange-400 font-bold text-sm">{eta} min</p>
            <p className="text-white/40 text-xs">ETA</p>
          </div>
        )}
      </div>

      {/* Status banner */}
      <div className="flex items-center gap-3 px-4 py-2.5 bg-orange-500/10 border-b border-orange-500/20 shrink-0">
        <span className="relative flex h-2.5 w-2.5 shrink-0">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-orange-500" />
        </span>
        <p className="text-orange-300 text-xs font-semibold">
          Rider on the way from <span className="text-white">{restName}</span>
        </p>
      </div>

      {/* Map */}
      <div className="flex-1 relative">
        {!customerPos && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/80 z-10 gap-3">
            <div className="w-10 h-10 border-2 border-orange-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-white/60 text-sm">Getting your location…</p>
          </div>
        )}
        <div ref={mapRef} className="w-full h-full" />
      </div>

      {/* Legend */}
      <div className="flex items-center justify-around px-4 py-3 bg-black/90 border-t border-white/10 shrink-0">
        {[
          { icon: '🍽️', label: restName.split(' ')[0], color: 'text-green-400' },
          { icon: '🛵', label: 'Rider',  color: 'text-orange-400' },
          { icon: '🏠', label: 'You',    color: 'text-blue-400' },
        ].map(({ icon, label, color }) => (
          <div key={label} className="flex items-center gap-1.5">
            <span className="text-lg">{icon}</span>
            <span className={`text-xs font-semibold ${color}`}>{label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
