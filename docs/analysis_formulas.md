# Analysis Formulas

## KPI
- GPR: 満室想定年収
- EGI = GPR * (1 - vacancy_rate)
- OPEX = EGI * opex_ratio
- NOI = EGI - OPEX
- ADS: 年間返済額
- pre_tax_cf = NOI - ADS
- dscr = NOI / ADS
- debt_ratio = ADS / GPR
- break_even_occupancy = (OPEX + ADS) / GPR
- hand_nokori_ratio_pct = pre_tax_cf / total_project_cost * 100

## Stress Scenario
- optimistic / base / stress の3ケース
- stress最低条件: vacancy +5pt, rent -5%, opex +10%, rate +0.5%

## 路線価の注意
- simple: `route_value_per_m2 * land_area_m2`
- corrected: 補正率が揃う場合のみ
- manual: 接道/奥行/形状/固定資産税評価額等が不足時
- 倍率地域: `fixed_asset_tax_value * multiplier`（不足時 manual review）
