import streamlit as st
import pandas as pd

st.set_page_config(page_title="Financial Plan Dashboard", layout="wide")

# --- Input Variables ---
st.sidebar.header("Adjust Product Parameters")

products = ['Ca_rd', 'St_Ry', 'E_Is']
params = {}

for product in products:
    st.sidebar.subheader(f"{product} Inputs")
    params[product] = {
        'Target_Unit': st.sidebar.number_input(f"{product} - Target Unit", min_value=0, value=15 if product == "Ca_rd" else 18 if product == "St_Ry" else 54),
        'AOV': st.sidebar.number_input(f"{product} - AOV", min_value=0, step=1000, value=20000 if product in ['Ca_rd', 'St_Ry'] else 10000),
        'Ven_Cost': st.sidebar.number_input(f"{product} - Vendor Cost (per unit)", min_value=0, step=500, value=10000 if product == "Ca_rd" else 10000 if product == "St_Ry" else 0),
        'Mark_Cost': st.sidebar.number_input(f"{product} - Marketing Cost (total)", min_value=0, step=500, value=18000 if product == "Ca_rd" else 21000 if product == "St_Ry" else 32000),
        'Pack_Cost': st.sidebar.number_input(f"{product} - Packaging Cost (total)", min_value=0, step=500, value=12500 if product == "Ca_rd" else 15000 if product == "St_Ry" else 0),
    }

# --- Monthly Distribution Percentage ---
monthly_distribution = {
    'Jul': 0.13,
    'Aug': 0.29,
    'Sep': 0.27,
    'Oct': 0.17,
    'Nov': 0.08,
    'Dec': 0.07,
}

# --- Weekly Distribution ---
weekly_distribution = {
    f"Week {i+1}": pct for i, pct in enumerate([
        0.0375, 0.0313, 0.0300, 0.0188, 0.0125, 0.0875, 0.0875, 0.0583, 0.0438, 0.0929, 0.0933, 0.0637,
        0.0600, 0.0500, 0.0413, 0.0413, 0.0250, 0.0250, 0.0250, 0.0296, 0.0325, 0.0288, 0.0267, 0.0200,
        0.0167, 0.0133, 0.0100, 0.0067
    ])
}

# --- Main Data Aggregation ---
data = []
for product, values in params.items():
    unit = values['Target_Unit']
    aov = values['AOV']
    gross = unit * aov
    net = gross  # Assuming no deductions
    revenue = net if product == "E_Is" else unit * aov / 2  # Half of AOV for revenue for Ca_rd and St_Ry
    ven_cost = unit * values['Ven_Cost']
    mark_cost = values['Mark_Cost']
    pack_cost = values['Pack_Cost']
    total_cost = ven_cost + mark_cost + pack_cost
    ebitda = revenue - total_cost
    net_cash = net - total_cost

    data.append({
        'Product': product,
        'Target_Unit': unit,
        'AOV': aov,
        'Target_Gross_Collection': gross,
        'Target_Net_Collection': net,
        'Target_Revenue': revenue,
        'Ven_Cost': ven_cost,
        'Mark_Cost': mark_cost,
        'Pack_Cost': pack_cost,
        'Total_Cost': total_cost,
        'EBITDA': ebitda,
        'EBITDA_%': f"{(ebitda / revenue * 100):.0f}%" if revenue else '0%',
        'Net_Cash_Flow': net_cash,
        'Net_Cash_Flow_%': f"{(net_cash / net * 100):.0f}%" if net else '0%'
    })

df = pd.DataFrame(data)
totals = df[['Target_Unit', 'Target_Gross_Collection', 'Target_Net_Collection',
             'Target_Revenue', 'Ven_Cost', 'Mark_Cost', 'Pack_Cost',
             'Total_Cost', 'EBITDA', 'Net_Cash_Flow']].sum()

