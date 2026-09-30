export interface OverviewKPIs {
  total_users: number;
  total_sessions: number;
  total_pageviews: number;
  total_transactions: number;
  total_revenue: number;
  conversion_rate_pct: number;
  average_order_value_usd: number;
}

export interface TrafficChannel {
  traffic_medium: string;
  total_users: number;
  total_sessions: number;
  total_pageviews: number;
  total_transactions: number;
  total_revenue: number;
  conversion_rate: number;
}

export interface OverviewData {
  kpis: OverviewKPIs;
  traffic_channels: TrafficChannel[];
}

export interface FunnelStep {
  step_number: number;
  name: string;
  users: number;
  pct_of_step_1: number;
  drop_off_pct: number;
}

export interface FunnelMetrics {
  overall_conversion_rate_pct: number;
  cart_abandonment_rate_pct: number;
  step1_to_step2_cr: number;
  step2_to_step3_cr: number;
  step3_to_step4_cr: number;
}

export interface FunnelDeviceBreakdown {
  device_category: string;
  step_1_view_item_users: number;
  step_2_add_to_cart_users: number;
  step_3_begin_checkout_users: number;
  step_4_purchase_users: number;
  overall_conversion_rate_pct: number;
  cart_abandonment_rate_pct: number;
}

export interface FunnelData {
  device_filter: string;
  steps: FunnelStep[];
  metrics: FunnelMetrics;
  devices_breakdown: FunnelDeviceBreakdown[];
}

export interface PersonaProfile {
  "Cluster ID": number;
  "Chân dung Khách hàng (Persona)": string;
  "Số lượng Users": string;
  "Recency TB (ngày)": number;
  "Sessions TB": number;
  "Doanh thu TB ($)": number;
  "Thời gian Tương tác TB (s)": number;
  "Số SP Xem TB": number;
  "Số SP Thêm Giỏ TB": number;
  "Tỷ lệ Giỏ/Xem": number;
  "Đơn hàng TB": number;
  "Hành vi Nổi bật": string;
}

export interface PcaScatterPoint {
  user_pseudo_id: string;
  persona_name: string;
  persona_color: string;
  cluster_id: number;
  pca_2d_x: number;
  pca_2d_y: number;
  pca_3d_x: number;
  pca_3d_y: number;
  pca_3d_z: number;
  recency_days: number;
  total_sessions: number;
  monetary_value: number;
  total_engagement_sec: number;
  cart_to_view_ratio: number;
  purchase_count: number;
  primary_device: string;
}

export interface PersonasData {
  personas_summary: PersonaProfile[];
  cluster_evaluation: {
    silhouette_score: number;
    k_values: number[];
    inertias: number[];
    silhouette_scores: number[];
    pca_explained_variance_2d: number[];
    pca_explained_variance_3d: number[];
  };
  pca_scatter_points: PcaScatterPoint[];
}

export interface UserDetail {
  user_pseudo_id: string;
  persona_name: string;
  recency_days: number;
  total_sessions: number;
  monetary_value: number;
  total_engagement_sec: number;
  items_viewed_count: number;
  items_added_to_cart_count: number;
  cart_to_view_ratio: number;
  purchase_count: number;
  primary_device: string;
  primary_channel: string;
}

export interface CrossSellingRecommendation {
  "Sản phẩm Đã mua (A)": string;
  "Sản phẩm Gợi ý Mua kèm (B)": string;
  "Độ phổ biến (Support)": string;
  "Xác suất mua kèm (Confidence)": string;
  "Hệ số Tương quan (Lift)": string;
  "Ý nghĩa Kinh doanh": string;
}

export interface AssociationRule {
  antecedents_str: string;
  consequents_str: string;
  antecedent_support: number;
  consequent_support: number;
  support: number;
  confidence: number;
  lift: number;
}

export interface MarketBasketData {
  cross_selling_recommendations: CrossSellingRecommendation[];
  top_rules: AssociationRule[];
}

export interface CroStrategy {
  title: string;
  description: string;
  impact: string;
  priority: string;
}

export interface PersonaStrategy {
  persona: string;
  badge: string;
  actions: string[];
}

export interface InsightsData {
  cro_strategies: CroStrategy[];
  persona_strategies: PersonaStrategy[];
}
