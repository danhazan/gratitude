"use client"

import { useRouter } from "next/navigation"
import { Heart, Bell } from "lucide-react"
import { useEffect, useRef, useState } from "react"

interface NavbarProps {
  boxed?: boolean
  activeAuthTab?: 'login' | 'signup'
}

export default function Navbar({ boxed, activeAuthTab }: NavbarProps) {
  const router = useRouter()
  const [notifications, setNotifications] = useState<any[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const res = await fetch(`/api/notifications`)
        if (res.ok) {
          const data = await res.json()
          setNotifications(data.notifications)
          setUnreadCount(data.notifications.filter((n: any) => !n.readAt).length)
        }
      } catch {}
    }
    fetchNotifications()
  }, [])

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
      router.push("/feed")
  }

  const handleLogout = async () => {
    // No sign out logic here, as session is managed externally
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
        {/* Notifications dropdown removed as session is not available */}
        {/* Auth buttons removed as session is not available */}
        <button
          onClick={() => router.push('/auth/login')}
          className={
            [
              'px-4 py-2 rounded font-semibold transition',
              activeAuthTab === 'login'
                ? 'bg-purple-600 text-white hover:bg-purple-700'
                : boxed || activeAuthTab === undefined
                  ? 'bg-transparent text-purple-700 hover:bg-purple-100'
                  : 'bg-purple-100 text-purple-700 hover:bg-purple-200'
            ].join(' ')
          }
        >
          Log in
        </button>
        <button
          onClick={() => router.push('/auth/signup')}
          className={
            [
              'px-4 py-2 rounded font-semibold transition',
              activeAuthTab === 'signup'
                ? 'bg-purple-600 text-white hover:bg-purple-700'
                : boxed || activeAuthTab === undefined
                  ? 'bg-transparent text-purple-700 hover:bg-purple-100'
                  : 'bg-purple-100 text-purple-700 hover:bg-purple-200'
            ].join(' ')
          }
        >
          Sign Up
        </button>
      </div>
    </nav>
  )
} 