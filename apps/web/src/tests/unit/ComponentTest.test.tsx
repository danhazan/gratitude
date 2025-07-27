import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'

// Simple test component
const TestComponent = ({ message }: { message: string }) => {
  return <div data-testid="test-component">{message}</div>
}

describe('React Component Test', () => {
  it('should render a React component correctly', () => {
    render(<TestComponent message="Hello Test" />)
    
    const element = screen.getByTestId('test-component')
    expect(element).toBeInTheDocument()
    expect(element).toHaveTextContent('Hello Test')
  })

  it('should handle component props', () => {
    render(<TestComponent message="Different Message" />)
    
    const element = screen.getByTestId('test-component')
    expect(element).toHaveTextContent('Different Message')
  })
}) 