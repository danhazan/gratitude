import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'

// Simple test component that could represent a UI element in our app
const TestComponent = ({ message, className }: { message: string; className?: string }) => {
  return (
    <div data-testid="test-component" className={className}>
      {message}
    </div>
  )
}

describe('Component Testing', () => {
  it('should render a React component correctly', () => {
    render(<TestComponent message="Hello Test" />)
    
    const element = screen.getByTestId('test-component')
    expect(element).toBeInTheDocument()
    expect(element).toHaveTextContent('Hello Test')
  })

  it('should handle component props correctly', () => {
    render(<TestComponent message="Different Message" className="test-class" />)
    
    const element = screen.getByTestId('test-component')
    expect(element).toHaveTextContent('Different Message')
    expect(element).toHaveClass('test-class')
  })

  it('should handle optional props', () => {
    render(<TestComponent message="No class" />)
    
    const element = screen.getByTestId('test-component')
    expect(element).toBeInTheDocument()
    expect(element).not.toHaveClass('test-class')
  })
}) 