"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, ListTodo, FileText, Settings, ShieldAlert } from "lucide-react";

export default function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { label: "Dashboard", href: "/", icon: LayoutDashboard },
    { label: "Investigation Queue", href: "/queue", icon: ListTodo },
    { label: "Rule Engine", href: "/policies", icon: FileText },
    { label: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <aside className="w-64 bg-forest-900 text-cream-50 h-screen sticky top-0 left-0 flex flex-col border-r border-forest-800">
      <div className="p-6 flex items-center gap-3 border-b border-forest-800">
        <ShieldAlert className="w-8 h-8 text-cream-200" />
        <h1 className="text-xl font-bold font-serif tracking-tight text-cream-50">LedgerGuard</h1>
      </div>

      <nav className="flex-1 py-6 px-4 flex flex-col gap-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
          const Icon = item.icon;
          
          return (
            <Link 
              key={item.href} 
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-md transition-colors ${
                isActive 
                  ? "bg-forest-800 text-cream-100 font-medium" 
                  : "text-forest-300 hover:bg-forest-800/50 hover:text-cream-200"
              }`}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-6 border-t border-forest-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-forest-800 flex items-center justify-center font-bold text-cream-200 border border-forest-700">
            JD
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-medium text-cream-100">Jane Doe</span>
            <span className="text-xs text-forest-400">Finance Controller</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
