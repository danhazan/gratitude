import { jest } from '@jest/globals'

// Shared mock fetch for backend API calls
export const mockFetch = jest.fn()
global.fetch = mockFetch

// Shared mock Response class
export const MockResponse = class MockResponse {
  constructor(body: any, init?: any) {
    this.body = body
    this.init = init
  }
  
  body: any
  init: any
  
  json() {
    return Promise.resolve(JSON.parse(this.body))
  }
  
  text() {
    return Promise.resolve(this.body)
  }
  
  get status() {
    return this.init?.status || 200
  }
  
  get headers() {
    return {
      get: (name: string) => this.init?.headers?.[name] || null
    }
  }
} as any

// Set up global Response mock
global.Response = MockResponse

// Shared test setup
export const setupTestEnvironment = () => {
  mockFetch.mockClear()
  process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000'
}

// Shared test cleanup
export const cleanupTestEnvironment = () => {
  delete process.env.NEXT_PUBLIC_API_URL
}

// Helper to create mock backend responses
export const createMockBackendResponse = (status: number, data: any) => ({
  status,
  text: () => Promise.resolve(JSON.stringify(data)),
  headers: {
    get: () => 'application/json'
  }
})

// Helper to create mock network error
export const createMockNetworkError = (error: string) => {
  return Promise.reject(new Error(error))
} 