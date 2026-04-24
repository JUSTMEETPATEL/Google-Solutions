/** FairCheck Web — main App component. */

import { useEffect, useCallback } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './components/Dashboard';
import { ToastContainer } from './components/Toast';
import { useAppStore } from './store/appStore';
import { fetchSessions } from './api/client';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 30_000 } },
});

function AppContent() {
  const { setSessions, currentScanResult } = useAppStore();

  const refreshSessions = useCallback(() => {
    fetchSessions()
      .then(setSessions)
      .catch(() => setSessions([]));
  }, [setSessions]);

  // Load sessions on mount
  useEffect(() => {
    refreshSessions();
  }, [refreshSessions]);

  // Auto-refresh sidebar after a new scan completes
  useEffect(() => {
    if (currentScanResult?.session_id) {
      refreshSessions();
    }
  }, [currentScanResult, refreshSessions]);

  return (
    <div className="flex min-h-screen w-full bg-transparent">
      <Sidebar />
      <Dashboard />
      <ToastContainer />
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
