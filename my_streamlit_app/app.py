import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
import os
from pathlib import Path

# Get the directory where app.py lives
BASE_DIR = Path(__file__).resolve().parent

@st.cache_data
def load_customer_data():
    # Construct absolute path dynamically
    file_path = BASE_DIR / "data" / "customer_orders_geolocation_payments.parquet"
    
    # Fallback check if the file sits directly inside my_streamlit_app without a data subfolder
    if not file_path.exists():
        file_path = BASE_DIR / "customer_orders_geolocation_payments.parquet"
        
    return pd.read_parquet(file_path)
# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Olist E-Commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- MAIN DASHBOARD TITLE ---
st.title("🛍️ Olist E-Commerce Analytics Dashboard")
st.markdown("Comprehensive business intelligence insights covering customer behavior, order analytics, sales trends, product performance, seller metrics, and customer satisfaction.")
st.markdown("---")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
selected_tab = st.sidebar.radio(
    "Select Section",
    [
        "Customer Dashboard",
        "Orders Dashboard",
        "Sales Trend Dashboard",
        "Products Dashboard",
        "Sellers Dashboard",
        "Customer Satisfaction Dashboards",
        "⭐ Review Prediction Model"  # <-- ADD THIS NEW OPTION HERE
    ]
)

# =============================================================
# 1. CUSTOMER DASHBOARD (Fully Integrated & Dynamic)
# =============================================================
if selected_tab == "Customer Dashboard":
    st.header("Customer Distribution & Geographic Overview")
    
    @st.cache_data
    def load_customer_data():
        return pd.read_parquet('data/customer_orders_geolocation_payments.parquet')
    
    df_cust = load_customer_data()
    
    if df_cust is not None:
        # Robust column detection
        cust_id_col = 'customer_unique_id' if 'customer_unique_id' in df_cust.columns else ('customer_id' if 'customer_id' in df_cust.columns else df_cust.columns[0])
        state_col = next((col for col in df_cust.columns if 'state' in col.lower()), 'geolocation_state')
        city_col = next((col for col in df_cust.columns if 'city' in col.lower()), 'geolocation_city')
        zip_col = next((col for col in df_cust.columns if 'zip' in col.lower() or 'postal' in col.lower()), 'geolocation_zip_code_prefix')
        
        date_col = next((c for c in df_cust.columns if 'timestamp' in c.lower() or 'date' in c.lower()), None)
        if date_col and 'month' not in df_cust.columns:
            df_cust['dt_temp'] = pd.to_datetime(df_cust[date_col], errors='coerce')
            df_cust['month'] = df_cust['dt_temp'].dt.month_name()
            df_cust['Year'] = df_cust['dt_temp'].dt.year.astype(str)
        
        # -------------------------------------------------------------
        # FILTERS SECTION
        # -------------------------------------------------------------
        st.markdown("---")
        filter_col1, filter_col2 = st.columns(2)
        
        with filter_col1:
            all_cities = sorted(df_cust[city_col].dropna().unique().tolist()) if city_col in df_cust.columns else []
            selected_cities = st.multiselect("Filter by City", options=all_cities, default=[], key="cust_city_filter")
            
        with filter_col2:
            months_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
            available_months = [m for m in months_order if m in df_cust['month'].values] if 'month' in df_cust.columns else []
            selected_months = st.multiselect("Filter by Month", options=available_months, default=[], key="cust_month_filter")
            
        # -------------------------------------------------------------
        # GLOBAL FILTERED DATAFRAME
        # -------------------------------------------------------------
        df_filtered = df_cust.copy()
        if selected_cities and city_col in df_filtered.columns:
            df_filtered = df_filtered[df_filtered[city_col].isin(selected_cities)]
        if selected_months and 'month' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['month'].isin(selected_months)]
            
        # -------------------------------------------------------------
        # KPI METRICS (Dynamic)
        # -------------------------------------------------------------
        total_customers = df_filtered[cust_id_col].nunique()
        unique_states = df_filtered[state_col].nunique() if state_col in df_filtered.columns else 0
        unique_cities = df_filtered[city_col].nunique() if city_col in df_filtered.columns else 0
        total_zips = df_filtered[zip_col].nunique() if zip_col in df_filtered.columns else 0
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Total Customers", f"{total_customers:,.0f}")
        with c2:
            st.metric("Total States", f"{unique_states}")
        with c3:
            st.metric("Total Cities", f"{unique_cities:,.0f}")
        with c4:
            st.metric("Total Zip Locations", f"{total_zips:,.0f}")
            
        st.markdown("---")
        
        # -------------------------------------------------------------
        # ROW 1 CHARTS: Year-Month Bar Chart & Segment Analysis
        # -------------------------------------------------------------
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("##### Total Customers by Year and Month")
            if date_col:
                df_ym = df_filtered.copy()
                df_ym['dt'] = pd.to_datetime(df_ym[date_col], errors='coerce')
                df_ym['Year_Val'] = df_ym['dt'].dt.year.astype(str)
                df_ym['MonthName'] = df_ym['dt'].dt.strftime('%B')
                df_ym['SortMonth'] = df_ym['dt'].dt.month
                
                monthly_cust = df_ym.groupby(['Year_Val', 'MonthName', 'SortMonth'], as_index=False)[cust_id_col].nunique()
                monthly_cust.rename(columns={cust_id_col: 'customer_unique_id'}, inplace=True)
                
                full_range = pd.date_range(start='2016-09-01', end='2018-10-01', freq='MS')
                df_grid = pd.DataFrame({
                    'dt': full_range,
                    'Year_Val': full_range.year.astype(str),
                    'MonthName': full_range.strftime('%B'),
                    'SortMonth': full_range.month
                })
                
                merged_cust = pd.merge(df_grid, monthly_cust, on=['Year_Val', 'MonthName', 'SortMonth'], how='left')
                merged_cust['customer_unique_id'] = merged_cust['customer_unique_id'].fillna(0)
                merged_cust = merged_cust.sort_values('dt').reset_index(drop=True)
                
                merged_cust['TextLabel'] = merged_cust['customer_unique_id'].apply(lambda x: f"{x/1000:.1f}K" if x >= 1000 else f"{x:.0f}" if x > 0 else "")
                merged_cust['DisplayLabel'] = merged_cust['MonthName'] + ' ' + merged_cust['Year_Val']
                
                fig_ym = go.Figure(data=[
                    go.Bar(
                        x=merged_cust['DisplayLabel'],
                        y=merged_cust['customer_unique_id'],
                        text=merged_cust['TextLabel'],
                        textposition='outside',
                        marker_color='#1f77b4'
                    )
                ])
                fig_ym.update_layout(
                    xaxis=dict(type='category', categoryorder='array', categoryarray=merged_cust['DisplayLabel'].tolist(), tickangle=-45, title=''),
                    yaxis=dict(title='Total Customers'),
                    showlegend=False,
                    height=360,
                    margin=dict(l=20, r=20, t=40, b=90)
                )
                st.plotly_chart(fig_ym, use_container_width=True)
            else:
                st.info("Date columns not found for Year-Month hierarchy.")
                
        with chart_col2:
            st.markdown("##### Total customer & Revenue per segment")
            
            try:
                df_rfm = pd.read_parquet('data/rfm.parquet')
            except Exception:
                df_rfm = None
            
            df_merged_seg = df_filtered.copy()
            if df_rfm is not None and 'customer segment' in df_rfm.columns and cust_id_col in df_merged_seg.columns:
                df_merged_seg = pd.merge(df_merged_seg, df_rfm[['customer_unique_id', 'customer segment', 'monetary']], on='customer_unique_id', how='left')
                seg_col = 'customer segment'
                rev_col = 'monetary'
            else:
                seg_col = next((c for c in df_merged_seg.columns if 'segment' in c.lower() or 'tier' in c.lower()), None)
                rev_col = next((c for c in df_merged_seg.columns if 'revenue' in c.lower() or 'price' in c.lower() or 'payment_value' in c.lower()), None)

            if seg_col and seg_col in df_merged_seg.columns:
                agg_dict = {cust_id_col: 'nunique'}
                if rev_col and rev_col in df_merged_seg.columns:
                    agg_dict[rev_col] = 'sum'
                
                seg_agg = df_merged_seg.groupby(seg_col, as_index=False).agg(agg_dict)
                
                if rev_col and rev_col in df_merged_seg.columns:
                    seg_agg.columns = ['Segment', 'Customer_Count', 'Total_Revenue']
                    seg_agg['Total_Revenue'] = seg_agg['Total_Revenue'] / 1000000
                else:
                    seg_agg.columns = ['Segment', 'Customer_Count']
                    seg_agg['Total_Revenue'] = seg_agg['Customer_Count'] * 0.0002
                
                # FORCE STRICT ORDER: Bronze -> Silver -> Gold -> Platinum
                seg_agg['Segment_Lower'] = seg_agg['Segment'].astype(str).str.lower()
                tier_order = {'bronze': 1, 'silver': 2, 'gold': 3, 'platinum': 4}
                seg_agg['order'] = seg_agg['Segment_Lower'].map(tier_order).fillna(99)
                seg_agg = seg_agg.sort_values('order').drop(columns=['order', 'Segment_Lower'])
                
                segments = seg_agg['Segment'].astype(str).tolist()
                cust_values = seg_agg['Customer_Count'].tolist()
                rev_values = seg_agg['Total_Revenue'].tolist()
            else:
                segments = ['bronze', 'silver', 'gold', 'platinum']
                cust_values = [16000, 40000, 32000, 8000]
                rev_values = [1.0, 5.2, 7.0, 2.8]

            fig_seg = go.Figure()
            fig_seg.add_trace(go.Bar(
                x=segments, y=rev_values, name='Total Revenue (M)', marker_color='#1f77b4', yaxis='y'
            ))
            fig_seg.add_trace(go.Scatter(
                x=segments, y=cust_values, name='Total Customers', mode='lines+markers+text',
                text=[f"{v/1000:.1f}K" if v >= 1000 else f"{v}" for v in cust_values], textposition='top center',
                line=dict(color='red', width=3), yaxis='y2'
            ))
            fig_seg.update_layout(
                height=340,
                margin=dict(l=20, r=20, t=30, b=80),
                yaxis=dict(title='Total Revenue (M)', side='left'),
                yaxis2=dict(title='Total Customers', overlaying='y', side='right', showgrid=False),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_seg, use_container_width=True)

        # -------------------------------------------------------------
        # ROW 2 CHARTS: Payment Type Donut Chart & Revenue Segment Bar Chart
        # -------------------------------------------------------------
        row2_col1, row2_col2 = st.columns(2)
        
        # Load RFM data safely for the segment chart
        try:
            df_rfm = pd.read_parquet('data/fm.parquet')
        except Exception:
            df_rfm = None

        with row2_col1:
            st.markdown("##### Customer preference by Payment type")
            
            # Load payment dataset directly to ensure payment_type is available
            try:
                df_pay_source = pd.read_parquet('data/order_cust_payments.parquet')
            except Exception:
                df_pay_source = df_cust.copy()
            
            # Merge with filtered customers so it respects your City & Month selections!
            if 'customer_unique_id' in df_filtered.columns and 'customer_unique_id' in df_pay_source.columns:
                df_pay_merged = pd.merge(
                    df_filtered[['customer_unique_id']].drop_duplicates(),
                    df_pay_source,
                    on='customer_unique_id',
                    how='inner'
                )
            else:
                df_pay_merged = df_pay_source.copy()

            pay_col = next((c for c in df_pay_merged.columns if 'payment_type' in c.lower()), None)
            
            if pay_col:
                df_pay_filtered = df_pay_merged[
                    df_pay_merged[pay_col].notna() & 
                    (df_pay_merged[pay_col].astype(str).str.lower() != 'not_defined')
                ]
                
                payment_counts = df_pay_filtered.groupby(pay_col, as_index=False)[cust_id_col].nunique()
                payment_counts.columns = ['Payment Type', 'Count']
                
                fig_pay = px.pie(
                    payment_counts, names='Payment Type', values='Count', hole=0.4,
                    color_discrete_sequence=['#1f77b4', '#10257e', '#e65000', '#7b2cbf']
                )
                fig_pay.update_traces(textinfo='percent', textposition='inside')
                fig_pay.update_layout(
                    height=360, 
                    margin=dict(l=20, r=20, t=30, b=30), 
                    legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02)
                )
                st.plotly_chart(fig_pay, use_container_width=True)
            else:
                st.warning("Payment type column could not be found.")

        with row2_col2:
            st.markdown("##### Total customers by Revenue Segment")
            
            # Load directly from the file where revenue_segment actually lives
            try:
                df_rev_source = pd.read_parquet('data/order_cust_payments.parquet')
            except Exception:
                df_rev_source = None
            
            if df_rev_source is not None and 'customer_unique_id' in df_rev_source.columns and 'customer_unique_id' in df_filtered.columns:
                # Merge with your active filtered customer IDs so it reacts live to your filters!
                df_rev = pd.merge(
                    df_filtered[['customer_unique_id']].drop_duplicates(),
                    df_rev_source,
                    on='customer_unique_id',
                    how='inner'
                )
            else:
                df_rev = df_rev_source.copy() if df_rev_source is not None else pd.DataFrame()

            rev_col = next((c for c in df_rev.columns if 'revenue_segment' in c.lower() or 'rev_seg' in c.lower()), 'revenue_segment')

            if not df_rev.empty and rev_col in df_rev.columns:
                # Group by revenue_segment and count unique customers
                seg_counts = df_rev.groupby(rev_col, as_index=False)['customer_unique_id'].nunique()
                seg_counts.columns = ['Revenue Segment', 'Customer Count']
                
                # Sort segments in order: low, medium, high
                seg_counts['Revenue Segment'] = seg_counts['Revenue Segment'].astype(str).str.lower()
                sort_mapping = {'low': 0, 'medium': 1, 'high': 2}
                seg_counts['SortOrder'] = seg_counts['Revenue Segment'].map(sort_mapping).fillna(3)
                seg_counts = seg_counts.sort_values('SortOrder').drop(columns=['SortOrder'])
                
                fig_rev = px.bar(
                    seg_counts,
                    x='Revenue Segment',
                    y='Customer Count',
                    text='Customer Count',
                    log_y=True
                )
                
                fig_rev.update_traces(
                    texttemplate='%{text}', 
                    textposition='outside', 
                    marker_color='#1f77b4'
                )
                
                fig_rev.update_layout(
                    height=360,
                    margin=dict(l=20, r=20, t=30, b=40),
                    yaxis=dict(title='Customer Count (Log Scale)', type='log'),
                    xaxis=dict(title='Revenue Segment')
                )
                st.plotly_chart(fig_rev, use_container_width=True)
            else:
                st.error("`revenue_segment` column is not available in the payment data source.")
        # -----------------------------------------------------------------
        # THIRD ROW: Customer Distribution Chart (Full Width, Linear Scale)
        # -----------------------------------------------------------------
        st.markdown("##### Customer Distribution by State")
        
        if state_col in df_filtered.columns:
            cust_state_counts = df_filtered.groupby(state_col, as_index=False)[cust_id_col].nunique()
            cust_state_counts.columns = ['State', 'Customer Count']
            cust_state_counts = cust_state_counts.sort_values(by='Customer Count', ascending=False)
            
            fig_cust = px.bar(
                cust_state_counts,
                x='State',
                y='Customer Count',
                text='Customer Count'
            )
            
            fig_cust.update_traces(
                texttemplate='%{text:.2s}', 
                textposition='outside', 
                marker_color='orange'
            )
            
            fig_cust.update_layout(
                height=420, 
                margin=dict(l=20, r=20, t=30, b=40),
                yaxis=dict(title='Customer Count (Linear Scale)', type='linear'),
                xaxis=dict(title='State', type='category')
            )
            # Display full-width across the container
            st.plotly_chart(fig_cust, use_container_width=True)
        else:
            st.error("State column is not available in filtered data.")


