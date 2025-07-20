import { NextRequest, NextResponse } from "next/server"
import { PrismaClient } from "@prisma/client"

const prisma = new PrismaClient()

// GET /api/notifications?unread=1&page=1&pageSize=20
export async function GET(request: NextRequest) {
  try {
    // For MVP, get userId from query (in real app, use session)
    const { searchParams } = new URL(request.url)
    const userId = searchParams.get("userId")
    const unread = searchParams.get("unread") === "1"
    const page = parseInt(searchParams.get("page") || "1", 10)
    const pageSize = parseInt(searchParams.get("pageSize") || "20", 10)
    if (!userId) {
      return NextResponse.json({ error: "User ID is required" }, { status: 400 })
    }
    const where: any = { userId }
    if (unread) where.readAt = null
    const notifications = await prisma.notification.findMany({
      where,
      orderBy: { createdAt: "desc" },
      skip: (page - 1) * pageSize,
      take: pageSize
    })
    const total = await prisma.notification.count({ where })
    return NextResponse.json({ notifications, total })
  } catch (error) {
    console.error("Notifications GET error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}

// POST /api/notifications (internal: trigger notification)
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { userId, type, priority, title, message, data, channel } = body
    if (!userId || !type || !title || !message) {
      return NextResponse.json({ error: "Missing required fields" }, { status: 400 })
    }
    const notification = await prisma.notification.create({
      data: {
        userId,
        type,
        priority: priority || "normal",
        title,
        message,
        data: data || {},
        channel: channel || "in_app"
      }
    })
    return NextResponse.json({ notification }, { status: 201 })
  } catch (error) {
    console.error("Notifications POST error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
} 