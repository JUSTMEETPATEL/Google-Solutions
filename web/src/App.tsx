/** FairCheck Web — main App component. */

import { useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './components/Dashboard';
import { useAppStore } from './store/appStore';
import { fetchSessions } from './api/client';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 30_000 } },
});

function AppContent() {
  const { setSessions } = useAppStore();

  useEffect(() => {
    // Load sessions on mount (WEB-01)
    fetchSessions()
      .then(setSessions)
      .catch(() => setSessions([]));
  }, [setSessions]);

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#0f172a' }}>
      <Sidebar />
      <Dashboard />
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}
