"""
Streamlit Web Application for Price Elasticity Analysis
Interactive deployment of the price elasticity model
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from price_elasticity_model import PriceElasticityModel
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Price Elasticity Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'model' not in st.session_state:
    st.session_state.model = PriceElasticityModel()
    st.session_state.data_loaded = False
    st.session_state.analysis_done = False

# Title
st.markdown('<h1 class="main-header">📊 Price Elasticity Analysis Dashboard</h1>', 
            unsafe_allow_html=True)
st.markdown("---")

# Sidebar
st.sidebar.title("⚙️ Configuration")

# File upload
uploaded_file = st.sidebar.file_uploader(
    "Upload CSV File",
    type=['csv'],
    help="Upload your retail data CSV file"
)

# Configuration options
st.sidebar.subheader("Column Mapping")
price_col = st.sidebar.text_input("Price Column", value="Item_MRP")
sales_col = st.sidebar.text_input("Sales Column", value="Item_Outlet_Sales")
category_col = st.sidebar.text_input("Category Column", value="Item_Type")

min_observations = st.sidebar.slider(
    "Minimum Observations per Category",
    min_value=5,
    max_value=50,
    value=10,
    help="Minimum number of products required per category for analysis"
)

# Main content
if uploaded_file is not None:
    # Load data
    if not st.session_state.data_loaded:
        with st.spinner("Loading and preprocessing data..."):
            try:
                load_info = st.session_state.model.load_data(
                    uploaded_file,
                    price_col=price_col,
                    sales_col=sales_col,
                    category_col=category_col
                )
                st.session_state.data_loaded = True
                st.success(f"✅ Data loaded successfully! ({load_info['cleaned_size']:,} records)")
            except Exception as e:
                st.error(f"Error loading data: {str(e)}")
                st.stop()
    
    # Run analysis
    if st.session_state.data_loaded and not st.session_state.analysis_done:
        if st.button("🚀 Run Price Elasticity Analysis", type="primary"):
            with st.spinner("Calculating price elasticity by category..."):
                try:
                    results = st.session_state.model.calculate_elasticity(
                        min_observations=min_observations
                    )
                    st.session_state.analysis_done = True
                    st.success("✅ Analysis complete!")
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
                    st.stop()
    
    # Display results
    if st.session_state.analysis_done:
        # Summary metrics
        summary = st.session_state.model.get_summary_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Categories", summary['total_categories'])
        
        with col2:
            st.metric(
                "Inelastic Categories",
                summary['inelastic_categories'],
                help="Categories where price can be increased"
            )
        
        with col3:
            st.metric(
                "Average Elasticity",
                f"{summary['avg_elasticity']:.3f}"
            )
        
        with col4:
            st.metric(
                "Significant Results",
                f"{summary['significant_results']}/{summary['total_categories']}"
            )
        
        st.markdown("---")
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Overview", 
            "💰 Pricing Opportunities", 
            "🎯 Price Simulation",
            "📊 Detailed Results"
        ])
        
        with tab1:
            st.subheader("Price Elasticity by Category")
            
            # Get results
            results = st.session_state.model.elasticity_results.copy()
            
            # Color coding
            results['color'] = results['elasticity'].apply(
                lambda x: '#27ae60' if x < 1 else '#e74c3c'
            )
            
            # Visualization
            fig, ax = plt.subplots(figsize=(12, 8))
            colors = ['#27ae60' if x < 1 else '#e74c3c' for x in results['elasticity']]
            
            bars = ax.barh(results['category'], results['elasticity'], color=colors, alpha=0.8)
            ax.axvline(x=1, color='black', linestyle='--', linewidth=2, label='Unit Elastic (E = 1)')
            ax.set_xlabel('Price Elasticity Coefficient', fontsize=12, fontweight='bold')
            ax.set_ylabel('Product Category', fontsize=12, fontweight='bold')
            ax.set_title('Price Elasticity by Product Category\nGreen = Price Increase Opportunity | Red = Price Sensitive',
                        fontsize=14, fontweight='bold', pad=20)
            ax.legend()
            ax.grid(True, alpha=0.3, axis='x')
            plt.tight_layout()
            
            st.pyplot(fig)
            
            # Demand type distribution
            st.subheader("Demand Type Distribution")
            col1, col2 = st.columns(2)
            
            with col1:
                demand_counts = results['demand_type'].value_counts()
                fig2, ax2 = plt.subplots(figsize=(8, 6))
                ax2.pie(demand_counts.values, labels=demand_counts.index, autopct='%1.1f%%',
                       startangle=90, textprops={'fontsize': 10})
                ax2.set_title('Demand Classification Distribution', fontweight='bold')
                st.pyplot(fig2)
            
            with col2:
                simple_counts = results['can_increase_price'].value_counts()
                fig3, ax3 = plt.subplots(figsize=(8, 6))
                colors_pie = ['#27ae60', '#e74c3c']
                ax3.pie(simple_counts.values, labels=simple_counts.index, 
                       autopct='%1.1f%%', colors=colors_pie, startangle=90,
                       textprops={'fontsize': 10, 'fontweight': 'bold'})
                ax3.set_title('Price Increase Opportunity', fontweight='bold')
                st.pyplot(fig3)
        
        with tab2:
            st.subheader("💰 Pricing Opportunities (Inelastic Categories)")
            st.info("These categories show inelastic demand - customers will continue buying even with moderate price increases (5-10%)")
            
            inelastic = st.session_state.model.get_inelastic_categories()
            
            if len(inelastic) > 0:
                # Display table
                display_cols = ['category', 'elasticity', 'avg_price', 'total_sales', 'num_products']
                st.dataframe(
                    inelastic[display_cols].style.format({
                        'elasticity': '{:.3f}',
                        'avg_price': '₹{:.2f}',
                        'total_sales': '₹{:,.2f}'
                    }),
                    use_container_width=True
                )
                
                # Top opportunity
                top_opp = inelastic.iloc[0]
                st.success(f"""
                **🎯 Top Opportunity: {top_opp['category']}**
                - Elasticity: {top_opp['elasticity']:.3f} (highly inelastic)
                - Average Price: ₹{top_opp['avg_price']:.2f}
                - Total Sales: ₹{top_opp['total_sales']:,.2f}
                """)
            else:
                st.warning("No inelastic categories found in the dataset.")
        
        with tab3:
            st.subheader("🎯 Price Change Simulation")
            st.info("Simulate the revenue impact of price changes for specific categories")
            
            results = st.session_state.model.elasticity_results
            categories = results['category'].tolist()
            
            col1, col2 = st.columns(2)
            
            with col1:
                selected_category = st.selectbox(
                    "Select Category",
                    categories
                )
            
            with col2:
                price_change = st.slider(
                    "Price Change (%)",
                    min_value=-20.0,
                    max_value=20.0,
                    value=5.0,
                    step=0.5,
                    help="Positive = price increase, Negative = price decrease"
                )
            
            if st.button("Run Simulation"):
                simulation = st.session_state.model.simulate_price_change(
                    selected_category,
                    price_change_pct=price_change / 100
                )
                
                if simulation:
                    st.subheader(f"Simulation Results: {simulation['category']}")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Current Price",
                            f"₹{simulation['current_price']:.2f}"
                        )
                    
                    with col2:
                        st.metric(
                            "New Price",
                            f"₹{simulation['new_price']:.2f}",
                            delta=f"{simulation['price_change_pct']:+.1f}%"
                        )
                    
                    with col3:
                        st.metric(
                            "Expected Qty Change",
                            f"{simulation['quantity_change_pct']:+.2f}%"
                        )
                    
                    with col4:
                        st.metric(
                            "Revenue Impact",
                            f"₹{simulation['estimated_revenue_impact']:+,.2f}",
                            delta=f"{simulation['revenue_change_pct']:+.2f}%"
                        )
                    
                    # Interpretation
                    if simulation['revenue_change_pct'] > 0:
                        st.success("✅ Price change likely to improve revenue")
                    else:
                        st.warning("⚠️ Revenue may decrease with this price change")
        
        with tab4:
            st.subheader("📊 Detailed Results")
            
            # Full results table
            results = st.session_state.model.elasticity_results.copy()
            
            # Format for display
            display_results = results[[
                'category', 'elasticity', 'p_value', 'r_squared',
                'avg_price', 'total_sales', 'num_products', 'demand_type'
            ]].copy()
            
            st.dataframe(
                display_results.style.format({
                    'elasticity': '{:.4f}',
                    'p_value': '{:.4f}',
                    'r_squared': '{:.3f}',
                    'avg_price': '₹{:.2f}',
                    'total_sales': '₹{:,.2f}'
                }),
                use_container_width=True,
                height=400
            )
            
            # Download button
            csv = results.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name="price_elasticity_results.csv",
                mime="text/csv"
            )
            
            # Correlation
            correlation = st.session_state.model.get_correlation()
            st.metric("Overall Price-Sales Correlation", f"{correlation:.3f}")

else:
    # Welcome screen
    st.info("👈 Please upload a CSV file in the sidebar to begin analysis")
    
    st.markdown("""
    ### 📋 Expected CSV Format
    
    Your CSV file should contain the following columns:
    - **Price Column**: Product prices (e.g., `Item_MRP`)
    - **Sales Column**: Sales volumes (e.g., `Item_Outlet_Sales`)
    - **Category Column**: Product categories (e.g., `Item_Type`)
    
    ### 🔍 What This Tool Does
    
    1. **Calculates Price Elasticity** for each product category using econometric methods
    2. **Identifies Pricing Opportunities** where prices can be increased without losing customers
    3. **Simulates Revenue Impact** of price changes
    4. **Provides Business Insights** for strategic pricing decisions
    
    ### 📊 Methodology
    
    Uses **log-log OLS regression** to estimate price elasticity:
    - `log(Sales) = β₀ + β₁ × log(Price)`
    - The coefficient β₁ directly represents elasticity
    - **Elasticity < 1**: Inelastic (can increase price)
    - **Elasticity > 1**: Elastic (price-sensitive)
    """)

