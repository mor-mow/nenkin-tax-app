import streamlit as st

st.set_page_config(page_title="年金手取りシミュレーター", layout="centered")

st.title("年金手取りシミュレーター")
st.write("年金収入から、所得税・住民税・社会保険料を差し引いた「手取り額」を計算します。")

# --- サイドバー：入力設定 ---
st.sidebar.header("入力設定")
annual_pension = st.sidebar.number_input("年金収入（年額/円）", min_value=0, value=2000000, step=10000)
age_category = st.sidebar.selectbox("年齢区分", ["65歳以上", "65歳未満"])
has_spouse = st.sidebar.checkbox("配偶者を扶養している", value=False)

# --- 計算ロジック ---
def calculate_take_home(amount, age_cat, spouse):
    # 1. 公的年金等控除
    if age_cat == "65歳以上":
        deduction = 1100000 if amount <= 3300000 else amount * 0.15 + 605000
        rt_limit = 2110000 if spouse else 1550000
    else:
        deduction = 600000 if amount <= 1300000 else amount * 0.25 + 275000
        rt_limit = 1710000 if spouse else 1050000
    
    income = max(0, amount - deduction)

    # 2. 社会保険料（概算：所得の約14% + 基礎分）
    hoken = int(income * 0.14 + 40000) if amount > 1000000 else 0
    
    # 3. 所得税（基礎控除48万 + 社会保険料控除 + 配偶者控除38万）
    it_deduction = 480000 + hoken + (380000 if spouse else 0)
    tax_it = int(max(0, income - it_deduction) * 0.05105)

    # 4. 住民税
    tax_rt = 0
    if amount > rt_limit:
        rt_deduction = 430000 + hoken + (330000 if spouse else 0)
        tax_rt = int(max(0, income - rt_deduction) * 0.10 + 5000)
        
    take_home_annual = amount - hoken - tax_it - tax_rt
    return hoken, tax_it, tax_rt, take_home_annual

hoken, tax_it, tax_rt, take_home_annual = calculate_take_home(annual_pension, age_category, has_spouse)

# --- 結果表示 ---
st.subheader("シミュレーション結果")

col1, col2 = st.columns(2)
with col1:
    st.metric("1か月あたりの手取り額", f"{take_home_annual // 12:,} 円")
with col2:
    st.metric("年間の手取り額", f"{take_home_annual:,} 円")

st.markdown("---")
st.write("### 内訳（年額ベース）")
st.table({
    "項目": ["年金総額（額面）", "社会保険料（概算）", "所得税", "住民税", "合計手取り"],
    "金額 (円)": [
        f"{annual_pension:,}",
        f"- {hoken:,}",
        f"- {tax_it:,}",
        f"- {tax_rt:,}",
        f"{take_home_annual:,}"
    ]
})

st.info("※この計算はあくまで概算です。お住まいの自治体や他の所得、医療費控除等により実際の金額は異なります。")
