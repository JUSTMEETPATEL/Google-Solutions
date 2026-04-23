/** Zustand store for app state. */

import { create } from 'zustand';
import type { SessionSummary, ScanResult } from '../api/client';

interface AppState {
  selectedSessionId: string | null;
  currentScanResult: ScanResult | null;
  regulation: string;
  sessions: SessionSummary[];

  setSelectedSession: (id: string | null) => void;
  setCurrentScanResult: (result: ScanResult | null) => void;
  setRegulation: (reg: string) => void;
  setSessions: (sessions: SessionSummary[]) => void;
}

export const useAppStore = create<AppState>((set) => ({
  selectedSessionId: null,
  currentScanResult: null,
  regulation: 'eu_ai_act_high',
  sessions: [],

  setSelectedSession: (id) => set({ selectedSessionId: id }),
  setCurrentScanResult: (result) => set({ currentScanResult: result }),
  setRegulation: (reg) => set({ regulation: reg }),
  setSessions: (sessions) => set({ sessions }),
}));
