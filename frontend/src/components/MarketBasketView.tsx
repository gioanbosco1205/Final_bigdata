import React from 'react';
import { ShoppingBag, ArrowRight, TrendingUp, Sparkles, CheckCircle2, Tag } from 'lucide-react';
import { MarketBasketData } from '../types/analytics';

interface MarketBasketViewProps {
  data: MarketBasketData | null;
}

export const MarketBasketView: React.FC<MarketBasketViewProps> = ({ data }) => {
  if (!data) {
    return <div className="text-center py-20 text-slate-400">Đang nạp luật kết hợp giỏ hàng...</div>;
  }

  const { cross_selling_recommendations, top_rules } = data;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <ShoppingBag className="w-4 h-4" />
            <span>Khai phá Dữ liệu Đơn hàng (Market Basket Analysis & Apriori)</span>
          </div>
          <h2 className="text-xl font-bold text-slate-100">
            Luật Kết hợp Sản phẩm & Đề xuất Bán chéo (Cross-Selling)
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Phân tích các cặp sản phẩm xuất hiện cùng nhau trong đơn hàng mua thành công (Lift &gt; 1.0).
          </p>
        </div>

        <div className="flex items-center gap-2 bg-slate-900/80 px-3 py-2 rounded-xl border border-slate-800 text-xs font-medium text-emerald-400">
          <Sparkles className="w-4 h-4" />
          <span>Apriori Mining Engine Active</span>
        </div>
      </div>

      {/* 3 Metrics Explanation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-2xl glass-card border border-slate-800">
          <div className="text-xs font-bold text-blue-400 uppercase tracking-wider mb-1">
            1. ĐỘ PHỔ BIẾN (SUPPORT)
          </div>
          <div className="text-xs text-slate-300 leading-relaxed">
            Tỷ lệ đơn hàng chứa cả 2 sản phẩm A và B trên toàn bộ số đơn hàng. Đo lường quy mô thị trường của combo.
          </div>
        </div>

        <div className="p-4 rounded-2xl glass-card border border-slate-800">
          <div className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-1">
            2. XÁC SUẤT MUA KÈM (CONFIDENCE)
          </div>
          <div className="text-xs text-slate-300 leading-relaxed">
            Xác suất khách hàng sẽ mua sản phẩm B sau khi đã bỏ sản phẩm A vào giỏ hàng: P(B | A).
          </div>
        </div>

        <div className="p-4 rounded-2xl glass-card border border-emerald-500/20 bg-emerald-500/5">
          <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-1">
            3. HỆ SỐ TƯƠNG QUAN (LIFT &gt; 1.0)
          </div>
          <div className="text-xs text-slate-300 leading-relaxed">
            Mức độ liên kết thực sự giữa A và B. Lift &gt; 1 chứng tỏ 2 sản phẩm kích thích mua kèm lẫn nhau nhiều hơn ngẫu nhiên.
          </div>
        </div>
      </div>

      {/* Top Cross-selling Recommendations Grid */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800">
        <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center justify-between">
          <span>Top Gợi ý Combo Bán chéo Hiệu quả nhất (Cross-Selling Rules)</span>
          <span className="text-xs text-emerald-400 font-semibold">Ưu tiên Lift cao nhất</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {cross_selling_recommendations.slice(0, 6).map((rec, i) => (
            <div
              key={i}
              className="p-5 rounded-2xl glass-card border border-slate-700/60 bg-slate-800/40 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-blue-500/20 text-blue-300 border border-blue-500/30">
                    COMBO #{i + 1}
                  </span>
                  <span className="text-xs font-extrabold px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                    Lift: {rec['Hệ số Tương quan (Lift)']}
                  </span>
                </div>

                {/* Product Pair Flow */}
                <div className="space-y-2 mb-4">
                  <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-200 font-medium">
                    <span className="text-slate-400 text-[10px] block font-semibold uppercase">Sản phẩm khách đã chọn:</span>
                    📦 {rec['Sản phẩm Đã mua (A)']}
                  </div>
                  <div className="flex justify-center text-blue-400">
                    <ArrowRight className="w-4 h-4 rotate-90 md:rotate-0" />
                  </div>
                  <div className="p-2.5 rounded-xl bg-emerald-950/30 border border-emerald-500/30 text-xs text-emerald-200 font-semibold">
                    <span className="text-emerald-400 text-[10px] block font-semibold uppercase">Gợi ý mua kèm tại Checkout:</span>
                    🎁 {rec['Sản phẩm Gợi ý Mua kèm (B)']}
                  </div>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed mb-3">
                  {rec['Ý nghĩa Kinh doanh']}
                </p>
              </div>

              {/* Badges */}
              <div className="flex items-center justify-between pt-3 border-t border-slate-700/40 text-xs text-slate-400">
                <span>Support: <b>{rec['Độ phổ biến (Support)']}</b></span>
                <span>Confidence: <b className="text-slate-200">{rec['Xác suất mua kèm (Confidence)']}</b></span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
