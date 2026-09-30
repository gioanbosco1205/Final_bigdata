import React, { useState } from 'react';
import { 
  Users, 
  Crown, 
  Sparkles, 
  ShoppingCart, 
  AlertCircle, 
  Search, 
  BarChart2, 
  Layers, 
  CheckCircle2,
  Clock,
  DollarSign
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  ScatterChart, 
  Scatter, 
  XAxis, 
  YAxis, 
  ZAxis, 
  Tooltip, 
  CartesianGrid, 
  Cell 
} from 'recharts';
import { PersonasData, UserDetail } from '../types/analytics';
import { analyticsApi } from '../services/api';

interface PersonasViewProps {
  data: PersonasData | null;
  sampleUsers: UserDetail[];
}

export const PersonasView: React.FC<PersonasViewProps> = ({ data, sampleUsers }) => {
  const [selectedUser, setSelectedUser] = useState<UserDetail | null>(sampleUsers.length > 0 ? sampleUsers[0] : null);
  const [searchQuery, setSearchQuery] = useState<string>('');

  if (!data) {
    return <div className="text-center py-20 text-slate-400">Đang nạp dữ liệu phân khúc...</div>;
  }

  const { personas_summary, cluster_evaluation, pca_scatter_points } = data;

  const personaConfig: Record<string, { icon: any; color: string; border: string; bg: string; badgeColor: string }> = {
    'Loyal Champions (VIPs)': {
      icon: Crown,
      color: '#10b981',
      border: 'border-emerald-500/30',
      bg: 'bg-emerald-500/10',
      badgeColor: 'bg-emerald-500/20 text-emerald-400'
    },
    'Potential Loyalists': {
      icon: Sparkles,
      color: '#3b82f6',
      border: 'border-blue-500/30',
      bg: 'bg-blue-500/10',
      badgeColor: 'bg-blue-500/20 text-blue-400'
    },
    'Cart Abandoners / Window Shoppers': {
      icon: ShoppingCart,
      color: '#f59e0b',
      border: 'border-amber-500/30',
      bg: 'bg-amber-500/10',
      badgeColor: 'bg-amber-500/20 text-amber-400'
    },
    'At-Risk / Inactive Customers': {
      icon: AlertCircle,
      color: '#ef4444',
      border: 'border-rose-500/30',
      bg: 'bg-rose-500/10',
      badgeColor: 'bg-rose-500/20 text-rose-400'
    }
  };

  const handleSelectUser = async (userId: string) => {
    try {
      const u = await analyticsApi.getUserDetail(userId);
      setSelectedUser(u);
    } catch {
      const found = sampleUsers.find(x => x.user_pseudo_id === userId);
      if (found) setSelectedUser(found);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & ML Evaluation Badge */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <Users className="w-4 h-4" />
            <span>Mô hình Học máy Không giám sát (Unsupervised K-Means Clustering)</span>
          </div>
          <h2 className="text-xl font-bold text-slate-100">
            Khám phá 4 Chân dung Khách hàng (Customer Personas)
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Phân cụm tự động trên không gian 9 đặc trưng RFM & Hành vi tương tác từ BigQuery.
          </p>
        </div>

        {/* ML Evaluation Metrics Box */}
        <div className="flex items-center gap-3 bg-slate-900/90 p-2.5 rounded-xl border border-slate-800 text-xs">
          <div className="px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
            <span className="text-slate-400">Silhouette Score: </span>
            <span className="font-bold text-emerald-400">{cluster_evaluation.silhouette_score} (Xuất sắc &gt; 0.35)</span>
          </div>
          <div className="px-2.5 py-1 rounded-lg bg-blue-500/10 border border-blue-500/20">
            <span className="text-slate-400">PCA Variance: </span>
            <span className="font-bold text-blue-400">91.10% (3D)</span>
          </div>
        </div>
      </div>

      {/* 4 Persona Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {personas_summary.map((p, i) => {
          const cfg = personaConfig[p['Chân dung Khách hàng (Persona)']] || {
            icon: Users,
            color: '#3b82f6',
            border: 'border-slate-800',
            bg: 'bg-slate-800/40',
            badgeColor: 'bg-slate-800 text-slate-300'
          };
          const Icon = cfg.icon;
          return (
            <div
              key={i}
              className={`p-5 rounded-2xl glass-card border ${cfg.border} ${cfg.bg} flex flex-col justify-between`}
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className={`p-2.5 rounded-xl ${cfg.badgeColor}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${cfg.badgeColor}`}>
                    {p['Số lượng Users']}
                  </span>
                </div>

                <h4 className="text-base font-bold text-slate-100 mb-1">
                  {p['Chân dung Khách hàng (Persona)']}
                </h4>
                <p className="text-xs text-slate-300 line-clamp-2 mb-4 leading-relaxed">
                  {p['Hành vi Nổi bật']}
                </p>
              </div>

              {/* Stats Mini Grid */}
              <div className="grid grid-cols-2 gap-2 pt-3 border-t border-slate-700/40 text-xs">
                <div>
                  <div className="text-slate-400 text-[10px] uppercase font-semibold">Doanh thu TB</div>
                  <div className="font-extrabold text-slate-100">${p['Doanh thu TB ($)']}</div>
                </div>
                <div>
                  <div className="text-slate-400 text-[10px] uppercase font-semibold">Recency TB</div>
                  <div className="font-extrabold text-slate-100">{p['Recency TB (ngày)']} ngày</div>
                </div>
                <div>
                  <div className="text-slate-400 text-[10px] uppercase font-semibold">Sessions TB</div>
                  <div className="font-extrabold text-slate-100">{p['Sessions TB']}</div>
                </div>
                <div>
                  <div className="text-slate-400 text-[10px] uppercase font-semibold">Tỷ lệ Giỏ/Xem</div>
                  <div className="font-extrabold text-slate-100">{p['Tỷ lệ Giỏ/Xem']}</div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* PCA Scatter Chart & Detailed Persona Table */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* PCA 2D Scatter */}
        <div className="p-6 rounded-2xl glass-panel border border-slate-800">
          <h3 className="text-sm font-bold text-slate-200 mb-2 flex items-center justify-between">
            <span>Không gian Phân cụm PCA 2D (Cluster Boundary Projection)</span>
            <span className="text-xs text-slate-400">82.3% Variance</span>
          </h3>
          <p className="text-xs text-slate-400 mb-4">
            Mỗi điểm đại diện cho 1 khách hàng thực tế được chiếu từ không gian 9 chiều.
          </p>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 10, right: 10, bottom: 10, left: -20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis type="number" dataKey="pca_2d_x" name="PCA Component 1" stroke="#64748b" fontSize={10} />
                <YAxis type="number" dataKey="pca_2d_y" name="PCA Component 2" stroke="#64748b" fontSize={10} />
                <Tooltip
                  cursor={{ strokeDasharray: '3 3' }}
                  content={({ payload }) => {
                    if (payload && payload.length) {
                      const d = payload[0].payload;
                      return (
                        <div className="p-3 bg-slate-900 border border-slate-700 rounded-xl text-xs space-y-1 shadow-xl">
                          <div className="font-bold text-slate-100">{d.user_pseudo_id}</div>
                          <div className="text-emerald-400 font-semibold">{d.persona_name}</div>
                          <div className="text-slate-300">Doanh thu: <b>${d.monetary_value}</b> | Sessions: <b>{d.total_sessions}</b></div>
                          <div className="text-slate-300">Recency: <b>{d.recency_days} ngày</b> | Tương tác: <b>{d.total_engagement_sec}s</b></div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Scatter name="Users" data={pca_scatter_points}>
                  {pca_scatter_points.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.persona_color || '#3b82f6'} fillOpacity={0.8} />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Persona Comparison Table */}
        <div className="p-6 rounded-2xl glass-panel border border-slate-800 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-200 mb-4">
              Bảng Tổng hợp Đặc tính Trung bình Đa chiều của 4 Nhóm
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-800/60 uppercase font-semibold text-slate-400 border-b border-slate-700">
                  <tr>
                    <th className="py-2.5 px-3">Persona</th>
                    <th className="py-2.5 px-3 text-right">Recency</th>
                    <th className="py-2.5 px-3 text-right">Sessions</th>
                    <th className="py-2.5 px-3 text-right">Doanh thu</th>
                    <th className="py-2.5 px-3 text-right">Đơn hàng</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {personas_summary.map((p, i) => (
                    <tr key={i} className="hover:bg-slate-800/40 transition">
                      <td className="py-3 px-3 font-semibold text-slate-200 flex items-center gap-2">
                        <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: personaConfig[p['Chân dung Khách hàng (Persona)']]?.color || '#3b82f6' }}></span>
                        <span>{p['Chân dung Khách hàng (Persona)']}</span>
                      </td>
                      <td className="py-3 px-3 text-right">{p['Recency TB (ngày)']} ngày</td>
                      <td className="py-3 px-3 text-right">{p['Sessions TB']}</td>
                      <td className="py-3 px-3 text-right font-bold text-emerald-400">${p['Doanh thu TB ($)']}</td>
                      <td className="py-3 px-3 text-right font-bold text-slate-100">{p['Đơn hàng TB']}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Quick Academic Takeaway */}
          <div className="mt-4 p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs text-blue-300">
            💡 <b>Đánh giá mô hình:</b> K-Means tách biệt rõ ràng nhóm <b>VIPs</b> ($380+ chi tiêu) và nhóm <b>Cart Abandoners</b> (tỷ lệ giỏ/xem cao 0.25 nhưng doanh thu $0.03).
          </div>
        </div>
      </div>

      {/* User Lookup Inspector */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800">
        <h3 className="text-sm font-bold text-slate-200 mb-3 flex items-center gap-2">
          <Search className="w-4 h-4 text-blue-400" />
          <span>Hộp thoại Tra cứu Chi tiết Hành vi Khách hàng (`user_pseudo_id`)</span>
        </h3>
        <p className="text-xs text-slate-400 mb-4">
          Tìm kiếm và kiểm tra hồ sơ RFM + hành vi thực tế của từng người dùng trong tập dữ liệu BigQuery.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="md:col-span-1">
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
              Chọn User ID mẫu:
            </label>
            <select
              value={selectedUser?.user_pseudo_id || ''}
              onChange={(e) => handleSelectUser(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
            >
              {sampleUsers.map((u, i) => (
                <option key={i} value={u.user_pseudo_id}>
                  {u.user_pseudo_id} ({u.persona_name})
                </option>
              ))}
            </select>
          </div>

          {selectedUser && (
            <div className="md:col-span-2 grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
              <div>
                <div className="text-[10px] text-slate-400 uppercase font-semibold">Phân khúc Persona</div>
                <div className="font-bold text-xs text-emerald-400 mt-0.5">{selectedUser.persona_name}</div>
              </div>
              <div>
                <div className="text-[10px] text-slate-400 uppercase font-semibold">Tổng Doanh thu (M)</div>
                <div className="font-bold text-xs text-slate-100 mt-0.5">${selectedUser.monetary_value.toFixed(2)}</div>
              </div>
              <div>
                <div className="text-[10px] text-slate-400 uppercase font-semibold">Lần cuối (R)</div>
                <div className="font-bold text-xs text-slate-100 mt-0.5">{selectedUser.recency_days} ngày trước</div>
              </div>
              <div>
                <div className="text-[10px] text-slate-400 uppercase font-semibold">Tương tác</div>
                <div className="font-bold text-xs text-slate-100 mt-0.5">{selectedUser.total_engagement_sec.toFixed(0)} giây</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
