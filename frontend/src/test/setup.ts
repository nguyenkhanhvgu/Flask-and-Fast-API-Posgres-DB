import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock window.open
Object.defineProperty(window, 'open', {
  writable: true,
  value: vi.fn(),
});

// Make vi available globally for Jest-style mocking
global.jest = vi;