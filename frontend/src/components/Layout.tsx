import type { PropsWithChildren } from 'react';

interface LayoutProps extends PropsWithChildren {
  title: string;
  description?: string;
}

export function Layout({ children, title, description }: LayoutProps) {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{ padding: '2rem', textAlign: 'center' }}>
        <h1 style={{ marginBottom: '0.5rem' }}>{title}</h1>
        {description && <p style={{ color: '#475569', marginTop: 0 }}>{description}</p>}
      </header>
      <main style={{ flex: 1 }}>{children}</main>
      <footer style={{ textAlign: 'center', padding: '2rem', color: '#94a3b8' }}>
        Environment aware frontend connected to FastAPI backend.
      </footer>
    </div>
  );
}
