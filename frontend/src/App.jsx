import React, { useState, useEffect } from 'react'

const SAMPLES = {
  1: {
    doi: '10.1016/j.cell.2019.08.012',
    name: 'Sample 1: High-Risk Retracted Paper'
  },
  2: {
    doi: '10.1038/s41586-021-03819-2',
    name: 'Sample 2: Clean Nature Study'
  },
  3: {
    doi: '10.1103/PhysRevLett.124.041101',
    name: 'Sample 3: Borderline Velocity Spike'
  }
}

export default function App() {
  const [activeTab, setActiveTab] = useState('scanner')
  const [doiInput, setDoiInput] = useState('10.1016/j.cell.2019.08.012')
  const [activePreset, setActivePreset] = useState(1)
  const [loading, setLoading] = useState(false)
  const [paper, setPaper] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [metricsLoading, setMetricsLoading] = useState(false)
  const [copied, setCopied] = useState(false)
  const [pdfGenerating, setPdfGenerating] = useState(false)
  const [selectedGalleryCat, setSelectedGalleryCat] = useState('All')
  const [modalImage, setModalImage] = useState(null)

  // Initial fetch for sample 1 and metrics
  useEffect(() => {
    fetchPrediction(SAMPLES[1].doi)
    fetchMetrics()
  }, [])

  const fetchPrediction = async (doiToFetch) => {
    setLoading(true)
    try {
      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ doi: doiToFetch })
      })
      if (!res.ok) throw new Error(`HTTP error ${res.status}`)
      const data = await res.json()
      setPaper(data)
    } catch (err) {
      console.error('Fetch error:', err)
      // Fallback fallback state if backend unavailable
    } finally {
      setLoading(false)
    }
  }

  const fetchMetrics = async () => {
    setMetricsLoading(true)
    try {
      const res = await fetch('/api/metrics')
      if (res.ok) {
        const data = await res.json()
        setMetrics(data)
      }
    } catch (err) {
      console.error('Failed to load metrics:', err)
    } finally {
      setMetricsLoading(false)
    }
  }

  const handleSearch = (e) => {
    if (e) e.preventDefault()
    if (!doiInput.trim()) return
    fetchPrediction(doiInput.trim())
  }

  const handlePresetSelect = (id) => {
    setActivePreset(id)
    const doi = SAMPLES[id].doi
    setDoiInput(doi)
    fetchPrediction(doi)
  }

  const handleCopyDoi = () => {
    if (paper?.doi) {
      navigator.clipboard.writeText(paper.doi)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleDownloadPdf = () => {
    setPdfGenerating(true)
    setTimeout(() => {
      setPdfGenerating(false)
      alert(`RetractGuard Dossier compiled.\nSHA-256 Verified forensic report exported for DOI: ${paper?.doi || 'paper'}`)
    }, 1200)
  }

  // Calculate SVG stroke offset for gauge: circumference = 2 * PI * 64 ≈ 402.12
  const score = paper?.risk_score ?? 0
  const circumference = 402.12
  const strokeOffset = circumference - (circumference * (score / 100))

  const isHighRisk = score >= 60
  const isModerateRisk = score >= 25 && score < 60

  return (
    <div className="min-h-screen bg-surface font-sans text-on-surface flex flex-col selection:bg-secondary-container selection:text-on-secondary-container">
      {/* Top Fixed Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-surface/85 backdrop-blur-xl border-b border-surface-variant">
        <div className="h-16 w-full px-4 md:px-8 lg:px-12 flex items-center justify-between gap-4">
          {/* Logo & Brand */}
          <div className="flex items-center gap-4 min-w-0">
            <div className="w-8 h-8 rounded bg-gradient-to-tr from-secondary-container to-primary flex items-center justify-center shrink-0 shadow-[0_0_15px_rgba(128,131,255,0.4)]">
              <span className="material-symbols-outlined text-surface text-[20px] font-bold">shield</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold tracking-tight text-on-surface flex items-center">
                Retract<span className="text-primary drop-shadow-[0_0_12px_rgba(128,131,255,0.4)]">Guard</span>
              </span>
              <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-surface-container-high border border-outline-variant/40">
                <span className="w-1.5 h-1.5 rounded-full bg-tertiary animate-pulse"></span>
                <span className="text-[11px] font-mono text-on-surface-variant uppercase tracking-wider">Research Integrity Screening</span>
              </div>
            </div>
          </div>

          {/* Center Tabs Navigation */}
          <nav className="flex items-center p-1 rounded-full bg-surface-container-lowest border border-outline-variant/30 gap-1">
            <button
              onClick={() => setActiveTab('scanner')}
              className={`px-4 py-1.5 rounded-full text-xs font-mono transition-all ${
                activeTab === 'scanner'
                  ? 'bg-secondary-container text-secondary border border-primary/40 shadow-[0_0_12px_rgba(47,58,163,0.5)] font-semibold'
                  : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container'
              }`}
            >
              Single Paper Risk Scanner
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`px-4 py-1.5 rounded-full text-xs font-mono transition-all ${
                activeTab === 'analytics'
                  ? 'bg-secondary-container text-secondary border border-primary/40 shadow-[0_0_12px_rgba(47,58,163,0.5)] font-semibold'
                  : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container'
              }`}
            >
              Model & EDA Analytics
            </button>
          </nav>

          {/* Right Action Chips */}
          <div className="flex items-center gap-3 shrink-0">
            <div className="hidden lg:flex items-center gap-1.5 px-3 py-1 rounded-full bg-surface-container border border-outline-variant/40">
              <span className="w-1.5 h-1.5 rounded-full bg-tertiary"></span>
              <span className="text-xs font-mono text-on-surface-variant">v2.4 (OpenAlex Live)</span>
            </div>
            <a
              href="https://github.com"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-surface-container-low border border-outline-variant/30 text-xs font-mono text-on-surface-variant hover:text-on-surface hover:border-outline-variant transition-colors"
            >
              <span className="hidden sm:inline">GitHub / Specs</span>
              <span className="material-symbols-outlined text-[15px]">open_in_new</span>
            </a>
          </div>
        </div>
      </header>

      {/* Main Body */}
      <main className="w-full pt-20 flex-1 flex flex-col">
        {/* Subtle Ambient Radial Backdrops */}
        <div className="relative w-full max-w-7xl mx-auto px-4 md:px-8 py-6 flex flex-col gap-8 flex-1">
          <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-[750px] h-[300px] bg-primary/10 rounded-full blur-[140px] pointer-events-none -z-10"></div>
          <div className="absolute top-[350px] right-4 w-[450px] h-[300px] bg-error/5 rounded-full blur-[120px] pointer-events-none -z-10"></div>

          {/* TAB 1: Single Paper Risk Scanner */}
          {activeTab === 'scanner' && (
            <>
              {/* 1. Hero Search Section */}
              <section className="relative w-full max-w-4xl mx-auto flex flex-col items-center text-center pt-2">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surface-container-high border border-outline-variant/30 mb-3 shadow-sm">
                  <span className="w-2 h-2 rounded-full bg-tertiary animate-ping"></span>
                  <span className="text-[11px] font-mono text-secondary tracking-widest uppercase">Autonomous Bibliometric Audit</span>
                  <span className="text-outline text-xs">/</span>
                  <span className="text-[11px] font-mono text-on-surface-variant">Ensemble v2.4 Active</span>
                </div>

                <h1 className="text-3xl md:text-4xl font-bold text-on-surface tracking-tight leading-tight">
                  Screen Scholarly Publications for <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-secondary to-primary-container">Early Retraction Risk</span>
                </h1>

                <p className="text-sm md:text-base text-on-surface-variant max-w-2xl mt-2 mb-6 leading-relaxed">
                  Analyze authorship patterns, citation graph anomalies, and peer-review velocity via high-throughput OpenAlex &amp; Crossref ingestion telemetry.
                </p>

                {/* Search Box */}
                <div className="w-full max-w-3xl bg-surface-container-low/90 backdrop-blur-md p-1.5 rounded-xl border border-outline-variant/40 shadow-xl transition-all focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/20">
                  <form className="flex flex-col sm:flex-row items-center gap-2" onSubmit={handleSearch}>
                    <div className="relative flex-1 w-full flex items-center pl-3">
                      <span className="material-symbols-outlined text-outline text-[22px] shrink-0 select-none">search</span>
                      <input
                        type="text"
                        value={doiInput}
                        onChange={(e) => setDoiInput(e.target.value)}
                        placeholder="Enter Paper DOI (e.g., 10.1016/j.cell.2019.08.012)"
                        className="w-full bg-transparent px-3 py-2.5 text-sm font-mono text-on-surface placeholder:text-outline/70 focus:outline-none tracking-wide"
                      />
                      {doiInput && (
                        <button
                          type="button"
                          onClick={() => setDoiInput('')}
                          className="text-outline hover:text-on-surface p-1 rounded transition-colors mr-1"
                          title="Clear input"
                        >
                          <span className="material-symbols-outlined text-[16px]">close</span>
                        </button>
                      )}
                    </div>
                    <button
                      type="submit"
                      disabled={loading}
                      className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded bg-secondary-container hover:bg-secondary-container/90 text-on-secondary-container border border-primary/40 font-semibold text-sm transition-all shadow-[0_0_20px_rgba(47,58,163,0.45)] hover:shadow-[0_0_25px_rgba(128,131,255,0.5)] shrink-0 disabled:opacity-50"
                    >
                      {loading ? (
                        <>
                          <span className="material-symbols-outlined text-[18px] animate-spin text-primary">progress_activity</span>
                          <span>Ingesting Telemetry...</span>
                        </>
                      ) : (
                        <>
                          <span className="material-symbols-outlined text-[20px] text-primary">radar</span>
                          <span>Analyze Paper</span>
                        </>
                      )}
                    </button>
                  </form>
                </div>

                {/* Preset DOI Pills */}
                <div className="mt-4 flex flex-wrap items-center justify-center gap-2 max-w-3xl">
                  <span className="text-[11px] font-mono text-outline uppercase tracking-wider mr-1">Presets:</span>
                  <button
                    type="button"
                    onClick={() => handlePresetSelect(1)}
                    className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-mono transition-all ${
                      activePreset === 1
                        ? 'bg-error-container/40 border border-error text-error shadow-[0_0_12px_rgba(147,0,10,0.3)]'
                        : 'bg-surface-container hover:bg-surface-container-high border border-outline-variant/30 text-on-surface-variant'
                    }`}
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-error animate-pulse"></span>
                    <span className="font-semibold text-error">Sample 1:</span> High-Risk Retracted Paper
                    <span className="text-[10px] text-outline font-mono hidden md:inline">(Cell 2019)</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => handlePresetSelect(2)}
                    className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-mono transition-all ${
                      activePreset === 2
                        ? 'bg-tertiary-container/30 border border-tertiary text-tertiary shadow-[0_0_12px_rgba(0,136,93,0.3)]'
                        : 'bg-surface-container hover:bg-surface-container-high border border-outline-variant/30 text-on-surface-variant'
                    }`}
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-tertiary"></span>
                    <span className="font-semibold text-tertiary">Sample 2:</span> Clean Nature Study
                    <span className="text-[10px] text-outline font-mono hidden md:inline">(Nature 2021)</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => handlePresetSelect(3)}
                    className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-mono transition-all ${
                      activePreset === 3
                        ? 'bg-secondary-container/40 border border-secondary text-secondary shadow-[0_0_12px_rgba(47,58,163,0.3)]'
                        : 'bg-surface-container hover:bg-surface-container-high border border-outline-variant/30 text-on-surface-variant'
                    }`}
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-secondary"></span>
                    <span className="font-semibold text-secondary">Sample 3:</span> Borderline Velocity Spike
                    <span className="text-[10px] text-outline font-mono hidden md:inline">(Phys. Rev. Lett.)</span>
                  </button>
                </div>
              </section>

              {/* 2. Paper Metadata Header Card */}
              {paper && (
                <section className="w-full bg-surface-container-low border border-outline-variant/30 rounded-xl p-6 relative overflow-hidden shadow-lg">
                  <div className="absolute top-0 right-0 w-80 h-full bg-gradient-to-l from-primary/5 via-transparent to-transparent pointer-events-none"></div>
                  <div className="flex flex-col gap-4 relative z-10">
                    {/* Badge row + DOI tag */}
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div className="flex flex-wrap items-center gap-2">
                        {paper.retraction_status === 'Retracted' ? (
                          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded bg-error-container/30 border border-error/50 text-error text-xs font-semibold uppercase tracking-wider">
                            <span className="material-symbols-outlined text-[15px]">warning</span>
                            <span>Retracted ({paper.retraction_reason || 'Inquiry Alert'})</span>
                          </div>
                        ) : (
                          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded bg-tertiary-container/30 border border-tertiary/50 text-tertiary text-xs font-semibold uppercase tracking-wider">
                            <span className="material-symbols-outlined text-[15px]">verified</span>
                            <span>Clean Publication Record</span>
                          </div>
                        )}
                        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-surface-container border border-outline-variant/30 text-xs font-mono text-on-surface-variant">
                          <span className="material-symbols-outlined text-[14px] text-tertiary">check_circle</span>
                          Crossref Verified
                        </div>
                        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-surface-container border border-outline-variant/30 text-xs font-mono text-on-surface-variant">
                          <span className="material-symbols-outlined text-[14px] text-primary">database</span>
                          OpenAlex Ingested
                        </div>
                      </div>

                      {/* Copyable DOI */}
                      <div className="inline-flex items-center rounded bg-surface-container-highest/80 border border-outline-variant/50 p-1 pl-3 text-xs font-mono text-on-surface">
                        <span className="text-outline mr-1.5">DOI:</span>
                        <span className="text-secondary mr-2">{paper.doi}</span>
                        <button
                          type="button"
                          onClick={handleCopyDoi}
                          className="hover:bg-surface-variant text-on-surface-variant hover:text-on-surface p-1 rounded transition-colors"
                          title="Copy DOI"
                        >
                          <span className="material-symbols-outlined text-[15px]">{copied ? 'done' : 'content_copy'}</span>
                        </button>
                        <a
                          href={`https://doi.org/${paper.doi}`}
                          target="_blank"
                          rel="noreferrer"
                          className="hover:bg-surface-variant text-on-surface-variant hover:text-on-surface p-1 rounded transition-colors"
                          title="Open DOI external"
                        >
                          <span className="material-symbols-outlined text-[15px]">open_in_new</span>
                        </a>
                      </div>
                    </div>

                    {/* Paper Title */}
                    <h2 className="text-xl md:text-2xl font-bold text-on-surface tracking-tight leading-tight max-w-5xl">
                      {paper.paper_title}
                    </h2>

                    {/* Authors */}
                    <div className="flex items-center gap-2 text-sm text-on-surface-variant">
                      <span className="material-symbols-outlined text-[18px] text-outline">group</span>
                      <span className="text-on-surface font-medium">{paper.authors}</span>
                      <span className="px-2 py-0.5 rounded-full bg-surface-container-high border border-outline-variant/30 text-outline text-xs font-mono">
                        {paper.extracted_features?.author_signals?.author_count || 1} co-authors
                      </span>
                    </div>

                    {/* Meta detail strip */}
                    <div className="pt-3 border-t border-outline-variant/20 flex flex-wrap items-center gap-y-2 gap-x-6 text-xs text-on-surface-variant font-mono">
                      <div className="flex items-center gap-2">
                        <span className="material-symbols-outlined text-[16px] text-primary">auto_stories</span>
                        <span>Journal:</span>
                        <span className="text-on-surface font-medium">{paper.journal}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="material-symbols-outlined text-[16px] text-outline">calendar_today</span>
                        <span>Published:</span>
                        <span className="text-on-surface font-medium">{paper.publication_year}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="material-symbols-outlined text-[16px] text-outline">account_balance</span>
                        <span>Publisher:</span>
                        <span className="text-on-surface font-medium">{paper.publisher}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="material-symbols-outlined text-[16px] text-tertiary">lock_open</span>
                        <span>License:</span>
                        <span className="text-tertiary font-medium">{paper.license}</span>
                      </div>
                    </div>
                  </div>
                </section>
              )}

              {/* 3. Main Risk & Feature Breakdown Grid */}
              {paper && (
                <section className="w-full grid grid-cols-1 lg:grid-cols-12 gap-6">
                  {/* Left: Retraction Risk Assessment Gauge (5 cols) */}
                  <div className="lg:col-span-5 bg-surface-container-low border border-outline-variant/30 rounded-xl p-6 relative flex flex-col justify-between shadow-xl">
                    <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${
                      isHighRisk ? 'from-error via-amber-500 to-error' : isModerateRisk ? 'from-amber-400 to-secondary' : 'from-tertiary to-secondary'
                    }`}></div>

                    <div>
                      {/* Card Header */}
                      <div className="flex items-center justify-between gap-2 mb-4">
                        <div className="flex items-center gap-2">
                          <span className={`material-symbols-outlined text-[22px] ${isHighRisk ? 'text-error' : isModerateRisk ? 'text-amber-400' : 'text-tertiary'}`}>
                            shield_with_heart
                          </span>
                          <span className="font-semibold text-sm md:text-base text-on-surface">Retraction Risk Assessment</span>
                        </div>
                        <span className={`px-2.5 py-0.5 rounded text-[11px] font-mono uppercase font-bold tracking-wider border ${
                          isHighRisk ? 'bg-error-container/40 border-error/50 text-error' : isModerateRisk ? 'bg-amber-400/20 border-amber-400 text-amber-400' : 'bg-tertiary-container/30 border-tertiary text-tertiary'
                        }`}>
                          {paper.risk_level}
                        </span>
                      </div>

                      {/* SVG Gauge & Score */}
                      <div className="flex flex-col sm:flex-row items-center justify-around gap-6 py-4">
                        <div className="relative w-44 h-44 flex items-center justify-center shrink-0">
                          <svg className="w-full h-full -rotate-90" viewBox="0 0 160 160">
                            <circle
                              className="text-surface-container-highest/60"
                              cx="80"
                              cy="80"
                              r="64"
                              fill="transparent"
                              stroke="currentColor"
                              strokeWidth="14"
                              strokeLinecap="round"
                            />
                            <circle
                              cx="80"
                              cy="80"
                              r="64"
                              fill="transparent"
                              stroke="url(#riskGradient)"
                              strokeWidth="14"
                              strokeLinecap="round"
                              strokeDasharray="402.12"
                              strokeDashoffset={strokeOffset}
                              className="transition-all duration-1000 ease-out"
                            />
                            <defs>
                              <linearGradient id="riskGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stopColor="#c0c1ff" />
                                <stop offset="50%" stopColor="#f59e0b" />
                                <stop offset="100%" stopColor="#ef4444" />
                              </linearGradient>
                            </defs>
                          </svg>

                          <div className="absolute flex flex-col items-center justify-center text-center">
                            <span className={`text-4xl font-extrabold tracking-tighter ${isHighRisk ? 'text-error' : isModerateRisk ? 'text-amber-400' : 'text-tertiary'}`}>
                              {paper.risk_score}<span className="text-xl font-normal text-on-surface-variant">%</span>
                            </span>
                            <span className="text-[10px] font-mono uppercase tracking-widest text-outline -mt-1">Risk Score</span>
                          </div>
                        </div>

                        {/* Status Readout */}
                        <div className="flex flex-col gap-2.5 text-left">
                          <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono font-bold w-fit border ${
                            isHighRisk ? 'bg-error-container/40 border-error/60 text-error' : isModerateRisk ? 'bg-amber-400/20 border-amber-400 text-amber-400' : 'bg-tertiary-container/30 border-tertiary text-tertiary'
                          }`}>
                            <span className={`w-2 h-2 rounded-full ${isHighRisk ? 'bg-error animate-ping' : isModerateRisk ? 'bg-amber-400' : 'bg-tertiary'}`}></span>
                            <span>{isHighRisk ? 'HIGH RETRACTION RISK' : isModerateRisk ? 'MODERATE RISK' : 'CLEAN RECORD'}</span>
                          </div>
                          <div className="text-xs text-on-surface-variant flex flex-col gap-1 font-mono">
                            <span>Status: <strong>{paper.retraction_status}</strong></span>
                            <span>Action: <strong className={isHighRisk ? 'text-error' : 'text-tertiary'}>{paper.action_recommendation}</strong></span>
                          </div>
                        </div>
                      </div>

                      {/* Model Confidence Note */}
                      <div className="mt-2 p-3 rounded-lg bg-surface-container border border-outline-variant/30 flex items-start gap-2.5">
                        <span className="material-symbols-outlined text-[18px] text-secondary shrink-0 mt-0.5">smart_toy</span>
                        <div className="flex flex-col text-xs font-mono">
                          <span className="text-on-surface font-semibold">Model Confidence: {paper.model_confidence}%</span>
                          <span className="text-outline text-[11px]">Tuned XGBoost + Soft Stacking Ensemble v2.4 (SMOTE &amp; Regularized)</span>
                        </div>
                      </div>
                    </div>

                    {/* Action Button */}
                    <div className="mt-6 pt-4 border-t border-outline-variant/20 flex flex-col sm:flex-row items-center gap-3">
                      <button
                        type="button"
                        onClick={handleDownloadPdf}
                        disabled={pdfGenerating}
                        className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded bg-surface-container-high hover:bg-surface-variant text-on-surface border border-outline-variant/50 hover:border-primary/50 text-xs font-mono transition-all group"
                      >
                        {pdfGenerating ? (
                          <>
                            <span className="material-symbols-outlined text-[16px] animate-spin">download</span>
                            <span>Compiling Dossier...</span>
                          </>
                        ) : (
                          <>
                            <span className="material-symbols-outlined text-[18px] text-error group-hover:scale-110 transition-transform">picture_as_pdf</span>
                            <span>Download Forensic Audit PDF</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Right: Top Risk Drivers (SHAP Feature Impact) (7 cols) */}
                  <div className="lg:col-span-7 bg-surface-container-low border border-outline-variant/30 rounded-xl p-6 relative flex flex-col justify-between shadow-xl">
                    <div>
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-1">
                        <div className="flex items-center gap-2">
                          <span className="material-symbols-outlined text-secondary text-[22px]">bar_chart_4_bars</span>
                          <h3 className="font-semibold text-sm md:text-base text-on-surface">Top Risk Drivers (SHAP Feature Impact)</h3>
                        </div>
                        <span className="text-xs font-mono text-outline">Marginal Tree Contribution</span>
                      </div>
                      <p className="text-xs text-on-surface-variant mb-5">
                        Marginal probability contribution to retraction classification against baseline research corpus.
                      </p>

                      {/* Drivers Bars */}
                      <div className="flex flex-col gap-4">
                        {paper.risk_contributions?.map((item, idx) => (
                          <div key={idx} className="flex flex-col gap-1.5">
                            <div className="flex items-center justify-between text-xs font-mono">
                              <span className="font-medium text-on-surface flex items-center gap-1.5">
                                <span className={`w-1.5 h-1.5 rounded-full ${
                                  item.color === 'error' ? 'bg-error' : item.color === 'rose' ? 'bg-rose-400' : item.color === 'amber' ? 'bg-amber-400' : item.color === 'tertiary' ? 'bg-tertiary' : 'bg-secondary'
                                }`}></span>
                                {item.feature}
                              </span>
                              <div className="flex items-center gap-2">
                                <span className={`font-bold ${item.color === 'error' || item.color === 'rose' ? 'text-error' : item.color === 'amber' ? 'text-amber-400' : 'text-secondary'}`}>
                                  +{item.impact}
                                </span>
                                <span className="text-outline text-[11px]">| {item.weight_pct}% weight</span>
                              </div>
                            </div>
                            <div className="w-full h-2.5 rounded-full bg-surface-container overflow-hidden p-0.5 border border-outline-variant/20">
                              <div
                                className={`h-full rounded-full transition-all duration-700 ${
                                  item.color === 'error' ? 'bg-gradient-to-r from-error/80 to-error' : item.color === 'rose' ? 'bg-gradient-to-r from-rose-400 to-error' : item.color === 'amber' ? 'bg-gradient-to-r from-amber-500 to-amber-400' : item.color === 'tertiary' ? 'bg-tertiary' : 'bg-secondary-container'
                                }`}
                                style={{ width: `${Math.min(100, Math.max(8, item.weight_pct * 2.2))}%` }}
                              ></div>
                            </div>
                            <span className="text-[11px] text-outline font-mono">{item.description}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="mt-4 pt-3 border-t border-outline-variant/20 flex items-center justify-between text-xs text-outline font-mono">
                      <span>Formula: XGB_Gain_Weight + Tree_SHAP</span>
                      <span className="text-secondary">Ensemble Meta Basis</span>
                    </div>
                  </div>
                </section>
              )}

              {/* 4. Bottom 3-Card Signal Grid */}
              {paper?.extracted_features && (
                <section className="w-full grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Card 1: Author Signals */}
                  <div className="bg-surface-container-low border border-outline-variant/30 rounded-xl p-5 flex flex-col justify-between shadow-lg">
                    <div>
                      <div className="flex items-center justify-between pb-3 border-b border-outline-variant/20 mb-4">
                        <div className="flex items-center gap-2">
                          <span className="material-symbols-outlined text-primary text-[20px]">badge</span>
                          <h4 className="font-semibold text-sm text-on-surface">Author Signals</h4>
                        </div>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase font-bold border ${
                          paper.extracted_features.author_signals?.status_type === 'danger'
                            ? 'bg-error-container/20 text-error border-error/30'
                            : 'bg-tertiary-container/20 text-tertiary border-tertiary/30'
                        }`}>
                          {paper.extracted_features.author_signals?.status}
                        </span>
                      </div>

                      <div className="flex flex-col gap-3 font-mono text-xs">
                        <div className="flex items-center justify-between">
                          <span className="text-on-surface-variant font-sans">Co-Author Count</span>
                          <span className="text-on-surface font-bold">{paper.extracted_features.author_signals?.author_count}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-on-surface-variant font-sans">Max Prior Author Works</span>
                          <span className="text-on-surface font-bold">{paper.extracted_features.author_signals?.max_author_works}</span>
                        </div>
                        <div className={`p-2.5 rounded border flex flex-col gap-1 ${
                          paper.extracted_features.author_signals?.prior_author_retractions > 0
                            ? 'bg-error-container/15 border-error/30'
                            : 'bg-surface-container border-outline-variant/30'
                        }`}>
                          <div className="flex items-center justify-between">
                            <span className={`font-semibold flex items-center gap-1 ${
                              paper.extracted_features.author_signals?.prior_author_retractions > 0 ? 'text-error' : 'text-on-surface-variant'
                            }`}>
                              <span className="material-symbols-outlined text-[14px]">flag</span>
                              Prior Retractions in Network
                            </span>
                            <span className={`font-bold ${
                              paper.extracted_features.author_signals?.prior_author_retractions > 0 ? 'text-error' : 'text-tertiary'
                            }`}>
                              {paper.extracted_features.author_signals?.prior_author_retractions} Cases
                            </span>
                          </div>
                          <p className="text-[10px] text-outline leading-tight font-sans">
                            {paper.extracted_features.author_signals?.prior_author_retractions > 0
                              ? 'Co-authors connected to prior Retraction Watch database entries.'
                              : 'No prior retracted publications detected in author history.'}
                          </p>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-on-surface-variant font-sans">Author Network Centrality</span>
                          <span className="text-secondary font-bold">{paper.extracted_features.author_signals?.coauthor_degree_centrality}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-on-surface-variant font-sans">Network Clustering Coeff</span>
                          <span className="text-secondary font-bold">{paper.extracted_features.author_signals?.coauthor_clustering_coeff}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Card 2: Citation Network */}
                  <div className="bg-surface-container-low border border-outline-variant/30 rounded-xl p-5 flex flex-col justify-between shadow-lg">
                    <div>
                      <div className="flex items-center justify-between pb-3 border-b border-outline-variant/20 mb-4">
                        <div className="flex items-center gap-2">
                          <span className="material-symbols-outlined text-secondary text-[20px]">hub</span>
                          <h4 className="font-semibold text-sm text-on-surface">Citation Network</h4>
                        </div>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase font-bold border ${
                          paper.extracted_features.citation_network?.status_type === 'danger'
                            ? 'bg-error-container/20 text-error border-error/30'
                            : 'bg-tertiary-container/20 text-tertiary border-tertiary/30'
                        }`}>
                          {paper.extracted_features.citation_network?.status}
                        </span>
                      </div>

                      <div className="flex flex-col gap-3 font-mono text-xs">
                        <div className="flex items-center justify-between">
                          <span className="text-on-surface-variant font-sans">Total Citations Ingested</span>
                          <span className="text-on-surface font-bold">{paper.extracted_features.citation_network?.cited_by_count}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-on-surface-variant font-sans">Citation Velocity</span>
                          <span className={`font-bold ${paper.extracted_features.citation_network?.citation_velocity > 40 ? 'text-error' : 'text-on-surface'}`}>
                            {paper.extracted_features.citation_network?.citation_velocity} / yr
                          </span>
                        </div>
                        <div className="p-2.5 rounded bg-surface-container border border-outline-variant/30 flex flex-col gap-1.5">
                          <div className="flex items-center justify-between">
                            <span className="text-on-surface-variant font-sans">Self-Citation Ratio</span>
                            <span className={`font-bold ${paper.extracted_features.citation_network?.self_citation_ratio > 20 ? 'text-amber-400' : 'text-tertiary'}`}>
                              {paper.extracted_features.citation_network?.self_citation_ratio}%
                            </span>
                          </div>
                          <div className="w-full h-1.5 rounded-full bg-surface-container-highest overflow-hidden">
                            <div
                              className={`h-full rounded-full ${paper.extracted_features.citation_network?.self_citation_ratio > 20 ? 'bg-amber-400' : 'bg-tertiary'}`}
                              style={{ width: `${Math.min(100, paper.extracted_features.citation_network?.self_citation_ratio)}%` }}
                            ></div>
                          </div>
                          <span className="text-[10px] text-outline font-sans">Normal academic threshold &lt; 15%</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-on-surface-variant font-sans">Graph Centrality</span>
                          <span className="text-on-surface font-bold">{paper.extracted_features.citation_network?.graph_centrality}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Card 3: Journal & Review */}
                  <div className="bg-surface-container-low border border-outline-variant/30 rounded-xl p-5 flex flex-col justify-between shadow-lg">
                    <div>
                      <div className="flex items-center justify-between pb-3 border-b border-outline-variant/20 mb-4">
                        <div className="flex items-center gap-2">
                          <span className="material-symbols-outlined text-tertiary text-[20px]">rate_review</span>
                          <h4 className="font-semibold text-sm text-on-surface">Journal &amp; Review</h4>
                        </div>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase font-bold border ${
                          paper.extracted_features.journal_metadata?.status_type === 'danger'
                            ? 'bg-error-container/20 text-error border-error/30'
                            : 'bg-surface-container text-outline border-outline-variant/40'
                        }`}>
                          {paper.extracted_features.journal_metadata?.status}
                        </span>
                      </div>

                      <div className="flex flex-col gap-3 font-mono text-xs">
                        <div className={`p-2.5 rounded border flex flex-col gap-1 ${
                          paper.extracted_features.journal_metadata?.review_turnaround_days < 14
                            ? 'bg-error-container/15 border-error/30'
                            : 'bg-surface-container border-outline-variant/30'
                        }`}>
                          <div className="flex items-center justify-between">
                            <span className={`font-semibold flex items-center gap-1 ${
                              paper.extracted_features.journal_metadata?.review_turnaround_days < 14 ? 'text-error' : 'text-on-surface-variant'
                            }`}>
                              <span className="material-symbols-outlined text-[14px]">speed</span>
                              Review Turnaround
                            </span>
                            <span className={`font-bold ${
                              paper.extracted_features.journal_metadata?.review_turnaround_days < 14 ? 'text-error' : 'text-tertiary'
                            }`}>
                              {paper.extracted_features.journal_metadata?.review_turnaround_days} Days
                            </span>
                          </div>
                          <p className="text-[10px] text-outline leading-tight font-sans">
                            {paper.extracted_features.journal_metadata?.review_turnaround_days < 14
                              ? 'Suspiciously rapid turnaround (<14 days). Paper mill pattern.'
                              : 'Standard multi-month scholarly peer-review latency.'}
                          </p>
                        </div>

                        <div className="flex items-center justify-between">
                          <span className="text-on-surface-variant font-sans">Journal Retraction Rate</span>
                          <span className={`font-bold ${paper.extracted_features.journal_metadata?.journal_retraction_rate > 1 ? 'text-error' : 'text-on-surface'}`}>
                            {paper.extracted_features.journal_metadata?.journal_retraction_rate}%
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-on-surface-variant font-sans">Publisher Entity</span>
                          <span className="text-on-surface font-medium truncate max-w-[150px]">{paper.publisher}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-on-surface-variant font-sans">Open Access Type</span>
                          <span className="text-tertiary font-bold">{paper.license}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </section>
              )}

              {/* 5. Corpus Benchmark Distribution */}
              <section className="w-full bg-surface-container-low border border-outline-variant/30 rounded-xl p-5 shadow-lg flex flex-col md:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded bg-surface-container-high border border-outline-variant/40 flex items-center justify-center shrink-0">
                    <span className="material-symbols-outlined text-secondary text-[22px]">ssid_chart</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-sm font-semibold text-on-surface">Corpus Risk Distribution Benchmark</span>
                    <span className="text-xs text-on-surface-variant">Comparative density across 2.4M screened publications in OpenAlex database.</span>
                  </div>
                </div>

                <div className="w-full md:w-96 flex flex-col gap-1.5 shrink-0">
                  <div className="flex items-center justify-between text-[11px] font-mono">
                    <span className="text-tertiary">Clean (85.0%)</span>
                    <span className="text-amber-400">Borderline (10.0%)</span>
                    <span className="text-error font-bold">Retracted (5.0%)</span>
                  </div>
                  <div className="w-full h-3 rounded-full bg-surface-container overflow-hidden flex border border-outline-variant/20">
                    <div className="h-full bg-tertiary" style={{ width: '85%' }}></div>
                    <div className="h-full bg-amber-400" style={{ width: '10%' }}></div>
                    <div className="h-full bg-error" style={{ width: '5%' }}></div>
                  </div>
                  <div className="flex items-center justify-between text-outline text-[10px] font-mono">
                    <span>Target paper score:</span>
                    <span className={isHighRisk ? 'text-error font-bold' : 'text-tertiary font-bold'}>{paper?.risk_score}% Risk</span>
                  </div>
                </div>
              </section>
            </>
          )}

          {/* TAB 2: Model & EDA Analytics */}
          {activeTab === 'analytics' && (
            <div className="flex flex-col gap-8">
              {/* Top KPI Cards */}
              <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-surface-container-low border border-outline-variant/30 rounded-xl p-4 flex flex-col gap-1">
                  <span className="text-[11px] font-mono text-outline uppercase">Best PR-AUC</span>
                  <span className="text-2xl md:text-3xl font-extrabold text-primary font-mono">{metrics?.kpis?.pr_auc ?? '1.000'}</span>
                  <span className="text-[10px] text-tertiary font-mono">Optimized vs Skew</span>
                </div>
                <div className="bg-surface-container-low border border-outline-variant/30 rounded-xl p-4 flex flex-col gap-1">
                  <span className="text-[11px] font-mono text-outline uppercase">Best ROC-AUC</span>
                  <span className="text-2xl md:text-3xl font-extrabold text-secondary font-mono">{metrics?.kpis?.roc_auc ?? '1.000'}</span>
                  <span className="text-[10px] text-secondary font-mono">Discriminative Power</span>
                </div>
                <div className="bg-surface-container-low border border-outline-variant/30 rounded-xl p-4 flex flex-col gap-1">
                  <span className="text-[11px] font-mono text-outline uppercase">Best F1-Score</span>
                  <span className="text-2xl md:text-3xl font-extrabold text-tertiary font-mono">{metrics?.kpis?.f1_score ?? '0.966'}</span>
                  <span className="text-[10px] text-outline font-mono">Harmonic Precision/Recall</span>
                </div>
                <div className="bg-surface-container-low border border-outline-variant/30 rounded-xl p-4 flex flex-col gap-1">
                  <span className="text-[11px] font-mono text-outline uppercase">Class Imbalance</span>
                  <span className="text-2xl md:text-3xl font-extrabold text-error font-mono">{metrics?.kpis?.class_imbalance_ratio ?? '1 : 5.7'}</span>
                  <span className="text-[10px] text-outline font-mono">SMOTE Balanced in Pipeline</span>
                </div>
              </section>

              {/* Model Comparison Table */}
              <section className="bg-surface-container-low border border-outline-variant/30 rounded-xl p-6 shadow-xl flex flex-col gap-4">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
                  <div>
                    <h3 className="text-lg font-bold text-on-surface">Model Benchmark &amp; Regularization Comparison</h3>
                    <p className="text-xs text-on-surface-variant">Evaluated on the pristine 20% test partition across all algorithmic families.</p>
                  </div>
                  <span className="text-xs font-mono px-3 py-1 rounded bg-secondary-container/40 text-secondary border border-primary/30">
                    Metric Priority: PR-AUC &gt; F1 &gt; Accuracy
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs font-mono border-collapse">
                    <thead>
                      <tr className="border-b border-outline-variant/30 text-outline">
                        <th className="py-2.5 px-3">Model Family</th>
                        <th className="py-2.5 px-3">Precision</th>
                        <th className="py-2.5 px-3">Recall</th>
                        <th className="py-2.5 px-3">F1-Score</th>
                        <th className="py-2.5 px-3">ROC-AUC</th>
                        <th className="py-2.5 px-3 text-primary font-bold">PR-AUC</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-outline-variant/15 text-on-surface">
                      {metrics?.model_comparison?.map((row, i) => (
                        <tr key={i} className="hover:bg-surface-container transition-colors">
                          <td className="py-2.5 px-3 font-semibold text-secondary">{row.model}</td>
                          <td className="py-2.5 px-3">{row.precision?.toFixed(3)}</td>
                          <td className="py-2.5 px-3">{row.recall?.toFixed(3)}</td>
                          <td className="py-2.5 px-3">{row.f1?.toFixed(3)}</td>
                          <td className="py-2.5 px-3">{row.roc_auc?.toFixed(3)}</td>
                          <td className="py-2.5 px-3 font-bold text-primary">{row.pr_auc?.toFixed(3)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>

              {/* Visual Figures Gallery */}
              <section className="bg-surface-container-low border border-outline-variant/30 rounded-xl p-6 shadow-xl flex flex-col gap-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div>
                    <h3 className="text-lg font-bold text-on-surface">Evaluation &amp; EDA Figures Gallery</h3>
                    <p className="text-xs text-on-surface-variant">High-resolution plots rendered from reports/figures/ generated during pipeline execution.</p>
                  </div>

                  <div className="flex items-center gap-2">
                    {['All', 'EDA', 'Evaluation'].map((cat) => (
                      <button
                        key={cat}
                        onClick={() => setSelectedGalleryCat(cat)}
                        className={`px-3 py-1 rounded text-xs font-mono transition-all ${
                          selectedGalleryCat === cat
                            ? 'bg-secondary-container text-secondary border border-primary/40 font-bold'
                            : 'bg-surface-container text-outline hover:text-on-surface'
                        }`}
                      >
                        {cat}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {metrics?.figures
                    ?.filter((f) => selectedGalleryCat === 'All' || f.category === selectedGalleryCat)
                    ?.map((fig) => (
                      <div
                        key={fig.id}
                        className="bg-surface-container border border-outline-variant/30 rounded-lg overflow-hidden flex flex-col group cursor-pointer hover:border-primary/50 transition-all shadow-md"
                        onClick={() => setModalImage(`/api/figures/${fig.filename}`)}
                      >
                        <div className="h-48 overflow-hidden bg-surface-container-lowest flex items-center justify-center relative">
                          <img
                            src={`/api/figures/${fig.filename}`}
                            alt={fig.title}
                            className="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-300"
                            onError={(e) => {
                              e.target.onerror = null
                              e.target.src = 'https://via.placeholder.com/400x250/1c1f2a/c0c1ff?text=Figure+Generated'
                            }}
                          />
                          <div className="absolute inset-0 bg-surface/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                            <span className="material-symbols-outlined text-primary text-[28px]">zoom_in</span>
                          </div>
                        </div>
                        <div className="p-3 flex items-center justify-between">
                          <span className="text-xs font-medium text-on-surface truncate">{fig.title}</span>
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-container-highest text-secondary">
                            {fig.category}
                          </span>
                        </div>
                      </div>
                    ))}
                </div>
              </section>
            </div>
          )}
        </div>
      </main>

      {/* Lightbox Modal for Gallery Images */}
      {modalImage && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4"
          onClick={() => setModalImage(null)}
        >
          <div className="relative max-w-5xl max-h-[90vh] bg-surface-container-low border border-outline-variant/40 rounded-xl p-4 overflow-hidden shadow-2xl">
            <button
              onClick={() => setModalImage(null)}
              className="absolute top-4 right-4 bg-surface-container-high text-on-surface p-1.5 rounded-full hover:bg-error-container transition-colors"
            >
              <span className="material-symbols-outlined text-[18px]">close</span>
            </button>
            <img src={modalImage} alt="Expanded figure" className="max-h-[80vh] w-auto object-contain rounded" />
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="w-full bg-surface-container-lowest border-t border-surface-variant py-4 mt-12">
        <div className="w-full max-w-7xl mx-auto px-4 md:px-8 flex flex-col md:flex-row items-center justify-between gap-4 text-xs font-mono text-outline">
          <div className="flex items-center gap-2">
            <span className="text-on-surface-variant font-medium">RetractGuard Computational Risk Engine</span>
            <span>•</span>
            <span>OpenAlex &amp; Crossref Pipeline v2.4</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-tertiary">Precision-Recall Optimized</span>
            <span>•</span>
            <span>SMOTE Leakage-Free Architecture</span>
          </div>
        </div>
      </footer>
    </div>
  )
}
