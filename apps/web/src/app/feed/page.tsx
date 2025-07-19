"use client"

import { useState } from "react"
import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import { Heart, MessageCircle, Share, Plus, Camera, MapPin, Calendar } from "lucide-react"

interface Post {
  id: string
  content: string
  author: {
    name: string
    image: string
  }
  createdAt: string
  likesCount: number
  commentsCount: number
  postType: "daily" | "photo" | "spontaneous"
  imageUrl?: string
  location?: string
}

export default function FeedPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [showCreatePost, setShowCreatePost] = useState(false)
  const [newPost, setNewPost] = useState({
    content: "",
    postType: "daily" as const,
    imageUrl: "",
    location: ""
  })

  // Mock data for demonstration
  const [posts, setPosts] = useState<Post[]>([
    {
      id: "1",
      content: "I'm grateful for the beautiful sunset I witnessed today. Nature's daily reminder that even endings can be beautiful.",
      author: {
        name: "Sarah Johnson",
        image: "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face"
      },
      createdAt: "2024-01-15T10:30:00Z",
      likesCount: 24,
      commentsCount: 8,
      postType: "daily",
      imageUrl: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&h=400&fit=crop"
    },
    {
      id: "2",
      content: "Thankful for my morning coffee and the quiet moments before the day begins.",
      author: {
        name: "Mike Chen",
        image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face"
      },
      createdAt: "2024-01-15T08:15:00Z",
      likesCount: 12,
      commentsCount: 3,
      postType: "spontaneous"
    }
  ])

  if (status === "loading") {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your gratitude feed...</p>
        </div>
      </div>
    )
  }

  if (status === "unauthenticated") {
    router.push("/auth/login")
    return null
  }

  const handleCreatePost = async () => {
    if (!newPost.content.trim()) return

    const post: Post = {
      id: Date.now().toString(),
      content: newPost.content,
      author: {
        name: session?.user?.name || "Anonymous",
        image: session?.user?.image || "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face"
      },
      createdAt: new Date().toISOString(),
      likesCount: 0,
      commentsCount: 0,
      postType: newPost.postType,
      imageUrl: newPost.imageUrl || undefined,
      location: newPost.location || undefined
    }

    setPosts([post, ...posts])
    setNewPost({ content: "", postType: "daily", imageUrl: "", location: "" })
    setShowCreatePost(false)
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)
    
    if (diffInHours < 1) return "Just now"
    if (diffInHours < 24) return `${Math.floor(diffInHours)}h ago`
    return date.toLocaleDateString()
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Heart className="h-6 w-6 text-purple-600" />
              <span className="text-xl font-bold text-gray-900">Grateful</span>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowCreatePost(true)}
                className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center space-x-2"
              >
                <Plus className="h-4 w-4" />
                <span>Share Gratitude</span>
              </button>
              <button
                onClick={() => router.push("/profile")}
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                Profile
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

      {/* Create Post Modal */}
      {showCreatePost && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold mb-4">Share Your Gratitude</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  What are you grateful for?
                </label>
                <textarea
                  value={newPost.content}
                  onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  rows={4}
                  placeholder="Share what you're grateful for today..."
                  maxLength={500}
                />
                <div className="text-xs text-gray-500 mt-1">
                  {newPost.content.length}/500 characters
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Post Type
                </label>
                <select
                  value={newPost.postType}
                  onChange={(e) => setNewPost({ ...newPost, postType: e.target.value as any })}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="daily">Daily Gratitude</option>
                  <option value="photo">Photo Gratitude</option>
                  <option value="spontaneous">Spontaneous Text</option>
                </select>
              </div>

              <div className="flex space-x-2">
                <button className="flex-1 flex items-center justify-center space-x-2 p-3 border border-gray-300 rounded-lg hover:bg-gray-50">
                  <Camera className="h-4 w-4" />
                  <span className="text-sm">Add Photo</span>
                </button>
                <button className="flex-1 flex items-center justify-center space-x-2 p-3 border border-gray-300 rounded-lg hover:bg-gray-50">
                  <MapPin className="h-4 w-4" />
                  <span className="text-sm">Add Location</span>
                </button>
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowCreatePost(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleCreatePost}
                disabled={!newPost.content.trim()}
                className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Share
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Feed */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto space-y-6">
          {posts.map((post) => (
            <article key={post.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              {/* Post Header */}
              <div className="p-4 border-b border-gray-100">
                <div className="flex items-center space-x-3">
                  <img
                    src={post.author.image}
                    alt={post.author.name}
                    className="w-10 h-10 rounded-full"
                  />
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{post.author.name}</h3>
                    <div className="flex items-center space-x-2 text-sm text-gray-500">
                      <Calendar className="h-4 w-4" />
                      <span>{formatDate(post.createdAt)}</span>
                      {post.location && (
                        <>
                          <MapPin className="h-4 w-4" />
                          <span>{post.location}</span>
                        </>
                      )}
                    </div>
                  </div>
                  <div className="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded-full capitalize">
                    {post.postType}
                  </div>
                </div>
              </div>

              {/* Post Content */}
              <div className="p-4">
                <p className="text-gray-900 leading-relaxed">{post.content}</p>
                {post.imageUrl && (
                  <img
                    src={post.imageUrl}
                    alt="Post image"
                    className="w-full h-64 object-cover rounded-lg mt-4"
                  />
                )}
              </div>

              {/* Post Actions */}
              <div className="px-4 py-3 border-t border-gray-100">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-6">
                    <button className="flex items-center space-x-2 text-gray-500 hover:text-red-500 transition-colors">
                      <Heart className="h-5 w-5" />
                      <span className="text-sm">{post.likesCount}</span>
                    </button>
                    <button className="flex items-center space-x-2 text-gray-500 hover:text-blue-500 transition-colors">
                      <MessageCircle className="h-5 w-5" />
                      <span className="text-sm">{post.commentsCount}</span>
                    </button>
                    <button className="flex items-center space-x-2 text-gray-500 hover:text-green-500 transition-colors">
                      <Share className="h-5 w-5" />
                      <span className="text-sm">Share</span>
                    </button>
                  </div>
                </div>
              </div>
            </article>
          ))}
        </div>
      </main>
    </div>
  )
} 