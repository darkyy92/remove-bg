import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';

// Mock the utils module
vi.mock('./lib/utils', () => ({
  removeBackground: vi.fn().mockImplementation(() => {
    return Promise.resolve('data:image/png;base64,fakeimagedatastring');
  }),
  cn: vi.fn((...inputs) => inputs.join(' ')),
}));

describe('App Component', () => {
  it('renders without crashing', () => {
    render(<App />);
    expect(screen.getByText('Hintergrund Entfernen')).toBeInTheDocument();
  });

  it('displays upload instructions', () => {
    render(<App />);
    expect(screen.getByText(/Ziehen Sie ein Bild hierher oder klicken Sie zum Auswählen/i)).toBeInTheDocument();
  });

  it('shows the result placeholder initially', () => {
    render(<App />);
    expect(screen.getByText(/Ihr Ergebnis wird hier angezeigt/i)).toBeInTheDocument();
  });

  // This is a partial test as we can't fully test the dropzone in JSDOM
  it('displays offline warning when browser is offline', () => {
    // Mock the navigator.onLine property
    Object.defineProperty(navigator, 'onLine', {
      writable: true,
      value: false,
    });
    
    render(<App />);
    expect(screen.getByText('Offline')).toBeInTheDocument();
    
    // Reset the navigator.onLine property
    Object.defineProperty(navigator, 'onLine', {
      writable: true,
      value: true,
    });
  });
});