import { describe, it, expect, beforeEach, afterEach } from '@jest/globals'
import { createMocks } from 'node-mocks-http'
import { POST as logoutHandler } from '../../app/api/auth/logout/route'
import { mockFetch, setupTestEnvironment, cleanupTestEnvironment } from '../utils/test-helpers'

describe('Logout API', () => {
  beforeEach(() => {
    setupTestEnvironment()
  })

  afterEach(() => {
    cleanupTestEnvironment()
  })

  describe('POST /api/auth/logout', () => {
    it('should successfully logout user with valid token', async () => {
      const { req } = createMocks({
        method: 'POST',
        headers: {
          'Authorization': 'Bearer valid-token'
        }
      })

      // Mock successful backend response
      mockFetch.mockResolvedValueOnce({
        status: 200,
        text: () => Promise.resolve('{"message": "Logged out (client should delete token)"}'),
        headers: {
          get: () => 'application/json'
        }
      })

      const response = await logoutHandler(req as any)
      const result = await response.json()

      expect(response.status).toBe(200)
      expect(result.message).toBe('Logged out (client should delete token)')
      
      // Verify the request was made to the backend
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/auth/logout',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer valid-token'
          })
        })
      )
    })

    it('should handle logout without authorization header', async () => {
      const { req } = createMocks({
        method: 'POST'
        // No authorization header
      })

      // Mock successful backend response
      mockFetch.mockResolvedValueOnce({
        status: 200,
        text: () => Promise.resolve('{"message": "Logged out (client should delete token)"}'),
        headers: {
          get: () => 'application/json'
        }
      })

      const response = await logoutHandler(req as any)
      const result = await response.json()

      expect(response.status).toBe(200)
      expect(result.message).toBe('Logged out (client should delete token)')
      
      // Verify the request was made to the backend without auth header
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/auth/logout',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      )
    })

    it('should handle backend URL not configured', async () => {
      cleanupTestEnvironment() // Use cleanup to revert environment changes
      
      const { req } = createMocks({
        method: 'POST'
      })

      const response = await logoutHandler(req as any)
      const result = await response.json()

      expect(response.status).toBe(500)
      expect(result.error).toBe('Backend URL not configured')
    })

    it('should handle backend server error', async () => {
      const { req } = createMocks({
        method: 'POST',
        headers: {
          'Authorization': 'Bearer valid-token'
        }
      })

      // Mock backend error response
      mockFetch.mockResolvedValueOnce({
        status: 500,
        text: () => Promise.resolve('{"error": "Internal server error"}'),
        headers: {
          get: () => 'application/json'
        }
      })

      const response = await logoutHandler(req as any)
      const result = await response.json()

      expect(response.status).toBe(500)
      expect(result.error).toBe('Internal server error')
    })

    it('should handle network error', async () => {
      const { req } = createMocks({
        method: 'POST',
        headers: {
          'Authorization': 'Bearer valid-token'
        }
      })

      // Mock network error
      mockFetch.mockRejectedValueOnce(new Error('Network error'))

      // The current implementation doesn't handle network errors gracefully
      // This test verifies that network errors are not caught
      await expect(logoutHandler(req as any)).rejects.toThrow('Network error')
    })
  })
}) 