# Pitfalls Research: AI Bias Detection & Fairness Platform

## Critical Pitfalls

### 1. Metric Mutual Exclusivity Trap
**What goes wrong:** Developers assume all fairness metrics can be satisfied simultaneously. They cannot — demographic parity and equalized odds are often mathematically contradictory (Chouldechova 2017, Kleinberg et al. 2016).

**Warning signs:**
- UI shows all metrics as "expected to pass"
- Documentation implies a model can be "fully fair"
- No guidance on metric selection for specific use cases

**Prevention:**
- Display clear warnings when contradictory metrics are selected
- Provide domain-specific metric recommendations (e.g., hiring → equalized odds; lending → predictive parity)
- Always include a "metric selection rationale" section in reports
- **Phase:** Bias Analysis module (Phase 1–2)

### 2. Protected Attribute Auto-Detection False Positives
**What goes wrong:** Column named "gender" is detected as protected, but it's actually a product category in an e-commerce dataset. Or worse, proxy variables (zip code → race) are missed entirely.

**Warning signs:**
- Auto-detection confidence scores are all high or all low
- No human confirmation step
- Proxy variables not surfaced

**Prevention:**
- ALWAYS require user confirmation of detected attributes
- Show confidence scores with rationale
- Document limitations: "Auto-detection identifies explicit attributes only. Proxy variables require manual identification."
- **Phase:** Ingestion module (Phase 1)

### 3. AIF360/Fairlearn API Breaking Changes
**What goes wrong:** Pinning to a specific version works until security patches are needed. Both libraries have had significant API changes between major versions.

**Warning signs:**
- Direct dependency on internal APIs
- No wrapper/abstraction layer
- Import statements scattered across codebase

**Prevention:**
- Create a `faircheck.algorithms` wrapper module that abstracts all AIF360/Fairlearn calls
- Pin versions in requirements.txt with acceptable ranges
- Test against both pinned and latest versions in CI
- **Phase:** Engine foundation (Phase 1)

### 4. WeasyPrint Installation Complexity
**What goes wrong:** WeasyPrint requires system-level dependencies (cairo, pango, gdk-pixbuf) that vary by OS. Mac users need Homebrew, Linux needs apt packages, Windows is painful.

**Warning signs:**
- `pip install weasyprint` fails on clean machine
- Different error messages per platform
- No fallback for report generation

**Prevention:**
- Document platform-specific prerequisites clearly
- Provide Docker image with all dependencies pre-installed
- Implement fallback: if WeasyPrint unavailable, generate Markdown-only report
- Consider adding `fpdf2` as lightweight PDF fallback (pure Python, no system deps)
- **Phase:** Report Builder (Phase 5)

### 5. SQLite Concurrent Write Contention
**What goes wrong:** TUI and Web both try to write to `sessions.db` simultaneously, causing "database is locked" errors.

**Warning signs:**
- Intermittent write failures during TUI→Web handoff
- Lost scan results
- Corrupted session data

**Prevention:**
- Use WAL (Write-Ahead Logging) mode for SQLite: `PRAGMA journal_mode=WAL`
- Implement retry logic with exponential backoff on write failures
- Consider having only FastAPI write to DB, with TUI/Web using REST API for writes
- **Phase:** Session Store (Phase 3)

### 6. Treating Fairness as Pure Software Problem
**What goes wrong:** The tool presents bias detection as a checkbox exercise. Users run scan → green checkmarks → assume model is "fair." This is both ethically dangerous and legally insufficient.

**Warning signs:**
- No contextual guidance on what metrics mean
- No warnings about limitations
- Report implies certification of fairness

**Prevention:**
- Include disclaimers: "This tool identifies statistical disparities. Fairness determination requires human judgment and domain expertise."
- Reports should say "Analysis" not "Certification"
- Human oversight log is mandatory for report generation, not optional
- Provide interpretive guidance per metric
- **Phase:** Report Builder + Web UI (Phases 5, 6)

### 7. Data Leakage in Mitigation
**What goes wrong:** Pre-processing mitigation (reweighing) is applied to entire dataset including test set, invalidating evaluation metrics. "Fixed" model appears fair only because test set was also manipulated.

**Warning signs:**
- Mitigation applied without train/test split distinction
- Before/after metrics use same data
- Suspiciously large improvement in fairness metrics post-mitigation

**Prevention:**
- Enforce train/test split before mitigation
- Apply mitigation only to training data
- Evaluate fairness metrics only on held-out test set
- Document this clearly in both UI and reports
- **Phase:** Mitigation Pipeline (Phase 7)

### 8. Intersectional Bias Blindspot
**What goes wrong:** Metrics show no bias for "gender" or "race" independently, but "Black women" or "elderly disabled" subgroups face significant disparities. Standard single-attribute analysis misses intersectional effects.

**Warning signs:**
- Only single protected attributes analyzed
- No subgroup analysis beyond top-level demographics
- "Fair" result across all single attributes

**Prevention:**
- Implement intersectional analysis as v1.1 feature (P1)
- For v1: document limitation clearly in report methodology section
- Use Fairlearn's `MetricFrame` which supports multiple sensitive features
- **Phase:** Bias Analysis enhancement (post-v1)

### 9. Regulation Template Accuracy Risk
**What goes wrong:** Report template claims compliance with specific EU AI Act articles but doesn't actually cover all requirements. A compliance officer signs off on an incomplete report. Legal liability follows.

**Warning signs:**
- Templates not reviewed by legal/regulatory experts
- Article references are superficial (just naming articles, not covering substance)
- No version tracking on templates

**Prevention:**
- Clearly label templates as "guidance" not "legal compliance"
- Version-control templates with changelog
- Include prominent disclaimer: "This report template is a starting point. Review by qualified legal counsel is required."
- Engage regulatory advisors for template review before public release
- **Phase:** Regulation Templates (Phase 9)

### 10. FastAPI Port Discovery Race Condition
**What goes wrong:** TUI starts FastAPI server, but web app tries to connect before server is ready. Or FastAPI writes port to file, but TUI reads stale port from previous session.

**Warning signs:**
- "Connection refused" on first web launch
- Port file contains wrong port
- Multiple FastAPI instances running

**Prevention:**
- Health check endpoint: `GET /api/health` — TUI polls until 200 before opening browser
- PID file: `~/.faircheck/server.pid` — check if process still alive before starting new one
- Lock file for port: atomic write with temp file rename
- **Phase:** Integration (Phase 10)

## Severity Summary

| Pitfall | Severity | Likelihood | Phase to Address |
|---------|----------|------------|-----------------|
| Metric mutual exclusivity | Critical | High | Phase 1–2 |
| Attribute false positives | Critical | High | Phase 1 |
| Library breaking changes | Medium | Medium | Phase 1 |
| WeasyPrint installation | High | High | Phase 5 |
| SQLite contention | Medium | Medium | Phase 3 |
| Fairness as checkbox | Critical | High | Phase 5–6 |
| Data leakage in mitigation | Critical | Medium | Phase 7 |
| Intersectional blindspot | High | High | Post-v1 |
| Template accuracy risk | Critical | Medium | Phase 9 |
| Port discovery race | Low | Medium | Phase 10 |

---
*Researched: 2026-04-10*
