import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 日本語表示のための設定 (Streamlit Cloud標準フォントを指定)
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['DejaVu Sans', 'Liberation Sans', 'Ubuntu', 'Arial', 'Hiragino Sans', 'IPAexGothic']

st.set_page_config(page_title="年金手取り率シミュレーター", layout="centered")

st.title("年金手取り率シミュレーター")
st.write("2026年度の制度に基づいた、年金収入に対する「手取り率」の推移グラフです。")

# --- 計算ロジック ---
def calculate_details(amount, age_cat, spouse):
    if amount <= 0: return 0, 0, 0, 0
    # 1. 公的年金等控除
    if age_cat == "65歳以上":
        deduction = 1100000 if amount <= 3300000 else amount * 0.15 + 605000
        rt_limit = 2110000 if spouse else 1550000
    else:
        deduction = 600000 if amount <= 1300000 else amount * 0.25 + 275000
        rt_limit = 1710000 if spouse else 1050000
    
    income = max(0, amount - deduction)
    # 2. 社会保険料（概算）
    hoken = int(income * 0.145 + 40000) if amount > 1000000 else 0
    # 3. 所得税
    it_dedu = 480000 + hoken + (380000 if spouse else 0)
    tax_it = int(max(0, income - it_dedu) * 0.05105)
    # 4. 住民税
    tax_rt = 0
    if amount > rt_limit:
        rt_dedu = 430000 + hoken + (330000 if spouse else 0)
        tax_rt = int(max(0, income - rt_dedu) * 0.10 + 5000)
        
    take_home = amount - hoken - tax_it - tax_rt
    rate = (take_home / amount) * 100
    return rate, hoken, tax_it, tax_rt

# --- サイドバー ---
st.sidebar.header("条件設定")
input_pension = st.sidebar.number_input("年金収入（年額/円）", min_value=10000, value=2000000, step=100000)
age_cat = st.sidebar.selectbox("年齢区分", ["65歳以上", "65歳未満"])
has_spouse = st.sidebar.checkbox("配偶者を扶養している", value=False)

# --- 計算 ---
current_rate, hoken, tax_it, tax_rt = calculate_details(input_pension, age_cat, has_spouse)

# --- 結果表示 ---
st.subheader("シミュレーション結果")
st.metric("現在の推定手取り率", f"{current_rate:.1f} %")
st.write(f"（額面 {input_pension/10000:.0f}万円に対し、手取り額は **{int(input_pension * current_rate / 100):,}円** です）")

# --- グラフ表示 ---
st.subheader("年金収入にともなう手取り率(%)の推移")

p_range = np.linspace(1000000, 5000000, 100)
rates = [calculate_details(p, age_cat, has_spouse)[0] for p in p_range]

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(p_range / 10000, rates, label="Take-home Rate (%)", color="#e74c3c", lw=2)

# 現在地をプロット
ax.plot(input_pension / 10000, current_rate, "ko", markersize=8)
ax.annotate(f"YOU: {current_rate:.1f}%", (input_pension/10000, current_rate), 
            textcoords="offset points", xytext=(0,10), ha='center', fontweight='bold')

ax.set_xlabel("Pension Income (10,000 JPY)")
ax.set_ylabel("Take-home Rate (%)")
ax.set_ylim(min(rates)-5, 105)
ax.grid(True, alpha=0.3)

st.pyplot(fig)

st.info("※グラフ内の日本語が表示されない場合は、ブラウザを更新するかRebootをお試しください。")
