import { describe, it, expect, beforeEach, afterEach } from '@jest/globals'
import { createMocks } from 'node-mocks-http'
import { POST, DELETE, GET } from './route'
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

describe('Hearts API', () => {
  beforeEach(async () => {
    // Clean up database before each test
    await prisma.heart.deleteMany()
    await prisma.post.deleteMany()
    await prisma.user.deleteMany()
  })

  afterEach(async () => {
    // Clean up after each test
    await prisma.heart.deleteMany()
    await prisma.post.deleteMany()
    await prisma.user.deleteMany()
  })

  describe('POST /api/posts/[id]/hearts', () => {
    it('should heart a post successfully', async () => {
      // Create a user
      const user = await prisma.user.create({
        data: {
          name: 'Test User',
          email: 'test@example.com',
          password: 'hashedpassword'
        }
      })

      // Create a post
      const post = await prisma.post.create({
        data: {
          content: 'I am grateful for this beautiful day',
          postType: 'daily',
          authorId: user.id
        }
      })

      const { req } = createMocks({
        method: 'POST',
        body: {
          userId: user.id
        }
      })

      // Mock the params
      const params = { id: post.id }

      const response = await POST(req, { params })
      const data = await response.json()

      expect(response.status).toBe(201)
      expect(data.message).toBe('Post hearted successfully')

      // Verify the heart was saved to database
      const savedHeart = await prisma.heart.findFirst({
        where: {
          userId: user.id,
          postId: post.id
        }
      })

      expect(savedHeart).toBeDefined()
      expect(savedHeart?.userId).toBe(user.id)
      expect(savedHeart?.postId).toBe(post.id)
    })

    it('should return 400 when user ID is missing', async () => {
      const { req } = createMocks({
        method: 'POST',
        body: {}
      })

      const params = { id: 'test-post-id' }

      const response = await POST(req, { params })
      const data = await response.json()

      expect(response.status).toBe(400)
      expect(data.error).toBe('User ID is required')
    })

    it('should return 404 when post does not exist', async () => {
      const user = await prisma.user.create({
        data: {
          name: 'Test User',
          email: 'test@example.com',
          password: 'hashedpassword'
        }
      })

      const { req } = createMocks({
        method: 'POST',
        body: {
          userId: user.id
        }
      })

      const params = { id: 'non-existent-post-id' }

      const response = await POST(req, { params })
      const data = await response.json()

      expect(response.status).toBe(404)
      expect(data.error).toBe('Post not found')
    })

    it('should return 409 when user already hearted the post', async () => {
      const user = await prisma.user.create({
        data: {
          name: 'Test User',
          email: 'test@example.com',
          password: 'hashedpassword'
        }
      })

      const post = await prisma.post.create({
        data: {
          content: 'I am grateful for this beautiful day',
          postType: 'daily',
          authorId: user.id
        }
      })

      // Create an existing heart
      await prisma.heart.create({
        data: {
          userId: user.id,
          postId: post.id
        }
      })

      const { req } = createMocks({
        method: 'POST',
        body: {
          userId: user.id
        }
      })

      const params = { id: post.id }

      const response = await POST(req, { params })
      const data = await response.json()

      expect(response.status).toBe(409)
      expect(data.error).toBe('User has already hearted this post')
    })
  })

  describe('DELETE /api/posts/[id]/hearts', () => {
    it('should unheart a post successfully', async () => {
      const user = await prisma.user.create({
        data: {
          name: 'Test User',
          email: 'test@example.com',
          password: 'hashedpassword'
        }
      })

      const post = await prisma.post.create({
        data: {
          content: 'I am grateful for this beautiful day',
          postType: 'daily',
          authorId: user.id
        }
      })

      // Create a heart first
      await prisma.heart.create({
        data: {
          userId: user.id,
          postId: post.id
        }
      })

      const { req } = createMocks({
        method: 'DELETE',
        body: {
          userId: user.id
        }
      })

      const params = { id: post.id }

      const response = await DELETE(req, { params })
      const data = await response.json()

      expect(response.status).toBe(200)
      expect(data.message).toBe('Post unhearted successfully')

      // Verify the heart was deleted
      const deletedHeart = await prisma.heart.findFirst({
        where: {
          userId: user.id,
          postId: post.id
        }
      })

      expect(deletedHeart).toBeNull()
    })

    it('should return 404 when heart does not exist', async () => {
      const user = await prisma.user.create({
        data: {
          name: 'Test User',
          email: 'test@example.com',
          password: 'hashedpassword'
        }
      })

      const post = await prisma.post.create({
        data: {
          content: 'I am grateful for this beautiful day',
          postType: 'daily',
          authorId: user.id
        }
      })

      const { req } = createMocks({
        method: 'DELETE',
        body: {
          userId: user.id
        }
      })

      const params = { id: post.id }

      const response = await DELETE(req, { params })
      const data = await response.json()

      expect(response.status).toBe(404)
      expect(data.error).toBe('Heart not found')
    })
  })

  describe('GET /api/posts/[id]/hearts', () => {
    it('should return hearts count for a post', async () => {
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

      const post = await prisma.post.create({
        data: {
          content: 'I am grateful for this beautiful day',
          postType: 'daily',
          authorId: user1.id
        }
      })

      // Create hearts
      await prisma.heart.createMany({
        data: [
          { userId: user1.id, postId: post.id },
          { userId: user2.id, postId: post.id }
        ]
      })

      const { req } = createMocks({
        method: 'GET'
      })

      const params = { id: post.id }

      const response = await GET(req, { params })
      const data = await response.json()

      expect(response.status).toBe(200)
      expect(data.heartsCount).toBe(2)
      expect(data.hearts).toHaveLength(2)
      expect(data.hearts[0].user.name).toBe('User 1')
      expect(data.hearts[1].user.name).toBe('User 2')
    })

    it('should return 0 hearts for post with no hearts', async () => {
      const user = await prisma.user.create({
        data: {
          name: 'Test User',
          email: 'test@example.com',
          password: 'hashedpassword'
        }
      })

      const post = await prisma.post.create({
        data: {
          content: 'I am grateful for this beautiful day',
          postType: 'daily',
          authorId: user.id
        }
      })

      const { req } = createMocks({
        method: 'GET'
      })

      const params = { id: post.id }

      const response = await GET(req, { params })
      const data = await response.json()

      expect(response.status).toBe(200)
      expect(data.heartsCount).toBe(0)
      expect(data.hearts).toHaveLength(0)
    })

    it('should return 404 when post does not exist', async () => {
      const { req } = createMocks({
        method: 'GET'
      })

      const params = { id: 'non-existent-post-id' }

      const response = await GET(req, { params })
      const data = await response.json()

      expect(response.status).toBe(404)
      expect(data.error).toBe('Post not found')
    })
  })
}) 