"use client"

import Link from 'next/link'
import { Heart } from 'lucide-react'
import Navbar from "@/components/Navbar"
import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function LandingPage() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to /feed if authenticated
    if (typeof window !== 'undefined' && localStorage.getItem("access_token")) {
      router.push("/feed")
      return
    }
  }, [])

  return (
    <>
      <Navbar />
      {/* Mission Statement */}
      <main className="container mx-auto px-4 py-20">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-6xl md:text-8xl font-bold text-gray-900 mb-8 leading-tight">
            Share What You're
            <span className="text-purple-600 block">Grateful For</span>
          </h1>
          <p className="text-2xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Join a community that celebrates life's beautiful moments. 
            Inspire others by sharing your gratitude and discover the joy of appreciating what matters most.
          </p>
        </div>
      </main>
    </>
  )
}
