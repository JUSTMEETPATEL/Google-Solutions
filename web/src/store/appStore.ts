/** Zustand store for app state. */

import { create } from 'zustand';
import type { SessionSummary, ScanResult } from '../api/client';

interface AppState {
  selectedSessionId: string | null;
  currentScanResult: ScanResult | null;
  regulation: string;
  sessions: SessionSummary[];
  oversightApproved: boolean;
  oversightReviewer: string | null;
  oversightDecision: string | null;
  oversightDate: string | null;

  setSelectedSession: (id: string | null) => void;
  setCurrentScanResult: (result: ScanResult | null) => void;
  setRegulation: (reg: string) => void;
  setSessions: (sessions: SessionSummary[]) => void;
  setOversightApproved: (val: boolean, reviewer?: string, decision?: string, date?: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
  selectedSessionId: null,
  currentScanResult: null,
  regulation: 'standard', // default standard
  sessions: [],
  oversightApproved: false,
  oversightReviewer: null,
  oversightDecision: null,
  oversightDate: null,

  setSelectedSession: (id) => set({ selectedSessionId: id, oversightApproved: false, oversightReviewer: null, oversightDecision: null, oversightDate: null }),
  setCurrentScanResult: (result) => set({ currentScanResult: result, oversightApproved: false, oversightReviewer: null, oversightDecision: null, oversightDate: null }),
  setRegulation: (reg) => set({ regulation: reg }),
  setSessions: (sessions) => set({ sessions }),
  setOversightApproved: (val, reviewer, decision, date) => set({ oversightApproved: val, oversightReviewer: reviewer || null, oversightDecision: decision || null, oversightDate: date || null }),
}));
