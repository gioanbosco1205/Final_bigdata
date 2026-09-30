"""
Market Basket Analysis Module: Transaction One-Hot Matrix Encoding,
Apriori Frequent Itemsets Mining, and Association Rules Generation (Support, Confidence, Lift).
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from itertools import combinations
import numpy as np
import pandas as pd

# Add parent directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))


class MarketBasketAnalyzer:
    """
    Implements Market Basket Analysis / Association Rule Mining:
    1. Converts transaction item list into a clean Order-by-Product One-Hot binary matrix.
    2. Mines Frequent Itemsets using the Apriori algorithm with min_support threshold.
    3. Derives Association Rules (A => B) prioritizing Lift > 1.0 for Cross-selling recommendations.
    Built with pure NumPy/Pandas matrix algebra for high-speed standalone execution.
    """

    def __init__(self, min_support: float = 0.04, min_confidence: float = 0.20, min_lift: float = 1.0):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.min_lift = min_lift
        self.frequent_itemsets: pd.DataFrame = pd.DataFrame()
        self.rules: pd.DataFrame = pd.DataFrame()

    def build_basket_matrix(
        self, 
        df_transactions: pd.DataFrame, 
        min_item_frequency: int = 5
    ) -> Tuple[pd.DataFrame, int]:
        """
        Transforms flat transaction records into a One-Hot Matrix:
        - Rows: Distinct transaction_id.
        - Columns: Distinct item_name.
        - Values: 1 if item was purchased in transaction, 0 otherwise.
        - Filters out rare items (< min_item_frequency) to optimize memory and computation.
        """
        # Ensure distinct item per transaction (no item duplication within same order)
        df_unique = df_transactions[["transaction_id", "item_name"]].drop_duplicates()
        
        # Filter rare items to prevent matrix explosion
        item_counts = df_unique["item_name"].value_counts()
        frequent_items = item_counts[item_counts >= min_item_frequency].index
        df_filtered = df_unique[df_unique["item_name"].isin(frequent_items)].copy()
        
        # Filter transactions with at least 2 distinct frequent items
        tx_item_counts = df_filtered.groupby("transaction_id")["item_name"].count()
        valid_tx_ids = tx_item_counts[tx_item_counts >= 2].index
        df_valid = df_filtered[df_filtered["transaction_id"].isin(valid_tx_ids)]
        
        # Pivot into One-Hot Matrix (Row = transaction_id, Col = item_name)
        basket_matrix = (
            df_valid.groupby(["transaction_id", "item_name"])["item_name"]
            .count()
            .unstack()
            .fillna(0)
        )
        
        # Convert to binary (1/0)
        basket_one_hot = (basket_matrix > 0).astype(int)
        
        total_valid_orders = len(basket_one_hot)
        print(f"✓ One-Hot Basket Matrix constructed:")
        print(f"  • Total Multi-Item Orders (Rows): {total_valid_orders:,}")
        print(f"  • Distinct Active Products (Cols): {basket_one_hot.shape[1]}")
        return basket_one_hot, total_valid_orders

    def run_apriori_and_rules(
        self, 
        basket_one_hot: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Standalone Apriori Algorithm:
        Computes 1-itemsets and 2-itemsets with matrix operations,
        deriving Support, Confidence, and Lift metrics.
        """
        n_orders = len(basket_one_hot)
        if n_orders == 0:
            return pd.DataFrame(), pd.DataFrame()

        items = list(basket_one_hot.columns)
        item_matrix = basket_one_hot.values  # (N, M)
        
        # 1. Compute 1-itemset Support
        item_counts = item_matrix.sum(axis=0)
        item_supports = item_counts / n_orders
        
        frequent_1 = []
        for idx, item in enumerate(items):
            supp = item_supports[idx]
            if supp >= self.min_support:
                frequent_1.append({"itemsets": frozenset([item]), "support": supp, "length": 1})
                
        # 2. Compute 2-itemset Support via Boolean Matrix Multiplication
        frequent_2 = []
        rules_list = []
        
        for (i1, item1), (i2, item2) in combinations(enumerate(items), 2):
            # Co-occurrence count
            both_count = np.sum((item_matrix[:, i1] == 1) & (item_matrix[:, i2] == 1))
            support_both = both_count / n_orders
            
            if support_both >= self.min_support:
                frequent_2.append({
                    "itemsets": frozenset([item1, item2]),
                    "support": support_both,
                    "length": 2
                })
                
                # Rule 1: item1 => item2
                supp_1 = item_supports[i1]
                supp_2 = item_supports[i2]
                
                conf_1_to_2 = support_both / supp_1 if supp_1 > 0 else 0
                lift_1_to_2 = conf_1_to_2 / supp_2 if supp_2 > 0 else 0
                
                if conf_1_to_2 >= self.min_confidence and lift_1_to_2 > self.min_lift:
                    rules_list.append({
                        "antecedents_str": item1,
                        "consequents_str": item2,
                        "antecedent_support": round(supp_1, 4),
                        "consequent_support": round(supp_2, 4),
                        "support": round(support_both, 4),
                        "confidence": round(conf_1_to_2, 4),
                        "lift": round(lift_1_to_2, 3)
                    })
                    
                # Rule 2: item2 => item1
                conf_2_to_1 = support_both / supp_2 if supp_2 > 0 else 0
                lift_2_to_1 = conf_2_to_1 / supp_1 if supp_1 > 0 else 0
                
                if conf_2_to_1 >= self.min_confidence and lift_2_to_1 > self.min_lift:
                    rules_list.append({
                        "antecedents_str": item2,
                        "consequents_str": item1,
                        "antecedent_support": round(supp_2, 4),
                        "consequent_support": round(supp_1, 4),
                        "support": round(support_both, 4),
                        "confidence": round(conf_2_to_1, 4),
                        "lift": round(lift_2_to_1, 3)
                    })

        self.frequent_itemsets = pd.DataFrame(frequent_1 + frequent_2).sort_values(by="support", ascending=False)
        self.rules = pd.DataFrame(rules_list)
        if not self.rules.empty:
            self.rules = self.rules.sort_values(by=["lift", "confidence"], ascending=[False, False])

        print(f"✓ Apriori & Association Mining Completed:")
        print(f"  • Frequent Itemsets found: {len(self.frequent_itemsets)}")
        print(f"  • High-Lift Association Rules (Lift > {self.min_lift}): {len(self.rules)}")
        return self.frequent_itemsets, self.rules

    def get_cross_selling_recommendations(self, top_n: int = 5) -> pd.DataFrame:
        """
        Generates clean, actionable cross-selling recommendations table for report & UI.
        """
        if self.rules.empty:
            return pd.DataFrame(columns=["Sản phẩm Đã mua (A)", "Sản phẩm Gợi ý Mua kèm (B)", "Độ phổ biến (Support)", "Xác suất mua kèm (Confidence)", "Hệ số Tương quan (Lift)", "Ý nghĩa Kinh doanh"])

        rec_list = []
        for _, row in self.rules.head(top_n).iterrows():
            lift_val = row["lift"]
            conf_pct = round(row["confidence"] * 100, 1)
            supp_pct = round(row["support"] * 100, 1)
            
            meaning = f"Khách mua [{row['antecedents_str']}] có xác suất {conf_pct}% sẽ mua kèm [{row['consequents_str']}] (Cao gấp {lift_val}x so với mua ngẫu nhiên)."
            
            rec_list.append({
                "Sản phẩm Đã mua (A)": row["antecedents_str"],
                "Sản phẩm Gợi ý Mua kèm (B)": row["consequents_str"],
                "Độ phổ biến (Support)": f"{supp_pct}%",
                "Xác suất mua kèm (Confidence)": f"{conf_pct}%",
                "Hệ số Tương quan (Lift)": f"{lift_val}x",
                "Ý nghĩa Kinh doanh": meaning
            })
        return pd.DataFrame(rec_list)


if __name__ == "__main__":
    from src.bq_client import BigQueryService
    
    print("Testing MarketBasketAnalyzer on GA4 Transactions...")
    bq = BigQueryService()
    df_tx = bq.query_to_dataframe("SELECT 1", cache_name="market_basket")
    
    analyzer = MarketBasketAnalyzer(min_support=0.04, min_confidence=0.25, min_lift=1.0)
    basket_matrix, total_orders = analyzer.build_basket_matrix(df_tx)
    frequent_sets, rules = analyzer.run_apriori_and_rules(basket_matrix)
    
    df_recs = analyzer.get_cross_selling_recommendations(top_n=5)
    print("\n" + "="*80)
    print("=== BẢNG GỢI Ý COMBO BÁN CHÉO (CROSS-SELLING RECOMMENDATIONS) ===")
    print("="*80)
    print(df_recs.to_string(index=False))
