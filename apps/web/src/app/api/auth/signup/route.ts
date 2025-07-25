import { NextRequest, NextResponse } from "next/server"
import bcrypt from "bcryptjs"

export async function POST(request: Request) {
  const body = await request.json();
  const backendUrl = process.env.NEXT_PUBLIC_API_URL?.replace(/\/api\/v1$/, '')
  if (!backendUrl) {
    return new Response(JSON.stringify({ error: 'Backend URL not configured' }), { status: 500 })
  }
  // The FastAPI endpoint expects email, username, and password
  if (!body.email || !body.password || !body.username) {
    return new Response(JSON.stringify({ error: 'Email, username, and password are required' }), { status: 400 })
  }
  const res = await fetch(backendUrl + '/api/v1/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: body.email, username: body.username, password: body.password }),
  });
  const data = await res.text();
  return new Response(data, { status: res.status, headers: { 'Content-Type': res.headers.get('Content-Type') || 'application/json' } });
} 