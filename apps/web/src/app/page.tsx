"use client";

import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { ShieldAlert, CheckCircle2, Clock, Activity } from "lucide-react";

export default function Dashboard() {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8001/api/metrics")
      .then((res) => res.json())
      .then((data) => {
        setMetrics(data);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full text-forest-500">
        <Activity className="w-8 h-8 animate-pulse" />
      </div>
    );
  }

  const chartData = [
    { name: "Resolved", value: metrics?.resolved || 0, color: "#10b981" },
    { name: "Unresolved", value: metrics?.unresolved || 0, color: "#eab308" },
    { name: "Exceptions", value: metrics?.exceptions || 0, color: "#ef4444" },
  ];

  return (
    <div className="p-10 max-w-6xl mx-auto">
      <header className="mb-10">
        <h1 className="text-4xl font-serif font-bold text-forest-900 mb-2">Platform Overview</h1>
        <p className="text-forest-600 text-lg">Real-time ledger reconciliation analytics</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        {/* Metric 1 */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-forest-200 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-forest-600 font-medium">Total Volume</h3>
            <ShieldAlert className="w-5 h-5 text-forest-400" />
          </div>
          <div className="text-4xl font-bold text-forest-900">{metrics?.total || 0}</div>
          <p className="text-sm text-forest-500 mt-2">Transactions processed</p>
        </div>

        {/* Metric 2 */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-forest-200 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-forest-600 font-medium">Auto-Resolved</h3>
            <CheckCircle2 className="w-5 h-5 text-green-500" />
          </div>
          <div className="text-4xl font-bold text-green-600">{metrics?.resolved || 0}</div>
          <p className="text-sm text-forest-500 mt-2">Without human intervention</p>
        </div>

        {/* Metric 3 */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-forest-200 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-forest-600 font-medium">Human Hours Saved</h3>
            <Clock className="w-5 h-5 text-forest-400" />
          </div>
          <div className="text-4xl font-bold text-forest-900">{metrics?.human_hours_saved || 0}<span className="text-xl ml-1 text-forest-500">hrs</span></div>
          <p className="text-sm text-forest-500 mt-2">Based on 5 mins per exception</p>
        </div>

        {/* Metric 4 */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-forest-200 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-forest-600 font-medium">Accuracy Rate</h3>
            <Activity className="w-5 h-5 text-forest-400" />
          </div>
          <div className="text-4xl font-bold text-forest-900">{metrics?.accuracy_rate || 0}%</div>
          <p className="text-sm text-forest-500 mt-2">True Positive Rate</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-xl shadow-sm border border-forest-200 p-8">
          <h2 className="text-xl font-serif font-bold text-forest-900 mb-6">Queue Distribution</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <XAxis dataKey="name" stroke="#a3b8a1" />
                <YAxis stroke="#a3b8a1" />
                <Tooltip 
                  cursor={{fill: '#f3f4f1'}}
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} 
                />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
