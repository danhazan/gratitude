import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { createMocks } from 'node-mocks-http'
import { POST } from './route'
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

describe('Logout API', () => {
  beforeEach(async () => {
    // Clean up database before each test
    await prisma.session.deleteMany()
    await prisma.user.deleteMany()
  })

  afterEach(async () => {
    // Clean up after each test
    await prisma.session.deleteMany()
    await prisma.user.deleteMany()
  })

  describe('POST /api/auth/logout', () => {
    it('should successfully logout user and clear session', async () => {
      // Create a test user
      const user = await prisma.user.create({
        data: {
          name: 'Test User',
          email: 'test@example.com',
          password: 'hashedpassword'
        }
      })

      // Create a session for the user
      const session = await prisma.session.create({
        data: {
          sessionToken: 'test-session-token',
          userId: user.id,
          expires: new Date(Date.now() + 24 * 60 * 60 * 1000) // 24 hours from now
        }
      })

      // Verify session exists
      const existingSession = await prisma.session.findUnique({
        where: { sessionToken: 'test-session-token' }
      })
      expect(existingSession).toBeDefined()

      const { req } = createMocks({
        method: 'POST',
        body: {
          sessionToken: 'test-session-token'
        }
      })

      const response = await POST(req)
      const data = await response.json()

      expect(response.status).toBe(200)
      expect(data.message).toBe('Logged out successfully')

      // Verify session was deleted
      const deletedSession = await prisma.session.findUnique({
        where: { sessionToken: 'test-session-token' }
      })
      expect(deletedSession).toBeNull()
    })

    it('should return 400 when no session token provided', async () => {
      const { req } = createMocks({
        method: 'POST',
        body: {}
      })

      const response = await POST(req)
      const data = await response.json()

      expect(response.status).toBe(400)
      expect(data.error).toBe('Session token is required')
    })

    it('should return 404 when session token does not exist', async () => {
      const { req } = createMocks({
        method: 'POST',
        body: {
          sessionToken: 'non-existent-token'
        }
      })

      const response = await POST(req)
      const data = await response.json()

      expect(response.status).toBe(404)
      expect(data.error).toBe('Session not found')
    })

    it('should handle expired sessions gracefully', async () => {
      // Create a test user
      const user = await prisma.user.create({
        data: {
          name: 'Test User',
          email: 'test@example.com',
          password: 'hashedpassword'
        }
      })

      // Create an expired session
      const expiredSession = await prisma.session.create({
        data: {
          sessionToken: 'expired-session-token',
          userId: user.id,
          expires: new Date(Date.now() - 24 * 60 * 60 * 1000) // 24 hours ago
        }
      })

      const { req } = createMocks({
        method: 'POST',
        body: {
          sessionToken: 'expired-session-token'
        }
      })

      const response = await POST(req)
      const data = await response.json()

      expect(response.status).toBe(200)
      expect(data.message).toBe('Logged out successfully')

      // Verify expired session was also deleted
      const deletedSession = await prisma.session.findUnique({
        where: { sessionToken: 'expired-session-token' }
      })
      expect(deletedSession).toBeNull()
    })
  })
}) 