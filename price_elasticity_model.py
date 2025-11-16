"""
Price Elasticity Analysis Model
Core module for calculating price elasticity of demand by product category
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')


class PriceElasticityModel:
    """Price Elasticity Analysis Model using log-log OLS regression"""
    
    def __init__(self):
        self.elasticity_results = None
        self.df = None
        
    def load_data(self, filepath, price_col='Item_MRP', sales_col='Item_Outlet_Sales', 
                  category_col='Item_Type'):
        """
        Load and preprocess retail data
        
        Parameters:
        -----------
        filepath : str
            Path to CSV file
        price_col : str
            Column name for price
        sales_col : str
            Column name for sales
        category_col : str
            Column name for product category
        """
        self.df = pd.read_csv(filepath)
        
        # Rename columns for clarity
        self.df = self.df.rename(columns={
            price_col: 'price',
            sales_col: 'sales',
            category_col: 'category'
        })
        
        # Clean data
        original_size = len(self.df)
        self.df = self.df.dropna(subset=['price', 'sales'])
        self.df = self.df[(self.df['price'] > 0) & (self.df['sales'] > 0)]
        
        removed_records = original_size - len(self.df)
        
        return {
            'original_size': original_size,
            'cleaned_size': len(self.df),
            'removed_records': removed_records,
            'removal_pct': (removed_records / original_size * 100) if original_size > 0 else 0
        }
    
    def calculate_elasticity(self, min_observations=10):
        """
        Calculate price elasticity for each product category using log-log regression
        
        Parameters:
        -----------
        min_observations : int
            Minimum number of observations required per category
            
        Returns:
        --------
        pd.DataFrame: Elasticity results by category
        """
        elasticity_results = []
        
        for category in self.df['category'].unique():
            cat_data = self.df[self.df['category'] == category].copy()
            
            if len(cat_data) < min_observations:
                continue
            
            # Log-log transformation
            cat_data['log_price'] = np.log(cat_data['price'])
            cat_data['log_sales'] = np.log(cat_data['sales'])
            
            # Prepare regression
            X = sm.add_constant(cat_data['log_price'])
            y = cat_data['log_sales']
            
            try:
                model = sm.OLS(y, X).fit()
                elasticity = model.params['log_price']
                p_value = model.pvalues['log_price']
                r_squared = model.rsquared
                
                elasticity_results.append({
                    'category': category,
                    'elasticity': elasticity,
                    'p_value': p_value,
                    'r_squared': r_squared,
                    'avg_price': cat_data['price'].mean(),
                    'median_price': cat_data['price'].median(),
                    'total_sales': cat_data['sales'].sum(),
                    'num_products': len(cat_data)
                })
            except Exception as e:
                print(f"[ERROR] {category}: Regression failed - {str(e)}")
                continue
        
        self.elasticity_results = pd.DataFrame(elasticity_results)
        self.elasticity_results = self.elasticity_results.sort_values('elasticity', ascending=False)
        
        # Add classifications
        self.elasticity_results['demand_type'] = self.elasticity_results['elasticity'].apply(
            self._classify_demand
        )
        self.elasticity_results['can_increase_price'] = self.elasticity_results['elasticity'].apply(
            lambda x: 'No' if x > 1 else 'Yes'
        )
        
        return self.elasticity_results
    
    def _classify_demand(self, elasticity):
        """Classify demand elasticity"""
        abs_elasticity = abs(elasticity)
        if abs_elasticity < 0.5:
            return "Highly Inelastic"
        elif abs_elasticity < 1:
            return "Inelastic"
        elif abs_elasticity == 1:
            return "Unit Elastic"
        elif abs_elasticity > 1 and abs_elasticity < 1.5:
            return "Elastic"
        else:
            return "Highly Elastic"
    
    def get_inelastic_categories(self):
        """Get categories with inelastic demand (pricing opportunities)"""
        if self.elasticity_results is None:
            return pd.DataFrame()
        return self.elasticity_results[self.elasticity_results['elasticity'] < 1].sort_values(
            'avg_price', ascending=False
        )
    
    def get_elastic_categories(self):
        """Get categories with elastic demand (price-sensitive)"""
        if self.elasticity_results is None:
            return pd.DataFrame()
        return self.elasticity_results[self.elasticity_results['elasticity'] > 1].sort_values(
            'elasticity'
        )
    
    def simulate_price_change(self, category, price_change_pct=0.05):
        """
        Simulate revenue impact of price change for a category
        
        Parameters:
        -----------
        category : str
            Category name
        price_change_pct : float
            Percentage price change (0.05 = 5% increase)
            
        Returns:
        --------
        dict: Simulation results
        """
        if self.elasticity_results is None:
            return None
        
        category_data = self.elasticity_results[
            self.elasticity_results['category'] == category
        ]
        
        if len(category_data) == 0:
            return None
        
        row = category_data.iloc[0]
        elasticity = row['elasticity']
        
        # Calculate expected quantity change
        quantity_change = elasticity * price_change_pct
        
        # Calculate revenue change
        revenue_change = (1 + price_change_pct) * (1 + quantity_change) - 1
        
        # Estimated dollar impact
        estimated_revenue_impact = row['total_sales'] * revenue_change
        
        return {
            'category': category,
            'current_price': row['avg_price'],
            'new_price': row['avg_price'] * (1 + price_change_pct),
            'elasticity': elasticity,
            'price_change_pct': price_change_pct * 100,
            'quantity_change_pct': quantity_change * 100,
            'revenue_change_pct': revenue_change * 100,
            'estimated_revenue_impact': estimated_revenue_impact,
            'current_total_sales': row['total_sales']
        }
    
    def get_summary_stats(self):
        """Get summary statistics"""
        if self.elasticity_results is None:
            return None
        
        inelastic_count = (self.elasticity_results['elasticity'] < 1).sum()
        total_count = len(self.elasticity_results)
        
        return {
            'total_categories': total_count,
            'inelastic_categories': inelastic_count,
            'elastic_categories': total_count - inelastic_count,
            'inelastic_pct': (inelastic_count / total_count * 100) if total_count > 0 else 0,
            'avg_elasticity': self.elasticity_results['elasticity'].mean(),
            'significant_results': (self.elasticity_results['p_value'] < 0.05).sum(),
            'avg_r_squared': self.elasticity_results['r_squared'].mean()
        }
    
    def get_correlation(self):
        """Get overall price-sales correlation"""
        if self.df is None:
            return None
        return self.df['price'].corr(self.df['sales'])

