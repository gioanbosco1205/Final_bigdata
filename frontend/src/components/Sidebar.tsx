import React from 'react';
import { 
  BarChart3, 
  Filter, 
  Users, 
  ShoppingBag, 
  Lightbulb, 
  Database,
  Sparkles
} from 'lucide-react';

export type TabType = 'overview' | 'funnel' | 'personas' | 'basket' | 'insights';

interface SidebarProps {
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const navItems = [
    { id: 'overview', label: '1. Executive Overview', icon: BarChart3, badge: 'KPIs' },
    { id: 'funnel', label: '2. Funnel Diagnostics', icon: Filter, badge: 'Journey' },
    { id: 'personas', label: '3. Customer Personas', icon: Users, badge: 'K-Means' },
    { id: 'basket', label: '4. Market Basket & Rules', icon: ShoppingBag, badge: 'Apriori' },
    { id: 'insights', label: '5. Strategic Insights', icon: Lightbulb, badge: 'Action' },
  ];

  return (
    <aside className="w-64 bg-slate-900/90 border-r border-slate-800 flex flex-col justify-between p-4 min-h-screen">
      <div>
        {/* Brand Logo & Title */}
        <div className="flex items-center gap-3 px-3 py-4 mb-6 border-b border-slate-800/80">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="font-bold text-slate-100 text-sm tracking-tight leading-tight">
              E-COMMERCE AI
            </h2>
            <p className="text-xs text-blue-400 font-medium">BigQuery & Python ML</p>
          </div>
        </div>

        {/* Navigation Menu */}
        <nav className="space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id as TabType)}
                className={`w-full flex items-center justify-between px-3.5 py-3 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/25'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </div>
                <span className={`text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded-full ${
                  isActive ? 'bg-blue-700/80 text-blue-100' : 'bg-slate-800 text-slate-400'
                }`}>
                  {item.badge}
                </span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Dataset & Big Data Badge */}
      <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-800 text-xs">
        <div className="flex items-center gap-2 text-emerald-400 font-semibold mb-1.5">
          <Database className="w-3.5 h-3.5" />
          <span>GA4 Big Data Live</span>
        </div>
        <p className="text-slate-400 leading-relaxed text-[11px]">
          Dataset: Google Analytics 4 (Google Merchandise Store).
        </p>
      </div>
    </aside>
  );
};
