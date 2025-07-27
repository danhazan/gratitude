# Test Guidelines and Best Practices

## Overview

This document provides guidelines for writing and organizing tests in the Grateful project. We follow a structured approach to testing with clear separation between unit, integration, and end-to-end tests.

## Test Structure

### Backend Tests (`apps/api/tests/`)

```
tests/
├── conftest.py              # Shared test fixtures and configuration
├── unit/                    # Unit tests for individual components
│   ├── test_database.py     # Database operations and setup
│   ├── test_posts.py        # Post API unit tests
│   ├── test_users.py        # User API unit tests
│   └── test_follows.py      # Follow API unit tests
└── integration/             # Integration tests
    └── test_api_integration.py  # End-to-end API workflows
```

### Frontend Tests (`apps/web/src/tests/`)

```
tests/
├── setup.ts                 # Test configuration and setup
├── unit/                    # Unit tests for components
│   ├── components/          # React component tests
│   ├── hooks/              # Custom hook tests
│   └── utils/              # Utility function tests
├── integration/             # Integration tests for pages
│   ├── pages/              # Page component tests
│   └── api/                # API route tests
└── e2e/                    # End-to-end tests (future)
    └── workflows/          # User workflow tests
```

## Test Categories

### Unit Tests

**Purpose**: Test individual functions, components, or API endpoints in isolation.

**Backend Unit Tests**:
- Test individual API endpoints
- Mock database operations
- Test validation logic
- Test error handling

**Frontend Unit Tests**:
- Test React components in isolation
- Test custom hooks
- Test utility functions
- Mock external dependencies

**Best Practices**:
- Keep tests focused and atomic
- Mock external dependencies
- Test both success and error cases
- Use descriptive test names

### Integration Tests

**Purpose**: Test how components work together.

**Backend Integration Tests**:
- Test complete API workflows
- Use test databases
- Test data persistence
- Test authentication flows

**Frontend Integration Tests**:
- Test page components
- Test API route handlers
- Test component interactions
- Test form submissions

**Best Practices**:
- Test complete workflows
- Use test databases
- Test real data scenarios
- Verify data persistence

### End-to-End Tests (Future)

**Purpose**: Test complete user workflows from start to finish.

**Tools**: Playwright or Cypress

**Test Scenarios**:
- User registration and login
- Post creation and interaction
- Social features (likes, comments, follows)
- Profile management
- Search and discovery

**Best Practices**:
- Test real user scenarios
- Include authentication flows
- Test responsive design
- Test cross-browser compatibility

## Writing Tests

### Backend Test Examples

#### API Endpoint Test
```python
async def test_create_post_success(async_client, auth_headers):
    """Test successful post creation."""
    post_data = {
        "content": "I'm grateful for this test!",
        "post_type": "daily_gratitude",
        "title": "Test Post",
        "is_public": True
    }
    
    response = await async_client.post(
        "/api/v1/posts/",
        json=post_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == post_data["content"]
    assert data["post_type"] == post_data["post_type"]
```

#### Database Test
```python
async def test_user_creation(db_session):
    """Test user creation in database."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User"
    }
    
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    assert user.email == user_data["email"]
    assert user.username == user_data["username"]
```

### Frontend Test Examples

#### Component Test
```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { PostCard } from '@/components/PostCard'

describe('PostCard', () => {
  it('renders post content correctly', () => {
    const post = {
      id: '1',
      content: 'I am grateful for testing!',
      postType: 'daily_gratitude',
      author: { name: 'Test User' }
    }
    
    render(<PostCard post={post} />)
    
    expect(screen.getByText('I am grateful for testing!')).toBeInTheDocument()
    expect(screen.getByText('Test User')).toBeInTheDocument()
  })
  
  it('handles like button click', () => {
    const mockOnLike = jest.fn()
    const post = { id: '1', content: 'Test post' }
    
    render(<PostCard post={post} onLike={mockOnLike} />)
    
    fireEvent.click(screen.getByRole('button', { name: /like/i }))
    expect(mockOnLike).toHaveBeenCalledWith('1')
  })
})
```

#### API Route Test
```typescript
import { createMocks } from 'node-mocks-http'
import { GET } from '@/app/api/posts/route'

describe('/api/posts', () => {
  it('returns posts successfully', async () => {
    const { req, res } = createMocks({
      method: 'GET',
    })
    
    await GET(req, res)
    
    expect(res._getStatusCode()).toBe(200)
    const data = JSON.parse(res._getData())
    expect(Array.isArray(data)).toBe(true)
  })
})
```

## Test Configuration

### Backend Test Setup

**Dependencies**:
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `httpx` - HTTP client for testing
- `sqlalchemy` - Database testing

**Configuration** (`conftest.py`):
```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
async def async_client():
    """Async test client fixture."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def db_session():
    """Database session fixture."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        async with sessionmaker(engine)() as session:
            yield session
```

### Frontend Test Setup

**Dependencies**:
- `jest` - Test framework
- `@testing-library/react` - React testing utilities
- `@testing-library/jest-dom` - DOM testing utilities
- `msw` - API mocking

**Configuration** (`jest.config.js`):
```javascript
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/tests/setup.ts'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  testMatch: [
    '**/__tests__/**/*.test.(ts|tsx)',
    '**/*.test.(ts|tsx)'
  ]
}
```

## Running Tests

### Backend Tests
```bash
# Run all tests
cd apps/api
pytest

# Run specific test file
pytest tests/unit/test_posts.py

# Run with coverage
pytest --cov=app

# Run with verbose output
pytest -v
```

### Frontend Tests
```bash
# Run all tests
cd apps/web
npm test

# Run specific test file
npm test PostCard.test.tsx

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

## Test Data Management

### Backend Test Data
- Use factories for creating test data
- Clean up data after each test
- Use unique identifiers to avoid conflicts
- Mock external services

### Frontend Test Data
- Use mock data for components
- Mock API responses
- Use test utilities for common data
- Reset state between tests

## Best Practices

### General Guidelines
1. **Write tests first** (TDD approach)
2. **Keep tests simple and focused**
3. **Use descriptive test names**
4. **Test both success and error cases**
5. **Mock external dependencies**
6. **Use fixtures for common setup**

### Backend Specific
1. **Use async/await consistently**
2. **Test database operations**
3. **Verify API responses**
4. **Test authentication and authorization**
5. **Use test databases**

### Frontend Specific
1. **Test user interactions**
2. **Test component rendering**
3. **Test form validation**
4. **Test responsive design**
5. **Mock API calls**

## Common Patterns

### Backend Test Patterns
- **API Testing**: Use AsyncClient to test endpoints
- **Database Testing**: Use test database with fixtures
- **Authentication Testing**: Use JWT token fixtures
- **Error Testing**: Test various error scenarios

### Frontend Test Patterns
- **Component Testing**: Test rendering and interactions
- **Hook Testing**: Test custom hooks in isolation
- **API Testing**: Mock API responses
- **Form Testing**: Test form validation and submission

## Troubleshooting

### Common Issues
1. **Async/Await Issues**: Ensure proper async test setup
2. **Database Conflicts**: Use unique test data
3. **Mock Issues**: Verify mock setup and teardown
4. **Environment Issues**: Check test environment configuration

### Debugging Tips
1. **Use `pytest -s` for print statements**
2. **Use `console.log` in frontend tests**
3. **Check test database state**
4. **Verify mock configurations**

---

*Last updated: [Current Date]* 