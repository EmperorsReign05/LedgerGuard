"use client";

import { useEffect, useState, use } from "react";
import { ArrowLeft, Send, AlertCircle, Bot, User, CheckCircle2 } from "lucide-react";
import Link from "next/link";
import { format } from "date-fns";

export default function CaseDetails({ params }: { params: Promise<{ id: string }> }) {
  // Use React.use to unwrap the Promise
  const resolvedParams = use(params);
  
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [chatInput, setChatInput] = useState("");
  const [sending, setSending] = useState(false);

  const fetchCase = async () => {
    try {
      const res = await fetch(`http://127.0.0.1:8001/api/results/${resolvedParams.id}`);
      const json = await res.json();
      setData(json);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCase();
  }, [resolvedParams.id]);

  const sendChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    setSending(true);
    try {
      await fetch(`http://127.0.0.1:8001/api/results/${resolvedParams.id}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: chatInput })
      });
      setChatInput("");
      await fetchCase();
    } catch (err) {
      console.error(err);
    } finally {
      setSending(false);
    }
  };

  if (loading) return <div className="p-10 text-forest-500">Loading case details...</div>;
  if (!data || data.error) return <div className="p-10 text-red-500">Case not found.</div>;

  return (
    <div className="flex h-screen overflow-hidden">
      
      {/* LEFT COLUMN: Data diff */}
      <div className="w-1/2 h-full flex flex-col border-r border-forest-200 bg-cream-50 overflow-y-auto p-8">
        
        <Link href="/queue" className="flex items-center gap-2 text-forest-500 hover:text-forest-800 mb-8 w-fit transition-colors">
          <ArrowLeft className="w-4 h-4" /> Back to Queue
        </Link>

        <header className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <h1 className="text-3xl font-serif font-bold text-forest-900">Case #{data.id}</h1>
            {data.status === "EXCEPTION" ? (
              <span className="px-3 py-1 bg-red-100 text-red-700 text-xs font-bold tracking-wide rounded-full flex items-center w-fit gap-1">
                <AlertCircle className="w-3 h-3" /> EXCEPTION
              </span>
            ) : data.status === "RESOLVED" ? (
              <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-bold tracking-wide rounded-full flex items-center w-fit gap-1">
                <CheckCircle2 className="w-3 h-3" /> RESOLVED
              </span>
            ) : (
              <span className="px-3 py-1 bg-yellow-100 text-yellow-700 text-xs font-bold tracking-wide rounded-full w-fit">
                UNRESOLVED
              </span>
            )}
          </div>
          <div className="text-forest-600">
            <span className="font-bold">{data.match_type}</span> — Detected during reconciliation cycle.
          </div>
        </header>

        <div className="grid grid-cols-2 gap-6 mb-8">
          {/* PAYMENT */}
          <div className="bg-white p-6 rounded-xl border-t-4 border-t-forest-700 shadow-sm border border-forest-200">
            <h3 className="text-sm font-bold text-forest-500 uppercase tracking-wider mb-4">Source Payment</h3>
            {data.payment ? (
              <div className="flex flex-col gap-3">
                <div>
                  <div className="text-xs text-forest-400">Amount</div>
                  <div className="text-2xl font-serif font-bold text-forest-900">{data.payment.amount} <span className="text-sm font-sans font-normal">{data.payment.currency}</span></div>
                </div>
                <div>
                  <div className="text-xs text-forest-400">Payment ID</div>
                  <div className="font-mono text-sm text-forest-700 bg-forest-50 p-1 rounded border border-forest-100">{data.payment.id}</div>
                </div>
                <div>
                  <div className="text-xs text-forest-400">Status</div>
                  <div className="text-sm font-medium text-forest-800">{data.payment.status}</div>
                </div>
              </div>
            ) : (
              <div className="text-forest-400 italic">No linked payment record.</div>
            )}
          </div>

          {/* SETTLEMENT */}
          <div className="bg-white p-6 rounded-xl border-t-4 border-t-forest-700 shadow-sm border border-forest-200">
            <h3 className="text-sm font-bold text-forest-500 uppercase tracking-wider mb-4">Candidate Settlement</h3>
            {data.settlement ? (
              <div className="flex flex-col gap-3">
                <div>
                  <div className="text-xs text-forest-400">Amount</div>
                  <div className="text-2xl font-serif font-bold text-forest-900">{data.settlement.amount} <span className="text-sm font-sans font-normal">INR</span></div>
                </div>
                <div>
                  <div className="text-xs text-forest-400">Settlement ID</div>
                  <div className="font-mono text-sm text-forest-700 bg-forest-50 p-1 rounded border border-forest-100">{data.settlement.id}</div>
                </div>
                <div>
                  <div className="text-xs text-forest-400">UTR (Bank Ref)</div>
                  <div className="font-mono text-sm text-forest-700">{data.settlement.utr || "N/A"}</div>
                </div>
              </div>
            ) : (
              <div className="text-forest-400 italic">No linked settlement record.</div>
            )}
          </div>
        </div>
        
        {/* Discrepancy Alert */}
        {data.payment && data.settlement && data.payment.amount !== data.settlement.amount && (
          <div className="bg-red-50 border border-red-200 p-4 rounded-xl flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-bold text-red-800">Amount Discrepancy Detected</h4>
              <p className="text-sm text-red-600 mt-1">
                There is a difference of <span className="font-mono font-bold">{Math.abs(data.payment.amount - data.settlement.amount)} INR</span> between the Source and Candidate.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* RIGHT COLUMN: AI Chat & Audit Trail */}
      <div className="w-1/2 h-full flex flex-col bg-white">
        <div className="p-6 border-b border-forest-100 bg-forest-50">
          <h2 className="text-lg font-bold text-forest-900 font-serif">Investigation Audit Trail</h2>
          <p className="text-sm text-forest-500">Immutable ledger of AI and Human actions.</p>
        </div>

        <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-4">
          
          {/* Initial Reason */}
          {data.reason && (
             <div className="flex gap-4">
               <div className="w-8 h-8 rounded-full bg-forest-200 flex items-center justify-center flex-shrink-0">
                 <Bot className="w-4 h-4 text-forest-700" />
               </div>
               <div className="bg-forest-50 border border-forest-100 rounded-2xl rounded-tl-none p-4 text-sm text-forest-800">
                 <span className="text-xs font-bold text-forest-400 uppercase tracking-wide block mb-1">System Trace</span>
                 {data.reason}
               </div>
             </div>
          )}

          {/* Audit Logs */}
          {data.audit_logs?.map((log: any, i: number) => (
            <div key={i} className={`flex gap-4 ${log.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                log.role === 'user' ? 'bg-forest-800 text-cream-100' : 'bg-forest-200 text-forest-700'
              }`}>
                {log.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>
              <div className={`p-4 text-sm rounded-2xl max-w-[85%] ${
                log.role === 'user' 
                  ? 'bg-forest-800 text-cream-50 rounded-tr-none' 
                  : 'bg-forest-50 border border-forest-100 text-forest-800 rounded-tl-none whitespace-pre-wrap'
              }`}>
                <span className="text-xs font-bold opacity-50 uppercase tracking-wide block mb-1">
                  {format(new Date(log.timestamp), "HH:mm:ss")}
                </span>
                {log.content}
              </div>
            </div>
          ))}
        </div>

        {/* Chat Input */}
        <div className="p-4 border-t border-forest-200 bg-cream-50">
          <form onSubmit={sendChat} className="flex gap-2">
            <input 
              type="text" 
              placeholder="Ask the AI investigator a question..." 
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              disabled={sending}
              className="flex-1 bg-white border border-forest-200 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-forest-500 text-forest-900"
            />
            <button 
              type="submit" 
              disabled={sending || !chatInput.trim()}
              className="bg-forest-700 text-cream-50 p-3 rounded-lg hover:bg-forest-800 disabled:opacity-50 transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
        </div>
      </div>

    </div>
  );
}
