import { NextRequest } from "next/server"

export async function GET(request: NextRequest) {
  const backendUrl = process.env.NEXT_PUBLIC_API_URL?.replace(/\/api\/v1$/, '')
  if (!backendUrl) {
    return new Response(JSON.stringify({ error: 'Backend URL not configured' }), { status: 500 })
  }
  
  // Get the authorization header from the request
  const authHeader = request.headers.get('Authorization')
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return new Response(JSON.stringify({ error: 'No valid authorization header' }), { status: 401 })
  }
  
  const res = await fetch(backendUrl + '/api/v1/auth/session', {
    method: 'GET',
    headers: { 
      'Content-Type': 'application/json',
      'Authorization': authHeader
    },
  });
  
  const data = await res.text();
  return new Response(data, { 
    status: res.status, 
    headers: { 'Content-Type': res.headers.get('Content-Type') || 'application/json' } 
  });
} 