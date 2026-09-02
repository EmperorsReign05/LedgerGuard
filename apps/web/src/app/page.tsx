"use client";

import { useEffect, useState } from "react";

export default function Dashboard() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [metrics, setMetrics] = useState({ total: 0, resolved: 0, exceptions: 0, unresolved: 0 });

  const fetchResults = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8001/api/results");
      const data = await res.json();
      setResults(data);
      
      setMetrics({
        total: data.length,
        resolved: data.filter((d: any) => d.status === "RESOLVED").length,
        exceptions: data.filter((d: any) => d.status === "EXCEPTION").length,
        unresolved: data.filter((d: any) => d.status === "UNRESOLVED").length,
      });
    } catch (err) {
      console.error("Error fetching results", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResults();
  }, []);

  const runMatching = async () => {
    setRunning(true);
    try {
      await fetch("http://127.0.0.1:8001/api/run-matching", { method: "POST" });
      await fetchResults();
    } catch (err) {
      console.error("Error running matching", err);
    } finally {
      setRunning(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch(status) {
      case "RESOLVED": return <span className="badge badge-success">Resolved</span>;
      case "EXCEPTION": return <span className="badge badge-error">Exception</span>;
      case "UNRESOLVED": return <span className="badge badge-warning">Unresolved</span>;
      default: return <span className="badge badge-default">{status}</span>;
    }
  };

  return (
    <div className="layout-wrapper">
      {/* Dark Forest Green Header Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">Finance Controller.</h1>
          <p className="hero-subtitle">
            Evidence-based autonomous reconciliation. We use deterministic logic where possible, and AI only where ambiguity requires reasoning.
          </p>
          
          <div className="metrics-grid">
            <div className="metric-item">
              <h3>Total Processed</h3>
              <p>{metrics.total}</p>
            </div>
            <div className="metric-item">
              <h3>Auto Resolved</h3>
              <p>{metrics.resolved}</p>
            </div>
            <div className="metric-item">
              <h3>Exceptions</h3>
              <p>{metrics.exceptions}</p>
            </div>
            <div className="metric-item">
              <h3>Unresolved</h3>
              <p>{metrics.unresolved}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Cream Body Section */}
      <main className="main-content">
        <div className="content-container">
          
          <div className="section-header">
            <h2 className="section-title">Reconciliation Queue</h2>
            <button className="btn-primary" onClick={runMatching} disabled={running}>
              {running ? (
                <>
                  <svg className="animate-spin" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" strokeOpacity="0.25" />
                    <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="4" strokeLinecap="round" />
                  </svg>
                  Processing Batch...
                </>
              ) : (
                "Run AI Investigator"
              )}
            </button>
          </div>

          <div className="data-card">
            <table>
              <thead>
                <tr>
                  <th>Match ID</th>
                  <th>Status</th>
                  <th>Payment (Source)</th>
                  <th>Settlement (Candidate)</th>
                  <th>Investigation Evidence</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan={5} className="loading-state">Loading queue...</td></tr>
                ) : results.length === 0 ? (
                  <tr><td colSpan={5} className="loading-state" style={{fontSize: '1rem'}}>No records found. Seed DB and run pipeline.</td></tr>
                ) : (
                  results.map((r: any) => (
                    <tr key={r.id}>
                      <td>
                        <span style={{color: "var(--text-muted-dark)", fontSize: "0.875rem"}}>#{r.id}</span>
                      </td>
                      <td>{getStatusBadge(r.status)}</td>
                      <td>
                        {r.payment ? (
                          <div>
                            <div className="value-display">{r.payment.amount} <span style={{fontSize: "0.875rem", fontWeight: 400}}>{r.payment.currency}</span></div>
                            <div className="code-block">{r.payment.id}</div>
                          </div>
                        ) : <span style={{color: "var(--text-muted-dark)"}}>None</span>}
                      </td>
                      <td>
                        {r.settlement ? (
                          <div>
                            <div className="value-display">{r.settlement.amount} <span style={{fontSize: "0.875rem", fontWeight: 400}}>INR</span></div>
                            <div className="code-block">{r.settlement.id}</div>
                            {r.settlement.utr && <div style={{marginTop: "0.5rem", color: "var(--text-muted-dark)", fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em"}}>UTR: {r.settlement.utr}</div>}
                          </div>
                        ) : <span style={{color: "var(--text-muted-dark)"}}>None</span>}
                      </td>
                      <td>
                        <div style={{fontWeight: 600, color: "var(--text-dark)", textTransform: "capitalize"}}>{r.match_type.toLowerCase().replace("_", " ")}</div>
                        <div style={{color: "var(--text-muted-dark)", fontSize: "0.75rem", marginBottom: "0.5rem", textTransform: "uppercase", letterSpacing: "0.05em"}}>Confidence Score: {r.match_score}</div>
                        
                        {r.reason && (
                          <div className="ai-reasoning">
                            {r.reason}
                          </div>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}
