import React from 'react';
import { 
  Users, 
  DollarSign, 
  ShoppingCart, 
  TrendingUp, 
  Eye, 
  ArrowUpRight,
  Sparkles
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend, 
  LineChart, 
  Line, 
  CartesianGrid 
} from 'recharts';
import { OverviewData } from '../types/analytics';

interface OverviewViewProps {
  data: OverviewData | null;
  isLoading: boolean;
}

export const OverviewView: React.FC<OverviewViewProps> = ({ data, isLoading }) => {
  if (isLoading || !data) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex items-center gap-3 text-slate-400">
          <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <span>Đang nạp số liệu từ Google BigQuery...</span>
        </div>
      </div>
    );
  }

  const { kpis, traffic_channels } = data;

  const kpiCards = [
    {
      title: 'TỔNG NGƯỜI DÙNG (USERS)',
      value: kpis.total_users.toLocaleString(),
      subtext: 'Khách hàng phân biệt',
      icon: Users,
      color: 'from-blue-500/20 to-blue-600/5',
      textColor: 'text-blue-400',
    },
    {
      title: 'TỔNG PHIÊN (SESSIONS)',
      value: kpis.total_sessions.toLocaleString(),
      subtext: `${(kpis.total_sessions / Math.max(1, kpis.total_users)).toFixed(1)} sessions/user`,
      icon: Eye,
      color: 'from-cyan-500/20 to-cyan-600/5',
      textColor: 'text-cyan-400',
    },
    {
      title: 'TỔNG DOANH THU',
      value: `$${kpis.total_revenue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      subtext: `AOV: $${kpis.average_order_value_usd.toFixed(2)}`,
      icon: DollarSign,
      color: 'from-emerald-500/20 to-emerald-600/5',
      textColor: 'text-emerald-400',
    },
    {
      title: 'TỔNG ĐƠN HÀNG (PURCHASES)',
      value: kpis.total_transactions.toLocaleString(),
      subtext: 'Giao dịch thành công',
      icon: ShoppingCart,
      color: 'from-amber-500/20 to-amber-600/5',
      textColor: 'text-amber-400',
    },
    {
      title: 'TỶ LỆ CHUYỂN ĐỔI (CR)',
      value: `${kpis.conversion_rate_pct}%`,
      subtext: 'Tỷ lệ chốt đơn toàn sàn',
      icon: TrendingUp,
      color: 'from-purple-500/20 to-purple-600/5',
      textColor: 'text-purple-400',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-blue-900/40 via-slate-900/60 to-slate-900/90 border border-blue-500/20 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-1">
              <Sparkles className="w-4 h-4" />
              <span>Báo cáo Hiệu suất Thương mại Điện tử</span>
            </div>
            <h2 className="text-xl font-bold text-slate-100">
              Tổng quan Chỉ số Kinh doanh & Phân bổ Lưu lượng Truy cập
            </h2>
            <p className="text-sm text-slate-400 mt-1">
              Dữ liệu được truy vấn phân tán trực tiếp từ 92 bảng sự kiện GA4 trên Google BigQuery.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700 text-xs font-medium text-slate-300">
              92 Partitioned Tables
            </span>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {kpiCards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div
              key={idx}
              className="p-5 rounded-2xl glass-card bg-gradient-to-b border border-slate-800 flex flex-col justify-between"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold text-slate-400 tracking-wider">
                  {card.title}
                </span>
                <div className={`p-2 rounded-xl bg-slate-800/80 ${card.textColor}`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div>
                <div className="text-2xl font-bold text-slate-100 tracking-tight">
                  {card.value}
                </div>
                <div className="text-xs font-medium text-slate-400 mt-1">
                  {card.subtext}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue & Users by Channel */}
        <div className="p-6 rounded-2xl glass-panel border border-slate-800">
          <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center justify-between">
            <span>Doanh thu & Số lượng Khách hàng theo Kênh Tiếp thị</span>
            <span className="text-xs text-slate-400 font-normal">Traffic Medium</span>
          </h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={traffic_channels}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="traffic_medium" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} tickFormatter={(val) => `$${val}`} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: 8, fontSize: 12 }}
                  formatter={(val: any) => [`$${Number(val).toLocaleString()}`, 'Doanh thu']}
                />
                <Bar dataKey="total_revenue" fill="#3b82f6" radius={[6, 6, 0, 0]} name="Doanh thu ($ USD)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Conversion Rate by Channel */}
        <div className="p-6 rounded-2xl glass-panel border border-slate-800">
          <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center justify-between">
            <span>Tỷ lệ Chuyển đổi theo Kênh (Conversion Rate %)</span>
            <span className="text-xs text-emerald-400 font-medium">Tỷ lệ chốt đơn</span>
          </h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={traffic_channels} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" stroke="#64748b" fontSize={11} unit="%" />
                <YAxis dataKey="traffic_medium" type="category" stroke="#64748b" fontSize={11} width={90} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: 8, fontSize: 12 }}
                  formatter={(val: any) => [`${val}%`, 'Tỷ lệ chuyển đổi']}
                />
                <Bar dataKey="conversion_rate" fill="#10b981" radius={[0, 6, 6, 0]} name="Conversion Rate (%)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Traffic Channels Data Table */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800 overflow-hidden">
        <h3 className="text-sm font-bold text-slate-200 mb-4">
          Bảng Chi tiết Hiệu suất Kênh Tiếp thị (SQL Query 01_eda_overview)
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-800/60 uppercase font-semibold text-slate-400 border-b border-slate-700">
              <tr>
                <th className="py-3 px-4">Kênh Tiếp thị (Medium)</th>
                <th className="py-3 px-4 text-right">Tổng Users</th>
                <th className="py-3 px-4 text-right">Tổng Sessions</th>
                <th className="py-3 px-4 text-right">Tổng Pageviews</th>
                <th className="py-3 px-4 text-right">Số Đơn hàng</th>
                <th className="py-3 px-4 text-right">Tổng Doanh thu ($)</th>
                <th className="py-3 px-4 text-right">Tỷ lệ Chuyển đổi (%)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {traffic_channels.map((ch, i) => (
                <tr key={i} className="hover:bg-slate-800/40 transition">
                  <td className="py-3 px-4 font-semibold text-slate-200 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                    <span>{ch.traffic_medium}</span>
                  </td>
                  <td className="py-3 px-4 text-right">{ch.total_users.toLocaleString()}</td>
                  <td className="py-3 px-4 text-right">{ch.total_sessions.toLocaleString()}</td>
                  <td className="py-3 px-4 text-right">{ch.total_pageviews.toLocaleString()}</td>
                  <td className="py-3 px-4 text-right text-emerald-400 font-semibold">{ch.total_transactions.toLocaleString()}</td>
                  <td className="py-3 px-4 text-right font-bold text-slate-100">${ch.total_revenue.toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
                  <td className="py-3 px-4 text-right">
                    <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">
                      {ch.conversion_rate}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
