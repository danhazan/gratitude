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
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    // Demo: check for token in localStorage (replace with real logic as needed)
    setIsAuthenticated(!!localStorage.getItem("access_token"))
  }, [])

  const handleLogout = async () => {
    localStorage.removeItem("access_token")
    setIsAuthenticated(false)
    router.push("/auth/login")
  }

  const handleTitleClick = () => {
    router.push("/feed")
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
        {isAuthenticated ? (
          <>
            <button
              onClick={() => router.push("/feed")}
              className="px-4 py-2 rounded font-semibold transition bg-transparent text-purple-700 hover:bg-purple-100"
            >
              Feed
            </button>
            <button
              onClick={() => router.push("/profile")}
              className="px-4 py-2 rounded font-semibold transition bg-transparent text-purple-700 hover:bg-purple-100"
            >
              Profile
            </button>
            <button
              onClick={handleLogout}
              className="px-4 py-2 rounded font-semibold transition bg-purple-100 text-purple-700 hover:bg-purple-200"
            >
              Logout
            </button>
          </>
        ) : (
          <>
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
          </>
        )}
      </div>
    </nav>
  )
} 