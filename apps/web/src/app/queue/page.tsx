"use client";

import { useEffect, useState } from "react";
import { AlertCircle, CheckCircle2, ChevronRight, Activity, RotateCw } from "lucide-react";
import Link from "next/link";

export default function Queue() {
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  const fetchResults = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8001/api/results");
      const data = await res.json();
      setResults(data);
    } catch (err) {
      console.error("Failed to fetch results", err);
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
      
      let polls = 0;
      const interval = setInterval(async () => {
        await fetchResults();
        polls++;
        if (polls >= 5) {
          clearInterval(interval);
          setRunning(false);
        }
      }, 3000);
      
    } catch (err) {
      console.error("Error running matching", err);
      setRunning(false);
    }
  };

  if (loading) return (
    <div className="flex items-center justify-center h-full text-forest-500">
      <Activity className="w-8 h-8 animate-pulse" />
    </div>
  );

  return (
    <div className="p-10 max-w-7xl mx-auto">
      <div className="flex justify-between items-end mb-10">
        <header>
          <h1 className="text-4xl font-serif font-bold text-forest-900 mb-2">Investigation Queue</h1>
          <p className="text-forest-600 text-lg">Review and manage AI reconciliation decisions.</p>
        </header>
        <div className="flex gap-4">
          <button 
            onClick={fetchResults} 
            className="flex items-center gap-2 px-4 py-2 bg-white text-forest-700 border border-forest-300 font-medium rounded-md shadow-sm hover:bg-forest-50 transition-colors"
          >
            <RotateCw className="w-4 h-4" />
            Refresh
          </button>
          <button 
            onClick={runMatching} 
            disabled={running}
            className="px-6 py-2 bg-forest-700 text-white font-medium rounded-md shadow-sm hover:bg-forest-800 disabled:opacity-50 transition-colors flex items-center gap-2"
          >
            {running && <RotateCw className="w-4 h-4 animate-spin" />}
            {running ? "Processing Batch..." : "Run AI Investigator"}
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-forest-200 overflow-hidden">
        
        {/* Table Header */}
        <div className="grid grid-cols-12 gap-4 p-4 bg-forest-50 border-b border-forest-200 text-xs font-bold text-forest-700 tracking-wider uppercase">
          <div className="col-span-1">ID</div>
          <div className="col-span-2">Status</div>
          <div className="col-span-2">Payment</div>
          <div className="col-span-2">Settlement</div>
          <div className="col-span-5">Investigation Evidence</div>
        </div>

        {results.map((r, i) => (
          <div key={r.id} className={`grid grid-cols-12 gap-4 p-6 hover:bg-cream-50 transition-colors ${i !== results.length - 1 ? 'border-b border-forest-100' : ''}`}>
            
            <div className="col-span-1 font-mono text-sm text-forest-500 mt-1">
              #{r.id}
            </div>
            
            <div className="col-span-2">
              {r.status === "EXCEPTION" ? (
                <span className="px-3 py-1 bg-red-100 text-red-700 text-xs font-bold tracking-wide rounded-full flex items-center w-fit gap-1">
                  <AlertCircle className="w-3 h-3" /> EXCEPTION
                </span>
              ) : r.status === "RESOLVED" ? (
                <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-bold tracking-wide rounded-full flex items-center w-fit gap-1">
                  <CheckCircle2 className="w-3 h-3" /> RESOLVED
                </span>
              ) : (
                <span className="px-3 py-1 bg-yellow-100 text-yellow-700 text-xs font-bold tracking-wide rounded-full w-fit">
                  UNRESOLVED
                </span>
              )}
              
              <Link href={`/cases/${r.id}`} className="text-forest-600 hover:text-forest-900 flex items-center gap-1 text-sm font-medium mt-4">
                View Case <ChevronRight className="w-4 h-4" />
              </Link>
            </div>

            <div className="col-span-2 flex flex-col">
              <span className="text-lg font-serif font-semibold text-forest-900">
                {r.payment?.amount ? `${r.payment.amount} INR` : 'Missing'}
              </span>
              <span className="text-xs text-forest-500 font-mono mt-2 bg-forest-50 p-1.5 rounded inline-block w-fit border border-forest-100">
                P-{r.payment?.id?.substring(0, 8) || 'N/A'}
              </span>
            </div>

            <div className="col-span-2 flex flex-col">
              <span className="text-lg font-serif font-semibold text-forest-900">
                {r.settlement?.amount ? `${r.settlement.amount} INR` : 'Missing'}
              </span>
              <span className="text-xs text-forest-500 font-mono mt-2 bg-forest-50 p-1.5 rounded inline-block w-fit border border-forest-100">
                S-{r.settlement?.id?.substring(0, 8) || 'N/A'}
              </span>
              <span className="text-xs text-forest-400 font-mono mt-1">
                UTR: {r.settlement?.utr || 'N/A'}
              </span>
            </div>

            <div className="col-span-5 flex flex-col justify-center h-full">
               <div className="mb-2">
                 <h4 className="text-sm font-bold text-forest-800">{r.match_type}</h4>
                 {r.match_score && <span className="text-xs text-forest-500 uppercase tracking-wide">Confidence Score: {r.match_score}</span>}
               </div>
               <div className="bg-forest-900 text-cream-100 p-4 rounded-lg text-sm border-l-4 border-green-500 leading-relaxed shadow-inner">
                 {r.reason || "No reasoning provided."}
               </div>
            </div>
            
          </div>
        ))}

        {results.length === 0 && (
          <div className="p-12 text-center text-forest-500">
            No records found in the database.
          </div>
        )}
      </div>
    </div>
  );
}
