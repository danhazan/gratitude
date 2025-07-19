"use client"

import { useSession, signIn, signOut } from "next-auth/react"
import { Heart } from "lucide-react"

export default function TestAuthPage() {
  const { data: session, status } = useSession()

  if (status === "loading") {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Heart className="h-12 w-12 text-purple-600 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (status === "authenticated") {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
          <div className="text-center mb-6">
            <Heart className="h-12 w-12 text-purple-600 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900">Authentication Test</h1>
          </div>
          
          <div className="space-y-4">
            <div className="bg-green-50 p-4 rounded-lg">
              <h2 className="font-semibold text-green-800">✅ Authentication Working!</h2>
              <p className="text-green-700 text-sm mt-1">
                You are signed in as: {session.user?.email}
              </p>
            </div>
            
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold text-blue-800">User Details:</h3>
              <pre className="text-xs text-blue-700 mt-2 overflow-auto">
                {JSON.stringify(session, null, 2)}
              </pre>
            </div>
            
            <button
              onClick={() => signOut()}
              className="w-full bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition-colors"
            >
              Sign Out
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
        <div className="text-center mb-6">
          <Heart className="h-12 w-12 text-purple-600 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900">Authentication Test</h1>
        </div>
        
        <div className="space-y-4">
          <div className="bg-yellow-50 p-4 rounded-lg">
            <h2 className="font-semibold text-yellow-800">⚠️ Not Authenticated</h2>
            <p className="text-yellow-700 text-sm mt-1">
              You need to sign in to test the authentication
            </p>
          </div>
          
          <div className="space-y-2">
            <button
              onClick={() => signIn()}
              className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors"
            >
              Sign In
            </button>
            <button
              onClick={() => signIn("google")}
              className="w-full bg-white border border-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Sign In with Google
            </button>
            <button
              onClick={() => signIn("github")}
              className="w-full bg-gray-800 text-white py-2 px-4 rounded-lg hover:bg-gray-900 transition-colors"
            >
              Sign In with GitHub
            </button>
          </div>
        </div>
      </div>
    </div>
  )
} 