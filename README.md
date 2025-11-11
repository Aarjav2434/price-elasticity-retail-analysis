# price-elasticity-retail-analysis
Economic analysis of price elasticity in retail using econometric modeling

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Economics](https://img.shields.io/badge/Economics-Microeconomics-green.svg)]()
[![Statistics](https://img.shields.io/badge/Statistics-Econometrics-orange.svg)]()

---

##  Project Overview

This project applies **microeconomic demand theory** to real retail data, calculating price elasticity of demand across product categories to inform pricing strategy.

### Business Problem
Retailers face a critical question: **Which products can sustain price increases without losing customers?**

Without elasticity analysis, pricing decisions are guesswork. This project provides data-driven answers.

---

##  Key Objectives

1. **Calculate price elasticity** for each product category using econometric methods
2. **Classify products** as elastic (price-sensitive) vs. inelastic (price-insensitive)
3. **Identify pricing opportunities** where revenue can be optimized
4. **Simulate revenue impact** of strategic price changes

---

##  Methodology

### Economic Framework

**Price Elasticity of Demand (PED)**:
```
PED = (% Change in Quantity Demanded) / (% Change in Price)
```

**Classification**:
- **PED< 1**: Inelastic demand → Can increase prices
- **PED > 1**: Elastic demand → Price-sensitive, maintain competitive pricing
- **PED = 1**: Unit elastic → Proportional response

### Technical Approach

**1. Log-Log Regression Model**
```
log(Sales) = β₀ + β₁ × log(Price) + ε
```
- **Why log-log?** The coefficient β₁ directly represents elasticity
- **Advantage**: Constant elasticity interpretation across price ranges
- **Method**: Ordinary Least Squares (OLS) regression

**2. Category-Level Analysis**
- Segment by product type (16 categories in Big Mart data)
- Individual elasticity estimates for each category
- Statistical validation using p-values and R² metrics

**3. Business Simulation**
- Model revenue impact of 5% price increases
- Compare scenarios across product categories
- Quantify optimization opportunities

---

##  Key Findings

### Summary Statistics
- **Total Categories Analyzed**: 16
- **Inelastic Categories**: 25% (pricing optimization candidates)
- **Average Elasticity**: 1.02
- **Statistically Significant Results**: 100%

### Strategic Insights

####  **Inelastic Products** (XX categories)
*These can sustain price increases:*
- [Seafood]: Elasticity = 0.864
- [Breads]: Elasticity = 0.968
- [Soft Drinks]: Elasticity = 0.89

**Recommendation**: Implement 5-10% strategic price increases to improve margins

####  **Elastic Products** (XX categories)
*These are price-sensitive:*
- [Meat]: Elasticity = 1.0072
- [Baking Goods]: Elasticity = 1.0104

**Recommendation**: Maintain competitive pricing, focus on volume and promotions

### Revenue Impact Simulation

**Scenario**: 5% price increase on top 3 inelastic categories

| Category | Current Price | Elasticity | Expected Revenue Change |
|----------|---------------|------------|-------------------------|
| [Seafood] | Rs 141.84 | 0.864 | +4.32% |
| [Name] | Rs 140.95 | 0.968 | +4.84% |
| [Name] | Rs 131.49  |    0.898 | +4.49% |

**Total Estimated Impact**: Rs 156,744.80  revenue increase

---

##  Visualizations

### 1. Price-Sales Relationship
<img width="2962" height="1763" alt="image" src="https://github.com/user-attachments/assets/a3eb1ff1-71c1-4e01-ac4c-657160908f27" />
*Shows overall correlation and data distribution across all products*

### 2. Elasticity by Category
<img width="3561" height="2363" alt="image" src="https://github.com/user-attachments/assets/d59288e3-7387-40ca-b63c-3cd1cf2b0e8a" />

*Green categories = pricing opportunities | Red categories = price-sensitive*

### 3. Demand Classification Summary
<img width="1901" height="1763" alt="image" src="https://github.com/user-attachments/assets/b3a41a1c-4675-42ba-8b33-d9348d3168bd" />

*High-level breakdown for executive presentation*

---

**Statistical Methods**:
- Ordinary Least Squares (OLS) Regression
- Log-log transformation for elasticity estimation
- Hypothesis testing (p-values, confidence intervals)

---
---

##  Dataset

**Source**: (https://www.kaggle.com/code/mragpavank/big-mart-sales-data/input)

**Description**: 
- Retail sales data from Big Mart supermarkets
- 8,523 products across 10 stores
- 16 product categories
- Variables: Product details, pricing, outlet characteristics, sales figures

**Key Variables Used**:
- `Item_MRP`: Maximum Retail Price (₹)
- `Item_Outlet_Sales`: Sales volume
- `Item_Type`: Product category

---

##  Business Applications

This analysis framework applies to:

**E-commerce**:
- Dynamic pricing algorithms
- Category-specific pricing strategies

**Retail**:
- Markdown optimization
- Private label pricing
- Competitive positioning

**SaaS/Subscription**:
- Tier pricing optimization
- Feature bundling decisions
- Churn prevention through pricing

**Marketplace Platforms**:
- Commission rate optimization
- Seller pricing guidance
- Demand-based pricing

---

## Econometric Background

### Why Log-Log Regression?

Traditional linear regression gives: `Sales = β₀ + β₁ × Price`

But elasticity varies with price level. Log-log gives **constant elasticity**:
- `log(Sales) = β₀ + β₁ × log(Price)`
- Taking derivatives: `d(log Sales)/d(log Price) = β₁ = Elasticity`
- **Result**: β₁ coefficient is directly interpretable as price elasticity
