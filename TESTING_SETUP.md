# Installation Instructions for Testing Setup

## Required Dependencies

To install all testing dependencies, run:

```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event jest jest-environment-jsdom @babel/preset-env @babel/preset-react babel-jest
```

## Individual Package Installation

If you prefer to install packages individually:

```bash
# Core testing libraries
npm install --save-dev jest
npm install --save-dev jest-environment-jsdom

# React Testing Library
npm install --save-dev @testing-library/react
npm install --save-dev @testing-library/jest-dom
npm install --save-dev @testing-library/user-event

# Babel for JSX transformation
npm install --save-dev @babel/preset-env
npm install --save-dev @babel/preset-react
npm install --save-dev babel-jest
```

## Optional Testing Dependencies

```bash
# For testing coverage visualization
npm install --save-dev @testing-library/jest-dom

# For mocking modules
npm install --save-dev jest-mock

# For snapshot testing
npm install --save-dev jest-serializer-html
```

## Verification

After installation, you can verify the setup by running:

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run unit tests only
npm run test:unit

# Run integration tests only
npm run test:integration

# Run tests with coverage
npm run test:coverage
```

## Alternative: Using Vitest (Recommended for Vite projects)

If you prefer to use Vitest (which is more compatible with Vite), you can install:

```bash
npm install --save-dev vitest @vitest/ui jsdom
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

Then update your `package.json` scripts to use `vitest` instead of `jest`.

## Troubleshooting

- If you encounter module resolution issues, make sure all path aliases in `jest.config.json` match your `vite.config.ts`
- For CSS import errors, ensure the CSS mocking in `setupTests.js` is working correctly
- If tests fail to run, check that all required peer dependencies are installed
