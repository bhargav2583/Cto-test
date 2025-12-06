import { useCallback, useEffect, useState } from 'react';
import { Layout } from './components/Layout';
import { apiClient } from './lib/apiClient';

type HealthResponse = {
  status: string;
  environment: string;
  app: string;
};

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchHealth = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await apiClient.get<HealthResponse>('/health');
      setHealth(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to reach the API');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
  }, [fetchHealth]);

  return (
    <Layout title="FastAPI + React Starter" description="Connected to your FastAPI backend">
      <div className="card">
        <p className="status">{health?.status ?? 'unknown'}</p>
        <p>Environment: {health?.environment ?? 'n/a'}</p>
        <small>Service: {health?.app ?? 'Backend offline'}</small>

        {error && (
          <p role="alert" style={{ color: '#dc2626', marginTop: '1rem' }}>
            {error}
          </p>
        )}

        <button onClick={fetchHealth} disabled={isLoading} style={{ marginTop: '1.5rem' }}>
          {isLoading ? 'Checking…' : 'Re-run health check'}
        </button>
      </div>
    </Layout>
  );
}
