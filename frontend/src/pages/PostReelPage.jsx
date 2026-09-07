import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { reelsApi } from '../api/reelsApi'
import Toast, { useToast } from '../components/shared/Toast'
import { isYouTubeUrl } from '../utils/youtube'

export default function PostReelPage() {
  const { user, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const { toasts, show } = useToast()
  
  const [loading, setLoading] = useState(false)
  const [reel, setReel] = useState({
    title: '',
    description: '',
    video_url: '',
    thumbnail_url: '',
    audio_url: '',
    cuisine_tag: ''
  })

  // Food item being built
  const [newItem, setNewItem] = useState({
    name: '',
    price: '',
    category: 'Main Course',
    is_veg: true,
    description: '',
    image_url: ''
  })

  // Menu items list
  const [foodItems, setFoodItems] = useState([])

  // Redirect if not authorized as restaurant
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
    } else if (user && user.role !== 'restaurant') {
      navigate('/')
    }
  }, [user, isAuthenticated, navigate])

  const setReelVal = (k) => (e) => setReel((r) => ({ ...r, [k]: e.target.value }))
  const setNewItemVal = (k) => (e) => {
    const val = e.target.type === 'checkbox' ? e.target.checked : e.target.value
    setNewItem((i) => ({ ...i, [k]: val }))
  }

  // Preset data for easy testing
  const autofillDemoData = () => {
    setReel({
      title: 'Creamy Garlic Butter Pasta 🍝',
      description: 'Watch this delicious pasta cook in real-time. Tossed with olive oil, minced garlic, parmesan cheese, and fresh parsley!',
      video_url: 'https://player.vimeo.com/external/371433846.sd.mp4?s=236da2f3c0227e339d37a2f5f6e80b271d9d9f96&profile_id=165&oauth2_token_id=57447761',
      thumbnail_url: 'https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?auto=compress&cs=tinysrgb&w=600',
      audio_url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3',
      cuisine_tag: 'Italian'
    })

    setFoodItems([
      {
        name: 'Sizzling Garlic Butter Pasta',
        price: '349.00',
        category: 'Main Course',
        is_veg: true,
        description: 'Warm fettuccine pasta in rich butter sauce, seasoned with roasted garlic and fresh herbs.',
        image_url: 'https://images.pexels.com/photos/1437267/pexels-photo-1437267.jpeg?auto=compress&cs=tinysrgb&w=600'
      },
      {
        name: 'Crispy Cheese Garlic Bread',
        price: '149.00',
        category: 'Starter',
        is_veg: true,
        description: 'Toasted baguette slices slathered in garlic butter and topped with bubbling mozzarella.',
        image_url: 'https://images.pexels.com/photos/70497/pexels-photo-70497.jpeg?auto=compress&cs=tinysrgb&w=600'
      }
    ])
    show('Demo data loaded! 🍝')
  }

  const addFoodItem = () => {
    if (!newItem.name.trim()) {
      show('Food item name is required.', 'error')
      return
    }
    if (!newItem.price || isNaN(Number(newItem.price)) || Number(newItem.price) <= 0) {
      show('Please enter a valid price.', 'error')
      return
    }

    setFoodItems((prev) => [...prev, { ...newItem, price: Number(newItem.price).toFixed(2) }])
    
    // Reset form
    setNewItem({
      name: '',
      price: '',
      category: 'Main Course',
      is_veg: true,
      description: '',
      image_url: ''
    })
    show('Food item added to menu!')
  }

  const removeFoodItem = (index) => {
    setFoodItems((prev) => prev.filter((_, i) => i !== index))
    show('Food item removed.')
  }

  const handlePublish = async (e) => {
    e.preventDefault()
    if (!reel.title.trim()) {
      show('Reel title is required.', 'error')
      return
    }
    if (!reel.video_url.trim()) {
      show('Video URL is required.', 'error')
      return
    }

    setLoading(true)
    try {
      await reelsApi.create({
        ...reel,
        food_items: foodItems.map((item) => ({
          name: item.name,
          description: item.description || null,
          price: parseFloat(item.price),
          currency: 'INR',
          image_url: item.image_url || null,
          category: item.category || null,
          is_veg: item.is_veg
        }))
      })
      show('Reel published successfully! 🎉')
      setTimeout(() => navigate('/'), 1000)
    } catch (err) {
      show(err.response?.data?.detail ?? 'Failed to publish reel. Please try again.', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-surface pt-20 pb-12 px-4">
      <div className="glass p-6 sm:p-8 rounded-2xl max-w-2xl w-full mx-auto border border-white/10 shadow-2xl relative">
        
        {/* Autofill Demo Data Button */}
        <button
          onClick={autofillDemoData}
          className="absolute top-6 right-6 text-xs text-brand-400 border border-brand-500/30 bg-brand-500/10 px-3 py-1.5 rounded-lg hover:bg-brand-500/25 transition-all font-semibold active:scale-95"
        >
          🪄 Autofill Demo
        </button>

        <h1 className="text-2xl sm:text-3xl font-extrabold text-white mb-6 gradient-text">
          Create Food Reel
        </h1>

        <form onSubmit={handlePublish} className="flex flex-col gap-6">
          
          {/* Reel Details Section */}
          <div className="flex flex-col gap-4">
            <h2 className="text-sm font-semibold text-white/50 uppercase tracking-wider">
              Reel Information
            </h2>
            
            <div className="flex flex-col gap-1">
              <label className="text-xs font-semibold text-white/70">Reel Title *</label>
              <input
                type="text"
                value={reel.title}
                onChange={setReelVal('title')}
                placeholder="e.g. Fluffy Chocolate Souffle 🍫"
                required
                className="w-full bg-surface-overlay border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-white/30 focus:outline-none focus:border-brand-500 transition-colors text-sm"
              />
            </div>

            <div className="flex flex-col gap-1">
              <label className="text-xs font-semibold text-white/70">Description</label>
              <textarea
                value={reel.description}
                onChange={setReelVal('description')}
                placeholder="Describe your dish or share the recipe..."
                rows={3}
                className="w-full bg-surface-overlay border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-white/30 focus:outline-none focus:border-brand-500 transition-colors text-sm resize-none"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex flex-col gap-1">
                <label className="text-xs font-semibold text-white/70">
                  Video URL (MP4 or YouTube / YouTube Shorts) *
                </label>
                <div className="relative">
                  <input
                    type="url"
                    value={reel.video_url}
                    onChange={setReelVal('video_url')}
                    placeholder="https://youtube.com/shorts/... or https://example.com/video.mp4"
                    required
                    className="w-full bg-surface-overlay border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-white/30 focus:outline-none focus:border-brand-500 transition-colors text-sm pr-24"
                  />
                  {reel.video_url && (
                    <span className={`absolute right-2 top-1/2 -translate-y-1/2 text-xs font-bold px-2 py-0.5 rounded-full ${
                      isYouTubeUrl(reel.video_url)
                        ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                        : 'bg-green-500/20 text-green-400 border border-green-500/30'
                    }`}>
                      {isYouTubeUrl(reel.video_url) ? '▶ YouTube' : '📁 Direct'}
                    </span>
                  )}
                </div>
                <p className="text-white/30 text-xs mt-0.5">
                  ✅ Supports YouTube Shorts, YouTube links, and direct MP4 URLs
                </p>
              </div>

              <div className="flex flex-col gap-1">
                <label className="text-xs font-semibold text-white/70">Thumbnail URL</label>
                <input
                  type="url"
                  value={reel.thumbnail_url}
                  onChange={setReelVal('thumbnail_url')}
                  placeholder="https://example.com/thumbnail.jpg"
                  className="w-full bg-surface-overlay border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-white/30 focus:outline-none focus:border-brand-500 transition-colors text-sm"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex flex-col gap-1">
                <label className="text-xs font-semibold text-white/70">Background Music (MP3 URL)</label>
                <input
                  type="url"
                  value={reel.audio_url}
                  onChange={setReelVal('audio_url')}
                  placeholder="https://example.com/music.mp3"
                  className="w-full bg-surface-overlay border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-white/30 focus:outline-none focus:border-brand-500 transition-colors text-sm"
                />
              </div>

              <div className="flex flex-col gap-1">
                <label className="text-xs font-semibold text-white/70">Cuisine Tag</label>
                <input
                  type="text"
                  value={reel.cuisine_tag}
                  onChange={setReelVal('cuisine_tag')}
                  placeholder="e.g. Desserts, Fast Food"
                  className="w-full bg-surface-overlay border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-white/30 focus:outline-none focus:border-brand-500 transition-colors text-sm"
                />
              </div>
            </div>
          </div>

          <hr className="border-white/10 my-2" />

          {/* Menu / Food Items Section */}
          <div className="flex flex-col gap-4">
            <h2 className="text-sm font-semibold text-white/50 uppercase tracking-wider">
              Add Food Items to Menu
            </h2>

            {/* Existing added items */}
            {foodItems.length > 0 && (
              <div className="flex flex-col gap-2">
                <label className="text-xs font-semibold text-white/50">Current Menu Items ({foodItems.length})</label>
                <div className="flex flex-col gap-2 max-h-40 overflow-y-auto pr-1">
                  {foodItems.map((item, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between bg-white/5 rounded-xl px-4 py-2.5 border border-white/10 hover:bg-white/10 transition-all"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-lg">{item.is_veg ? '🟢' : '🔴'}</span>
                        <div>
                          <p className="text-sm font-semibold text-white">{item.name}</p>
                          <p className="text-xs text-white/60">₹{item.price} · {item.category}</p>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeFoodItem(idx)}
                        className="text-white/40 hover:text-red-400 transition-colors p-1"
                        aria-label="Remove item"
                      >
                        🗑️
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Add Item form */}
            <div className="bg-white/5 p-4 rounded-xl border border-white/10 flex flex-col gap-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-semibold text-white/70">Item Name</label>
                  <input
                    type="text"
                    value={newItem.name}
                    onChange={setNewItemVal('name')}
                    placeholder="e.g. Souffle Pancake"
                    className="w-full bg-surface-overlay border border-white/10 rounded-lg px-3 py-2 text-white placeholder-white/30 focus:outline-none focus:border-brand-500 transition-colors text-sm"
                  />
                </div>

                <div className="flex flex-col gap-1">
                  <label className="text-xs font-semibold text-white/70">Price (INR)</label>
                  <input
                    type="text"
                    value={newItem.price}
                    onChange={setNewItemVal('price')}
                    placeholder="e.g. 299"
                    className="w-full bg-surface-overlay border border-white/10 rounded-lg px-3 py-2 text-white placeholder-white/30 focus:outline-none focus:border-brand-500 transition-colors text-sm"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-center">
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-semibold text-white/70">Category</label>
                  <select
                    value={newItem.category}
                    onChange={setNewItemVal('category')}
                    className="bg-surface-overlay border border-white/10 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-brand-500 transition-colors text-sm"
                  >
                    <option value="Starter">Starter</option>
                    <option value="Main Course">Main Course</option>
                    <option value="Dessert">Dessert</option>
                    <option value="Drinks">Drinks</option>
                  </select>
                </div>

                <div className="flex flex-col gap-1">
                  <label className="text-xs font-semibold text-white/70">Image URL</label>
                  <input
                    type="url"
                    value={newItem.image_url}
                    onChange={setNewItemVal('image_url')}
                    placeholder="https://example.com/food.jpg"
                    className="w-full bg-surface-overlay border border-white/10 rounded-lg px-3 py-2 text-white placeholder-white/30 focus:outline-none focus:border-brand-500 transition-colors text-sm"
                  />
                </div>

                <div className="flex items-center gap-2 mt-4 sm:justify-center">
                  <input
                    id="veg-checkbox"
                    type="checkbox"
                    checked={newItem.is_veg}
                    onChange={setNewItemVal('is_veg')}
                    className="w-4 h-4 text-brand-600 bg-surface-overlay border-white/10 rounded focus:ring-brand-500"
                  />
                  <label htmlFor="veg-checkbox" className="text-sm font-semibold text-white/70 cursor-pointer">
                    Veg Item 🟢
                  </label>
                </div>
              </div>

              <div className="flex flex-col gap-1">
                <label className="text-xs font-semibold text-white/70">Item Description</label>
                <input
                  type="text"
                  value={newItem.description}
                  onChange={setNewItemVal('description')}
                  placeholder="e.g. Soft and fluffy pancakes served with pure maple syrup."
                  className="w-full bg-surface-overlay border border-white/10 rounded-lg px-3 py-2 text-white placeholder-white/30 focus:outline-none focus:border-brand-500 transition-colors text-sm"
                />
              </div>

              <button
                type="button"
                onClick={addFoodItem}
                className="w-full py-2 bg-white/10 hover:bg-white/15 text-white font-semibold text-sm rounded-lg border border-white/10 transition-all active:scale-95"
              >
                ➕ Add Item to Menu
              </button>
            </div>
          </div>

          {/* Submit Actions */}
          <button
            type="submit"
            disabled={loading}
            className="w-full gradient-bg text-white font-semibold py-3.5 rounded-xl hover:opacity-90 active:scale-95 transition-all disabled:opacity-50 mt-4 shadow-lg text-base"
          >
            {loading ? 'Publishing Reel…' : '🚀 Publish Reel'}
          </button>

        </form>
      </div>

      <Toast toasts={toasts} />
    </div>
  )
}
