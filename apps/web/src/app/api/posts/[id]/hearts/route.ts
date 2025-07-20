import { NextRequest, NextResponse } from "next/server"
import { PrismaClient } from "@prisma/client"

// Use singleton pattern for Prisma client
const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

const prisma = globalForPrisma.prisma ?? new PrismaClient()

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma

export async function POST(request: NextRequest, params: any) {
  try {
    // Handle both real requests and test mocks
    let body
    if (request.json) {
      body = await request.json()
    } else {
      // For test mocks, the body is already available
      body = (request as any).body
    }

    const { userId } = body

    // Validate input
    if (!userId) {
      return NextResponse.json(
        { error: "User ID is required" },
        { status: 400 }
      )
    }

    const { id } = params?.params || {}

    // Verify post exists
    const post = await prisma.post.findUnique({
      where: { id }
    })

    if (!post) {
      return NextResponse.json(
        { error: "Post not found" },
        { status: 404 }
      )
    }

    // Check if user already hearted this post
    const existingHeart = await prisma.heart.findUnique({
      where: {
        userId_postId: {
          userId,
          postId: id
        }
      }
    })

    if (existingHeart) {
      return NextResponse.json(
        { error: "User has already hearted this post" },
        { status: 409 }
      )
    }

    // Create heart
    await prisma.heart.create({
      data: {
        userId,
        postId: id
      }
    })

    return NextResponse.json(
      { message: "Post hearted successfully" },
      { status: 201 }
    )
  } catch (error) {
    console.error("Heart creation error:", error)
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    )
  }
}

export async function DELETE(request: NextRequest, params: any) {
  try {
    // Handle both real requests and test mocks
    let body
    if (request.json) {
      body = await request.json()
    } else {
      // For test mocks, the body is already available
      body = (request as any).body
    }

    const { userId } = body

    // Validate input
    if (!userId) {
      return NextResponse.json(
        { error: "User ID is required" },
        { status: 400 }
      )
    }

    const { id } = params?.params || {}

    // Find and delete the heart
    const heart = await prisma.heart.findUnique({
      where: {
        userId_postId: {
          userId,
          postId: id
        }
      }
    })

    if (!heart) {
      return NextResponse.json(
        { error: "Heart not found" },
        { status: 404 }
      )
    }

    await prisma.heart.delete({
      where: {
        userId_postId: {
          userId,
          postId: id
        }
      }
    })

    return NextResponse.json(
      { message: "Post unhearted successfully" },
      { status: 200 }
    )
  } catch (error) {
    console.error("Heart deletion error:", error)
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    )
  }
}

export async function GET(request: NextRequest, params: any) {
  try {
    const { id } = params?.params || {}
    
    // Verify post exists
    const post = await prisma.post.findUnique({
      where: { id }
    })

    if (!post) {
      return NextResponse.json(
        { error: "Post not found" },
        { status: 404 }
      )
    }

    // Get hearts count and hearts with user info
    const hearts = await prisma.heart.findMany({
      where: { postId: id },
      include: {
        user: {
          select: {
            id: true,
            name: true,
            image: true
          }
        }
      },
      orderBy: {
        createdAt: 'desc'
      }
    })

    return NextResponse.json({
      heartsCount: hearts.length,
      hearts: hearts.map((heart: any) => ({
        id: heart.id,
        createdAt: heart.createdAt,
        user: heart.user
      }))
    })
  } catch (error) {
    console.error("Hearts retrieval error:", error)
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    )
  }
} 