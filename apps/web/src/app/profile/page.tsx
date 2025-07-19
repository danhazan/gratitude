"use client"

import { useState } from "react"
import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import { Heart, Edit, Camera, Settings, Calendar, MapPin, Users, MessageCircle } from "lucide-react"

interface UserProfile {
  id: string
  name: string
  email: string
  image: string
  bio: string
  location: string
  joinedDate: string
  stats: {
    postsCount: number
    followersCount: number
    followingCount: number
    heartsReceived: number
  }
}

export default function ProfilePage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [isEditing, setIsEditing] = useState(false)
  const [profile, setProfile] = useState<UserProfile>({
    id: "1",
    name: session?.user?.name || "User",
    email: session?.user?.email || "",
    image: session?.user?.image || "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
    bio: "I'm grateful for every day and the opportunity to share positivity with others.",
    location: "San Francisco, CA",
    joinedDate: "2024-01-01",
    stats: {
      postsCount: 42,
      followersCount: 156,
      followingCount: 89,
      heartsReceived: 324
    }
  })

  const [editForm, setEditForm] = useState({
    name: profile.name,
    bio: profile.bio,
    location: profile.location
  })

  if (status === "loading") {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your profile...</p>
        </div>
      </div>
    )
  }

  if (status === "unauthenticated") {
    router.push("/auth/login")
    return null
  }

  const handleSaveProfile = () => {
    setProfile({
      ...profile,
      ...editForm
    })
    setIsEditing(false)
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Heart className="h-6 w-6 text-purple-600" />
              <span className="text-xl font-bold text-gray-900">Grateful</span>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push("/feed")}
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                Feed
              </button>
              <div className="flex items-center space-x-2">
                <img
                  src={session?.user?.image || "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=32&h=32&fit=crop&crop=face"}
                  alt={session?.user?.name || "User"}
                  className="w-8 h-8 rounded-full"
                />
                <span className="text-sm text-gray-700">{session?.user?.name}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Profile Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Profile Header */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <div className="flex items-start space-x-6">
              {/* Profile Image */}
              <div className="relative">
                <img
                  src={profile.image}
                  alt={profile.name}
                  className="w-24 h-24 rounded-full object-cover"
                />
                <button className="absolute bottom-0 right-0 bg-purple-600 text-white p-2 rounded-full hover:bg-purple-700 transition-colors">
                  <Camera className="h-4 w-4" />
                </button>
              </div>

              {/* Profile Info */}
              <div className="flex-1">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h1 className="text-2xl font-bold text-gray-900">{profile.name}</h1>
                    <p className="text-gray-600">{profile.email}</p>
                  </div>
                  <div className="flex items-center space-x-3">
                    {isEditing ? (
                      <>
                        <button
                          onClick={() => setIsEditing(false)}
                          className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={handleSaveProfile}
                          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                        >
                          Save
                        </button>
                      </>
                    ) : (
                      <button
                        onClick={() => setIsEditing(true)}
                        className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                      >
                        <Edit className="h-4 w-4" />
                        <span>Edit Profile</span>
                      </button>
                    )}
                  </div>
                </div>

                {isEditing ? (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Name
                      </label>
                      <input
                        type="text"
                        value={editForm.name}
                        onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Bio
                      </label>
                      <textarea
                        value={editForm.bio}
                        onChange={(e) => setEditForm({ ...editForm, bio: e.target.value })}
                        rows={3}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        placeholder="Tell us about yourself..."
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Location
                      </label>
                      <input
                        type="text"
                        value={editForm.location}
                        onChange={(e) => setEditForm({ ...editForm, location: e.target.value })}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        placeholder="Where are you located?"
                      />
                    </div>
                  </div>
                ) : (
                  <div>
                    <p className="text-gray-700 mb-4">{profile.bio}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <div className="flex items-center space-x-1">
                        <MapPin className="h-4 w-4" />
                        <span>{profile.location}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Calendar className="h-4 w-4" />
                        <span>Joined {formatDate(profile.joinedDate)}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">{profile.stats.postsCount}</div>
              <div className="text-sm text-gray-600">Posts</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">{profile.stats.followersCount}</div>
              <div className="text-sm text-gray-600">Followers</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">{profile.stats.followingCount}</div>
              <div className="text-sm text-gray-600">Following</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">{profile.stats.heartsReceived}</div>
              <div className="text-sm text-gray-600">Hearts Received</div>
            </div>
          </div>

          {/* Recent Posts */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Gratitude Posts</h2>
            <div className="space-y-4">
              {/* Mock recent posts */}
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center space-x-3 mb-3">
                  <img
                    src={profile.image}
                    alt={profile.name}
                    className="w-10 h-10 rounded-full"
                  />
                  <div>
                    <h3 className="font-medium text-gray-900">{profile.name}</h3>
                    <p className="text-sm text-gray-500">2 hours ago</p>
                  </div>
                </div>
                <p className="text-gray-700 mb-3">
                  "I'm grateful for the peaceful morning walks and the way the sunlight filters through the trees."
                </p>
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <div className="flex items-center space-x-1">
                    <Heart className="h-4 w-4" />
                    <span>12</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <MessageCircle className="h-4 w-4" />
                    <span>3</span>
                  </div>
                </div>
              </div>

              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center space-x-3 mb-3">
                  <img
                    src={profile.image}
                    alt={profile.name}
                    className="w-10 h-10 rounded-full"
                  />
                  <div>
                    <h3 className="font-medium text-gray-900">{profile.name}</h3>
                    <p className="text-sm text-gray-500">1 day ago</p>
                  </div>
                </div>
                <p className="text-gray-700 mb-3">
                  "Thankful for the amazing support from my friends and family during challenging times."
                </p>
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <div className="flex items-center space-x-1">
                    <Heart className="h-4 w-4" />
                    <span>8</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <MessageCircle className="h-4 w-4" />
                    <span>2</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
} 