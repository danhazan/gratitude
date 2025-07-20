import { NextRequest, NextResponse } from "next/server"
import { PrismaClient } from "@prisma/client"

// Use singleton pattern for Prisma client
const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

const prisma = globalForPrisma.prisma ?? new PrismaClient()

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma

export async function GET(request: NextRequest) {
  try {
    let userId: string | null = null
    try {
      // Try to get userId from URL (real request)
      const { searchParams } = new URL(request.url)
      userId = searchParams.get('userId')
    } catch {
      // Fallback for test mocks
      userId = (request as any).query?.userId || null
    }

    if (!userId) {
      return NextResponse.json(
        { error: "User ID is required" },
        { status: 400 }
      )
    }

    const user = await prisma.user.findUnique({
      where: { id: userId },
      select: {
        id: true,
        name: true,
        email: true,
        image: true,
        createdAt: true,
        updatedAt: true,
        location: true,
        about: true,
        birthday: true,
        gender: true,
        website: true,
        interests: true,
        occupation: true
      }
    })

    if (!user) {
      return NextResponse.json(
        { error: "User not found" },
        { status: 404 }
      )
    }

    return NextResponse.json({ user })
  } catch (error) {
    console.error("Profile retrieval error:", error)
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    )
  }
}

export async function PUT(request: NextRequest) {
  try {
    // Handle both real requests and test mocks
    let body
    if (request.json) {
      body = await request.json()
    } else {
      // For test mocks, the body is already available
      body = (request as any).body
    }

    const { userId, name, email, image, location, about, birthday, gender, website, interests, occupation } = body

    // Validate input
    if (!userId) {
      return NextResponse.json(
        { error: "User ID is required" },
        { status: 400 }
      )
    }

    if (name && (name.length < 1 || name.length > 100)) {
      return NextResponse.json(
        { error: "Name must be between 1 and 100 characters" },
        { status: 400 }
      )
    }

    if (email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(email)) {
        return NextResponse.json(
          { error: "Invalid email format" },
          { status: 400 }
        )
      }
    }

    if (birthday && isNaN(Date.parse(birthday))) {
      return NextResponse.json(
        { error: "Invalid birthday format" },
        { status: 400 }
      )
    }

    if (gender && !["male", "female", "other", "prefer_not_to_say"].includes(gender)) {
      return NextResponse.json(
        { error: "Invalid gender value" },
        { status: 400 }
      )
    }

    if (website && website.length > 0) {
      try {
        new URL(website)
      } catch {
        return NextResponse.json(
          { error: "Invalid website URL" },
          { status: 400 }
        )
      }
    }

    // Check if user exists
    const existingUser = await prisma.user.findUnique({
      where: { id: userId }
    })

    if (!existingUser) {
      return NextResponse.json(
        { error: "User not found" },
        { status: 404 }
      )
    }

    // Check if email is already taken by another user
    if (email && email !== existingUser.email) {
      const emailExists = await prisma.user.findUnique({
        where: { email }
      })

      if (emailExists) {
        return NextResponse.json(
          { error: "Email is already taken" },
          { status: 409 }
        )
      }
    }

    // Update user profile
    const updatedUser = await prisma.user.update({
      where: { id: userId },
      data: {
        ...(name && { name }),
        ...(email && { email }),
        ...(image && { image }),
        ...(location && { location }),
        ...(about && { about }),
        ...(birthday && { birthday: new Date(birthday) }),
        ...(gender && { gender }),
        ...(website && { website }),
        ...(Array.isArray(interests) && { interests }),
        ...(occupation && { occupation }),
        updatedAt: new Date()
      },
      select: {
        id: true,
        name: true,
        email: true,
        image: true,
        createdAt: true,
        updatedAt: true,
        location: true,
        about: true,
        birthday: true,
        gender: true,
        website: true,
        interests: true,
        occupation: true
      }
    })

    return NextResponse.json({
      message: "Profile updated successfully",
      user: updatedUser
    })
  } catch (error) {
    console.error("Profile update error:", error)
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    )
  }
} 