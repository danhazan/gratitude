import { render, screen } from '@testing-library/react'
import { SessionProvider } from 'next-auth/react'
import FeedPage from './page'

// Mock NextAuth
const mockSession = {
  data: {
    user: {
      id: 'test-user-id',
      name: 'Test User',
      email: 'test@example.com',
      image: 'https://example.com/avatar.jpg'
    }
  },
  status: 'authenticated'
}

// Mock fetch for posts
global.fetch = jest.fn()

const mockPosts = [
  {
    id: '1',
    content: 'I am grateful for this beautiful day!',
    author: {
      id: 'user1',
      name: 'John Doe',
      image: 'https://example.com/john.jpg'
    },
    createdAt: '2024-01-01T10:00:00Z',
    postType: 'daily',
    heartsCount: 5,
    isHearted: false
  },
  {
    id: '2',
    content: 'Grateful for this amazing photo!',
    author: {
      id: 'user2',
      name: 'Jane Smith',
      image: 'https://example.com/jane.jpg'
    },
    createdAt: '2024-01-01T11:00:00Z',
    postType: 'photo',
    imageUrl: 'https://example.com/photo.jpg',
    heartsCount: 3,
    isHearted: true
  },
  {
    id: '3',
    content: 'Quick gratitude note',
    author: {
      id: 'user3',
      name: 'Bob Wilson',
      image: 'https://example.com/bob.jpg'
    },
    createdAt: '2024-01-01T12:00:00Z',
    postType: 'spontaneous',
    heartsCount: 1,
    isHearted: false
  }
]

describe('FeedPage Content Hierarchy', () => {
  beforeEach(() => {
    // Mock fetch responses
    ;(fetch as jest.Mock).mockImplementation((url) => {
      if (url === '/api/posts') {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ posts: mockPosts })
        })
      }
      if (url.includes('/hearts')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ 
            heartsCount: 0, 
            hearts: [] 
          })
        })
      }
      return Promise.resolve({ ok: false })
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders daily gratitude posts with 3x larger styling', () => {
    render(
      <SessionProvider session={mockSession}>
        <FeedPage />
      </SessionProvider>
    )

    // Check that daily gratitude posts have larger styling
    const dailyPost = screen.getByText('I am grateful for this beautiful day!')
    const dailyPostContainer = dailyPost.closest('article')
    
    expect(dailyPostContainer).toHaveClass('rounded-xl', 'shadow-lg', 'border-2', 'border-purple-100')
  })

  it('renders photo posts with 2x boost styling', () => {
    render(
      <SessionProvider session={mockSession}>
        <FeedPage />
      </SessionProvider>
    )

    // Check that photo posts have medium styling
    const photoPost = screen.getByText('Grateful for this amazing photo!')
    const photoPostContainer = photoPost.closest('article')
    
    expect(photoPostContainer).toHaveClass('shadow-md')
  })

  it('renders spontaneous text posts with compact styling', () => {
    render(
      <SessionProvider session={mockSession}>
        <FeedPage />
      </SessionProvider>
    )

    // Check that spontaneous posts have compact styling
    const spontaneousPost = screen.getByText('Quick gratitude note')
    const spontaneousPostContainer = spontaneousPost.closest('article')
    
    expect(spontaneousPostContainer).toHaveClass('shadow-sm')
  })

  it('applies correct text sizes based on post type', () => {
    render(
      <SessionProvider session={mockSession}>
        <FeedPage />
      </SessionProvider>
    )

    // Daily gratitude should have larger text
    const dailyPost = screen.getByText('I am grateful for this beautiful day!')
    expect(dailyPost).toHaveClass('text-lg')

    // Photo post should have medium text
    const photoPost = screen.getByText('Grateful for this amazing photo!')
    expect(photoPost).toHaveClass('text-base')

    // Spontaneous post should have compact text
    const spontaneousPost = screen.getByText('Quick gratitude note')
    expect(spontaneousPost).toHaveClass('text-sm')
  })

  it('applies correct padding based on post type', () => {
    render(
      <SessionProvider session={mockSession}>
        <FeedPage />
      </SessionProvider>
    )

    // Check that different post types have different padding
    const articles = screen.getAllByRole('article')
    
    // Daily gratitude should have largest padding
    expect(articles[0]).toHaveClass('p-6')
    
    // Photo post should have medium padding
    expect(articles[1]).toHaveClass('p-5')
    
    // Spontaneous post should have compact padding
    expect(articles[2]).toHaveClass('p-3')
  })
}) 