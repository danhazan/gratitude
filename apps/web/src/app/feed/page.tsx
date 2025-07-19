"use client"

import { useState, useEffect } from "react"
import { useSession, signOut } from "next-auth/react"
import { useRouter } from "next/navigation"
import { Heart, MessageCircle, Share, Plus, Camera, MapPin, Calendar, LogOut } from "lucide-react"

interface Post {
  id: string
  content: string
  author: {
    id: string
    name: string
    image: string
  }
  createdAt: string
  postType: "daily" | "photo" | "spontaneous"
  imageUrl?: string
  location?: string
}

export default function FeedPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [showCreatePost, setShowCreatePost] = useState(false)
  const [posts, setPosts] = useState<Post[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isLoggingOut, setIsLoggingOut] = useState(false)
  const [newPost, setNewPost] = useState({
    content: "",
    postType: "daily" as const,
    imageUrl: "",
    location: ""
  })

  // Fetch posts from API
  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const response = await fetch('/api/posts')
        if (response.ok) {
          const data = await response.json()
          setPosts(data.posts)
        }
      } catch (error) {
        console.error('Failed to fetch posts:', error)
      } finally {
        setIsLoading(false)
      }
    }

    if (status === 'authenticated') {
      fetchPosts()
    }
  }, [status])

  if (status === "loading" || isLoading) {
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
    if (!newPost.content.trim() || !session?.user?.id) return

    try {
      const response = await fetch('/api/posts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: newPost.content,
          postType: newPost.postType,
          authorId: session.user.id,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        // Add the new post to the beginning of the list
        setPosts([data.post, ...posts])
        setNewPost({ content: "", postType: "daily", imageUrl: "", location: "" })
        setShowCreatePost(false)
      } else {
        console.error('Failed to create post')
      }
    } catch (error) {
      console.error('Error creating post:', error)
    }
  }

  const handleLogout = async () => {
    setIsLoggingOut(true)
    try {
      await signOut({ 
        callbackUrl: '/auth/login',
        redirect: true 
      })
    } catch (error) {
      console.error('Logout error:', error)
      setIsLoggingOut(false)
    }
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
                <button
                  onClick={handleLogout}
                  disabled={isLoggingOut}
                  className="flex items-center space-x-1 text-gray-500 hover:text-red-600 transition-colors disabled:opacity-50"
                  title="Logout"
                >
                  <LogOut className="h-4 w-4" />
                  {isLoggingOut && (
                    <div className="animate-spin rounded-full h-3 w-3 border-b border-red-600"></div>
                  )}
                </button>
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
          {posts.length === 0 ? (
            <div className="text-center py-12">
              <Heart className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No posts yet</h3>
              <p className="text-gray-500 mb-6">
                Be the first to share what you're grateful for!
              </p>
              <button
                onClick={() => setShowCreatePost(true)}
                className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors"
              >
                Create Your First Post
              </button>
            </div>
          ) : (
            posts.map((post) => (
              <article key={post.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                {/* Post Header */}
                <div className="p-4 border-b border-gray-100">
                  <div className="flex items-center space-x-3">
                    <img
                      src={post.author.image || "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face"}
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
                        <span className="text-sm">0</span>
                      </button>
                      <button className="flex items-center space-x-2 text-gray-500 hover:text-blue-500 transition-colors">
                        <MessageCircle className="h-5 w-5" />
                        <span className="text-sm">0</span>
                      </button>
                      <button className="flex items-center space-x-2 text-gray-500 hover:text-green-500 transition-colors">
                        <Share className="h-5 w-5" />
                        <span className="text-sm">Share</span>
                      </button>
                    </div>
                  </div>
                </div>
              </article>
            ))
          )}
        </div>
      </main>
    </div>
  )
} 