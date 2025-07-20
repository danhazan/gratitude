"use client"

import { useState, useEffect } from "react"
import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import { Heart, Edit, Camera, Settings, Calendar, MapPin, Users, MessageCircle } from "lucide-react"
import Navbar from "@/components/Navbar"

interface UserProfile {
  id: string
  name: string
  email: string
  image: string | null
  createdAt: string
  updatedAt: string
  location?: string
  about?: string
  birthday?: string
  gender?: string
  website?: string
  interests?: string[]
  occupation?: string
}

export default function ProfilePage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [isEditing, setIsEditing] = useState(false)
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [editForm, setEditForm] = useState({
    name: "",
    email: "",
    image: "",
    location: "",
    about: "",
    birthday: "",
    gender: "prefer_not_to_say",
    website: "",
    interests: "",
    occupation: ""
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  useEffect(() => {
    const fetchProfile = async () => {
      if (!session?.user?.id) return
      setLoading(true)
      setError(null)
      try {
        const res = await fetch(`/api/users/profile?userId=${session.user.id}`)
        if (res.ok) {
          const data = await res.json()
          setProfile(data.user)
          setEditForm({
            name: data.user.name || "",
            email: data.user.email || "",
            image: data.user.image || "",
            location: data.user.location || "",
            about: data.user.about || "",
            birthday: data.user.birthday ? data.user.birthday.slice(0, 10) : "",
            gender: data.user.gender || "prefer_not_to_say",
            website: data.user.website || "",
            interests: (data.user.interests || []).join(", "),
            occupation: data.user.occupation || ""
          })
        } else {
          const data = await res.json()
          setError(data.error || "Failed to load profile")
        }
      } catch (e) {
        setError("Failed to load profile")
      } finally {
        setLoading(false)
      }
    }
    if (status === "authenticated") fetchProfile()
  }, [session?.user?.id, status])

  if (status === "loading" || loading) {
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

  if (!profile) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <p className="text-red-500">{error || "Profile not found."}</p>
        </div>
      </div>
    )
  }

  const handleEdit = () => {
    setIsEditing(true)
    setSuccess(null)
    setError(null)
  }

  const handleCancel = () => {
    setIsEditing(false)
    setEditForm({
      name: profile.name || "",
      email: profile.email || "",
      image: profile.image || "",
      location: profile.location || "",
      about: profile.about || "",
      birthday: profile.birthday || "",
      gender: profile.gender || "prefer_not_to_say",
      website: profile.website || "",
      interests: (profile.interests || []).join(", "),
      occupation: profile.occupation || ""
    })
    setError(null)
    setSuccess(null)
  }

  const handleSave = async () => {
    setSaving(true)
    setError(null)
    setSuccess(null)
    try {
      const res = await fetch("/api/users/profile", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userId: profile.id,
          name: editForm.name,
          email: editForm.email,
          image: editForm.image,
          location: editForm.location,
          about: editForm.about,
          birthday: editForm.birthday,
          gender: editForm.gender,
          website: editForm.website,
          interests: editForm.interests.split(",").map((s: string) => s.trim()).filter(Boolean),
          occupation: editForm.occupation
        })
      })
      const data = await res.json()
      if (res.ok) {
        setProfile(data.user)
        setIsEditing(false)
        setSuccess("Profile updated successfully!")
      } else {
        setError(data.error || "Failed to update profile")
      }
    } catch (e) {
      setError("Failed to update profile")
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-10">
      <div className="max-w-xl mx-auto bg-white rounded-lg shadow p-8 relative flex flex-col min-h-[600px]">
        <Navbar boxed />
        <div className="flex flex-col items-center flex-1">
          <div className="relative">
            <img
              src={profile.image || "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face"}
              alt={profile.name}
              className="w-28 h-28 rounded-full object-cover border-4 border-purple-200"
            />
            {isEditing && (
              <button
                className="absolute bottom-0 right-0 bg-purple-600 text-white rounded-full p-2 shadow hover:bg-purple-700"
                title="Change photo (stubbed)"
                onClick={() => alert('Photo upload coming soon!')}
              >
                <Camera className="h-5 w-5" />
              </button>
            )}
          </div>
          <div className="mt-4 text-center">
            {isEditing ? (
              <>
                <input
                  type="text"
                  className="text-xl font-bold text-gray-900 border-b border-gray-300 focus:outline-none focus:border-purple-500 bg-transparent text-center"
                  value={editForm.name}
                  onChange={e => setEditForm(f => ({ ...f, name: e.target.value }))}
                  maxLength={100}
                  placeholder="Your name"
                />
                <input
                  type="email"
                  className="block mt-2 text-gray-600 border-b border-gray-300 focus:outline-none focus:border-purple-500 bg-transparent text-center mx-auto"
                  value={editForm.email}
                  onChange={e => setEditForm(f => ({ ...f, email: e.target.value }))}
                  maxLength={100}
                  placeholder="Your email"
                />
              </>
            ) : (
              <>
                <h2 className="text-xl font-bold text-gray-900">{profile.name}</h2>
                <p className="text-gray-600">{profile.email}</p>
              </>
            )}
            <div className="flex items-center justify-center space-x-2 mt-2 text-gray-500 text-sm">
              <Calendar className="h-4 w-4" />
              <span>Joined {new Date(profile.createdAt).toLocaleDateString()}</span>
            </div>
          </div>
        </div>
        <div className="mt-8">
          {isEditing ? (
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Name</label>
                <input type="text" className="w-full p-2 border rounded" value={editForm.name} onChange={e => setEditForm(f => ({ ...f, name: e.target.value }))} maxLength={100} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input type="email" className="w-full p-2 border rounded" value={editForm.email} onChange={e => setEditForm(f => ({ ...f, email: e.target.value }))} maxLength={100} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Location</label>
                <input type="text" className="w-full p-2 border rounded" value={editForm.location} onChange={e => setEditForm(f => ({ ...f, location: e.target.value }))} maxLength={100} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">About</label>
                <textarea className="w-full p-2 border rounded" value={editForm.about} onChange={e => setEditForm(f => ({ ...f, about: e.target.value }))} maxLength={300} rows={3} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Birthday</label>
                <input type="date" className="w-full p-2 border rounded" value={editForm.birthday} onChange={e => setEditForm(f => ({ ...f, birthday: e.target.value }))} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Gender</label>
                <select className="w-full p-2 border rounded" value={editForm.gender} onChange={e => setEditForm(f => ({ ...f, gender: e.target.value }))}>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                  <option value="prefer_not_to_say">Prefer not to say</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Website</label>
                <input type="url" className="w-full p-2 border rounded" value={editForm.website} onChange={e => setEditForm(f => ({ ...f, website: e.target.value }))} maxLength={100} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Interests (comma separated)</label>
                <input type="text" className="w-full p-2 border rounded" value={editForm.interests} onChange={e => setEditForm(f => ({ ...f, interests: e.target.value }))} maxLength={200} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Occupation</label>
                <input type="text" className="w-full p-2 border rounded" value={editForm.occupation} onChange={e => setEditForm(f => ({ ...f, occupation: e.target.value }))} maxLength={100} />
              </div>
              <div className="flex space-x-3 mt-6">
                <button type="button" onClick={handleCancel} className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50" disabled={saving}>Cancel</button>
                <button type="button" onClick={handleSave} className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed" disabled={saving}>{saving ? "Saving..." : "Save"}</button>
              </div>
            </form>
          ) : (
            <div className="space-y-2 mt-4 text-gray-700">
              {profile.location && <div><span className="font-medium">Location:</span> {profile.location}</div>}
              {profile.about && <div><span className="font-medium">About:</span> {profile.about}</div>}
              {profile.birthday && <div><span className="font-medium">Birthday:</span> {new Date(profile.birthday).toLocaleDateString()}</div>}
              {profile.gender && <div><span className="font-medium">Gender:</span> {profile.gender.charAt(0).toUpperCase() + profile.gender.slice(1).replace(/_/g, ' ')}</div>}
              {profile.website && <div><span className="font-medium">Website:</span> <a href={profile.website} className="text-purple-600 hover:underline" target="_blank" rel="noopener noreferrer">{profile.website}</a></div>}
              {profile.interests && profile.interests.length > 0 && <div><span className="font-medium">Interests:</span> {profile.interests.join(", ")}</div>}
              {profile.occupation && <div><span className="font-medium">Occupation:</span> {profile.occupation}</div>}
            </div>
          )}
        </div>
        {error && <div className="text-red-500 mt-4">{error}</div>}
        {success && <div className="text-green-600 mt-4">{success}</div>}
        {/* Edit Profile Button at the bottom right */}
        {!isEditing && (
          <div className="flex justify-end mt-8">
            <button
              className="flex items-center space-x-2 bg-purple-600 text-white px-4 py-2 rounded-lg shadow hover:bg-purple-700 transition-colors"
              onClick={handleEdit}
              aria-label="Edit Profile"
            >
              <Edit className="h-5 w-5 mr-1" />
              <span>Edit Profile</span>
            </button>
          </div>
        )}
      </div>
    </div>
  )
} 