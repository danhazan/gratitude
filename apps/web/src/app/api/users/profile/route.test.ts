import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { createMocks } from 'node-mocks-http'
import { GET, PUT } from './route'
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

describe('User Profile API', () => {
  beforeEach(async () => {
    // Clean up database before each test
    await prisma.user.deleteMany()
  })

  afterEach(async () => {
    // Clean up after each test
    await prisma.user.deleteMany()
  })

  describe('GET /api/users/profile', () => {
    it('should return user profile successfully', async () => {
      // Create a user
      const user = await prisma.user.create({
        data: {
          name: 'Test User',
          email: 'test@example.com',
          password: 'hashedpassword',
          image: 'https://example.com/avatar.jpg'
        }
      })

      const { req } = createMocks({
        method: 'GET',
        query: {
          userId: user.id
        }
      })

      const response = await GET(req)
      const data = await response.json()

      expect(response.status).toBe(200)
      expect(data.user.id).toBe(user.id)
      expect(data.user.name).toBe('Test User')
      expect(data.user.email).toBe('test@example.com')
      expect(data.user.image).toBe('https://example.com/avatar.jpg')
      expect(data.user.password).toBeUndefined() // Password should not be returned
    })

    it('should return 404 when user does not exist', async () => {
      const { req } = createMocks({
        method: 'GET',
        query: {
          userId: 'non-existent-user-id'
        }
      })

      const response = await GET(req)
      const data = await response.json()

      expect(response.status).toBe(404)
      expect(data.error).toBe('User not found')
    })

    it('should return 400 when userId is missing', async () => {
      const { req } = createMocks({
        method: 'GET',
        query: {}
      })

      const response = await GET(req)
      const data = await response.json()

      expect(response.status).toBe(400)
      expect(data.error).toBe('User ID is required')
    })
  })

  describe('PUT /api/users/profile', () => {
    it('should update user profile successfully', async () => {
      // Create a user
      const user = await prisma.user.create({
        data: {
          name: 'Original Name',
          email: 'original@example.com',
          password: 'hashedpassword'
        }
      })

      const { req } = createMocks({
        method: 'PUT',
        body: {
          userId: user.id,
          name: 'Updated Name',
          email: 'updated@example.com',
          image: 'https://example.com/new-avatar.jpg'
        }
      })

      const response = await PUT(req)
      const data = await response.json()

      expect(response.status).toBe(200)
      expect(data.message).toBe('Profile updated successfully')
      expect(data.user.name).toBe('Updated Name')
      expect(data.user.email).toBe('updated@example.com')
      expect(data.user.image).toBe('https://example.com/new-avatar.jpg')

      // Verify the user was updated in database
      const updatedUser = await prisma.user.findUnique({
        where: { id: user.id }
      })

      expect(updatedUser?.name).toBe('Updated Name')
      expect(updatedUser?.email).toBe('updated@example.com')
      expect(updatedUser?.image).toBe('https://example.com/new-avatar.jpg')
    })

    it('should return 400 when userId is missing', async () => {
      const { req } = createMocks({
        method: 'PUT',
        body: {
          name: 'Updated Name',
          email: 'updated@example.com'
        }
      })

      const response = await PUT(req)
      const data = await response.json()

      expect(response.status).toBe(400)
      expect(data.error).toBe('User ID is required')
    })

    it('should return 404 when user does not exist', async () => {
      const { req } = createMocks({
        method: 'PUT',
        body: {
          userId: 'non-existent-user-id',
          name: 'Updated Name',
          email: 'updated@example.com'
        }
      })

      const response = await PUT(req)
      const data = await response.json()

      expect(response.status).toBe(404)
      expect(data.error).toBe('User not found')
    })

    it('should return 409 when email is already taken by another user', async () => {
      // Create two users
      const user1 = await prisma.user.create({
        data: {
          name: 'User 1',
          email: 'user1@example.com',
          password: 'hashedpassword'
        }
      })

      const user2 = await prisma.user.create({
        data: {
          name: 'User 2',
          email: 'user2@example.com',
          password: 'hashedpassword'
        }
      })

      const { req } = createMocks({
        method: 'PUT',
        body: {
          userId: user2.id,
          name: 'Updated Name',
          email: 'user1@example.com' // Try to use user1's email
        }
      })

      const response = await PUT(req)
      const data = await response.json()

      expect(response.status).toBe(409)
      expect(data.error).toBe('Email is already taken')
    })

    it('should allow user to keep their own email', async () => {
      // Create a user
      const user = await prisma.user.create({
        data: {
          name: 'Test User',
          email: 'test@example.com',
          password: 'hashedpassword'
        }
      })

      const { req } = createMocks({
        method: 'PUT',
        body: {
          userId: user.id,
          name: 'Updated Name',
          email: 'test@example.com' // Same email as before
        }
      })

      const response = await PUT(req)
      const data = await response.json()

      expect(response.status).toBe(200)
      expect(data.message).toBe('Profile updated successfully')
    })

    it('should validate email format', async () => {
      const user = await prisma.user.create({
        data: {
          name: 'Test User',
          email: 'test@example.com',
          password: 'hashedpassword'
        }
      })

      const { req } = createMocks({
        method: 'PUT',
        body: {
          userId: user.id,
          name: 'Updated Name',
          email: 'invalid-email-format'
        }
      })

      const response = await PUT(req)
      const data = await response.json()

      expect(response.status).toBe(400)
      expect(data.error).toBe('Invalid email format')
    })

    it('should validate name length', async () => {
      const user = await prisma.user.create({
        data: {
          name: 'Test User',
          email: 'test@example.com',
          password: 'hashedpassword'
        }
      })

      const { req } = createMocks({
        method: 'PUT',
        body: {
          userId: user.id,
          name: 'A'.repeat(101), // Name too long
          email: 'updated@example.com'
        }
      })

      const response = await PUT(req)
      const data = await response.json()

      expect(response.status).toBe(400)
      expect(data.error).toBe('Name must be between 1 and 100 characters')
    })
  })
}) 