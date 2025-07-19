import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { createMocks } from 'node-mocks-http'
import { POST, GET } from './route'
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

describe('Posts API', () => {
  beforeEach(async () => {
    // Clean up database before each test
    await prisma.post.deleteMany()
    await prisma.user.deleteMany()
  })

  afterEach(async () => {
    // Clean up after each test
    await prisma.post.deleteMany()
    await prisma.user.deleteMany()
  })

  describe('POST /api/posts', () => {
    it('should create a new post and persist it to database', async () => {
      // First create a user
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
          content: 'I am grateful for this beautiful day',
          postType: 'daily',
          authorId: user.id
        }
      })

      const response = await POST(req)
      const data = await response.json()

      expect(response.status).toBe(201)
      expect(data.post).toBeDefined()
      expect(data.post.content).toBe('I am grateful for this beautiful day')
      expect(data.post.postType).toBe('daily')
      expect(data.post.authorId).toBe(user.id)

      // Verify the post was actually saved to database
      const savedPost = await prisma.post.findUnique({
        where: { id: data.post.id },
        include: { author: true }
      })

      expect(savedPost).toBeDefined()
      expect(savedPost?.content).toBe('I am grateful for this beautiful day')
      expect(savedPost?.postType).toBe('daily')
      expect(savedPost?.authorId).toBe(user.id)
    })

    it('should return 400 for invalid post data', async () => {
      const { req } = createMocks({
        method: 'POST',
        body: {
          content: '', // Empty content
          postType: 'daily'
        }
      })

      const response = await POST(req)
      expect(response.status).toBe(400)
    })
  })

  describe('GET /api/posts', () => {
    it('should return all posts from database', async () => {
      // Create a user
      const user = await prisma.user.create({
        data: {
          name: 'Test User',
          email: 'test@example.com',
          password: 'hashedpassword'
        }
      })

      // Create some test posts
      await prisma.post.createMany({
        data: [
          {
            content: 'First grateful post',
            postType: 'daily',
            authorId: user.id
          },
          {
            content: 'Second grateful post',
            postType: 'spontaneous',
            authorId: user.id
          }
        ]
      })

      const { req } = createMocks({
        method: 'GET'
      })

      const response = await GET(req)
      const data = await response.json()

      expect(response.status).toBe(200)
      expect(data.posts).toBeDefined()
      expect(data.posts).toHaveLength(2)
      expect(data.posts[0].content).toBe('First grateful post')
      expect(data.posts[1].content).toBe('Second grateful post')
    })

    it('should return empty array when no posts exist', async () => {
      const { req } = createMocks({
        method: 'GET'
      })

      const response = await GET(req)
      const data = await response.json()

      expect(response.status).toBe(200)
      expect(data.posts).toBeDefined()
      expect(data.posts).toHaveLength(0)
    })
  })
}) 