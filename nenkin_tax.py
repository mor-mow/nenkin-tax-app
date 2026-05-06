import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="年金手取りシミュレーター", layout="centered")

st.title("年金手取り・推移シミュレーター")

# --- 計算ロジックの定義 ---
def calculate_details(amount, age_cat, spouse):
    # 1. 公的年金等控除
    if age_cat == "65歳以上":
        deduction = 1100000 if amount <= 3300000 else amount * 0.15 + 605000
        rt_limit = 2110000 if spouse else 1550000
    else:
        deduction = 600000 if amount <= 1300000 else amount * 0.25 + 275000
        rt_limit = 1710000 if spouse else 1050000
    
    income = max(0, amount - deduction)
    # 2. 社会保険料（所得の約14% + 基礎分）
    hoken = int(income * 0.14 + 40000) if amount > 1000000 else 0
    # 3. 所得税
    it_dedu = 480000 + hoken + (380000 if spouse else 0)
    tax_it = int(max(0, income - it_dedu) * 0.05105)
    # 4. 住民税
    tax_rt = 0
    if amount > rt_limit:
        rt_dedu = 430000 + hoken + (330000 if spouse else 0)
        tax_rt = int(max(0, income - rt_dedu) * 0.10 + 5000)
        
    take_home = amount - hoken - tax_it - tax_rt
    return take_home, hoken, tax_it, tax_rt

# --- サイドバー入力 ---
st.sidebar.header("条件設定")
input_pension = st.sidebar.number_input("あなたの年金収入（年額/円）", min_value=0, value=2000000, step=100000)
age_cat = st.sidebar.selectbox("年齢区分", ["65歳以上", "65歳未満"])
has_spouse = st.sidebar.checkbox("配偶者を扶養している", value=False)

# --- 計算実行 ---
take_home, hoken, tax_it, tax_rt = calculate_details(input_pension, age_cat, has_spouse)

# --- 結果表示 ---
st.subheader("あなたのシミュレーション結果")
col1, col2 = st.columns(2)
col1.metric("1か月あたりの手取り", f"{take_home // 12:,} 円")
col2.metric("年間の手取り額", f"{take_home:,} 円")

# --- グラフ作成 ---
st.subheader("年金収入にともなう手取り額の推移")

# 100万〜500万までの推移データ作成
p_range = np.linspace(1000000, 5000000, 50)
th_range = [calculate_details(p, age_cat, has_spouse)[0] for p in p_range]

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(p_range / 10000, np.array(th_range) / 10000, label="手取り額", color="#2c7be5", lw=2)
ax.plot(p_range / 10000, p_range / 10000, "--", label="額面（100%）", color="gray", alpha=0.5)

# 現在の入力値をプロット
ax.plot(input_pension / 10000, take_home / 10000, "ro", markersize=10, label="現在の位置")
ax.annotate(f"ここ: {take_home//10000}万円", (input_pension/10000, take_home/10000), textcoords="offset points", xytext=(0,10), ha='center')

ax.set_xlabel("年金収入（万円）")
ax.set_ylabel("手取り額（万円）")
ax.legend()
ax.grid(True, alpha=0.3)

st.pyplot(fig)

# --- 内訳表 ---
with st.expander("詳しい計算内訳を見る"):
    st.table({
        "項目": ["年金総額", "社会保険料", "所得税", "住民税", "手取り合計"],
        "年額 (円)": [f"{input_pension:,}", f"-{hoken:,}", f"-{tax_it:,}", f"-{tax_rt:,}", f"{take_home:,}"]
    })
