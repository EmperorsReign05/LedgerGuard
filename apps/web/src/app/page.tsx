"use client";

import { useEffect, useState } from "react";

export default function Dashboard() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [metrics, setMetrics] = useState({ total: 0, resolved: 0, exceptions: 0, unresolved: 0 });

  const fetchResults = async () => {
    try {
      const res = await fetch("http://localhost:8001/api/results");
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
      await fetch("http://localhost:8001/api/run-matching", { method: "POST" });
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
    <div className="container">
      <div className="header">
        <h1>LedgerGuard Finance Controller</h1>
        <p>AI-assisted evidence-based reconciliation dashboard.</p>
      </div>

      <div className="metrics-grid">
        <div className="metric-card">
          <h3>Total Processed</h3>
          <p>{metrics.total}</p>
        </div>
        <div className="metric-card">
          <h3>Auto Resolved</h3>
          <p>{metrics.resolved}</p>
        </div>
        <div className="metric-card">
          <h3>Escalated Exceptions</h3>
          <p>{metrics.exceptions}</p>
        </div>
        <div className="metric-card">
          <h3>Unresolved</h3>
          <p>{metrics.unresolved}</p>
        </div>
      </div>

      <div className="controls">
        <button className="btn" onClick={runMatching} disabled={running}>
          {running ? "Processing Batch..." : "Run AI Matching Pipeline"}
        </button>
      </div>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Status</th>
              <th>Payment</th>
              <th>Settlement</th>
              <th>Details & AI Reasoning</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5} style={{textAlign: "center"}}>Loading...</td></tr>
            ) : results.length === 0 ? (
              <tr><td colSpan={5} style={{textAlign: "center"}}>No records found. Seed DB and run pipeline.</td></tr>
            ) : (
              results.map((r: any) => (
                <tr key={r.id}>
                  <td><strong>#{r.id}</strong></td>
                  <td>{getStatusBadge(r.status)}</td>
                  <td>
                    {r.payment ? (
                      <div>
                        <div>{r.payment.amount} {r.payment.currency}</div>
                        <div className="code-block">{r.payment.id}</div>
                      </div>
                    ) : "None"}
                  </td>
                  <td>
                    {r.settlement ? (
                      <div>
                        <div>{r.settlement.amount} INR</div>
                        <div className="code-block">{r.settlement.id}</div>
                        {r.settlement.utr && <div style={{marginTop: "0.25rem", color: "var(--muted)", fontSize: "0.75rem"}}>UTR: {r.settlement.utr}</div>}
                      </div>
                    ) : "None"}
                  </td>
                  <td>
                    <div style={{fontWeight: 500}}>{r.match_type.replace("_", " ")}</div>
                    <div style={{color: "var(--muted)", fontSize: "0.75rem", marginBottom: "0.5rem"}}>Score: {r.match_score}</div>
                    
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
  );
}
