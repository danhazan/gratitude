import { NextRequest } from "next/server"

export async function POST(request: NextRequest) {
  const body = await request.json();
  const backendUrl = process.env.NEXT_PUBLIC_API_URL?.replace(/\/api\/v1$/, '')
  if (!backendUrl) {
    return new Response(JSON.stringify({ error: 'Backend URL not configured' }), { status: 500 })
  }
  const res = await fetch(backendUrl + '/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await res.text();
  return new Response(data, { status: res.status, headers: { 'Content-Type': res.headers.get('Content-Type') || 'application/json' } });
} 