import { describe, it, expect, beforeEach, afterEach } from '@jest/globals'
import { createMocks } from 'node-mocks-http'
import { POST as signupHandler } from '../../app/api/auth/signup/route'
import { POST as loginHandler } from '../../app/api/auth/login/route'
import { GET as sessionHandler } from '../../app/api/auth/session/route'
import { POST as logoutHandler } from '../../app/api/auth/logout/route'
import { mockFetch, setupTestEnvironment, cleanupTestEnvironment } from '../utils/test-helpers'

describe('Authentication Flow', () => {
  let accessToken: string = ''

  beforeEach(() => {
    setupTestEnvironment()
    accessToken = ''
  })

  afterEach(() => {
    cleanupTestEnvironment()
  })

  describe('Complete Authentication Flow', () => {
    it('should handle full authentication flow: signup -> login -> session -> logout', async () => {
      // Step 1: Signup
      const signupData = {
        username: 'testuser',
        email: 'test@example.com',
        password: 'testpassword123'
      }

      mockFetch.mockResolvedValueOnce({
        status: 201,
        text: () => Promise.resolve(JSON.stringify({
          id: 'user123',
          username: 'testuser',
          email: 'test@example.com'
        })),
        headers: new Map([['content-type', 'application/json']])
      })

      const { req: signupReq } = createMocks({
        method: 'POST',
        body: signupData
      })

      // Mock the json method on the request
      signupReq.json = jest.fn().mockResolvedValue(signupData)

      const signupResponse = await signupHandler(signupReq as any)
      const signupResult = await signupResponse.json()

      expect(signupResponse.status).toBe(201)
      expect(signupResult).toHaveProperty('id')
      expect(signupResult.username).toBe('testuser')
      expect(signupResult.email).toBe('test@example.com')

      // Step 2: Login
      const loginData = {
        email: 'test@example.com',
        password: 'testpassword123'
      }

      mockFetch.mockResolvedValueOnce({
        status: 200,
        text: () => Promise.resolve(JSON.stringify({
          access_token: 'mock-jwt-token-123',
          token_type: 'bearer'
        })),
        headers: new Map([['content-type', 'application/json']])
      })

      const { req: loginReq } = createMocks({
        method: 'POST',
        body: loginData
      })

      // Mock the json method on the request
      loginReq.json = jest.fn().mockResolvedValue(loginData)

      const loginResponse = await loginHandler(loginReq as any)
      const loginResult = await loginResponse.json()

      expect(loginResponse.status).toBe(200)
      expect(loginResult).toHaveProperty('access_token')
      expect(loginResult.token_type).toBe('bearer')

      accessToken = loginResult.access_token

      // Step 3: Check Session
      mockFetch.mockResolvedValueOnce({
        status: 200,
        text: () => Promise.resolve(JSON.stringify({
          id: 'user123',
          email: 'test@example.com',
          username: 'testuser'
        })),
        headers: new Map([['content-type', 'application/json']])
      })

      const { req: sessionReq } = createMocks({
        method: 'GET',
        headers: {
          'authorization': `Bearer ${accessToken}`
        }
      })

      const sessionResponse = await sessionHandler(sessionReq as any)
      const sessionResult = await sessionResponse.json()

      expect(sessionResponse.status).toBe(200)
      expect(sessionResult).toHaveProperty('id')
      expect(sessionResult.email).toBe('test@example.com')
      expect(sessionResult.username).toBe('testuser')

      // Step 4: Logout
      mockFetch.mockResolvedValueOnce({
        status: 200,
        text: () => Promise.resolve(JSON.stringify({
          message: 'Logged out (client should delete token)'
        })),
        headers: new Map([['content-type', 'application/json']])
      })

      const { req: logoutReq } = createMocks({
        method: 'POST',
        headers: {
          'authorization': `Bearer ${accessToken}`
        }
      })

      const logoutResponse = await logoutHandler(logoutReq as any)
      const logoutResult = await logoutResponse.json()

      expect(logoutResponse.status).toBe(200)
      expect(logoutResult.message).toBe('Logged out (client should delete token)')
    })
  })

  describe('Error Handling', () => {
    it('should handle signup with existing email', async () => {
      const signupData = {
        username: 'existinguser',
        email: 'existing@example.com',
        password: 'testpassword123'
      }

      mockFetch.mockResolvedValueOnce({
        status: 400,
        text: () => Promise.resolve(JSON.stringify({
          detail: 'Email already registered'
        })),
        headers: new Map([['content-type', 'application/json']])
      })

      const { req } = createMocks({
        method: 'POST',
        body: signupData
      })

      // Mock the json method on the request
      req.json = jest.fn().mockResolvedValue(signupData)

      const response = await signupHandler(req as any)
      const result = await response.json()

      expect(response.status).toBe(400)
      expect(result.detail).toBe('Email already registered')
    })

    it('should handle login with invalid credentials', async () => {
      const loginData = {
        email: 'wrong@example.com',
        password: 'wrongpassword'
      }

      mockFetch.mockResolvedValueOnce({
        status: 401,
        text: () => Promise.resolve(JSON.stringify({
          detail: 'Invalid credentials'
        })),
        headers: new Map([['content-type', 'application/json']])
      })

      const { req } = createMocks({
        method: 'POST',
        body: loginData
      })

      // Mock the json method on the request
      req.json = jest.fn().mockResolvedValue(loginData)

      const response = await loginHandler(req as any)
      const result = await response.json()

      expect(response.status).toBe(401)
      expect(result.detail).toBe('Invalid credentials')
    })

    it('should handle session check without token', async () => {
      const { req } = createMocks({
        method: 'GET'
        // No authorization header
      })

      const response = await sessionHandler(req as any)
      const result = await response.json()

      expect(response.status).toBe(401)
      expect(result.error).toBe('No valid authorization header')
    })

    it('should handle session check with invalid token', async () => {
      mockFetch.mockResolvedValueOnce({
        status: 401,
        text: () => Promise.resolve(JSON.stringify({
          detail: 'Invalid token'
        })),
        headers: new Map([['content-type', 'application/json']])
      })

      const { req } = createMocks({
        method: 'GET',
        headers: {
          'authorization': 'Bearer invalid-token'
        }
      })

      const response = await sessionHandler(req as any)
      const result = await response.json()

      expect(response.status).toBe(401)
      expect(result.detail).toBe('Invalid token')
    })
  })

  describe('Backend URL Configuration', () => {
    it('should handle missing backend URL configuration', async () => {
      // Temporarily remove the environment variable
      const originalUrl = process.env.NEXT_PUBLIC_API_URL
      delete process.env.NEXT_PUBLIC_API_URL

      const { req } = createMocks({
        method: 'POST',
        body: { email: 'test@example.com', password: 'password' }
      })

      // Mock the json method on the request
      req.json = jest.fn().mockResolvedValue({ email: 'test@example.com', password: 'password' })

      const response = await loginHandler(req as any)
      const result = await response.json()

      expect(response.status).toBe(500)
      expect(result.error).toBe('Backend URL not configured')

      // Restore the environment variable
      process.env.NEXT_PUBLIC_API_URL = originalUrl
    })
  })
}) 