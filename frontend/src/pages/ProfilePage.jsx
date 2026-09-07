import { useParams } from 'react-router-dom'
import { useEffect, useState } from 'react'
import axiosClient from '../api/axiosClient'
import Avatar from '../components/shared/Avatar'
import Spinner from '../components/shared/Spinner'

export default function ProfilePage() {
  const { username } = useParams()
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    axiosClient.get(`/users/${username}`)
      .then(r => setProfile(r.data))
      .catch(() => setError('User not found.'))
      .finally(() => setLoading(false))
  }, [username])

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <Spinner size="lg" />
    </div>
  )

  if (error) return (
    <div className="min-h-screen flex items-center justify-center text-white/40">
      <div className="text-center">
        <p className="text-4xl mb-3">👤</p>
        <p>{error}</p>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-surface pt-14 px-4">
      <div className="max-w-lg mx-auto py-8">
        {/* Profile header */}
        <div className="flex items-center gap-4 mb-6">
          <Avatar src={profile.avatar_url} name={profile.username} size="lg" />
          <div>
            <h1 className="font-bold text-xl text-white">@{profile.username}</h1>
            {profile.bio && <p className="text-white/60 text-sm mt-0.5">{profile.bio}</p>}
          </div>
        </div>

        {/* Stats */}
        <div className="flex gap-6 mb-8">
          {[
            { label: 'Reels', value: profile.reel_count },
            { label: 'Followers', value: profile.follower_count },
            { label: 'Following', value: profile.following_count },
          ].map(({ label, value }) => (
            <div key={label} className="text-center">
              <p className="font-bold text-white text-lg">{value.toLocaleString()}</p>
              <p className="text-white/50 text-xs">{label}</p>
            </div>
          ))}
        </div>

        <p className="text-white/30 text-sm text-center">Reels grid — Phase 2</p>
      </div>
    </div>
  )
}