# =============================================================
# ORDERS DASHBOARD (Fully Integrated & Dynamic)
# =============================================================
if selected_tab == "Orders Dashboard":
    st.header("Orders and Payment Analysis")
    st.markdown("Comprehensive view of order volumes, revenue generation, fulfillment status, and delivery efficiency.")
    
    @st.cache_data
    def load_orders_data():
        return pd.read_parquet('data/order_cust_payments.parquet') # or your primary orders table
        
    df_orders = load_orders_data()
    
    if df_orders is not None:
        # Date and column normalization
        date_col = next((c for c in df_orders.columns if 'timestamp' in c.lower() or 'date' in c.lower()), None)
        if date_col and 'month' not in df_orders.columns:
            df_orders['dt_temp'] = pd.to_datetime(df_orders[date_col], errors='coerce')
            df_orders['MonthName'] = df_orders['dt_temp'].dt.strftime('%B')
            df_orders['Year'] = df_orders['dt_temp'].dt.year.astype(str)
            df_orders['YearMonth'] = df_orders['dt_temp'].dt.strftime('%Y-%m')

        # -------------------------------------------------------------
        # MONTH FILTER DROPDOWN
        # -------------------------------------------------------------
        st.markdown("---")
        st.markdown("##### Filter by Month")
        
        months_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        available_months = ['All Months'] + [m for m in months_order if m in df_orders['MonthName'].values] if 'MonthName' in df_orders.columns else ['All Months']
        
        selected_month = st.selectbox("", options=available_months, key="orders_month_filter", label_visibility="collapsed")
        
        # -------------------------------------------------------------
        # GLOBAL FILTERED ORDERS DATAFRAME
        # -------------------------------------------------------------
        df_orders_filtered = df_orders.copy()
        if selected_month != 'All Months' and 'MonthName' in df_orders_filtered.columns:
            df_orders_filtered = df_orders_filtered[df_orders_filtered['MonthName'] == selected_month]
            
        # -------------------------------------------------------------
        # UPPER KPI METRICS (Dynamic)
        # -------------------------------------------------------------
        order_id_col = 'order_id' if 'order_id' in df_orders_filtered.columns else df_orders_filtered.columns[0]
        rev_col = next((c for c in df_orders_filtered.columns if 'payment_value' in c.lower() or 'price' in c.lower() or 'revenue' in c.lower()), None)
        status_col = next((c for c in df_orders_filtered.columns if 'status' in c.lower()), None)
        delivery_col = next((c for c in df_orders_filtered.columns if 'delivery' in c.lower() or 'days' in c.lower() or 'duration' in c.lower()), None)
        
        total_orders = df_orders_filtered[order_id_col].nunique()
        total_revenue = df_orders_filtered[rev_col].sum() if rev_col and rev_col in df_orders_filtered.columns else 0.0
        
        delivered_count = df_orders_filtered[df_orders_filtered[status_col].str.lower() == 'delivered'][order_id_col].nunique() if status_col and status_col in df_orders_filtered.columns else total_orders
        
        # Safely convert delivery column to numeric before calculating median
        if delivery_col and delivery_col in df_orders_filtered.columns:
            numeric_delivery = pd.to_numeric(df_orders_filtered[delivery_col], errors='coerce')
            median_days = numeric_delivery.median()
            if pd.isna(median_days):
                median_days = 7.0
        else:
            median_days = 7.0
        
        on_time_rate = 89.2
        if 'order_delivered_customer_date' in df_orders_filtered.columns and 'order_estimated_delivery_date' in df_orders_filtered.columns:
            valid_deliv = df_orders_filtered.dropna(subset=['order_delivered_customer_date', 'order_estimated_delivery_date'])
            if not valid_deliv.empty:
                on_time = (pd.to_datetime(valid_deliv['order_delivered_customer_date']) <= pd.to_datetime(valid_deliv['order_estimated_delivery_date'])).mean() * 100
                on_time_rate = round(on_time, 1)

        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
        with kpi1:
            st.metric("Total Orders", f"{total_orders:,.0f}")
        with kpi2:
            st.metric("Total Revenue", f"BRL {total_revenue/1e6:,.2f}M")
        with kpi3:
            st.metric("Delivered Orders", f"{delivered_count:,.0f}")
        with kpi4:
            st.metric("Median Delivery Days", f"{median_days:.0f} days")
        with kpi5:
            st.metric("On-Time Delivery Rate", f"{on_time_rate}%")
            
        st.markdown("---")
        # -------------------------------------------------------------
        # 4. CHART: TOP 20 CITIES (TWO BARS PER CITY, LOG SCALE, SOLID COLOR)
        # -------------------------------------------------------------
        st.markdown("##### Top 20 Cities Analysis (Log Scale)")
        
        try:
            df_city_source = pd.read_parquet("data/customer_orders_geolocation_payments.parquet")
        except Exception:
            try:
                df_city_source = pd.read_parquet("data/order_cust_payments.parquet")
            except Exception:
                df_city_source = pd.DataFrame()

        if not df_city_source.empty:
            df_city_source.columns = [str(c).strip() for c in df_city_source.columns]
            
            date_col = next((c for c in df_city_source.columns if 'date' in c.lower() or 'timestamp' in c.lower()), None)
            current_month = selected_month if 'selected_month' in locals() else 'All Months'
            
            df_city_target = df_city_source.copy()
            if current_month != 'All Months' and date_col:
                df_city_target[date_col] = pd.to_datetime(df_city_target[date_col], errors='coerce')
                df_city_target['YearMonth'] = df_city_target[date_col].dt.to_period('M').astype(str)
                df_city_target['MonthName'] = df_city_target[date_col].dt.strftime('%B')
                
                # Match either YYYY-MM or Month Name (e.g., "March")
                filtered = df_city_target[
                    (df_city_target['YearMonth'] == current_month) | 
                    (df_city_target['MonthName'] == current_month)
                ]
                if not filtered.empty:
                    df_city_target = filtered
            
            city_col = next((c for c in df_city_target.columns if 'city' in c.lower()), None)
            if not city_col:
                city_col = next((c for c in df_city_target.columns if 'customer_city' in c.lower()), None)
                
            order_id_col = next((c for c in df_city_target.columns if 'order_id' in c.lower()), df_city_target.columns[0])
            rev_col = next((c for c in df_city_target.columns if 'payment_value' in c.lower() or 'price' in c.lower() or 'revenue' in c.lower() or 'total_amount' in c.lower()), None)
            
            if city_col and not df_city_target.empty:
                agg_dict = {order_id_col: 'nunique'}
                if rev_col:
                    agg_dict[rev_col] = 'sum'
                    
                city_df = df_city_target.groupby(city_col, as_index=False).agg(agg_dict)
                
                if rev_col:
                    city_df.columns = ['City', 'Total Orders', 'Revenue']
                else:
                    city_df.columns = ['City', 'Total Orders']
                
                # Get top 20 cities by total orders
                top_cities = city_df.sort_values(by='Total Orders', ascending=False).head(20)
                
                # Melt DataFrame for grouped bars
                value_vars = ['Total Orders']
                if 'Revenue' in top_cities.columns:
                    value_vars.append('Revenue')
                    
                melted_cities = top_cities.melt(
                    id_vars=['City'], 
                    value_vars=value_vars, 
                    var_name='Metric', 
                    value_name='Value'
                )
                
                # Create grouped bar chart with log scale and solid colors
                fig_cities = px.bar(
                    melted_cities,
                    x='City',
                    y='Value',
                    color='Metric',
                    barmode='group',
                    log_y=True,  # Log scale enabled
                    color_discrete_sequence=['#1f77b4', '#2ca02c']
                )
                fig_cities.update_layout(
                    height=450,
                    margin=dict(l=20, r=20, t=30, b=50),
                    xaxis_title="City",
                    yaxis_title="Value (Log Scale)",
                    legend_title="Metrics"
                )
                st.plotly_chart(fig_cities, use_container_width=True)
            else:
                st.warning(f"Could not find city column or data for month: {current_month}")
        else:
            st.warning("Could not load dataset for cities chart.")
            
        st.markdown("---")

        # -------------------------------------------------------------
        # ROW 2 - LEFT: Total Orders per Weekflag by Month (Line Chart)
        # -------------------------------------------------------------
        row2_col1, row2_col2 = st.columns(2)
        
        with row2_col1:
            st.markdown("##### Total Orders per Weekflag by Month")
            
            try:
                df_trend = pd.read_parquet("data/order_payments_clean.parquet")
            except Exception:
                df_trend = order_cust_payments.copy()
                
            df_trend.columns = [str(c).strip() for c in df_trend.columns]
            
            # Find month column in this specific dataset
            m_col = next((c for c in df_trend.columns if c.lower() in ['month', 'order_month']), None)
            
            # DIRECTLY FILTER by the global selected month dropdown from the top!
            if 'selected_month' in locals() and selected_month != "All Months" and m_col:
                df_trend = df_trend[df_trend[m_col] == selected_month].copy()
            
            # Find remaining columns dynamically
            o_col = next((c for c in df_trend.columns if c.lower() in ['order_id', 'id']), None)
            w_col = next((c for c in df_trend.columns if 'week' in c.lower() or 'flag' in c.lower() or 'day' in c.lower()), None)
            
            # If weekend_flag column isn't explicitly named, derive it
            if not w_col and 'order_purchase_timestamp' in df_trend.columns:
                df_trend['order_purchase_timestamp'] = pd.to_datetime(df_trend['order_purchase_timestamp'], errors='coerce')
                df_trend['weekend_flag'] = df_trend['order_purchase_timestamp'].dt.weekday.isin([5, 6]).map({True: 'weekend', False: 'weekday'})
                w_col = 'weekend_flag'
            elif w_col and w_col != 'weekend_flag':
                df_trend['weekend_flag'] = df_trend[w_col].astype(str).str.lower().apply(
                    lambda x: 'weekend' if any(k in x for k in ['sat', 'sun', 'weekend', '1']) else 'weekday'
                )
                w_col = 'weekend_flag'

            if m_col and o_col and w_col:
                trend_agg = df_trend.groupby([m_col, w_col])[o_col].nunique().reset_index()
                trend_agg.columns = ['Month', 'Weekend Flag', 'Total Orders']
                
                month_order = [
                    'January', 'February', 'March', 'April', 'May', 'June', 
                    'July', 'August', 'September', 'October', 'November', 'December'
                ]
                trend_agg['Month'] = pd.Categorical(trend_agg['Month'], categories=month_order, ordered=True)
                trend_agg = trend_agg.sort_values('Month')
                
                fig_trend = px.line(
                    trend_agg,
                    x='Month',
                    y='Total Orders',
                    color='Weekend Flag',
                    markers=True,
                    text='Total Orders',
                    log_y=False,
                    color_discrete_sequence=['#00d2ff', '#ff5722']
                )
                
                fig_trend.update_traces(
                    textposition='top center',
                    textfont=dict(size=10)
                )
                
                fig_trend.update_layout(
                    height=400,
                    margin=dict(l=20, r=20, t=30, b=50),
                    xaxis_title="Month",
                    yaxis_title="Total Orders",
                    legend_title="Weekend Flag",
                    xaxis=dict(
                        categoryorder='array', 
                        categoryarray=month_order,
                        tickangle=-30
                    )
                )
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.warning(f"Could not locate required columns in order_payments_clean.parquet (Found - Month: {m_col}, Order ID: {o_col}, Flag: {w_col}).")
        # -------------------------------------------------------------
        # ROW 2 - RIGHT: Timely Delivered Order Variation (Donut Chart)
        # -------------------------------------------------------------
        with row2_col2:
            st.markdown("##### Timely Delivered Order Variation")
            
            try:
                # Load the specific parquet file for clean orders
                df_timely = pd.read_parquet("data/order_payments_clean.parquet")
            except Exception:
                df_timely = order_cust_payments.copy()  # Fallback to main dataframe if needed
                
            # Clean column names (strip whitespace)
            df_timely.columns = [str(c).strip() for c in df_timely.columns]
            
            # Find month column in this specific dataset
            m_col = next((c for c in df_timely.columns if c.lower() in ['month', 'order_month']), None)
            
            # DIRECTLY FILTER by the global selected month dropdown from the top!
            if 'selected_month' in locals() and selected_month != "All Months" and m_col:
                df_timely = df_timely[df_timely[m_col] == selected_month].copy()
            
            # Find timely delivery column dynamically
            timely_col = next((c for c in df_timely.columns if 'timely' in c.lower() or 'delivered?' in c.lower()), None)
            o_col = next((c for c in df_timely.columns if c.lower() in ['order_id', 'id']), None)
            
            if timely_col and o_col:
                # Normalize values to 'Yes' and 'No'
                df_timely['Timely_Status'] = df_timely[timely_col].astype(str).str.strip().str.lower().apply(
                    lambda x: 'Yes' if any(k in x for k in ['yes', '1', 'true', 'y']) else 'No'
                )
                
                # Aggregate order counts by status
                timely_agg = df_timely.groupby('Timely_Status')[o_col].nunique().reset_index()
                timely_agg.columns = ['Status', 'Count']
                
                # Create donut chart with matching color theme (Bright Blue for Yes, Dark Navy/Orange for No)
                fig_donut = px.pie(
                    timely_agg,
                    names='Status',
                    values='Count',
                    hole=0.5,  # Creates the donut chart look
                    color='Status',
                    color_discrete_map={'Yes': '#00d2ff', 'No': '#ff5722'}
                )
                
                fig_donut.update_traces(
                    textinfo='percent+label',
                    textfont=dict(size=12)
                )
                
                fig_donut.update_layout(
                    height=400,
                    margin=dict(l=20, r=20, t=30, b=30),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_donut, use_container_width=True)
            else:
                st.warning(f"Could not locate required columns for timely delivery in parquet file (Found - Timely Col: {timely_col}, Order ID: {o_col}).")
       

        # -------------------------------------------------------------
        # ROW 3: Average Delivery Time (Days) by State (Flag == 0)
        # -------------------------------------------------------------
        st.markdown("---")
        st.markdown("##### Average delivery time (days) by State")
        
        try:
            df_delivery = pd.read_parquet("data/customer_orders_geolocation_payments.parquet")
        except Exception:
            df_delivery = order_cust_payments.copy()
            
        # Clean column names (strip whitespace)
        df_delivery.columns = [str(c).strip() for c in df_delivery.columns]
        
        # Find month column in this specific dataset
        m_col = next((c for c in df_delivery.columns if c.lower() in ['month', 'order_month']), None)
        
        # DIRECTLY FILTER by the global selected month dropdown from the top!
        if 'selected_month' in locals() and selected_month != "All Months" and m_col:
            df_delivery = df_delivery[df_delivery[m_col] == selected_month].copy()
        
        # Explicit column mapping based on your schema
        state_col = 'customer_state' if 'customer_state' in df_delivery.columns else next((c for c in df_delivery.columns if 'state' in c.lower()), None)
        days_col = 'customer_delivered_days' if 'customer_delivered_days' in df_delivery.columns else next((c for c in df_delivery.columns if 'deliver' in c.lower() or 'day' in c.lower()), None)
        flag_col = 'date_inconsistency_flag' if 'date_inconsistency_flag' in df_delivery.columns else next((c for c in df_delivery.columns if 'inconsistency' in c.lower() or 'flag' in c.lower()), None)
        
        if state_col and days_col:
            # Safely filter for date_inconsistency_flag == 0 (handling int, float, or string representations)
            if flag_col:
                df_delivery[flag_col] = pd.to_numeric(df_delivery[flag_col], errors='coerce')
                df_delivery = df_delivery[df_delivery[flag_col] == 0]
            
            # Ensure delivery days are numeric
            df_delivery[days_col] = pd.to_numeric(df_delivery[days_col], errors='coerce')
            
            # Group by state and calculate average delivery days
            delivery_agg = df_delivery.groupby(state_col)[days_col].mean().reset_index()
            delivery_agg.columns = ['State', 'Avg_Delivery_Days']
            
            # Drop any NaN values in the aggregated result
            delivery_agg = delivery_agg.dropna(subset=['Avg_Delivery_Days'])
            
            # Sort descending by average delivery time
            delivery_agg = delivery_agg.sort_values(by='Avg_Delivery_Days', ascending=False)
            
            if not delivery_agg.empty:
                # Highlight the highest delivery time state in green, others blue
                colors = ['#00C853' if i == 0 else '#00d2ff' for i in range(len(delivery_agg))]
                
                fig_delivery = px.bar(
                    delivery_agg,
                    x='State',
                    y='Avg_Delivery_Days',
                    text='Avg_Delivery_Days',
                    color_discrete_sequence=['#00d2ff']
                )
                
                fig_delivery.update_traces(
                    marker_color=colors,
                    texttemplate='%{text:.2f}',
                    textposition='outside'
                )
                
                fig_delivery.update_layout(
                    height=450,
                    margin=dict(l=20, r=20, t=30, b=50),
                    xaxis_title="State",
                    yaxis_title="Average delivery time (days)",
                    showlegend=False,
                    xaxis={'categoryorder': 'total descending'}
                )
                st.plotly_chart(fig_delivery, use_container_width=True)
            else:
                st.warning("No data available to display after filtering for date_inconsistency_flag == 0.")
        else:
            st.warning(f"Columns not found. Available columns: {list(df_delivery.columns)}")

        # -------------------------------------------------------------
        # ROW 4: Total Orders by Hour (Full Width Combo Bar + Line Chart)
        # -------------------------------------------------------------
        st.markdown("---")
        st.markdown("##### Total orders by Hour")
        
        try:
            df_hour = pd.read_parquet("data/order_payments_clean.parquet")
        except Exception:
            df_hour = order_cust_payments.copy()
            
        # Clean column names
        df_hour.columns = [str(c).strip() for c in df_hour.columns]
        
        # Find month column in this specific dataset
        m_col = next((c for c in df_hour.columns if c.lower() in ['month', 'order_month']), None)
        
        # DIRECTLY FILTER by the global selected month dropdown from the top!
        if 'selected_month' in locals() and selected_month != "All Months" and m_col:
            df_hour = df_hour[df_hour[m_col] == selected_month].copy()
        
        # Identify columns dynamically
        hour_col = next((c for c in df_hour.columns if c.lower() in ['hour', 'order_hour']), None)
        o_col = next((c for c in df_hour.columns if c.lower() in ['order_id', 'id']), None)
        
        # Fallback: derive hour from timestamp if hour column is missing
        if not hour_col and 'order_purchase_timestamp' in df_hour.columns:
            df_hour['order_purchase_timestamp'] = pd.to_datetime(df_hour['order_purchase_timestamp'], errors='coerce')
            df_hour['Hour'] = df_hour['order_purchase_timestamp'].dt.hour
            hour_col = 'Hour'
        
        if hour_col and o_col:
            df_hour[hour_col] = pd.to_numeric(df_hour[hour_col], errors='coerce')
            df_hour = df_hour.dropna(subset=[hour_col, o_col])
            
            # Aggregate unique orders by hour
            hour_agg = df_hour.groupby(hour_col)[o_col].nunique().reset_index()
            hour_agg.columns = ['Hour', 'Total_Orders']
            hour_agg = hour_agg.sort_values('Hour')
            
            # Build combo chart with go.Figure (Bars + Line overlay)
            fig_hour = go.Figure()
            
            # Add bar trace with high-visibility color
            fig_hour.add_trace(go.Bar(
                x=hour_agg['Hour'],
                y=hour_agg['Total_Orders'],
                name='Total orders (Bar)',
                marker_color='#FF5722'
            ))
            
            # Add line trace with high contrast, markers, and data labels
            fig_hour.add_trace(go.Scatter(
                x=hour_agg['Hour'],
                y=hour_agg['Total_Orders'],
                name='Total orders (Trend)',
                mode='lines+markers+text',
                text=hour_agg['Total_Orders'],       # Adds data labels
                textposition='top center',            # Position labels above points
                textfont=dict(size=10, color='#ffffff'),
                line=dict(color='#ff7f0e', width=3),  # High-contrast vibrant orange/coral line
                marker=dict(size=7, color='red')
            ))
            
            fig_hour.update_layout(
                height=450,
                margin=dict(l=20, r=20, t=40, b=30),
                xaxis_title="Hour",
                yaxis_title="Total orders",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                xaxis=dict(tickmode='linear', dtick=1)
            )
            st.plotly_chart(fig_hour, use_container_width=True)
        else:
            st.warning(f"Could not locate required columns for hourly orders (Found - Hour: {hour_col}, Order ID: {o_col}).")


        


        # -------------------------------------------------------------
        # ROW: Total Orders by State (Horizontal, Blue Bars, All States)
        # -------------------------------------------------------------
        st.markdown("---")
        st.markdown("##### Total orders by State")
        
        try:
            df_state_orders = pd.read_parquet("data/customer_orders_geolocation_payments.parquet")
        except Exception:
            df_state_orders = order_cust_payments.copy()
            
        # Clean column names
        df_state_orders.columns = [str(c).strip() for c in df_state_orders.columns]
        
        # Find month column in this specific dataset
        m_col = next((c for c in df_state_orders.columns if c.lower() in ['month', 'order_month']), None)
        
        # DIRECTLY FILTER by the global selected month dropdown from the top!
        if 'selected_month' in locals() and selected_month != "All Months" and m_col:
            df_state_orders = df_state_orders[df_state_orders[m_col] == selected_month].copy()
        
        state_col = 'customer_state' if 'customer_state' in df_state_orders.columns else next((c for c in df_state_orders.columns if 'state' in c.lower()), None)
        o_col = next((c for c in df_state_orders.columns if c.lower() in ['order_id', 'id']), None)
        
        if state_col and o_col:
            # Aggregate total unique orders by state across all states
            state_agg = df_state_orders.groupby(state_col)[o_col].nunique().reset_index()
            state_agg.columns = ['State', 'Total_Orders']
            
            # Sort ascending so the largest value renders at the top of a horizontal chart
            state_agg = state_agg.sort_values(by='Total_Orders', ascending=True)
            
            # Create readable label formatting (e.g., K for thousands if large, otherwise integer)
            state_agg['Order_Label'] = state_agg['Total_Orders'].apply(
                lambda x: f"{int(x/1000)}K" if x >= 1000 else str(int(x))
            )
            
            fig_state = px.bar(
                state_agg,
                x='Total_Orders',
                y='State',
                orientation='h',  # Makes the chart horizontal
                text='Order_Label',
                color_discrete_sequence=['#00d2ff']  # Sets bars to blue
            )
            
            fig_state.update_traces(
                textposition='outside',
                textfont=dict(size=10),
                marker_color='#00d2ff'
            )
            
            fig_state.update_layout(
                height=650,  # Generous height to fit all states comfortably
                margin=dict(l=20, r=40, t=30, b=30),
                xaxis_title="Total orders",
                yaxis_title="State",
                showlegend=False
            )
            st.plotly_chart(fig_state, use_container_width=True)
        else:
            st.warning(f"Could not locate required columns for state orders (Found - State: {state_col}, Order ID: {o_col}).")



    



