import { NextRequest, NextResponse } from "next/server"
import { PrismaClient } from "@prisma/client"

// Use singleton pattern for Prisma client
const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

const prisma = globalForPrisma.prisma ?? new PrismaClient()

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma

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

    const { sessionToken } = body

    // Validate input
    if (!sessionToken) {
      return NextResponse.json(
        { error: "Session token is required" },
        { status: 400 }
      )
    }

    // Find and delete the session
    const session = await prisma.session.findUnique({
      where: { sessionToken }
    })

    if (!session) {
      return NextResponse.json(
        { error: "Session not found" },
        { status: 404 }
      )
    }

    // Delete the session
    await prisma.session.delete({
      where: { sessionToken }
    })

    return NextResponse.json(
      { message: "Logged out successfully" },
      { status: 200 }
    )
  } catch (error) {
    console.error("Logout error:", error)
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    )
  }
} 