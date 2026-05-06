import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 日本語表示の対策（クラウド環境用）
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['DejaVu Sans', 'Liberation Sans', 'Ubuntu', 'Arial', 'Hiragino Sans', 'IPAexGothic']

st.set_page_config(page_title="年金手取りシミュレーター", layout="centered")

st.title("年金手取りシミュレーター")
st.write("年金収入から引かれる税金・社会保険料を算出し、手取りをシミュレーションします。")

# --- 計算ロジック ---
def calculate_details(amount, age_cat, spouse):
    if amount <= 0: return 0, 0, 0, 0, 0
    # 1. 公的年金等控除
    if age_cat == "65歳以上":
        deduction = 1100000 if amount <= 3300000 else amount * 0.15 + 605000
        rt_limit = 2110000 if spouse else 1550000
    else:
        deduction = 600000 if amount <= 1300000 else amount * 0.25 + 275000
        rt_limit = 1710000 if spouse else 1050000
    
    income = max(0, amount - deduction)
    # 2. 社会保険料（所得の約14.5%と仮定）
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
    return take_home, hoken, tax_it, tax_rt, rate

# --- サイドバー設定 ---
st.sidebar.header("条件設定")
input_pension = st.sidebar.number_input("年金収入（年額/円）", min_value=10000, value=2000000, step=100000)
age_cat = st.sidebar.selectbox("年齢区分", ["65歳以上", "65歳未満"])
has_spouse = st.sidebar.checkbox("配偶者を扶養している", value=False)

# --- 計算実行 ---
take_home, hoken, tax_it, tax_rt, current_rate = calculate_details(input_pension, age_cat, has_spouse)

# --- 結果表示（復活！） ---
st.subheader("シミュレーション結果")

col1, col2 = st.columns(2)
with col1:
    st.metric("1か月あたりの手取り額", f"{take_home // 12:,} 円")
with col2:
    st.metric("現在の手取り率", f"{current_rate:.1f} %")

st.write(f"（年金額面 {input_pension/10000:.0f}万円 ＝ 月額 約{int(input_pension/12):,}円）")

# --- 内訳表（復活！） ---
with st.expander("詳しい計算内訳（年額）を見る"):
    st.table({
        "項目": ["年金総額（額面）", "社会保険料（概算）", "所得税", "住民税", "合計手取り"],
        "金額 (円)": [
            f"{input_pension:,}",
            f"- {hoken:,}",
            f"- {tax_it:,}",
            f"- {tax_rt:,}",
            f"{take_home:,}"
        ]
    })

# --- 手取り率の推移グラフ ---
st.subheader("年金収入にともなう手取り率(%)の推移")

p_range = np.linspace(1000000, 5000000, 50)
rates = [calculate_details(p, age_cat, has_spouse)[4] for p in p_range]

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(p_range / 10000, rates, color="#e74c3c", lw=2, label="Take-home Rate (%)")

# 現在地をプロット
ax.plot(input_pension / 10000, current_rate, "ko", markersize=8)
ax.annotate(f"YOU: {current_rate:.1f}%", (input_pension/10000, current_rate), 
            textcoords="offset points", xytext=(0,10), ha='center', fontweight='bold')

ax.set_xlabel("Annual Pension (10,000 JPY)")
ax.set_ylabel("Rate (%)")
ax.set_ylim(min(rates)-5, 105)
ax.grid(True, alpha=0.3)

st.pyplot(fig)

st.info("※2026年度（令和8年度）の制度見込みを反映した概算値です。")
