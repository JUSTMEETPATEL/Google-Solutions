/** Zustand store for app state. */

import { create } from 'zustand';
import type { SessionSummary } from '../api/client';

interface AppState {
  selectedSessionId: string | null;
  regulation: string;
  sessions: SessionSummary[];

  setSelectedSession: (id: string | null) => void;
  setRegulation: (reg: string) => void;
  setSessions: (sessions: SessionSummary[]) => void;
}

export const useAppStore = create<AppState>((set) => ({
  selectedSessionId: null,
  regulation: 'eu_ai_act_high',
  sessions: [],

  setSelectedSession: (id) => set({ selectedSessionId: id }),
  setRegulation: (reg) => set({ regulation: reg }),
  setSessions: (sessions) => set({ sessions }),
}));
