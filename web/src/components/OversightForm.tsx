/** OversightForm — human oversight log form (WEB-07). */

import { useState } from 'react';
import { submitOversight } from '../api/client';
import { useAppStore } from '../store/appStore';
import { UserCheck, CheckCircle2, Send } from 'lucide-react';

interface OversightFormProps {
  sessionId: string;
}

export function OversightForm({ sessionId }: OversightFormProps) {
  const [reviewer, setReviewer] = useState('');
  const [decision, setDecision] = useState('approved');
  const [notes, setNotes] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  
  const { setOversightApproved } = useAppStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    const today = new Date().toISOString().slice(0, 10);
    try {
      await submitOversight(sessionId, {
        reviewer,
        date: today,
        decision,
        notes: notes || undefined,
      });
      setSubmitted(true);
      if (decision === 'approved' || decision === 'conditional') {
        setOversightApproved(true, reviewer, decision, today);
      }
    } catch {
      // silently ignore
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="bg-success-500/10 border border-success-500/20 rounded-xl p-6 text-center animate-in fade-in zoom-in duration-500">
        <div className="inline-flex items-center justify-center p-2 bg-success-500/20 rounded-full mb-3">
          <CheckCircle2 className="w-6 h-6 text-success-500" />
        </div>
        <p className="text-sm text-success-500 font-bold mb-2 uppercase tracking-widest">
          Decision Recorded
        </p>
        <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-dark-900/50 rounded flex-wrap justify-center text-dark-300 text-[10px] font-mono border border-white/5">
          <span className="text-white">{reviewer}</span>
          <span className="text-dark-500">|</span>
          <span className="uppercase">{decision}</span>
          <span className="text-dark-500">|</span>
          <span>{new Date().toISOString().slice(0, 10)}</span>
        </div>
      </div>
    );
  }

  const inputClass = "w-full bg-dark-950/50 border border-white/10 rounded-lg px-3 py-2 text-white text-[11px] font-mono focus:outline-none focus:border-primary-500/50 transition-all placeholder:text-dark-500";

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="text-[10px] font-bold text-dark-400 uppercase tracking-widest block mb-1.5">
          Reviewer Name <span className="text-danger-500">*</span>
        </label>
        <div className="relative">
          <input
            value={reviewer}
            onChange={(e) => setReviewer(e.target.value)}
            placeholder="Jane Smith"
            required
            className={inputClass}
          />
          <UserCheck className="absolute right-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-dark-500" />
        </div>
      </div>

      <div>
        <label className="text-[10px] font-bold text-dark-400 uppercase tracking-widest block mb-1.5">
          Decision
        </label>
        <div className="relative">
          <select
            value={decision}
            onChange={(e) => setDecision(e.target.value)}
            className={`${inputClass} appearance-none cursor-pointer pr-8`}
          >
            <option value="approved">✅ APPROVED</option>
            <option value="conditional">⚠️ CONDITIONAL</option>
            <option value="rejected">❌ REJECTED</option>
          </select>
        </div>
      </div>

      <div>
        <label className="text-[10px] font-bold text-dark-400 uppercase tracking-widest block mb-1.5">
          Notes (optional)
        </label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Observations..."
          rows={2}
          className={`${inputClass} resize-y`}
        />
      </div>

      <button
        type="submit"
        disabled={!reviewer || submitting}
        className={`w-full py-2.5 px-4 rounded-lg font-bold text-[10px] uppercase tracking-widest transition-all duration-300 flex items-center justify-center gap-2 mt-2 ${
          reviewer && !submitting
            ? 'bg-purple-600/20 text-purple-400 border border-purple-500/30 hover:bg-purple-500/30 hover:text-purple-300'
            : 'bg-dark-900 text-dark-600 cursor-not-allowed border border-white/5'
        }`}
      >
        {submitting ? (
          <>
            <div className="w-3.5 h-3.5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
            Submitting...
          </>
        ) : (
          <>
            <Send className="w-3.5 h-3.5" />
            Record Decision
          </>
        )}
      </button>
    </form>
  );
}
