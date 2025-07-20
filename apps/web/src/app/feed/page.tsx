"use client"

import { useState, useEffect } from "react"
import { useSession, signOut } from "next-auth/react"
import { useRouter } from "next/navigation"
import { Heart, MessageCircle, Share, Plus, Camera, MapPin, Calendar, LogOut } from "lucide-react"
import Navbar from "@/components/Navbar"

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
  heartsCount?: number
  isHearted?: boolean
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
          // Add hearts data to posts
          const postsWithHearts = await Promise.all(
            data.posts.map(async (post: Post) => {
              try {
                const heartsResponse = await fetch(`/api/posts/${post.id}/hearts`)
                if (heartsResponse.ok) {
                  const heartsData = await heartsResponse.json()
                  return {
                    ...post,
                    heartsCount: heartsData.heartsCount,
                    isHearted: heartsData.hearts.some((heart: any) => heart.user.id === session?.user?.id)
                  }
                }
                return { ...post, heartsCount: 0, isHearted: false }
              } catch (error) {
                console.error('Failed to fetch hearts for post:', post.id, error)
                return { ...post, heartsCount: 0, isHearted: false }
              }
            })
          )
          setPosts(postsWithHearts)
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
  }, [status, session?.user?.id])

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
        // Add the new post to the beginning of the list with hearts data
        const newPostWithHearts = {
          ...data.post,
          heartsCount: 0,
          isHearted: false
        }
        setPosts([newPostWithHearts, ...posts])
        setNewPost({ content: "", postType: "daily", imageUrl: "", location: "" })
        setShowCreatePost(false)
      } else {
        console.error('Failed to create post')
      }
    } catch (error) {
      console.error('Error creating post:', error)
    }
  }

  const handleHeart = async (postId: string, isCurrentlyHearted: boolean) => {
    if (!session?.user?.id) return

    try {
      const method = isCurrentlyHearted ? 'DELETE' : 'POST'
      const response = await fetch(`/api/posts/${postId}/hearts`, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: session.user.id
        }),
      })

      if (response.ok) {
        // Update the post in the local state
        setPosts(posts.map(post => {
          if (post.id === postId) {
            return {
              ...post,
              heartsCount: isCurrentlyHearted ? (post.heartsCount || 1) - 1 : (post.heartsCount || 0) + 1,
              isHearted: !isCurrentlyHearted
            }
          }
          return post
        }))
      } else {
        console.error('Failed to heart/unheart post')
      }
    } catch (error) {
      console.error('Error hearting/unhearting post:', error)
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
      <Navbar />
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
            <>
              {/* Floating New Post Button */}
              <div className="fixed bottom-6 right-6 z-40">
                <button
                  onClick={() => setShowCreatePost(true)}
                  className="bg-purple-600 text-white p-4 rounded-full shadow-lg hover:bg-purple-700 transition-all duration-200 hover:scale-110"
                  title="Create New Post"
                >
                  <Plus className="h-6 w-6" />
                </button>
              </div>
              
              {posts.map((post) => (
              <article key={post.id} className={`${
                post.postType === 'daily' 
                  ? 'bg-white rounded-xl shadow-lg border-2 border-purple-100 overflow-hidden mb-8' // 3x larger, more prominent for daily
                  : post.postType === 'photo' 
                  ? 'bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden mb-6' // 2x boost for photo
                  : 'bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden mb-4' // Compact for spontaneous
              }`}>
                {/* Post Header */}
                <div className={`${
                  post.postType === 'daily' 
                    ? 'p-6 border-b border-gray-100' // Larger padding for daily
                    : post.postType === 'photo' 
                    ? 'p-5 border-b border-gray-100' // Medium padding for photo
                    : 'p-3 border-b border-gray-100' // Compact padding for spontaneous
                }`}>
                  <div className="flex items-center space-x-3">
                    <img
                      src={post.author.image || "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face"}
                      alt={post.author.name}
                      className={`${
                        post.postType === 'daily' 
                          ? 'w-12 h-12' // Larger avatar for daily
                          : post.postType === 'photo' 
                          ? 'w-10 h-10' // Medium avatar for photo
                          : 'w-8 h-8' // Compact avatar for spontaneous
                      } rounded-full`}
                    />
                    <div className="flex-1">
                      <h3 className={`${
                        post.postType === 'daily' 
                          ? 'font-bold text-lg' // Larger, bolder name for daily
                          : post.postType === 'photo' 
                          ? 'font-semibold text-base' // Medium name for photo
                          : 'font-medium text-sm' // Compact name for spontaneous
                      } text-gray-900`}>{post.author.name}</h3>
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
                    <div className={`${
                      post.postType === 'daily' 
                        ? 'text-sm px-3 py-2 bg-purple-100 text-purple-700 rounded-full capitalize font-medium' // More prominent badge for daily
                        : post.postType === 'photo' 
                        ? 'text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded-full capitalize' // Medium badge for photo
                        : 'text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-full capitalize' // Muted badge for spontaneous
                    }`}>
                      {post.postType}
                    </div>
                  </div>
                </div>

                {/* Post Content */}
                <div className={`${
                  post.postType === 'daily' 
                    ? 'p-6' // 3x larger for daily gratitude
                    : post.postType === 'photo' 
                    ? 'p-5' // 2x boost for photo posts
                    : 'p-3' // Compact for spontaneous text
                }`}>
                  <p className={`${
                    post.postType === 'daily' 
                      ? 'text-lg leading-relaxed' // Larger text for daily
                      : post.postType === 'photo' 
                      ? 'text-base leading-relaxed' // Medium text for photo
                      : 'text-sm leading-relaxed' // Compact text for spontaneous
                  } text-gray-900`}>{post.content}</p>
                  {post.imageUrl && (
                    <img
                      src={post.imageUrl}
                      alt="Post image"
                      className={`${
                        post.postType === 'daily' 
                          ? 'w-full h-80 object-cover rounded-lg mt-4' // Larger image for daily
                          : post.postType === 'photo' 
                          ? 'w-full h-64 object-cover rounded-lg mt-4' // Medium image for photo
                          : 'w-full h-48 object-cover rounded-lg mt-3' // Compact image for spontaneous
                      }`}
                    />
                  )}
                </div>

                {/* Post Actions */}
                <div className={`${
                  post.postType === 'daily' 
                    ? 'px-6 py-4 border-t border-gray-100' // Larger padding for daily
                    : post.postType === 'photo' 
                    ? 'px-5 py-3 border-t border-gray-100' // Medium padding for photo
                    : 'px-3 py-2 border-t border-gray-100' // Compact padding for spontaneous
                }`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-6">
                      <button 
                        onClick={() => handleHeart(post.id, post.isHearted || false)}
                        className={`flex items-center space-x-2 transition-colors ${
                          post.isHearted 
                            ? 'text-red-500 hover:text-red-600' 
                            : 'text-gray-500 hover:text-red-500'
                        }`}
                      >
                        <Heart className={`${
                          post.postType === 'daily' 
                            ? 'h-6 w-6' // Larger heart for daily
                            : post.postType === 'photo' 
                            ? 'h-5 w-5' // Medium heart for photo
                            : 'h-4 w-4' // Compact heart for spontaneous
                        } ${post.isHearted ? 'fill-current' : ''}`} />
                        <span className={`${
                          post.postType === 'daily' 
                            ? 'text-base font-medium' // Larger text for daily
                            : post.postType === 'photo' 
                            ? 'text-sm' // Medium text for photo
                            : 'text-xs' // Compact text for spontaneous
                        }`}>{post.heartsCount || 0}</span>
                      </button>
                      <button className={`flex items-center space-x-2 text-gray-500 hover:text-blue-500 transition-colors ${
                        post.postType === 'daily' 
                          ? 'text-base' // Larger text for daily
                          : post.postType === 'photo' 
                          ? 'text-sm' // Medium text for photo
                          : 'text-xs' // Compact text for spontaneous
                      }`}>
                        <MessageCircle className={`${
                          post.postType === 'daily' 
                            ? 'h-6 w-6' // Larger icon for daily
                            : post.postType === 'photo' 
                            ? 'h-5 w-5' // Medium icon for photo
                            : 'h-4 w-4' // Compact icon for spontaneous
                        }`} />
                        <span>0</span>
                      </button>
                      <button className={`flex items-center space-x-2 text-gray-500 hover:text-green-500 transition-colors ${
                        post.postType === 'daily' 
                          ? 'text-base' // Larger text for daily
                          : post.postType === 'photo' 
                          ? 'text-sm' // Medium text for photo
                          : 'text-xs' // Compact text for spontaneous
                      }`}>
                        <Share className={`${
                          post.postType === 'daily' 
                            ? 'h-6 w-6' // Larger icon for daily
                            : post.postType === 'photo' 
                            ? 'h-5 w-5' // Medium icon for photo
                            : 'h-4 w-4' // Compact icon for spontaneous
                        }`} />
                        <span>Share</span>
                      </button>
                    </div>
                  </div>
                </div>
              </article>
            ))}
            </>
          )}
        </div>
      </main>
    </div>
  )
} 