total_row = pd.DataFrame([{
    'Product': 'Total',
    'Target_Unit': totals['Target_Unit'],
    'AOV': '',
    'Target_Gross_Collection': totals['Target_Gross_Collection'],
    'Target_Net_Collection': totals['Target_Net_Collection'],
    'Target_Revenue': totals['Target_Revenue'],
    'Ven_Cost': totals['Ven_Cost'],
    'Mark_Cost': totals['Mark_Cost'],
    'Pack_Cost': totals['Pack_Cost'],
    'Total_Cost': totals['Total_Cost'],
    'EBITDA': totals['EBITDA'],
    'EBITDA_%': f"{(totals['EBITDA'] / totals['Target_Revenue'] * 100):.0f}%" if totals['Target_Revenue'] else '0%',
    'Net_Cash_Flow': totals['Net_Cash_Flow'],
    'Net_Cash_Flow_%': f"{(totals['Net_Cash_Flow'] / totals['Target_Net_Collection'] * 100):.0f}%" if totals['Target_Net_Collection'] else '0%',
}])

summary_df = pd.concat([df, total_row], ignore_index=True)

# --- Dashboard Output ---
st.title("📊 Financial Planning Dashboard")

st.subheader("🔹 Product-Level Summary")
st.dataframe(summary_df.style.format({
    'Target_Gross_Collection': '₹{:,.0f}',
    'Target_Net_Collection': '₹{:,.0f}',
    'Target_Revenue': '₹{:,.0f}',
    'Ven_Cost': '₹{:,.0f}',
    'Mark_Cost': '₹{:,.0f}',
    'Pack_Cost': '₹{:,.0f}',
    'Total_Cost': '₹{:,.0f}',
    'EBITDA': '₹{:,.0f}',
    'Net_Cash_Flow': '₹{:,.0f}',
}), use_container_width=True)

# --- Monthly Breakdown ---
st.subheader("📆 Monthly Collection & Earnings")

monthly_data = []
for month, pct in monthly_distribution.items():
    collection = totals['Target_Gross_Collection'] * pct
    ven_cost = totals['Ven_Cost'] * pct
    net_earning = collection - ven_cost
    monthly_data.append({
        'Month': month,
        '% Distribution': f"{pct*100:.0f}%",
        'Collection': collection,
        'Unit': round(totals['Target_Unit'] * pct),
        'Ven_Cost': ven_cost,
        'Net Earning': net_earning
    })

monthly_df = pd.DataFrame(monthly_data)
st.dataframe(monthly_df.style.format({
    'Collection': '₹{:,.0f}',
    'Ven_Cost': '₹{:,.0f}',
    'Net Earning': '₹{:,.0f}',
}), use_container_width=True)

# --- Per-Product Monthly Breakdowns ---
st.subheader("📦 Monthly Breakdown by Product")

for product, values in params.items():
    st.markdown(f"#### {product}")

    unit = values['Target_Unit']
    aov = values['AOV']
    gross = unit * aov
    ven_cost_per_unit = values['Ven_Cost']

    monthly_rows = []
    for month, pct in monthly_distribution.items():
        month_collection = gross * pct
        month_units = round(unit * pct)
        month_ven_cost = month_units * ven_cost_per_unit
        net_earning = month_collection - month_ven_cost
        monthly_rows.append({
            'Month': month,
            '% Distribution': f"{pct * 100:.0f}%",
            'Collection': month_collection,
            'Unit': month_units,
            'Ven_Cost': month_ven_cost,
            'Net Earning': net_earning
        })

    product_monthly_df = pd.DataFrame(monthly_rows)
    st.dataframe(product_monthly_df.style.format({
        'Collection': '₹{:,.0f}',
        'Ven_Cost': '₹{:,.0f}',
        'Net Earning': '₹{:,.0f}',
    }), use_container_width=True)

# --- Weekly Breakdown ---
st.subheader("📅 Weekly Breakdown (Overall Level)")

weekly_data = []
for week, pct in weekly_distribution.items():
    collection = totals['Target_Gross_Collection'] * pct
    ven_cost = totals['Ven_Cost'] * pct
    net_earning = collection - ven_cost
    weekly_data.append({
        'Week': week,
        '% Distribution': f"{pct*100:.2f}%",
        'Collection': collection,
        'Unit': round(totals['Target_Unit'] * pct),
        'Ven_Cost': ven_cost,
        'Net Earning': net_earning
    })

weekly_df = pd.DataFrame(weekly_data)
st.dataframe(weekly_df.style.format({
    'Collection': '₹{:,.0f}',
    'Ven_Cost': '₹{:,.0f}',
    'Net Earning': '₹{:,.0f}',
}), use_container_width=True)