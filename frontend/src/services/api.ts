import {
  OverviewData,
  FunnelData,
  PersonasData,
  UserDetail,
  MarketBasketData,
  InsightsData
} from '../types/analytics';

const API_BASE = 'http://127.0.0.1:8000/api';

export const analyticsApi = {
  async getOverview(): Promise<OverviewData> {
    const res = await fetch(`${API_BASE}/overview`);
    if (!res.ok) throw new Error('Failed to fetch overview metrics');
    return res.json();
  },

  async getFunnel(device: string = 'all'): Promise<FunnelData> {
    const res = await fetch(`${API_BASE}/funnel?device=${device}`);
    if (!res.ok) throw new Error('Failed to fetch funnel data');
    return res.json();
  },

  async getPersonas(): Promise<PersonasData> {
    const res = await fetch(`${API_BASE}/personas`);
    if (!res.ok) throw new Error('Failed to fetch personas data');
    return res.json();
  },

  async getUsersSample(limit: number = 50): Promise<UserDetail[]> {
    const res = await fetch(`${API_BASE}/users/sample?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch users sample');
    return res.json();
  },

  async getUserDetail(userId: string): Promise<UserDetail> {
    const res = await fetch(`${API_BASE}/user/${encodeURIComponent(userId)}`);
    if (!res.ok) throw new Error('User not found');
    return res.json();
  },

  async getMarketBasket(): Promise<MarketBasketData> {
    const res = await fetch(`${API_BASE}/basket`);
    if (!res.ok) throw new Error('Failed to fetch market basket data');
    return res.json();
  },

  async getInsights(): Promise<InsightsData> {
    const res = await fetch(`${API_BASE}/insights`);
    if (!res.ok) throw new Error('Failed to fetch actionable insights');
    return res.json();
  }
};
