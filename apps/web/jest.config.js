module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/src'],
  testMatch: [
    '**/__tests__/**/*.(ts|tsx)', 
    '**/?(*.)+(spec|test).(ts|tsx)'
  ],
  transform: {
    '^.+\\.(ts|tsx)$': ['ts-jest', {
      tsconfig: {
        jsx: 'react-jsx'
      }
    }]
  },
  collectCoverageFrom: [
    'src/**/*.(ts|tsx)',
    '!src/**/*.d.ts',
  ],
  setupFilesAfterEnv: ['<rootDir>/src/tests/setup.ts'],
  transformIgnorePatterns: [
    'node_modules/(?!(.*\\.mjs$))'
  ],
  testEnvironmentOptions: {
    customExportConditions: ['node', 'node-addons'],
  },
} 