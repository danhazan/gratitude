"use client"

import { useSession, signOut } from "next-auth/react"
import { useRouter } from "next/navigation"
import { Heart } from "lucide-react"

interface NavbarProps {
  boxed?: boolean
}

export default function Navbar({ boxed }: NavbarProps) {
  const { data: session, status } = useSession()
  const router = useRouter()

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
      <div className="flex items-center space-x-2">
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
              className="px-3 py-1 rounded hover:bg-purple-50 text-purple-700 font-medium"
            >
              Sign In
            </button>
            <button
              onClick={() => router.push("/auth/signup")}
              className="px-3 py-1 rounded hover:bg-purple-600 bg-purple-500 text-white font-medium"
            >
              Sign Up
            </button>
          </>
        )}
      </div>
    </nav>
  )
} 