import { useEffect, useState } from 'react'

export function useToast() {
  const [toasts, setToasts] = useState([])

  const show = (message, type = 'info') => {
    const id = Date.now()
    setToasts((t) => [...t, { id, message, type }])
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 3000)
  }

  return { toasts, show }
}

export default function Toast({ toasts }) {
  return (
    <div className="fixed bottom-24 left-1/2 -translate-x-1/2 z-[100] flex flex-col gap-2 items-center pointer-events-none">
      {toasts.map((t) => (
        <div
          key={t.id}
          className="animate-fade-in px-4 py-2 rounded-full text-sm font-medium glass text-white shadow-lg"
        >
          {t.message}
        </div>
      ))}
    </div>
  )
}
