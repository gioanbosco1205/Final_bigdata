"""Explicit synthetic query-result fixtures, never production dataset exports."""
import pandas as pd


def install_notebook_fixtures():
    import google.auth
    from google.auth.credentials import AnonymousCredentials
    from google.cloud import bigquery
    from unittest.mock import patch

    rows = []
    for i in range(6000):
        profile, variation = i % 4, (i // 4) % 15
        views = [30, 12, 3, 18][profile] + variation
        carts = [8, 2, 0, 12][profile] + (variation % 3 if profile != 2 else 0)
        purchases = [3, 1, 0, 0][profile]
        rows.append({
            'user_pseudo_id': f'fixture-user-{i}',
            'recency_days': [2, 15, 70, 8][profile] + variation,
            'frequency_sessions': [12, 5, 1, 8][profile] + variation % 3,
            'monetary_usd': float([800, 100, 0, 0][profile] + (variation * 20 if purchases else 0)),
            'view_item_count': views, 'add_to_cart_count': carts,
            'checkout_count': [6, 2, 0, 3][profile], 'purchase_count': purchases,
            'cart_to_view_ratio': carts / views,
            'total_engagement_time_sec': float([2400, 900, 30, 1600][profile] + variation * 10),
            'total_pageviews': [80, 30, 5, 60][profile] + variation,
        })
    rfm = pd.DataFrame(rows).convert_dtypes()
    sessions, revenue = int(rfm.frequency_sessions.sum()), float(rfm.monetary_usd.sum())
    orders, pages = int(rfm.purchase_count.sum()), int(rfm.total_pageviews.sum())
    eda = pd.DataFrame([
        ['overall', None, None, None, 6000, sessions, pages, orders, revenue],
        ['channel', 'organic', None, None, 3500, sessions // 2, pages // 2, orders // 2, revenue / 2],
        ['channel', 'direct', None, None, 2500, sessions - sessions // 2, pages - pages // 2,
         orders - orders // 2, revenue / 2],
        ['device', None, 'desktop', None, 4000, sessions // 2, pages // 2, orders // 2, revenue / 2],
        ['device', None, 'mobile', None, 3000, sessions - sessions // 2, pages - pages // 2,
         orders - orders // 2, revenue / 2],
    ], columns=['aggregation_level', 'traffic_medium', 'device_category', 'country',
                'total_users', 'total_sessions', 'total_pageviews', 'total_purchases', 'total_revenue_usd'])
    funnel = pd.DataFrame([
        ['all', 6000, 4500, 3200, 1800], ['desktop', 4000, 3000, 2500, 1500],
        ['mobile', 3000, 1800, 800, 400], ['tablet', 0, 0, 0, 0],
    ], columns=['device_category', 'step1_view_item', 'step2_add_to_cart',
                'step3_begin_checkout', 'step4_purchase'])
    basket = pd.DataFrame([
        {'transaction_id': f'fixture-tx-{i}', 'item_name': item, 'event_timestamp': i + 1,
         'user_pseudo_id': f'fixture-user-{i}', 'item_id': item, 'price_in_usd': 10.0}
        for i in range(600) for item in (['A', 'B'] if i < 300 else ['C', 'D'])
    ])

    class FixtureJob:
        location, total_bytes_processed, cache_hit = 'US', 0, False

        def __init__(self, frame, index):
            self.frame, self.job_id = frame, f'SYNTHETIC-FIXTURE-NOT-BIGQUERY-{index}'

        def result(self):
            return self

        def to_dataframe(self, create_bqstorage_client=False):
            return self.frame.copy(deep=True)

    class FixtureClient:
        def __init__(self, **kwargs):
            self.frames, self.index = [eda, funnel, rfm, basket], 0

        def query(self, sql, **kwargs):
            self.index += 1
            if self.index > len(self.frames):
                raise AssertionError('Fixture provides exactly four query results')
            print('KIỂM THỬ: SQL không gửi tới BigQuery; trả về fixture tổng hợp đã định nghĩa.')
            return FixtureJob(self.frames[self.index - 1], self.index)

    patches = [patch.object(google.auth, 'default', return_value=(AnonymousCredentials(), 'test-fixture-project')),
               patch.object(bigquery, 'Client', FixtureClient)]
    for item in patches:
        item.start()
    import matplotlib.pyplot as plt
    real_show = plt.show

    def fixture_show(*args, **kwargs):
        for number in plt.get_fignums():
            plt.figure(number).text(0.5, -0.02,
                'DỮ LIỆU KIỂM THỬ TỔNG HỢP · KHÔNG PHẢI KẾT QUẢ GA4',
                ha='center', fontsize=9, color='#9F1239')
        return real_show(*args, **kwargs)

    plt.show = fixture_show
    print('CHẾ ĐỘ KIỂM THỬ: 6.000 user tổng hợp. Không dùng số liệu này trong báo cáo thực nghiệm GA4.')
    return patches