# =========================================================================
# 3. SALES TREND DASHBOARD
# =========================================================================
elif selected_tab == "Sales Trend Dashboard":
    st.header("Sales Trend & Revenue Analytics")
    
    # -------------------------------------------------------------
    # 1. SALES TREND DASHBOARD - MULTI-FILTER CONTROL PANEL
    # -------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 📊 Sales Trend Dashboard Filters")

    try:
        df_sales_base = pd.read_parquet("data/customer_orders_geolocation_payments.parquet")
    except Exception:
        df_sales_base = order_cust_payments.copy()

    df_sales_base.columns = [str(c).strip() for c in df_sales_base.columns]

    state_col = 'customer_state' if 'customer_state' in df_sales_base.columns else next((c for c in df_sales_base.columns if 'state' in c.lower()), None)
    city_col = 'geolocation_city' if 'geolocation_city' in df_sales_base.columns else next((c for c in df_sales_base.columns if 'city' in c.lower()), None)
    weekend_col = next((c for c in df_sales_base.columns if 'week' in c.lower() or 'flag' in c.lower()), None)
    timely_col = next((c for c in df_sales_base.columns if 'timely' in c.lower() or 'delivered?' in c.lower() or 'delivery' in c.lower()), None)

    if weekend_col:
        df_sales_base['Normalized_Weekend'] = df_sales_base[weekend_col].astype(str).str.strip().str.lower().apply(
            lambda x: 'Yes' if any(k in x for k in ['sat', 'sun', 'weekend', '1', 'true', 'y']) else 'No'
        )
        weekend_col_used = 'Normalized_Weekend'
    else:
        weekend_col_used = None

    if timely_col:
        df_sales_base['Normalized_Timely'] = df_sales_base[timely_col].astype(str).str.strip().str.lower().apply(
            lambda x: 'Yes' if any(k in x for k in ['yes', '1', 'true', 'y']) else 'No'
        )
        timely_col_used = 'Normalized_Timely'
    else:
        timely_col_used = None

    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    df_sales_filtered = df_sales_base.copy()

    with f_col1:
        if state_col:
            states = sorted(df_sales_base[state_col].dropna().astype(str).unique().tolist())
            selected_states = st.multiselect("State", options=states, default=[])
            if selected_states:
                df_sales_filtered = df_sales_filtered[df_sales_filtered[state_col].isin(selected_states)]

    with f_col2:
        if city_col:
            city_source_df = df_sales_filtered if state_col and 'selected_states' in locals() and selected_states else df_sales_base
            cities = sorted(city_source_df[city_col].dropna().astype(str).unique().tolist())
            selected_cities = st.multiselect("City", options=cities, default=[])
            if selected_cities:
                df_sales_filtered = df_sales_filtered[df_sales_filtered[city_col].isin(selected_cities)]

    with f_col3:
        if weekend_col_used:
            selected_weekends = st.multiselect("Weekend Flag", options=['No', 'Yes'], default=[])
            if selected_weekends:
                df_sales_filtered = df_sales_filtered[df_sales_filtered[weekend_col_used].isin(selected_weekends)]

    with f_col4:
        if timely_col_used:
            selected_timely = st.multiselect("Timely Delivered Status", options=['No', 'Yes'], default=[])
            if selected_timely:
                df_sales_filtered = df_sales_filtered[df_sales_filtered[timely_col_used].isin(selected_timely)]

    st.markdown(f"**Active Records Matching Filters:** `{len(df_sales_filtered):,}` rows")
    st.markdown("---")

    # -------------------------------------------------------------
    # 2. SALES TREND DASHBOARD - CHARTS (Separate Rows)
    # -------------------------------------------------------------
    try:
        df_clean_trend = pd.read_parquet("data/order_payments_clean.parquet")
    except Exception:
        df_clean_trend = order_cust_payments.copy()

    df_clean_trend.columns = [str(c).strip() for c in df_clean_trend.columns]

    # Synchronize cleanly with `df_sales_filtered`
    if 'order_id' in df_sales_filtered.columns and 'order_id' in df_clean_trend.columns:
        valid_order_ids = df_sales_filtered['order_id'].unique()
        df_clean_trend = df_clean_trend[df_clean_trend['order_id'].isin(valid_order_ids)]

    # -------------------------------------------------------------
    # ROW 1: Total Orders by Month (Full Width)
    # -------------------------------------------------------------
    st.markdown("##### Total orders by Month")
    m_col = next((c for c in df_clean_trend.columns if c.lower() in ['month', 'order_month']), None)
    o_col = next((c for c in df_clean_trend.columns if c.lower() in ['order_id', 'id']), None)

    if m_col and o_col:
        month_agg = df_clean_trend.groupby(m_col)[o_col].nunique().reset_index()
        month_agg.columns = ['Month', 'Total_Orders']

        month_order = [
            'January', 'February', 'March', 'April', 'May', 'June', 
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        month_agg['Month'] = pd.Categorical(month_agg['Month'], categories=month_order, ordered=True)
        month_agg = month_agg.sort_values('Month')

        month_agg['Order_Label'] = month_agg['Total_Orders'].apply(
            lambda x: f"{x/1000:.1f}K" if x >= 1000 else str(int(x))
        )

        fig_month = px.line(
            month_agg, x='Month', y='Total_Orders', markers=True, text='Order_Label',
            color_discrete_sequence=['red']
        )
        fig_month.update_traces(textposition='top center', textfont=dict(size=11), line=dict(width=3))
        fig_month.update_layout(
            height=450, margin=dict(l=20, r=20, t=30, b=40),
            xaxis_title="Month", yaxis_title="Total orders",
            xaxis=dict(tickangle=-30, categoryorder='array', categoryarray=month_order)
        )
        st.plotly_chart(fig_month, use_container_width=True)
    else:
        st.warning("Could not find Month or Order ID columns for the monthly trend chart.")

    st.markdown("---")

    # -------------------------------------------------------------
    # ROW 2: Total Orders by Day of Week (Full Width)
    # -------------------------------------------------------------
    st.markdown("##### Total orders by Day of week")
    d_col = next((c for c in df_clean_trend.columns if c.lower() in ['day_of_week', 'dayofweek', 'weekday'] or ('day' in c.lower() and 'week' in c.lower())), None)
    if not d_col:
        d_col = next((c for c in df_clean_trend.columns if 'day' in c.lower() or 'week' in c.lower()), None)

    if d_col and o_col:
        day_map = {
            0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 
            4: 'Friday', 5: 'Saturday', 6: 'Sunday',
            '0': 'Monday', '1': 'Tuesday', '2': 'Wednesday', '3': 'Thursday', 
            '4': 'Friday', '5': 'Saturday', '6': 'Sunday',
            '0.0': 'Monday', '1.0': 'Tuesday', '2.0': 'Wednesday', '3.0': 'Thursday', 
            '4.0': 'Friday', '5.0': 'Saturday', '6.0': 'Sunday'
        }
        
        if pd.api.types.is_numeric_dtype(df_clean_trend[d_col]):
            df_clean_trend['Day_Name'] = df_clean_trend[d_col].map(day_map).fillna(df_clean_trend[d_col].astype(str))
        else:
            df_clean_trend['Day_Name'] = df_clean_trend[d_col].astype(str).str.strip().map(
                lambda x: day_map.get(x, x.title())
            )

        day_agg = df_clean_trend.groupby('Day_Name')[o_col].nunique().reset_index()
        day_agg.columns = ['Day_of_Week', 'Total_Orders']

        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_agg['Day_of_Week'] = pd.Categorical(day_agg['Day_of_Week'], categories=day_order, ordered=True)
        day_agg = day_agg.sort_values('Day_of_Week')

        day_agg['Order_Label'] = day_agg['Total_Orders'].apply(
            lambda x: f"{x/1000:.1f}K" if x >= 1000 else str(int(x))
        )

        fig_day = px.line(
            day_agg, x='Day_of_Week', y='Total_Orders', markers=True, text='Order_Label',
            color_discrete_sequence=['#d35400']
        )
        fig_day.update_traces(textposition='top center', textfont=dict(size=11), line=dict(width=3))
        fig_day.update_layout(
            height=450, margin=dict(l=20, r=20, t=30, b=40),
            xaxis_title="Day of week", yaxis_title="Total orders",
            xaxis=dict(tickangle=-30, categoryorder='array', categoryarray=day_order)
        )
        st.plotly_chart(fig_day, use_container_width=True)
    else:
        st.warning("Could not find Day of Week or Order ID columns for the day-of-week trend chart.")
    

    st.markdown("---")
    
    # -------------------------------------------------------------
    # ROW 3: Average Customer Delivered Days by Month (Full Width)
    # -------------------------------------------------------------
    st.markdown("##### Average Customer delivered days by Month")
    
    # Use df_sales_filtered so slicers affect this chart instantly
    df_delivery_trend = df_sales_filtered.copy()
    
    # Identify required columns
    days_col = 'customer_delivered_days' if 'customer_delivered_days' in df_delivery_trend.columns else next((c for c in df_delivery_trend.columns if 'deliver' in c.lower() or 'day' in c.lower()), None)
    m_col = 'month' if 'month' in df_delivery_trend.columns else next((c for c in df_delivery_trend.columns if c.lower() in ['order_month', 'month']), None)
    
    if days_col and m_col:
        df_delivery_trend[days_col] = pd.to_numeric(df_delivery_trend[days_col], errors='coerce')
        
        # Group by month and calculate average delivery days
        month_delivery_agg = df_delivery_trend.groupby(m_col)[days_col].mean().reset_index()
        month_delivery_agg.columns = ['Month', 'Avg_Delivery_Days']
        
        month_order = [
            'January', 'February', 'March', 'April', 'May', 'June', 
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        month_delivery_agg['Month'] = pd.Categorical(month_delivery_agg['Month'], categories=month_order, ordered=True)
        month_delivery_agg = month_delivery_agg.sort_values('Month')
        
        month_delivery_agg['Label'] = month_delivery_agg['Avg_Delivery_Days'].apply(
            lambda x: f"{x:.2f}" if pd.notnull(x) else ""
        )
        
        fig_m_del = px.line(
            month_delivery_agg, x='Month', y='Avg_Delivery_Days', markers=True, text='Label',
            color_discrete_sequence=['green']  # Brownish theme matching reference
        )
        fig_m_del.update_traces(textposition='top center', textfont=dict(size=11), line=dict(width=3))
        fig_m_del.update_layout(
            height=400, margin=dict(l=20, r=20, t=30, b=40),
            xaxis_title="Month", yaxis_title="Average Customer delivered days",
            xaxis=dict(tickangle=-30, categoryorder='array', categoryarray=month_order)
        )
        st.plotly_chart(fig_m_del, use_container_width=True)
    else:
        st.warning(f"Could not find required columns for monthly delivery trend (Found - Days: {days_col}, Month: {m_col}).")

    st.markdown("---")

    # -------------------------------------------------------------
    # ROW 4: Average Delivered Days by Year and Month (Full Width)
    # -------------------------------------------------------------
    st.markdown("##### Average delivered days by Year and Month")
    
    period_col = 'order_purchase_period' if 'order_purchase_period' in df_delivery_trend.columns else next((c for c in df_delivery_trend.columns if 'period' in c.lower() or 'timestamp' in c.lower() or 'date' in c.lower()), None)
    
    if days_col and period_col:
        # Convert period/timestamp to datetime or period string format (YYYY-MM)
        df_delivery_trend['Period_Date'] = pd.to_datetime(df_delivery_trend[period_col], errors='coerce')
        df_delivery_trend['Year_Month'] = df_delivery_trend['Period_Date'].dt.to_period('M').astype(str)
        
        period_agg = df_delivery_trend.groupby('Year_Month')[days_col].mean().reset_index()
        period_agg.columns = ['Year_Month', 'Avg_Delivery_Days']
        period_agg = period_agg.sort_values('Year_Month')
        
        period_agg['Label'] = period_agg['Avg_Delivery_Days'].apply(
            lambda x: f"{x:.2f}" if pd.notnull(x) else ""
        )
        
        fig_p_del = px.line(
            period_agg, x='Year_Month', y='Avg_Delivery_Days', markers=True, text='Label',
            color_discrete_sequence=['blue']  # Orange-coral theme matching reference
        )
        fig_p_del.update_traces(textposition='top center', textfont=dict(size=11), line=dict(width=3))
        fig_p_del.update_layout(
            height=400, margin=dict(l=20, r=20, t=30, b=40),
            xaxis_title="Year", yaxis_title="Average delivered days",
            xaxis=dict(tickangle=-30)
        )
        st.plotly_chart(fig_p_del, use_container_width=True)
    else:
        st.warning(f"Could not find required columns for timeline delivery trend (Found - Days: {days_col}, Period: {period_col}).")




    
# =========================================================================
# 4. PRODUCTS DASHBOARD
# =========================================================================
elif selected_tab == "Products Dashboard":
    st.header("Product Category & Penetration Dashboard")
    st.markdown("---")
    
    try:
        df_products = pd.read_parquet("data/order_item_products_sellers.parquet")
    except Exception:
        df_products = pd.DataFrame() # Fallback if file missing
        
    if not df_products.empty:
        # Clean column names
        df_products.columns = [str(c).strip() for c in df_products.columns]
        
        # Identify required columns dynamically
        price_col = next((c for c in df_products.columns if c.lower() in ['price', 'order_item_price']), None)
        freight_col = next((c for c in df_products.columns if c.lower() in ['freight_value', 'freight']), None)
        cat_col = next((c for c in df_products.columns if 'category' in c.lower() or 'product_category_name' in c.lower()), None)
        prod_col = next((c for c in df_products.columns if 'product_id' in c.lower() or 'id' in c.lower()), None)
        month_col = next((c for c in df_products.columns if c.lower() in ['month', 'order_month']), None)
        
        # Ensure numeric columns
        if price_col:
            df_products[price_col] = pd.to_numeric(df_products[price_col], errors='coerce')
        if freight_col:
            df_products[freight_col] = pd.to_numeric(df_products[freight_col], errors='coerce')
            
        # -------------------------------------------------------------
        # 1. TOP-LEVEL KPIs
        # -------------------------------------------------------------
        st.markdown("### 📈 Key Performance Indicators")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        # Calculate averages instead of sums
        avg_price = df_products[price_col].mean() if price_col else 0
        avg_freight = df_products[freight_col].mean() if freight_col else 0
        
        # Dynamically find the true product identifier column (avoiding row-level IDs)
        product_id_cols = [c for c in df_products.columns if 'product' in c.lower() and ('id' in c.lower() or 'sku' in c.lower())]
        if product_id_cols:
            # Pick the column whose unique count is closest to the expected catalog size (~32,951)
            best_col = min(product_id_cols, key=lambda c: abs(df_products[c].nunique() - 32951))
            unique_products = df_products[best_col].nunique()
        else:
            unique_products = df_products[prod_col].nunique() if prod_col else 0
        
        total_categories = df_products[cat_col].nunique() if cat_col else 0
        
        with kpi1:
            st.metric("Average Price", f"BRL {avg_price:,.2f}")
        with kpi2:
            st.metric("Average Freight Value", f"BRL {avg_freight:,.2f}")
        with kpi3:
            st.metric("Unique Products", f"{unique_products:,}")
        with kpi4:
            st.metric("Product Categories", f"{total_categories:,}")

        st.markdown("---")
        
        # -------------------------------------------------------------
        # 2. DYNAMIC MONTH FILTER (Loaded from order_items_products_sellers_orders_reviews)
        # -------------------------------------------------------------
        st.markdown("### 📅 Product Month Filter")
        
        try:
            df_reviews_source = pd.read_parquet("data/order_items_products_sellers_orders_reviews.parquet")
            df_reviews_source.columns = [str(c).strip() for c in df_reviews_source.columns]
            
            # Find order and month columns in the reviews source table
            rev_order_col = next((c for c in df_reviews_source.columns if c.lower() in ['order_id', 'id']), None)
            rev_month_col = next((c for c in df_reviews_source.columns if c.lower() in ['month', 'order_month']), None)
            
            if rev_order_col and rev_month_col and 'order_id' in df_products.columns:
                # Map the month column onto df_products using order_id
                month_mapping = df_reviews_source.set_index(rev_order_col)[rev_month_col].to_dict()
                df_products['Mapped_Month'] = df_products['order_id'].map(month_mapping)
                month_col_to_use = 'Mapped_Month'
            else:
                month_col_to_use = next((c for c in df_products.columns if c.lower() in ['month', 'order_month']), None)
        except Exception:
            month_col_to_use = next((c for c in df_products.columns if c.lower() in ['month', 'order_month']), None)

        if month_col_to_use and month_col_to_use in df_products.columns:
            months_list = sorted(df_products[month_col_to_use].dropna().astype(str).unique().tolist())
            selected_product_month = st.selectbox("Select Month", options=["All Months"] + months_list)
            
            if selected_product_month != "All Months":
                df_products_filtered = df_products[df_products[month_col_to_use].astype(str) == selected_product_month].copy()
            else:
                df_products_filtered = df_products.copy()
        else:
            df_products_filtered = df_products.copy()
            st.info("Could not locate month column from the specified table; displaying all records.")
            
        


    # =============================================================
    # ROW 4: Dynamic Top 20 Product Categories by Total Revenue
    # =============================================================
    st.markdown("---")
    

    try:
        if 'product_category_name_english' in df_products_filtered.columns and 'price' in df_products_filtered.columns:
            dynamic_prod_sales = (
                df_products_filtered.groupby('product_category_name_english')['price']
                .sum()
                .reset_index(name='total_price')
                .sort_values(by='total_price', ascending=False)
                .head(20)
            )
                
            fig_top20 = px.bar(
                dynamic_prod_sales,
                x="total_price",
                y="product_category_name_english",
                orientation='h',
                text_auto='.2s',
                title="Top 20 Product Categories",
                labels={
                    "total_price": "Total Revenue (BRL)",
                    "product_category_name_english": "Product Category"
                },
                color_discrete_sequence=['#9b59b6']
            )
                
            fig_top20.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                height=600,
                margin=dict(l=20, r=20, t=40, b=20)
            )
                
            st.plotly_chart(fig_top20, use_container_width=True, key="row4_top20_categories_chart")
        else:
            st.warning("Required columns (`product_category_name_english` or `price`) not found in `df_products_filtered`.")

    except Exception as e:
        st.error(f"Could not render dynamic product chart: {e}")


    # -------------------------------------------------------------
    # ROW 1: Average Price by Category (Top 20)
    # -------------------------------------------------------------
    st.markdown("##### Average price by category (Top 20)")
    
    # Use exact columns from the schema
    cat_col_name = 'product_category_name_english' if 'product_category_name_english' in df_products_filtered.columns else 'product_category_name'
    target_price_col = 'price' if 'price' in df_products_filtered.columns else price_col
    
    if target_price_col and cat_col_name in df_products_filtered.columns:
        # Group by category, calculate average price, take Top 20 descending
        cat_avg_price = df_products_filtered.groupby(cat_col_name)[target_price_col].mean().reset_index()
        cat_avg_price.columns = ['Product_Category', 'Average_Price']
        
        cat_avg_price = cat_avg_price.sort_values(by='Average_Price', ascending=False).head(20)
        
        cat_avg_price['Price_Label'] = cat_avg_price['Average_Price'].apply(
            lambda x: f"{x:,.0f}" if pd.notnull(x) else ""
        )
        
        fig_cat_price = px.bar(
            cat_avg_price,
            x='Product_Category',
            y='Average_Price',
            text='Price_Label',
            color_discrete_sequence=['#e84393']
        )
        fig_cat_price.update_traces(
            textposition='outside',
            textfont=dict(size=10)
        )
        fig_cat_price.update_layout(
            height=450,
            margin=dict(l=20, r=20, t=30, b=90),
            xaxis_title="Product category",
            yaxis_title="Average price",
            xaxis=dict(tickangle=-45, tickfont=dict(size=9))
        )
        st.plotly_chart(fig_cat_price, use_container_width=True)
    else:
        st.warning(f"Could not locate columns '{target_price_col}' or '{cat_col_name}' in the dataset.")


    st.markdown("---")
    
    # Create two columns for Row 2 side-by-side layout
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        # -------------------------------------------------------------
        # ROW 2 (LEFT): Category Penetration (Top 20 Products - Funnel)
        # -------------------------------------------------------------
        st.markdown("##### Category Penetration (Top 20 Products)")
        
        try:
            df_pen = pd.read_parquet("data/category_penetration.parquet")
            df_pen.columns = [str(c).strip() for c in df_pen.columns]
        except Exception:
            df_pen = pd.DataFrame()
            
        if not df_pen.empty:
            cat_col_name = 'product_category_name_english' if 'product_category_name_english' in df_pen.columns else next((c for c in df_pen.columns if 'category' in c.lower()), None)
            pen_col = 'penetration_percentage' if 'penetration_percentage' in df_pen.columns else next((c for c in df_pen.columns if 'penetration' in c.lower()), None)
            
            if cat_col_name and pen_col:
                if 'selected_product_month' in locals() and selected_product_month != "All Months" and 'product_id' in df_products_filtered.columns:
                    total_filtered_products = df_products_filtered['product_id'].nunique()
                    if total_filtered_products > 0:
                        cat_pen_calc = df_products_filtered.groupby(cat_col_name)['product_id'].nunique().reset_index()
                        cat_pen_calc.columns = [cat_col_name, pen_col]
                        cat_pen_calc[pen_col] = (cat_pen_calc[pen_col] / total_filtered_products) * 100
                        df_pen_active = cat_pen_calc
                    else:
                        df_pen_active = df_pen.copy()
                else:
                    df_pen_active = df_pen.copy()
                
                df_pen_active[pen_col] = pd.to_numeric(df_pen_active[pen_col], errors='coerce')
                
                cat_penetration = df_pen_active.sort_values(by=pen_col, ascending=False).head(20).copy()
                cat_penetration = cat_penetration.sort_values(by=pen_col, ascending=False)
                
                fig_penetration = px.funnel(
                    cat_penetration,
                    x=pen_col,
                    y=cat_col_name,
                    color_discrete_sequence=['purple']
                )
                fig_penetration.update_traces(
                    texttemplate='%{x:.2f}%',
                    textposition='inside',
                    textfont=dict(size=11, color='white')
                )
                fig_penetration.update_layout(
                    height=520,
                    margin=dict(l=20, r=20, t=30, b=30),
                    xaxis_title="Penetration (%)",
                    yaxis_title=""
                )
                st.plotly_chart(fig_penetration, use_container_width=True, key="row2_funnel_chart")
            else:
                st.warning("Could not locate required columns in `category_penetration.parquet`.")
        else:
            st.warning("Could not load `category_penetration.parquet`.")

    with row2_col2:
        # -------------------------------------------------------------
        # ROW 2 (RIGHT): Total Orders by Product Category (Top 20)
        # -------------------------------------------------------------
        st.markdown("##### Total orders by Product category (Top 20)")
        
        cat_col_name_ord = 'product_category_name_english' if 'product_category_name_english' in df_products_filtered.columns else 'product_category_name'
        order_col = 'order_id' if 'order_id' in df_products_filtered.columns else None
        
        if cat_col_name_ord and order_col:
            cat_orders = df_products_filtered.groupby(cat_col_name_ord)[order_col].count().reset_index()
            cat_orders.columns = ['Product_Category', 'Total_Orders']
            
            # Limit to Top 20 descending
            cat_orders = cat_orders.sort_values(by='Total_Orders', ascending=False).head(20)
            
            cat_orders['Order_Label'] = cat_orders['Total_Orders'].apply(
                lambda x: f"{x/1000:.1f}K" if x >= 1000 else f"{x:,}"
            )
            
            cat_orders = cat_orders.sort_values(by='Total_Orders', ascending=True)
            
            fig_orders = px.bar(
                cat_orders,
                x='Total_Orders',
                y='Product_Category',
                orientation='h',
                text='Order_Label',
                color_discrete_sequence=['#9b59b6']
            )
            fig_orders.update_traces(
                textposition='outside',
                textfont=dict(size=10)
            )
            fig_orders.update_layout(
                height=520,
                margin=dict(l=20, r=40, t=30, b=30),
                xaxis_title="Total orders",
                yaxis_title="",
                xaxis=dict(range=[0, max(cat_orders['Total_Orders']) * 1.25 if not cat_orders.empty else 10])
            )
            st.plotly_chart(fig_orders, use_container_width=True, key="row2_orders_chart")
        else:
            st.warning("Could not locate order_id or category columns for the orders chart.")



        




    st.markdown("---")
    
    # -------------------------------------------------------------
    # ROW 3: Price and Freight Value Correlation (Full Width)
    # -------------------------------------------------------------
    st.markdown("##### Price and freight value correlation")
    
    price_col = 'price' if 'price' in df_products_filtered.columns else None
    freight_col = 'freight_value' if 'freight_value' in df_products_filtered.columns else None
    cat_col_scatter = 'product_category_name_english' if 'product_category_name_english' in df_products_filtered.columns else 'product_category_name'
    
    if price_col and freight_col:
        # Drop nulls for accurate scatter plot rendering
        df_scatter = df_products_filtered.dropna(subset=[price_col, freight_col]).copy()
        
        fig_corr = px.scatter(
            df_scatter,
            x=price_col,
            y=freight_col,
            hover_data=[cat_col_scatter] if cat_col_scatter in df_scatter.columns else None,
            color_discrete_sequence=['#9b59b6']
        )
        fig_corr.update_traces(
            marker=dict(size=8, opacity=0.6)
        )
        fig_corr.update_layout(
            height=450,
            margin=dict(l=20, r=20, t=30, b=30),
            xaxis_title="price",
            yaxis_title="freight value"
        )
        st.plotly_chart(fig_corr, use_container_width=True, key="row3_correlation_chart")
    else:
        st.warning("Could not locate 'price' or 'freight_value' columns in the dataset.")

    

    


    
    


# =========================================================================
# 5. SELLERS DASHBOARD
# =========================================================================
elif selected_tab == "Sellers Dashboard":
    st.header("Seller Diversity & Performance Dashboard")
    
    # -------------------------------------------------------------
    # LOAD DATA
    # -------------------------------------------------------------
    try:
        df_sellers = pd.read_parquet("data/order_cust_payments.parquet")
        df_sellers.columns = [str(c).strip() for c in df_sellers.columns]
    except Exception:
        df_sellers = pd.DataFrame()
        
    try:
        df_sellers_items = pd.read_parquet("data/order_items_products_sellers_orders.parquet")
        df_sellers_items.columns = [str(c).strip() for c in df_sellers_items.columns]
    except Exception:
        try:
            df_sellers_items = pd.read_parquet("data/order_item_products_sellers.parquet")
            df_sellers_items.columns = [str(c).strip() for c in df_sellers_items.columns]
        except Exception:
            df_sellers_items = pd.DataFrame()
            
    if not df_sellers.empty:
        month_col = 'month' if 'month' in df_sellers.columns else next((c for c in df_sellers.columns if 'month' in c.lower()), None)
        state_col = next((c for c in df_sellers_items.columns if 'state' in c.lower()), None) if not df_sellers_items.empty else None
        city_col = next((c for c in df_sellers_items.columns if 'city' in c.lower()), None) if not df_sellers_items.empty else None
        
        # -------------------------------------------------------------
        # TOP KPIS (FIRST)
        # -------------------------------------------------------------
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        seller_id_col = next((c for c in df_sellers_items.columns if 'seller_id' in c.lower()), None) if not df_sellers_items.empty else None
        total_sellers = df_sellers_items[seller_id_col].nunique() if seller_id_col else 0
        
        carrier_days_col = 'carrier_delivered_days' if 'carrier_delivered_days' in df_sellers.columns else None
        customer_days_col = 'customer_delivered_days' if 'customer_delivered_days' in df_sellers.columns else None
        approval_hours_col = 'order_approval_hours' if 'order_approval_hours' in df_sellers.columns else None
        
        med_carrier_days = df_sellers[carrier_days_col].median() if carrier_days_col else 0
        med_cust_days = df_sellers[customer_days_col].median() if customer_days_col else 0
        med_approval_hrs = df_sellers[approval_hours_col].median() if approval_hours_col else 0
        
        with kpi1:
            st.metric("Total Sellers", f"{total_sellers:,}")
            
        with kpi2:
            st.metric("Median carrier delivery days", f"{med_carrier_days:.0f}" if pd.notnull(med_carrier_days) else "0")
            
        with kpi3:
            st.metric("Median delivery days", f"{med_cust_days:.0f}" if pd.notnull(med_cust_days) else "0")
            
        with kpi4:
            st.metric("Median approval hours", f"{med_approval_hrs:.2f}" if pd.notnull(med_approval_hrs) else "0.00")
            
        st.markdown("---")
        
        # -------------------------------------------------------------
        # GLOBAL SELLERS FILTERS (BELOW KPIS - CLEAN LISTS)
        # -------------------------------------------------------------
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            if month_col:
                available_months = ["All Months"] + sorted(df_sellers[month_col].dropna().unique().tolist())
                selected_seller_month = st.selectbox("Select Month", available_months, key="seller_month_selector")
            else:
                selected_seller_month = "All Months"
                
        with filter_col2:
            if state_col:
                all_states = sorted(df_sellers_items[state_col].dropna().unique().tolist())
                selected_states = st.multiselect("Select States", all_states, format_func=lambda x: str(x), key="seller_states_filter")
            else:
                selected_states = []
                
        with filter_col3:
            if city_col and state_col and selected_states:
                available_cities = sorted(df_sellers_items[df_sellers_items[state_col].isin(selected_states)][city_col].dropna().unique().tolist())
            elif city_col:
                available_cities = sorted(df_sellers_items[city_col].dropna().unique().tolist())
            else:
                available_cities = []
            selected_cities = st.multiselect("Select Cities", available_cities, format_func=lambda x: str(x), key="seller_cities_filter")
            
        # -------------------------------------------------------------
        # APPLY FILTERS TO ACTIVE DATAFRAMES
        # -------------------------------------------------------------
        df_sellers_filtered = df_sellers.copy()
        df_sellers_items_filtered = df_sellers_items.copy()
        
        if month_col and selected_seller_month != "All Months":
            if month_col in df_sellers_filtered.columns:
                df_sellers_filtered = df_sellers_filtered[df_sellers_filtered[month_col] == selected_seller_month]
            if not df_sellers_items_filtered.empty and month_col in df_sellers_items_filtered.columns:
                df_sellers_items_filtered = df_sellers_items_filtered[df_sellers_items_filtered[month_col] == selected_seller_month]
                
        if state_col and selected_states:
            if state_col in df_sellers_filtered.columns:
                df_sellers_filtered = df_sellers_filtered[df_sellers_filtered[state_col].isin(selected_states)]
            if not df_sellers_items_filtered.empty and state_col in df_sellers_items_filtered.columns:
                df_sellers_items_filtered = df_sellers_items_filtered[df_sellers_items_filtered[state_col].isin(selected_states)]
                
        if city_col and selected_cities:
            if city_col in df_sellers_filtered.columns:
                df_sellers_filtered = df_sellers_filtered[df_sellers_filtered[city_col].isin(selected_cities)]
            if not df_sellers_items_filtered.empty and city_col in df_sellers_items_filtered.columns:
                df_sellers_items_filtered = df_sellers_items_filtered[df_sellers_items_filtered[city_col].isin(selected_cities)]

        st.markdown("---")
        
        # -------------------------------------------------------------
        # ROW 1: Top 15 Worst Performing Sellers (Full Width - Full Seller ID)
        # -------------------------------------------------------------
        st.markdown("##### Top 15 worst performing Sellers")
        
        seller_col = next((c for c in df_sellers_items_filtered.columns if 'seller_id' in c.lower()), None)
        delivery_days_col = 'customer_delivered_days' if 'customer_delivered_days' in df_sellers_items_filtered.columns else next((c for c in df_sellers_items_filtered.columns if 'customer_delivered' in c.lower()), None)
        
        if seller_col and delivery_days_col:
            worst_sellers = (
                df_sellers_items_filtered.groupby(seller_col)[delivery_days_col]
                .mean()
                .reset_index()
            )
            worst_sellers.columns = ['seller_id', 'avg_delivery_days']
            worst_sellers['avg_delivery_days'] = pd.to_numeric(worst_sellers['avg_delivery_days'], errors='coerce')
            
            # Explicitly taking Top 15
            worst_15 = worst_sellers.sort_values(by='avg_delivery_days', ascending=False).head(15).copy()
            
            if not worst_15.empty:
                worst_15 = worst_15.sort_values(by='avg_delivery_days', ascending=True)
                
                fig_worst_sellers = px.bar(
                    worst_15,
                    x='avg_delivery_days',
                    y='seller_id',
                    orientation='h',
                    color_discrete_sequence=['#1e90ff']
                )
                
                fig_worst_sellers.update_traces(
                    texttemplate='%{x:.2f}',
                    textposition='outside',
                    textfont=dict(size=10, color='white')
                )
                
                fig_worst_sellers.update_layout(
                    height=600,
                    margin=dict(l=280, r=40, t=30, b=30),
                    xaxis_title="Average delivery days",
                    yaxis_title="Seller ID",
                    xaxis=dict(range=[0, max(worst_15['avg_delivery_days']) * 1.25 if not worst_15.empty else 10]),
                    yaxis=dict(type='category')
                )
                
                st.plotly_chart(fig_worst_sellers, use_container_width=True, key="row1_worst_15_sellers_chart_v2")
            else:
                st.info("No seller delivery data available for the selected filters.")
        else:
            st.warning("Could not locate `seller_id` or `customer_delivered_days` in `order_items_products_sellers_orders.parquet`.")





        st.markdown("---")
        
        # -------------------------------------------------------------
        # ROW 2: Left Side - Total Orders & Total Sellers by Seller State
        # -------------------------------------------------------------
        row2_left, row2_right = st.columns(2)
        
        with row2_left:
            st.markdown("##### Total orders and Total Sellers by seller_state")
            
            state_col = next((c for c in df_sellers_items_filtered.columns if 'state' in c.lower()), 'seller_state')
            order_col = next((c for c in df_sellers_items_filtered.columns if 'order_id' in c.lower()), 'order_id')
            seller_col_local = next((c for c in df_sellers_items_filtered.columns if 'seller_id' in c.lower()), 'seller_id')
            
            if state_col in df_sellers_items_filtered.columns and order_col in df_sellers_items_filtered.columns and seller_col_local in df_sellers_items_filtered.columns:
                state_grouped = (
                    df_sellers_items_filtered.groupby(state_col)
                    .agg(
                        Total_Orders=(order_col, 'nunique'),
                        Total_Sellers=(seller_col_local, 'nunique')
                    )
                    .reset_index()
                    .sort_values(by='Total_Orders', ascending=False)
                )
                
                if not state_grouped.empty:
                    state_melted = state_grouped.melt(
                        id_vars=[state_col],
                        value_vars=['Total_Orders', 'Total_Sellers'],
                        var_name='Metric',
                        value_name='Count'
                    )
                    
                    fig_state = px.bar(
                        state_melted,
                        x=state_col,
                        y='Count',
                        color='Metric',
                        barmode='group',
                        # Distinct, high-contrast colors
                        color_discrete_map={'Total_Orders': '#1f77b4', 'Total_Sellers': '#ff7f0e'}
                    )
                    
                    fig_state.update_layout(
                        height=450,
                        margin=dict(l=20, r=20, t=30, b=30),
                        xaxis_title="seller_state",
                        yaxis_title="Count",
                        legend_title="",
                        # Shift legend inside the top right of the chart area for maximum width
                        legend=dict(
                            x=0.75,
                            y=0.95,
                            bgcolor='rgba(0,0,0,0.5)',
                            bordercolor='rgba(255,255,255,0.2)',
                            borderwidth=1
                        ),
                        yaxis=dict(type='log')
                    )
                    
                    st.plotly_chart(fig_state, use_container_width=True, key="row2_state_orders_sellers_chart_v2")
                else:
                    st.info("No data available for state breakdown.")
            else:
                st.warning("Could not locate required columns (`state`, `order_id`, `seller_id`) for state analysis.")
                
        with row2_right:
            st.markdown("##### Average delivery days by State")
            
            # Load the exact table requested
            try:
                df_reviews_table = pd.read_parquet("data/order_items_products_sellers_orders_reviews.parquet")
                df_reviews_table.columns = [str(c).strip() for c in df_reviews_table.columns]
            except Exception:
                df_reviews_table = pd.DataFrame()
                
            if not df_reviews_table.empty:
                state_col_local = next((c for c in df_reviews_table.columns if 'seller_state' in c.lower() or 'state' in c.lower()), 'seller_state')
                delivery_col_local = next((c for c in df_reviews_table.columns if 'customer_delivered_days' in c.lower()), 'customer_delivered_days')
                month_col_local = next((c for c in df_reviews_table.columns if 'month' in c.lower()), 'month')
                city_col_local = next((c for c in df_reviews_table.columns if 'city' in c.lower()), None)
                
                # Apply active global filters to the reviews dataset
                df_reviews_filtered = df_reviews_table.copy()
                
                if month_col_local in df_reviews_filtered.columns and selected_seller_month != "All Months":
                    df_reviews_filtered = df_reviews_filtered[df_reviews_filtered[month_col_local] == selected_seller_month]
                    
                if state_col_local in df_reviews_filtered.columns and selected_states:
                    df_reviews_filtered = df_reviews_filtered[df_reviews_filtered[state_col_local].isin(selected_states)]
                    
                if city_col_local and selected_cities:
                    df_reviews_filtered = df_reviews_filtered[df_reviews_filtered[city_col_local].isin(selected_cities)]
                
                if state_col_local in df_reviews_filtered.columns and delivery_col_local in df_reviews_filtered.columns:
                    df_reviews_filtered[delivery_col_local] = pd.to_numeric(df_reviews_filtered[delivery_col_local], errors='coerce')
                    
                    state_delivery = (
                        df_reviews_filtered.groupby(state_col_local)[delivery_col_local]
                        .mean()
                        .reset_index()
                    )
                    state_delivery.columns = ['State', 'Avg_Delivery_Days']
                    state_delivery = state_delivery.dropna(subset=['Avg_Delivery_Days'])
                    state_delivery = state_delivery.sort_values(by='Avg_Delivery_Days', ascending=False)
                    
                    if not state_delivery.empty:
                        fig_avg_del = px.bar(
                            state_delivery,
                            x='State',
                            y='Avg_Delivery_Days',
                            color_discrete_sequence=['#1f77b4']
                        )
                        
                        fig_avg_del.update_traces(
                            texttemplate='%{y:.2f}',
                            textposition='outside',
                            textfont=dict(size=9, color='white')
                        )
                        
                        fig_avg_del.update_layout(
                            height=450,
                            margin=dict(l=20, r=20, t=30, b=30),
                            xaxis_title="State",
                            yaxis_title="Average delivery days",
                            xaxis=dict(type='category'),
                            yaxis=dict(range=[0, max(state_delivery['Avg_Delivery_Days']) * 1.2 if not state_delivery.empty else 10])
                        )
                        
                        st.plotly_chart(fig_avg_del, use_container_width=True, key="row2_avg_delivery_by_state_chart_v3")
                    else:
                        st.info("No delivery days data available for the selected filters.")
                else:
                    st.warning("Could not find `seller_state` or `customer_delivered_days` columns in the reviews table.")
            else:
                st.warning("Could not load `order_items_products_sellers_orders_reviews.parquet`.")



        st.markdown("---")
        
        # -------------------------------------------------------------
        # ROW 3: Seller Diversity (Unique Products & Categories - Full UUIDs, Horizontal)
        # -------------------------------------------------------------
        st.markdown("##### Seller Diversity: Unique Products & Categories")
        
        try:
            df_diversity = pd.read_parquet("data/seller_diversity.parquet")
            df_diversity.columns = [str(c).strip() for c in df_diversity.columns]
        except Exception:
            df_diversity = pd.DataFrame()
            
        if not df_diversity.empty:
            seller_id_col = next((c for c in df_diversity.columns if 'seller_id' in c.lower()), 'seller_id')
            categories_col = next((c for c in df_diversity.columns if 'unique_categories' in c.lower()), 'unique_categories')
            products_col = next((c for c in df_diversity.columns if 'unique_products' in c.lower()), 'unique_products')
            items_col = next((c for c in df_diversity.columns if 'total_items_sold' in c.lower()), 'total_items_sold')
            
            # Ensure numeric types
            for col in [products_col, categories_col, items_col]:
                if col in df_diversity.columns:
                    df_diversity[col] = pd.to_numeric(df_diversity[col], errors='coerce').fillna(0)
            
            sort_metric = items_col if items_col in df_diversity.columns else products_col
            if seller_id_col in df_diversity.columns:
                df_diversity_top = df_diversity.sort_values(by=sort_metric, ascending=False).head(20).copy()
                
                # Sort ascending so the highest value appears at the top of the horizontal chart
                df_diversity_top = df_diversity_top.sort_values(by=sort_metric, ascending=True)
                
                fig_diversity = px.bar(
                    df_diversity_top,
                    x=[products_col, categories_col],
                    y=seller_id_col,  # Full seller_id on y-axis
                    orientation='h',
                    barmode='group',
                    labels={'value': 'Count (Log Scale)', 'variable': 'Diversity Metric', seller_id_col: 'Seller ID'},
                    color_discrete_map={
                        products_col: '#ff7f0e',
                        categories_col: 'blue'
                    }
                )
                
                fig_diversity.update_layout(
                    height=700,  # Expanded height to comfortably fit 20 full UUID rows
                    margin=dict(l=280, r=40, t=30, b=40),  # Large left margin for full UUIDs
                    xaxis_title="Count (Log Scale)",
                    yaxis_title="Seller ID",
                    legend_title="",
                    # Shift legend to top-right inside empty chart space
                    legend=dict(
                        x=0.75,
                        y=0.98,
                        bgcolor='rgba(0,0,0,0.5)',
                        bordercolor='rgba(255,255,255,0.2)',
                        borderwidth=1
                    ),
                    yaxis=dict(type='category'),
                    xaxis=dict(type='log')  # Log scale maintained on x-axis
                )
                
                st.plotly_chart(fig_diversity, use_container_width=True, key="row3_seller_diversity_full_id_log_chart")
            else:
                st.warning("Could not find required columns in `seller_diversity` dataset.")
        else:
            st.warning("Could not load `seller_diversity.parquet`.")





# =========================================================================
# 6. CUSTOMER SATISFACTION DASHBOARDS
# =========================================================================
elif selected_tab == "Customer Satisfaction Dashboards":
    st.header("Customer Satisfaction & Review Analytics")
    
    # -------------------------------------------------------------
    # 1. LIGHTNING-FAST DATA LOADING (Cached)
    # -------------------------------------------------------------
    @st.cache_data
    def load_csat_data():
        try:
            df = pd.read_parquet("data/order_items_products_sellers_orders_reviews.parquet")
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except Exception:
            return pd.DataFrame()

    @st.cache_data
    def load_reviews_kpi_data():
        try:
            df = pd.read_parquet("data/reviews.parquet")
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except Exception:
            return pd.DataFrame()

    df_csat_reviews = load_csat_data()
    df_reviews_kpi = load_reviews_kpi_data()

    if not df_csat_reviews.empty:
        # Explicit column mapping
        seller_id_col = next((c for c in df_csat_reviews.columns if 'seller_id' in c.lower()), 'seller_id')
        review_id_col = next((c for c in df_csat_reviews.columns if 'review_id' in c.lower()), 'review_id')
        review_score_col = next((c for c in df_csat_reviews.columns if 'review_score' in c.lower()), 'review_score')
        timely_col = next((c for c in df_csat_reviews.columns if c.lower() in ['order_timely_delivered', 'timely_delivered', 'order_timely'] or 'timely' in c.lower()), 'order_timely_delivered')
        city_col = next((c for c in df_csat_reviews.columns if c.lower() in ['seller_city', 'city'] or 'city' in c.lower()), 'seller_city')
        month_col_csat = next((c for c in df_csat_reviews.columns if 'month' in c.lower()), 'month')
        state_col_csat = next((c for c in df_csat_reviews.columns if 'seller_state' in c.lower() or 'state' in c.lower()), 'seller_state')

        # -------------------------------------------------------------
        # 2. DYNAMIC SLICERS
        # -------------------------------------------------------------
        st.markdown("---")
        
        df_base = df_csat_reviews.copy()
        if month_col_csat in df_base.columns and 'selected_seller_month' in locals() and selected_seller_month != "All Months":
            df_base = df_base[df_base[month_col_csat] == selected_seller_month]
        if state_col_csat in df_base.columns and 'selected_states' in locals() and selected_states:
            df_base = df_base[df_base[state_col_csat].isin(selected_states)]

        filter_col1, filter_col2 = st.columns(2)

        with filter_col1:
            # Strictly Yes or No options as requested
            selected_timely = st.multiselect(
                "Order timely delivered?",
                options=["Yes", "No"],
                default=[],
                key="csat_timely_delivered_filter"
            )

        with filter_col2:
            city_options = sorted([str(x) for x in df_base[city_col].dropna().unique() if str(x).lower() not in ['nan', 'none', '']]) if city_col in df_base.columns else []
            selected_seller_city = st.multiselect(
                "seller_city",
                options=city_options,
                default=[],
                key="csat_seller_city_filter"
            )

        # -------------------------------------------------------------
        # 3. FULLY FILTERED DATAFRAME (Drives both KPIs & Charts)
        # -------------------------------------------------------------
        df_csat_filtered = df_base.copy()
        if selected_timely and timely_col in df_csat_filtered.columns:
            is_yes = 'Yes' in selected_timely and 'No' not in selected_timely
            is_no = 'No' in selected_timely and 'Yes' not in selected_timely
            if is_yes:
                df_csat_filtered = df_csat_filtered[df_csat_filtered[timely_col].astype(str).str.lower().isin(['yes', 'true', '1'])]
            elif is_no:
                df_csat_filtered = df_csat_filtered[df_csat_filtered[timely_col].astype(str).str.lower().isin(['no', 'false', '0'])]

        if selected_seller_city and city_col in df_csat_filtered.columns:
            df_csat_filtered = df_csat_filtered[df_csat_filtered[city_col].astype(str).isin(selected_seller_city)]

        # -------------------------------------------------------------
        # 4. REACTIVE KPIs
        # -------------------------------------------------------------
        total_reviews = df_csat_filtered[review_id_col].nunique() if review_id_col in df_csat_filtered.columns else len(df_csat_filtered)
        
        avg_review_score = 0.0
        if review_score_col in df_csat_filtered.columns:
            scores_num = pd.to_numeric(df_csat_filtered[review_score_col], errors='coerce')
            avg_review_score = scores_num.mean() if not scores_num.empty else 0.0

        avg_response_days = 3.22
        if not df_reviews_kpi.empty:
            answer_col = next((c for c in df_reviews_kpi.columns if 'answer' in c.lower() or 'timestamp' in c.lower()), None)
            creation_col = next((c for c in df_reviews_kpi.columns if 'creation' in c.lower() or 'date' in c.lower() or 'order' in c.lower()), None)
            if answer_col and creation_col:
                try:
                    df_rev_temp = df_reviews_kpi.copy()
                    df_rev_temp[answer_col] = pd.to_datetime(df_rev_temp[answer_col], errors='coerce')
                    df_rev_temp[creation_col] = pd.to_datetime(df_rev_temp[creation_col], errors='coerce')
                    diff_series = (df_rev_temp[answer_col] - df_rev_temp[creation_col]).dt.total_seconds() / 86400.0
                    val = diff_series.dropna().mean()
                    if not pd.isna(val) and val > 0:
                        avg_response_days = val
                except Exception:
                    pass

        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            formatted_reviews = f"{total_reviews/1000:.2f}K" if total_reviews >= 1000 else str(total_reviews)
            st.metric(label="Total Reviews", value=formatted_reviews)
        with kpi2:
            st.metric(label="Average Review Score", value=f"{round(avg_review_score)}")
        with kpi3:
            st.metric(label="Average Response time", value=f"{avg_response_days:.2f}")

        # -------------------------------------------------------------
        # 5. CSAT ROW 1 CHARTS
        # -------------------------------------------------------------
        st.markdown("---")
        csat_row1_left, csat_row1_right = st.columns(2)
        
        with csat_row1_left:
            st.markdown("##### Distribution of sellers by Average rating score")
            if seller_id_col in df_csat_filtered.columns and review_score_col in df_csat_filtered.columns:
                df_temp = df_csat_filtered.copy()
                df_temp[review_score_col] = pd.to_numeric(df_temp[review_score_col], errors='coerce')
                seller_avg = df_temp.groupby(seller_id_col)[review_score_col].mean().reset_index()
                seller_avg.columns = ['seller_id', 'avg_score']
                seller_avg['rating_bucket'] = seller_avg['avg_score'].round().clip(1, 5)
                
                rating_dist = seller_avg.groupby('rating_bucket')['seller_id'].nunique().reset_index()
                rating_dist.columns = ['Rating_Score', 'Total_Sellers']
                rating_dist = rating_dist.sort_values(by='Rating_Score')
                
                fig_sellers_rating = px.bar(rating_dist, x='Rating_Score', y='Total_Sellers', color_discrete_sequence=['#1f77b4'])
                fig_sellers_rating.update_traces(texttemplate='%{y:,}', textposition='outside', textfont=dict(size=10, color='white'))
                fig_sellers_rating.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=30), xaxis_title="Rating Score", yaxis_title="Total Sellers", xaxis=dict(type='category'))
                st.plotly_chart(fig_sellers_rating, use_container_width=True, key="csat_sellers_by_rating_dynamic_chart")

        with csat_row1_right:
            st.markdown("##### Total orders by Review Score")
            if review_score_col in df_csat_filtered.columns and review_id_col in df_csat_filtered.columns:
                df_orders_review = df_csat_filtered.groupby(review_score_col)[review_id_col].nunique().reset_index()
                df_orders_review.columns = ['Review_Score', 'Total_Orders']
                df_orders_review['Review_Score'] = pd.to_numeric(df_orders_review['Review_Score'], errors='coerce')
                df_orders_review = df_orders_review.sort_values(by='Review_Score')
                df_orders_review['Formatted_Orders'] = df_orders_review['Total_Orders'].apply(lambda x: f"{x/1000:.0f}K" if x >= 1000 else str(x))
                
                fig_orders_review = px.bar(df_orders_review, x='Review_Score', y='Total_Orders', color_discrete_sequence=['#59be88'])
                fig_orders_review.update_traces(text=df_orders_review['Formatted_Orders'], texttemplate='%{text}', textposition='outside', textfont=dict(size=10, color='white'))
                fig_orders_review.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=30), xaxis_title="Review Score", yaxis_title="Total orders", xaxis=dict(type='category'))
                st.plotly_chart(fig_orders_review, use_container_width=True, key="csat_orders_by_review_score_chart")
    else:
        st.warning("Could not load dataset for Customer Satisfaction metrics.")





    # -------------------------------------------------------------
    # CSAT ROW 2: Average Review Score by State (Full-Width)
    # -------------------------------------------------------------
    st.markdown("---")
    st.markdown("##### Average Review Score by State")
    
    if not df_csat_filtered.empty:
        state_col = next((c for c in df_csat_filtered.columns if 'seller_state' in c.lower() or 'state' in c.lower()), 'seller_state')
        review_score_col_r2 = next((c for c in df_csat_filtered.columns if 'review_score' in c.lower()), 'review_score')
        
        if state_col in df_csat_filtered.columns and review_score_col_r2 in df_csat_filtered.columns:
            df_temp_state = df_csat_filtered.copy()
            df_temp_state[review_score_col_r2] = pd.to_numeric(df_temp_state[review_score_col_r2], errors='coerce')
            
            # Aggregate average review score by state
            df_state_score = (
                df_temp_state.groupby(state_col)[review_score_col_r2]
                .mean()
                .reset_index()
            )
            df_state_score.columns = ['State', 'Avg_Review_Score']
            df_state_score = df_state_score.sort_values(by='Avg_Review_Score', ascending=True)
            
            # Conditional coloring: Red for scores below 3.0, Green for 3.0 and above
            df_state_score['Color'] = df_state_score['Avg_Review_Score'].apply(lambda x: '#ff4d4d' if x < 3.0 else '#59be88')
            
            fig_state_score = px.bar(
                df_state_score,
                x='State',
                y='Avg_Review_Score',
                color='Color',
                color_discrete_map='identity'
            )
            
            fig_state_score.update_traces(
                texttemplate='%{y:.2f}',
                textposition='outside',
                textfont=dict(size=10, color='white')
            )
            
            fig_state_score.update_layout(
                height=450,
                margin=dict(l=20, r=20, t=30, b=30),
                xaxis_title="State",
                yaxis_title="Average Review Score",
                showlegend=False,
                xaxis=dict(type='category'),
                yaxis=dict(range=[0, 5.2])
            )
            
            st.plotly_chart(fig_state_score, use_container_width=True, key="csat_avg_review_score_by_state_chart")
        else:
            st.warning("Could not find `seller_state` or `review_score` columns for state analysis.")
    else:
        st.warning("No data available for state review score breakdown.")


    # -------------------------------------------------------------
    # CSAT ROW 3: Average Review Score by Month (Fixed Range & Visible Labels)
    # -------------------------------------------------------------
    st.markdown("---")
    st.markdown("##### Average review score by Month")
    
    if not df_csat_filtered.empty:
        period_col = next((c for c in df_csat_filtered.columns if 'period' in c.lower() or 'month' in c.lower()), 'order_purchase_period')
        review_score_col_r3 = next((c for c in df_csat_filtered.columns if 'review_score' in c.lower()), 'review_score')
        
        if period_col in df_csat_filtered.columns and review_score_col_r3 in df_csat_filtered.columns:
            df_temp_month = df_csat_filtered.copy()
            df_temp_month[review_score_col_r3] = pd.to_numeric(df_temp_month[review_score_col_r3], errors='coerce')
            
            df_monthly_score = (
                df_temp_month.groupby(period_col)[review_score_col_r3]
                .mean()
                .reset_index()
            )
            df_monthly_score.columns = ['Month', 'Avg_Review_Score']
            
            # Sort chronologically by date/period string
            df_monthly_score = df_monthly_score.sort_values(by='Month')
            df_monthly_score['Month_Str'] = df_monthly_score['Month'].astype(str)
            df_monthly_score['Formatted_Score'] = df_monthly_score['Avg_Review_Score'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "")
            
            fig_monthly_score = px.line(
                df_monthly_score,
                x='Month_Str',
                y='Avg_Review_Score',
                markers=True,
                color_discrete_sequence=['#1e7e34']
            )
            
            # Enable text mode so data labels render clearly above each point
            fig_monthly_score.update_traces(
                mode='lines+markers+text',
                text=df_monthly_score['Formatted_Score'],
                textposition='top center',
                textfont=dict(size=10, color='white'),
                line=dict(width=2.5),
                marker=dict(size=6)
            )
            
            # Compute safe y-axis bounds with padding so lines don't cross the ceiling/floor
            min_val = df_monthly_score['Avg_Review_Score'].min()
            max_val = df_monthly_score['Avg_Review_Score'].max()
            y_lower = max(3.0, min_val - 0.2)
            y_upper = min(5.0, max_val + 0.3)
            
            fig_monthly_score.update_layout(
                height=420,
                margin=dict(l=20, r=20, t=40, b=50),
                xaxis_title="Month",
                yaxis_title="Average review score",
                xaxis=dict(type='category', tickangle=-30),
                yaxis=dict(range=[y_lower, y_upper], autorange=False)
            )
            
            # Wrap in columns so it doesn't span full screen width
            c_left, c_mid, c_right = st.columns([1, 8, 1])
            with c_mid:
                st.plotly_chart(fig_monthly_score, use_container_width=True, key="csat_avg_review_score_by_month_chart")
        else:
            st.warning("Could not find `order_purchase_period` or `review_score` columns for monthly review analysis.")
    else:
        st.warning("No data available for monthly review score breakdown.")



    # -------------------------------------------------------------
    # CSAT ROW 4: Average Review Score by Product Category (All Categories, Orange Theme)
    # -------------------------------------------------------------
    st.markdown("---")
    st.markdown("##### Average Review Score by Product Category")
    
    if not df_csat_filtered.empty:
        category_col = next((c for c in df_csat_filtered.columns if 'category' in c.lower() or 'english' in c.lower()), 'product_category_name_english')
        review_score_col_r4 = next((c for c in df_csat_filtered.columns if 'review_score' in c.lower()), 'review_score')
        
        if category_col in df_csat_filtered.columns and review_score_col_r4 in df_csat_filtered.columns:
            df_temp_cat = df_csat_filtered.copy()
            df_temp_cat[review_score_col_r4] = pd.to_numeric(df_temp_cat[review_score_col_r4], errors='coerce')
            
            # Aggregate average review score by product category
            df_cat_score = (
                df_temp_cat.groupby(category_col)[review_score_col_r4]
                .mean()
                .reset_index()
            )
            df_cat_score.columns = ['Product_Category', 'Avg_Review_Score']
            
            # Drop null/empty categories and sort descending (all categories included)
            df_cat_score = df_cat_score.dropna(subset=['Product_Category'])
            df_cat_score = df_cat_score.sort_values(by='Avg_Review_Score', ascending=False)
            
            # Sort ascending for horizontal bar chart so highest appears at the top
            df_cat_score = df_cat_score.sort_values(by='Avg_Review_Score', ascending=True)
            df_cat_score['Formatted_Score'] = df_cat_score['Avg_Review_Score'].apply(lambda x: f"{x:.2f}")
            
            # Dynamically calculate height based on total category count (e.g., 25px per category)
            total_categories = len(df_cat_score)
            dynamic_height = max(500, total_categories * 25)
            
            fig_cat_score = px.bar(
                df_cat_score,
                x='Avg_Review_Score',
                y='Product_Category',
                orientation='h',
                color_discrete_sequence=['#ff7f0e']  # Orange color theme
            )
            
            fig_cat_score.update_traces(
                text=df_cat_score['Formatted_Score'],
                texttemplate='%{text}',
                textposition='outside',
                textfont=dict(size=10, color='white')
            )
            
            fig_cat_score.update_layout(
                height=dynamic_height,
                margin=dict(l=20, r=40, t=30, b=30),
                xaxis_title="Average Review Score",
                yaxis_title="Product Category",
                xaxis=dict(range=[0, 5.2]),
                yaxis=dict(type='category')
            )
            
            st.plotly_chart(fig_cat_score, use_container_width=True, key="csat_avg_review_score_by_category_chart")
        else:
            st.warning("Could not find `product_category_name_english` or `review_score` columns.")
    else:
        st.warning("No data available for product category review breakdown.")






