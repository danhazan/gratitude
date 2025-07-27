// Example test to verify Jest setup
describe('Example Test', () => {
  it('should pass a basic test', () => {
    expect(1 + 1).toBe(2)
  })

  it('should have access to DOM environment', () => {
    const element = document.createElement('div')
    element.textContent = 'Hello World'
    expect(element.textContent).toBe('Hello World')
  })
}) 