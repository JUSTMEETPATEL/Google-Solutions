/** OversightForm — human oversight log form (WEB-07). */

import { useState } from 'react';
import { submitOversight } from '../api/client';
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await submitOversight(sessionId, {
        reviewer,
        date: new Date().toISOString().slice(0, 10),
        decision,
        notes: notes || undefined,
      });
      setSubmitted(true);
    } catch {
      // silently ignore
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-8 text-center animate-in fade-in zoom-in duration-500">
        <div className="inline-flex items-center justify-center p-3 bg-emerald-500/20 rounded-full mb-4">
          <CheckCircle2 className="w-10 h-10 text-emerald-400" />
        </div>
        <p className="text-lg text-emerald-400 font-bold mb-2">
          Oversight decision recorded
        </p>
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-dark-900/50 rounded-lg text-dark-300 text-sm mt-2 border border-white/5">
          <span className="font-semibold text-white">{reviewer}</span>
          <span className="text-dark-500">•</span>
          <span className="uppercase text-xs font-bold tracking-wider">{decision}</span>
          <span className="text-dark-500">•</span>
          <span>{new Date().toISOString().slice(0, 10)}</span>
        </div>
      </div>
    );
  }

  const inputClass = "w-full bg-dark-900/50 border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all placeholder:text-dark-500 shadow-inner";

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <label className="text-xs font-bold text-dark-400 uppercase tracking-wider block mb-2">
          Reviewer Name <span className="text-red-400">*</span>
        </label>
        <div className="relative">
          <input
            value={reviewer}
            onChange={(e) => setReviewer(e.target.value)}
            placeholder="Dr. Jane Smith"
            required
            className={inputClass}
          />
          <UserCheck className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
        </div>
      </div>

      <div>
        <label className="text-xs font-bold text-dark-400 uppercase tracking-wider block mb-2">
          Decision
        </label>
        <div className="relative">
          <select
            value={decision}
            onChange={(e) => setDecision(e.target.value)}
            className={`${inputClass} appearance-none cursor-pointer pr-10`}
          >
            <option value="approved">✅ Approved — Fair for deployment</option>
            <option value="conditional">⚠️ Conditional — Requires mitigation</option>
            <option value="rejected">❌ Rejected — Unacceptable bias</option>
          </select>
        </div>
      </div>

      <div>
        <label className="text-xs font-bold text-dark-400 uppercase tracking-wider block mb-2">
          Notes (optional)
        </label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Additional observations..."
          rows={3}
          className={`${inputClass} resize-y`}
        />
      </div>

      <button
        type="submit"
        disabled={!reviewer || submitting}
        className={`w-full py-3 px-4 rounded-xl font-bold text-sm transition-all duration-300 flex items-center justify-center gap-2 ${
          reviewer && !submitting
            ? 'bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-500 hover:to-purple-400 text-white shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40 hover:-translate-y-0.5'
            : 'bg-dark-800 text-dark-500 cursor-not-allowed border border-white/5'
        }`}
      >
        {submitting ? (
          <>
            <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
            Submitting...
          </>
        ) : (
          <>
            <Send className="w-4 h-4" />
            Record Decision
          </>
        )}
      </button>
    </form>
  );
}
