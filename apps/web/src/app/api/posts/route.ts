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
    console.log("Fetching posts from database...")
    
    // Simple query first
    const postCount = await prisma.post.count()
    console.log(`Total posts in database: ${postCount}`)
    
    const posts = await prisma.post.findMany({
      orderBy: {
        createdAt: 'desc'
      },
      include: {
        author: {
          select: {
            id: true,
            name: true,
            image: true
          }
        }
      }
    })

    console.log(`Found ${posts.length} posts`)

    return NextResponse.json({
      posts: posts.map((post: any) => ({
        id: post.id,
        content: post.content,
        postType: post.postType,
        createdAt: post.createdAt,
        author: post.author
      }))
    })
  } catch (error) {
    console.error("Posts retrieval error:", error)
    return NextResponse.json(
      { error: "Internal server error", details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    // Handle both real requests and test mocks
    let body
    if (request.json) {
      body = await request.json()
    } else {
      // For test mocks, the body is already available
      body = (request as any).body
    }

    const { content, postType, authorId } = body

    // Validate input
    if (!content || !content.trim()) {
      return NextResponse.json(
        { error: "Content is required" },
        { status: 400 }
      )
    }

    if (!postType || !['daily', 'photo', 'spontaneous'].includes(postType)) {
      return NextResponse.json(
        { error: "Invalid post type" },
        { status: 400 }
      )
    }

    if (!authorId) {
      return NextResponse.json(
        { error: "Author ID is required" },
        { status: 400 }
      )
    }

    // Verify user exists
    const user = await prisma.user.findUnique({
      where: { id: authorId }
    })

    if (!user) {
      return NextResponse.json(
        { error: "User not found" },
        { status: 404 }
      )
    }

    // Create post
    const post = await prisma.post.create({
      data: {
        content: content.trim(),
        postType,
        authorId,
      },
      include: {
        author: {
          select: {
            id: true,
            name: true,
            image: true
          }
        }
      }
    })

    return NextResponse.json(
      { 
        message: "Post created successfully", 
        post: {
          id: post.id,
          content: post.content,
          postType: post.postType,
          authorId: post.authorId,
          createdAt: post.createdAt,
          author: post.author
        }
      },
      { status: 201 }
    )
  } catch (error) {
    console.error("Post creation error:", error)
    return NextResponse.json(
      { error: "Internal server error", details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    )
  }
} 