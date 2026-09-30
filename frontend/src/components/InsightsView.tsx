import React from 'react';
import { Lightbulb, Target, ArrowUpRight, Zap, CheckCircle2, ShieldCheck, Award } from 'lucide-react';
import { InsightsData } from '../types/analytics';

interface InsightsViewProps {
  data: InsightsData | null;
}

export const InsightsView: React.FC<InsightsViewProps> = ({ data }) => {
  if (!data) {
    return <div className="text-center py-20 text-slate-400">Đang nạp đề xuất chiến lược...</div>;
  }

  const { cro_strategies, persona_strategies } = data;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <Lightbulb className="w-4 h-4" />
            <span>Chương 5: Đề xuất Chiến lược Kinh doanh Thực tiễn</span>
          </div>
          <h2 className="text-xl font-bold text-slate-100">
            Kế hoạch Tối ưu Chuyển đổi (CRO) & Tiếp thị Cá nhân hóa Phân khúc
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Chuyển hóa toàn bộ kết quả phân tích SQL & Machine Learning thành giải pháp tăng trưởng doanh thu.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-emerald-500/10 px-3 py-2 rounded-xl border border-emerald-500/20 text-xs font-bold text-emerald-400">
          <Award className="w-4 h-4" />
          <span>Actionable Business Impact</span>
        </div>
      </div>

      {/* CRO Strategies Section */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800">
        <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
          <Zap className="w-4 h-4 text-amber-400" />
          <span>1. Chiến lược Tối ưu hóa Tỷ lệ Chuyển đổi Phễu (Funnel CRO Optimization)</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {cro_strategies.map((strat, i) => (
            <div
              key={i}
              className="p-5 rounded-2xl glass-card border border-amber-500/20 bg-amber-500/5 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">
                    PRIORITY: {strat.priority}
                  </span>
                  <span className="text-xs font-semibold text-emerald-400">
                    {strat.impact}
                  </span>
                </div>

                <h4 className="text-base font-bold text-slate-100 mb-2">
                  {strat.title}
                </h4>
                <p className="text-xs text-slate-300 leading-relaxed mb-4">
                  {strat.description}
                </p>
              </div>

              <div className="flex items-center gap-2 text-xs text-blue-400 pt-3 border-t border-slate-700/40">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Căn cứ trực tiếp từ tỷ lệ Drop-off Phễu SQL Task 2.2</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Segment-specific Marketing Strategies */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800">
        <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
          <Target className="w-4 h-4 text-blue-400" />
          <span>2. Chiến lược Tiếp thị Định hướng Phân khúc Khách hàng (Segment-Targeted Marketing)</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {persona_strategies.map((ps, i) => (
            <div
              key={i}
              className="p-5 rounded-2xl glass-card border border-slate-700/80 bg-slate-800/40 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-base font-bold text-slate-100">
                    {ps.persona}
                  </h4>
                  <span className="text-xs font-semibold px-2 py-0.5 rounded-md bg-blue-500/20 text-blue-300 border border-blue-500/30">
                    {ps.badge}
                  </span>
                </div>

                <ul className="space-y-2 my-4">
                  {ps.actions.map((act, j) => (
                    <li key={j} className="flex items-start gap-2 text-xs text-slate-300 leading-relaxed">
                      <span className="text-emerald-400 mt-0.5">✓</span>
                      <span>{act}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="pt-3 border-t border-slate-700/40 text-[11px] text-slate-400">
                Gắn nhãn Persona tự động từ mô hình K-Means Task 3.3
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
