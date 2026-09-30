import React, { useState, useEffect } from 'react';
import { Sidebar, TabType } from './components/Sidebar';
import { Header } from './components/Header';
import { OverviewView } from './components/OverviewView';
import { FunnelView } from './components/FunnelView';
import { PersonasView } from './components/PersonasView';
import { MarketBasketView } from './components/MarketBasketView';
import { InsightsView } from './components/InsightsView';
import { analyticsApi } from './services/api';
import { 
  OverviewData, 
  FunnelData, 
  PersonasData, 
  UserDetail, 
  MarketBasketData, 
  InsightsData 
} from './types/analytics';

export function App() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [overviewData, setOverviewData] = useState<OverviewData | null>(null);
  const [funnelData, setFunnelData] = useState<FunnelData | null>(null);
  const [personasData, setPersonasData] = useState<PersonasData | null>(null);
  const [sampleUsers, setSampleUsers] = useState<UserDetail[]>([]);
  const [basketData, setBasketData] = useState<MarketBasketData | null>(null);
  const [insightsData, setInsightsData] = useState<InsightsData | null>(null);

  const loadAllData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [overview, funnel, personas, users, basket, insights] = await Promise.all([
        analyticsApi.getOverview(),
        analyticsApi.getFunnel('all'),
        analyticsApi.getPersonas(),
        analyticsApi.getUsersSample(50),
        analyticsApi.getMarketBasket(),
        analyticsApi.getInsights(),
      ]);

      setOverviewData(overview);
      setFunnelData(funnel);
      setPersonasData(personas);
      setSampleUsers(users);
      setBasketData(basket);
      setInsightsData(insights);
    } catch (err: any) {
      console.error('Error fetching analytics data:', err);
      setError(err.message || 'Không thể kết nối đến Backend API. Vui lòng đảm bảo backend FastAPI đang chạy.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  return (
    <div className="flex min-h-screen bg-[#0b0f19] text-slate-100">
      {/* Left Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header onRefresh={loadAllData} isLoading={isLoading} />

        <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto overflow-y-auto">
          {error && (
            <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between">
              <span>⚠️ {error}</span>
              <button 
                onClick={loadAllData}
                className="px-3 py-1 rounded bg-rose-600 hover:bg-rose-500 text-white font-medium"
              >
                Thử lại
              </button>
            </div>
          )}

          {activeTab === 'overview' && (
            <OverviewView data={overviewData} isLoading={isLoading} />
          )}

          {activeTab === 'funnel' && (
            <FunnelView initialData={funnelData} />
          )}

          {activeTab === 'personas' && (
            <PersonasView data={personasData} sampleUsers={sampleUsers} />
          )}

          {activeTab === 'basket' && (
            <MarketBasketView data={basketData} />
          )}

          {activeTab === 'insights' && (
            <InsightsView data={insightsData} />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
