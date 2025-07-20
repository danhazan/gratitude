"use client"

import { useSession, signOut } from "next-auth/react"
import { useRouter } from "next/navigation"
import { Heart, Bell } from "lucide-react"
import { useEffect, useRef, useState } from "react"

interface NavbarProps {
  boxed?: boolean
  activeAuthTab?: 'login' | 'signup'
}

export default function Navbar({ boxed, activeAuthTab }: NavbarProps) {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [notifications, setNotifications] = useState<any[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const fetchNotifications = async () => {
      if (!session?.user?.id) return
      try {
        const res = await fetch(`/api/notifications?userId=${session.user.id}`)
        if (res.ok) {
          const data = await res.json()
          setNotifications(data.notifications)
          setUnreadCount(data.notifications.filter((n: any) => !n.readAt).length)
        }
      } catch {}
    }
    if (status === "authenticated") fetchNotifications()
  }, [session?.user?.id, status])

  // Close dropdown on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false)
      }
    }
    if (dropdownOpen) document.addEventListener("mousedown", handleClick)
    return () => document.removeEventListener("mousedown", handleClick)
  }, [dropdownOpen])

  const handleMarkAsRead = async (id: string) => {
    // For now, just update UI (add API later)
    setNotifications(notifications.map(n => n.id === id ? { ...n, readAt: new Date().toISOString() } : n))
    setUnreadCount(notifications.filter(n => n.id !== id && !n.readAt).length)
  }

  const handleTitleClick = () => {
    if (status === "authenticated") {
      router.push("/feed")
    } else {
      router.push("/")
    }
  }

  const handleLogout = async () => {
    await signOut({ callbackUrl: "/auth/login" })
  }

  return (
    <nav
      className={
        boxed
          ? "w-full flex items-center justify-between py-4 border-b border-gray-200 mb-8"
          : "w-full bg-white border-b border-gray-200 px-4 py-4 flex items-center justify-between"
      }
      style={boxed ? { borderRadius: 12 } : {}}
    >
      <button
        onClick={handleTitleClick}
        className="text-xl font-bold text-purple-700 hover:text-purple-900 focus:outline-none flex items-center gap-2"
        aria-label="Go to main page"
        tabIndex={0}
      >
        <Heart className="h-6 w-6 text-purple-600" />
        Grateful
      </button>
      <div className="flex items-center space-x-2 relative">
        {status === "authenticated" && (
          <div className="relative" ref={dropdownRef}>
            <button
              className="relative p-2 rounded-full hover:bg-purple-50 focus:outline-none"
              onClick={() => setDropdownOpen(v => !v)}
              aria-label="Notifications"
            >
              <Bell className="h-6 w-6 text-purple-700" />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full px-1.5 py-0.5 font-bold">
                  {unreadCount}
                </span>
              )}
            </button>
            {dropdownOpen && (
              <div className="absolute right-0 mt-2 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
                <div className="p-4 border-b font-semibold text-gray-700">Notifications</div>
                <div className="max-h-80 overflow-y-auto divide-y">
                  {notifications.length === 0 ? (
                    <div className="p-4 text-gray-500 text-center">No notifications</div>
                  ) : (
                    notifications.slice(0, 10).map(n => (
                      <div key={n.id} className={`flex items-start gap-2 p-4 ${!n.readAt ? "bg-purple-50" : ""}`}>
                        <div className="flex-shrink-0 mt-1">
                          <Bell className="h-5 w-5 text-purple-400" />
                        </div>
                        <div className="flex-1">
                          <div className="font-medium text-gray-900">{n.title}</div>
                          <div className="text-gray-700 text-sm">{n.message}</div>
                          <div className="text-xs text-gray-400 mt-1">{new Date(n.createdAt).toLocaleString()}</div>
                        </div>
                        {!n.readAt && (
                          <button
                            className="ml-2 text-xs text-purple-600 hover:underline"
                            onClick={() => handleMarkAsRead(n.id)}
                          >Mark as read</button>
                        )}
                      </div>
                    ))
                  )}
                </div>
                <div className="p-2 text-center border-t">
                  <button className="text-purple-700 hover:underline text-sm">View all</button>
                </div>
              </div>
            )}
          </div>
        )}
        {status === "authenticated" ? (
          <>
            <button
              onClick={() => router.push("/feed")}
              className="px-3 py-1 rounded hover:bg-purple-50 text-purple-700 font-medium"
            >
              Feed
            </button>
            <button
              onClick={() => router.push("/profile")}
              className="px-3 py-1 rounded hover:bg-purple-50 text-purple-700 font-medium"
            >
              Profile
            </button>
            <button
              onClick={handleLogout}
              className="px-3 py-1 rounded hover:bg-red-50 text-red-600 font-medium"
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <button
              onClick={() => router.push("/auth/login")}
              className={
                `px-3 py-1 rounded font-medium ` +
                (activeAuthTab === "login"
                  ? "bg-purple-600 text-white"
                  : "hover:bg-purple-50 text-purple-700")
              }
            >
              Log in
            </button>
            <button
              onClick={() => router.push("/auth/signup")}
              className={
                `px-3 py-1 rounded font-medium ` +
                (activeAuthTab === "signup"
                  ? "bg-purple-600 text-white"
                  : "hover:bg-purple-50 text-purple-700")
              }
            >
              Sign up
            </button>
          </>
        )}
      </div>
    </nav>
  )
} 