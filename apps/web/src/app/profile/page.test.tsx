import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import ProfilePage from './page'
import { SessionProvider } from 'next-auth/react'
import { vi } from 'vitest'

// Mock fetch for profile API
const mockProfile = {
  id: 'user1',
  name: 'Test User',
  email: 'test@example.com',
  image: '',
  createdAt: '2023-01-01T00:00:00.000Z',
  updatedAt: '2023-01-01T00:00:00.000Z',
  location: 'Tel Aviv',
  about: 'I love gratitude!',
  birthday: '1990-05-10T00:00:00.000Z',
  gender: 'female',
  website: 'https://example.com',
  interests: ['Mindfulness', 'Travel'],
  occupation: 'Developer'
}

// @ts-ignore
// eslint-disable-next-line
// @ts-expect-error
// eslint-disable-next-line
// @ts-ignore
// eslint-disable-next-line
// @ts-expect-error
// eslint-disable-next-line
global.fetch = vi.fn((url: string, options?: any) => {
  if (typeof url === 'string' && url.startsWith('/api/users/profile')) {
    if (!options || options.method === 'GET') {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ user: mockProfile })
      })
    }
    if (options.method === 'PUT') {
      const body = JSON.parse(options.body)
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ user: { ...mockProfile, ...body } })
      })
    }
  }
  return Promise.reject(new Error('Unknown API call'))
})

const session = {
  user: { id: 'user1', name: 'Test User', email: 'test@example.com' },
  expires: '2099-01-01T00:00:00.000Z'
}

describe('ProfilePage', () => {
  it('renders profile fields and allows editing and saving', async () => {
    render(
      <SessionProvider session={session as any}>
        <ProfilePage />
      </SessionProvider>
    )

    // Wait for profile to load
    expect(await screen.findByDisplayValue('Test User')).toBeInTheDocument()
    expect(screen.getByDisplayValue('test@example.com')).toBeInTheDocument()
    expect(screen.getByText('Location:')).toBeInTheDocument()
    expect(screen.getByText('About:')).toBeInTheDocument()
    expect(screen.getByText('Birthday:')).toBeInTheDocument()
    expect(screen.getByText('Gender:')).toBeInTheDocument()
    expect(screen.getByText('Website:')).toBeInTheDocument()
    expect(screen.getByText('Interests:')).toBeInTheDocument()
    expect(screen.getByText('Occupation:')).toBeInTheDocument()

    // Click edit
    fireEvent.click(screen.getByRole('button', { name: /edit profile/i }))

    // Change some fields
    fireEvent.change(screen.getByLabelText(/Name/i), { target: { value: 'New Name' } })
    fireEvent.change(screen.getByLabelText(/Location/i), { target: { value: 'Jerusalem' } })
    fireEvent.change(screen.getByLabelText(/About/i), { target: { value: 'Updated bio' } })
    fireEvent.change(screen.getByLabelText(/Birthday/i), { target: { value: '1992-12-31' } })
    fireEvent.change(screen.getByLabelText(/Gender/i), { target: { value: 'male' } })
    fireEvent.change(screen.getByLabelText(/Website/i), { target: { value: 'https://newsite.com' } })
    fireEvent.change(screen.getByLabelText(/Interests/i), { target: { value: 'Coding, Music' } })
    fireEvent.change(screen.getByLabelText(/Occupation/i), { target: { value: 'Engineer' } })

    // Save
    fireEvent.click(screen.getByRole('button', { name: /save/i }))

    // Wait for save and view mode
    await waitFor(() => {
      expect(screen.getByText('Profile updated successfully!')).toBeInTheDocument()
      expect(screen.getByText('New Name')).toBeInTheDocument()
      expect(screen.getByText('Jerusalem')).toBeInTheDocument()
      expect(screen.getByText('Updated bio')).toBeInTheDocument()
      expect(screen.getByText('Engineer')).toBeInTheDocument()
      expect(screen.getByText('Coding, Music')).toBeInTheDocument()
      expect(screen.getByText('https://newsite.com')).toBeInTheDocument()
    })
  })
}) 