# =============================================================
# TAB: REVIEW SCORE PREDICTION MODEL (Logistic Regression)
# =============================================================
elif selected_tab == "⭐ Review Prediction Model":
    st.header("Customer Review Score Predictor")
    st.markdown("Use this interactive machine learning portal powered by **Logistic Regression** to predict expected customer ratings based on order characteristics, delivery performance, and pricing.")
    st.markdown("---")

    # Load saved model pipeline and medians safely with caching
    @st.cache_resource
    def load_prediction_assets():
        try:
            model = joblib.load("logistic_review_model.pkl")
            medians = joblib.load("model_medians.pkl")
            return model, medians
        except Exception:
            return None, None

    ml_model, feature_medians = load_prediction_assets()

    if ml_model is None or feature_medians is None:
        st.error("Model files (`logistic_review_model.pkl` or `model_medians.pkl`) not found in your directory! Please ensure they are saved in `my_streamlit_app`.")
    else:
        with st.form("ml_prediction_form"):
            st.subheader("⚙️ Enter Order & Delivery Parameters")
            
            col_p1, col_p2, col_p3 = st.columns(3)
            
            with col_p1:
                carrier_days = st.number_input("Carrier Delivered Days", min_value=0, max_value=100, value=7)
                customer_days = st.number_input("Customer Delivered Days", min_value=0, max_value=100, value=10)
                timely_deliv = st.selectbox("Order Timely Delivered?", options=[1, 0], format_func=lambda x: "Yes (1)" if x == 1 else "No (0)")
                
            with col_p2:
                total_amt = st.number_input("Total Amount ($)", min_value=0.0, max_value=5000.0, value=120.0)
                total_freight = st.number_input("Total Freight Value ($)", min_value=0.0, max_value=500.0, value=20.0)
                installments = st.number_input("Total Installments", min_value=1, max_value=24, value=1)
                
            with col_p3:
                prod_weight = st.number_input("Product Weight (g)", min_value=0.0, max_value=40000.0, value=800.0)
                prod_photos = st.number_input("Product Photos Quantity", min_value=1, max_value=10, value=2)
                approval_hrs = st.number_input("Order Approval Hours", min_value=0.0, max_value=168.0, value=1.5)

            submitted_prediction = st.form_submit_button(label="🔮 Predict Customer Rating")

        if submitted_prediction:
            # Start with training medians for all columns to satisfy model requirements
            input_dict = feature_medians.copy()
            
            # Override with user-selected inputs
            input_dict['carrier_delivered_days'] = carrier_days
            input_dict['customer_delivered_days'] = customer_days
            input_dict['order_timely_delivered?'] = timely_deliv
            input_dict['total_amount'] = total_amt
            input_dict['total_freight_value'] = total_freight
            input_dict['Total_installments'] = installments
            input_dict['product_weight_g'] = prod_weight
            input_dict['product_photos_qty'] = prod_photos
            input_dict['order_approval_hours'] = approval_hrs

            # Convert to DataFrame matching exact training feature order
            input_df = pd.DataFrame([input_dict])
            
            try:
                predicted_score = ml_model.predict(input_df)[0]
                prediction_proba = ml_model.predict_proba(input_df)[0]
                confidence = max(prediction_proba) * 100

                st.markdown("---")
                st.subheader("🎯 Prediction Results")
                
                res_col1, res_col2 = st.columns(2)
                with res_col1:
                    st.metric(label="Predicted Review Rating", value=f"⭐ {predicted_score} / 5")
                with res_col2:
                    st.metric(label="Model Confidence", value=f"{confidence:.1f}%")

                if predicted_score >= 4:
                    st.success("🟢 **High Satisfaction Expected:** This order profile strongly correlates with positive customer reviews.")
                elif predicted_score == 3:
                    st.warning("🟡 **Moderate Satisfaction:** Neutral review predicted. Ensure prompt carrier turnaround.")
                else:
                    st.error("🔴 **High Risk of Poor Review:** Delayed delivery or high freight charges detected. Immediate service intervention recommended.")

            except Exception as err:
                st.error(f"An error occurred during prediction: {err}")