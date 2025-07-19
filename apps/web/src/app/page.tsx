import Link from 'next/link'
import { Heart } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Heart className="h-6 w-6 text-purple-600" />
              <span className="text-xl font-bold text-gray-900">Grateful</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link 
                href="/auth/login" 
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                Sign In
              </Link>
              <Link 
                href="/auth/signup" 
                className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

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
    </div>
  )
}
