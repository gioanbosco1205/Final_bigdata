import React, { useState, useEffect } from 'react';
import { 
  Filter, 
  ArrowRight, 
  AlertTriangle, 
  Laptop, 
  Smartphone, 
  Tablet, 
  TrendingDown, 
  CheckCircle2,
  TrendingUp
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  Cell 
} from 'recharts';
import { FunnelData } from '../types/analytics';
import { analyticsApi } from '../services/api';

interface FunnelViewProps {
  initialData: FunnelData | null;
}

export const FunnelView: React.FC<FunnelViewProps> = ({ initialData }) => {
  const [device, setDevice] = useState<string>('all');
  const [funnelData, setFunnelData] = useState<FunnelData | null>(initialData);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    async function fetchFunnel() {
      setIsLoading(true);
      try {
        const res = await analyticsApi.getFunnel(device);
        setFunnelData(res);
      } catch (err) {
        console.error('Error fetching funnel:', err);
      } finally {
        setIsLoading(false);
      }
    }
    fetchFunnel();
  }, [device]);

  if (!funnelData) {
    return <div className="text-center py-20 text-slate-400">Đang tải dữ liệu phễu...</div>;
  }

  const { steps, metrics, devices_breakdown } = funnelData;
  const colors = ['#3b82f6', '#0ea5e9', '#f59e0b', '#10b981'];

  return (
    <div className="space-y-6">
      {/* Header & Device Filters */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <Filter className="w-4 h-4" />
            <span>Phân tích Hành trình Mua sắm Tuần tự (Sequential Funnel)</span>
          </div>
          <h2 className="text-xl font-bold text-slate-100">
            Chẩn đoán Điểm nghẽn Rơi rụng & Tỷ lệ Bỏ giỏ hàng
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Theo dõi chặt chẽ hành vi cùng 1 User qua 4 bước: View $\to$ Cart $\to$ Checkout $\to$ Purchase.
          </p>
        </div>

        {/* Device Pills */}
        <div className="flex items-center gap-2 bg-slate-900/80 p-1.5 rounded-xl border border-slate-800">
          {[
            { id: 'all', label: 'Tất cả thiết bị', icon: null },
            { id: 'desktop', label: 'Desktop', icon: Laptop },
            { id: 'mobile', label: 'Mobile', icon: Smartphone },
            { id: 'tablet', label: 'Tablet', icon: Tablet },
          ].map((item) => {
            const Icon = item.icon;
            const isSelected = device === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setDevice(item.id)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                  isSelected
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                {Icon && <Icon className="w-3.5 h-3.5" />}
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Funnel KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-5 rounded-2xl glass-card bg-emerald-500/5 border border-emerald-500/20 flex items-center justify-between">
          <div>
            <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-1">
              TỶ LỆ CHUYỂN ĐỔI TỔNG THỂ (OVERALL CR)
            </div>
            <div className="text-3xl font-extrabold text-slate-100">
              {metrics.overall_conversion_rate_pct}%
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Tỷ lệ từ Xem sản phẩm (Step 1) đến Mua hàng thành công (Step 4)
            </div>
          </div>
          <div className="p-3 rounded-2xl bg-emerald-500/20 text-emerald-400">
            <CheckCircle2 className="w-8 h-8" />
          </div>
        </div>

        <div className="p-5 rounded-2xl glass-card bg-amber-500/5 border border-amber-500/20 flex items-center justify-between">
          <div>
            <div className="text-xs font-bold text-amber-400 uppercase tracking-wider mb-1">
              TỶ LỆ BỎ GIỎ HÀNG (CART ABANDONMENT RATE)
            </div>
            <div className="text-3xl font-extrabold text-slate-100">
              {metrics.cart_abandonment_rate_pct}%
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Khách hàng thêm sản phẩm vào giỏ nhưng không hoàn tất thanh toán
            </div>
          </div>
          <div className="p-3 rounded-2xl bg-amber-500/20 text-amber-400">
            <AlertTriangle className="w-8 h-8" />
          </div>
        </div>
      </div>

      {/* 4 Sequential Funnel Steps */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {steps.map((st, i) => (
          <div
            key={i}
            className="p-5 rounded-2xl glass-card border border-slate-800 relative overflow-hidden"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold px-2 py-0.5 rounded-md bg-slate-800 text-blue-400 border border-slate-700">
                BƯỚC {st.step_number}
              </span>
              <span className="text-xs font-semibold text-slate-400">
                {st.pct_of_step_1}% tổng
              </span>
            </div>

            <h4 className="text-sm font-bold text-slate-200 mb-2">
              {st.name}
            </h4>

            <div className="text-2xl font-extrabold text-slate-100">
              {st.users.toLocaleString()}{' '}
              <span className="text-xs font-normal text-slate-400">users</span>
            </div>

            {st.drop_off_pct > 0 && (
              <div className="mt-3 flex items-center gap-1.5 text-xs text-rose-400 bg-rose-500/10 border border-rose-500/20 px-2.5 py-1 rounded-lg">
                <TrendingDown className="w-3.5 h-3.5" />
                <span>Rơi rụng: <b>{st.drop_off_pct}%</b> ở bước này</span>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Funnel Chart & Device Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Step Chart */}
        <div className="p-6 rounded-2xl glass-panel border border-slate-800">
          <h3 className="text-sm font-bold text-slate-200 mb-4">
            Biểu đồ Phễu Chuyển đổi (Users qua từng tầng)
          </h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={steps} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" stroke="#64748b" fontSize={11} tickFormatter={(v) => v.toLocaleString()} />
                <YAxis dataKey="name" type="category" stroke="#64748b" fontSize={10} width={130} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: 8, fontSize: 12 }}
                  formatter={(val: any) => [`${Number(val).toLocaleString()} users`, 'Số lượng']}
                />
                <Bar dataKey="users" radius={[0, 6, 6, 0]}>
                  {steps.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Device Breakdown Table */}
        <div className="p-6 rounded-2xl glass-panel border border-slate-800">
          <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center justify-between">
            <span>So sánh Hiệu suất Phễu theo Thiết bị</span>
            <span className="text-xs text-blue-400 font-medium">Desktop vs Mobile</span>
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-800/60 uppercase font-semibold text-slate-400 border-b border-slate-700">
                <tr>
                  <th className="py-2.5 px-3">Thiết bị</th>
                  <th className="py-2.5 px-3 text-right">Xem SP</th>
                  <th className="py-2.5 px-3 text-right">Thêm Giỏ</th>
                  <th className="py-2.5 px-3 text-right">Mua Hàng</th>
                  <th className="py-2.5 px-3 text-right">Overall CR</th>
                  <th className="py-2.5 px-3 text-right text-amber-400">Bỏ Giỏ</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {devices_breakdown.map((dev, i) => (
                  <tr key={i} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-3 font-semibold text-slate-200 capitalize flex items-center gap-2">
                      {dev.device_category === 'desktop' && <Laptop className="w-3.5 h-3.5 text-blue-400" />}
                      {dev.device_category === 'mobile' && <Smartphone className="w-3.5 h-3.5 text-cyan-400" />}
                      {dev.device_category === 'tablet' && <Tablet className="w-3.5 h-3.5 text-purple-400" />}
                      <span>{dev.device_category}</span>
                    </td>
                    <td className="py-3 px-3 text-right">{dev.step_1_view_item_users.toLocaleString()}</td>
                    <td className="py-3 px-3 text-right">{dev.step_2_add_to_cart_users.toLocaleString()}</td>
                    <td className="py-3 px-3 text-right text-emerald-400 font-bold">{dev.step_4_purchase_users.toLocaleString()}</td>
                    <td className="py-3 px-3 text-right font-bold text-slate-100">{dev.overall_conversion_rate_pct}%</td>
                    <td className="py-3 px-3 text-right font-bold text-amber-400">{dev.cart_abandonment_rate_pct}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-4 p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
            <p>
              <b>Chẩn đoán quan trọng:</b> Tỷ lệ bỏ giỏ trên Mobile (<b>&gt;84%</b>) cao vượt trội so với Desktop (<b>64.9%</b>). Cần tập trung cải thiện giao diện thanh toán mobile tại Chương 5 Báo cáo.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
