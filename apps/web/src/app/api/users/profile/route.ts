import { NextRequest } from "next/server"

export async function GET(request: NextRequest) {
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"
  const authHeader = request.headers.get("authorization")
  if (!authHeader) {
    return new Response(JSON.stringify({ error: "Not authenticated" }), { status: 401 })
  }
  const res = await fetch(`${backendUrl}/api/v1/auth/session`, {
    method: "GET",
    headers: {
      "Authorization": authHeader,
      "Content-Type": "application/json"
    }
  })
  const data = await res.text()
  return new Response(data, { status: res.status, headers: { "Content-Type": res.headers.get("Content-Type") || "application/json" } })
}

export async function PUT(request: NextRequest) {
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"
  const authHeader = request.headers.get("authorization")
  if (!authHeader) {
    return new Response(JSON.stringify({ error: "Not authenticated" }), { status: 401 })
  }
  const body = await request.text()
  const res = await fetch(`${backendUrl}/api/v1/auth/session`, {
    method: "PUT",
    headers: {
      "Authorization": authHeader,
      "Content-Type": "application/json"
    },
    body
  })
  const data = await res.text()
  return new Response(data, { status: res.status, headers: { "Content-Type": res.headers.get("Content-Type") || "application/json" } })
} 