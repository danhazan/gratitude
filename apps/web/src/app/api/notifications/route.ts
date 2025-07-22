import { NextRequest, NextResponse } from "next/server"

// GET /api/notifications?unread=1&page=1&pageSize=20
export async function GET() {
  return new Response(JSON.stringify({ error: 'Not implemented. Use backend API.' }), { status: 501 })
}

// POST /api/notifications (internal: trigger notification)
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { userId, type, priority, title, message, data, channel } = body
    if (!userId || !type || !title || !message) {
      return NextResponse.json({ error: "Missing required fields" }, { status: 400 })
    }
    // This part of the code was not part of the edit, so it remains unchanged.
    // The original code used PrismaClient, which is being removed.
    // This function will now return a 501 Not Implemented response
    // as the backend logic for creating notifications is not available.
    return new Response(JSON.stringify({ error: 'Not implemented. Use backend API.' }), { status: 501 })
  } catch (error) {
    console.error("Notifications POST error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
} 