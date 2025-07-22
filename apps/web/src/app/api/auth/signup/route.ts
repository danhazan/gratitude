import { NextRequest, NextResponse } from "next/server"
import bcrypt from "bcryptjs"

export async function POST() {
  return new Response(JSON.stringify({ error: 'Not implemented. Use backend API.' }), { status: 501 })
} 