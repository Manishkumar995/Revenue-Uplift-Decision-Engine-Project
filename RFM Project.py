import pandas as pd
import pyarrow
import numpy as np
import matplotlib.pyplot as plt


# Online Retail Table
retail = pd.read_excel(r'C:\Users\manish kumar\Downloads\Retention decision Engine Project\Online Retail.xlsx')

print(retail.head())
print(retail.info())
retail = retail.dropna(subset=['CustomerID'])
retail=retail[retail['Quantity']>0]
retail=retail[retail['UnitPrice']>0]
retail['InvoiceDate'] = pd.to_datetime(retail['InvoiceDate'])
retail['Revenue'] = retail['Quantity'] * retail['UnitPrice']

# RFM
snapshot_date = retail['InvoiceDate'].max()

rfm = retail.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
    'InvoiceNo': 'count',
    'Revenue': 'sum'
})

rfm.columns = ['Recency', 'Frequency', 'Monetary']
rfm=rfm.reset_index()

# Customer life time value & average order value- Who is priority customer
rfm['CLV'] = rfm['Monetary']/10
rfm['AvgOrderValue'] = rfm['Monetary'] / rfm['Frequency']


# Calculating the weak customer and loyal customer
rfm['Recency_norm'] = rfm['Recency'] / rfm['Recency'].max()
rfm['Frequency_norm'] = rfm['Frequency'] / rfm['Frequency'].max()
rfm['Churn_Prob'] = (
    0.6 * rfm['Recency_norm'] +
    0.4 * (1 - rfm['Frequency_norm'])
)

# Bifercating customers into high value, weak and average customers
def segment(row):
    if row['CLV'] > rfm['CLV'].quantile(0.75):
        return "High Value"
    elif row['Churn_Prob'] > 0.7:
        return "At Risk"
    else:
        return "Regular"

rfm['Segment'] = rfm.apply(segment, axis=1)


# Marketing Table:=
marketing=pd.read_csv(r'C:\Users\manish kumar\Downloads\Retention decision Engine Project\marketing_campaign.csv')

marketing = marketing[['Income','Education','Marital_Status']]
marketing['Income'] = pd.to_numeric(marketing['Income'], errors='coerce')
marketing = marketing.dropna(subset=['Income'])

# Mapping Marketing to Customers
marketing_sample = marketing.sample(n=len(rfm), replace=True).reset_index(drop=True)

rfm = rfm.reset_index(drop=True)
rfm = pd.concat([rfm, marketing_sample], axis=1)

# CREATING Income_Segment
rfm['Income_Segment'] = pd.qcut(
    rfm['Income'],
    3,
    labels=['Low','Medium','High']
)

# Cleaning
rfm['Income_Segment'] = rfm['Income_Segment'].astype(str).str.strip()

#Convert to numeric score
rfm['Income_Score'] = rfm['Income_Segment'].map({
    'Low': 1,
    'Medium': 0.5,
    'High': 0
})

#Handling missing (important)
rfm['Income_Score'] = rfm['Income_Score'].fillna(0.5)
print(rfm[['Income','Income_Segment','Income_Score']].head());


# Pricing Table =
df= pd.read_csv(r'C:\Users\manish kumar\Downloads\Retention decision Engine Project\avocado.csv')

df.rename(columns={
    'AveragePrice': 'price',
    'Total Volume': 'demand'
}, inplace=True)

# Removing invalid values
df = df[(df['price'] > 0) & (df['demand'] > 0)]

print(df[['price','demand']].describe())
pricing_df = df.groupby('price')['demand'].mean().reset_index()
print(pricing_df.head())

plt.scatter(pricing_df['price'], pricing_df['demand'])
plt.scatter(pricing_df['price'], pricing_df['demand'])
plt.title("Price vs Demand")
pricing_df = pricing_df.sort_values('price')
plt.show()

pricing_df['log_price'] = np.log(pricing_df['price'])
pricing_df['log_demand'] = np.log(pricing_df['demand'])

# Difference
pricing_df['price_change'] = pricing_df['log_price'].diff()
pricing_df['demand_change'] = pricing_df['log_demand'].diff()

# Calculate the effect of price on demand
pricing_df['elasticity'] = pricing_df['demand_change'] / pricing_df['price_change']
pricing_df = pricing_df.dropna()
avg_elasticity = pricing_df['elasticity'].mean()

# If i give 10% discount, how customer value changes
discount = 0.10

rfm['Demand_Change_%'] = avg_elasticity * (-discount)
rfm['Adjusted_CLV'] = rfm['CLV'] * (1 + rfm['Demand_Change_%'])

rfm['Discount_Cost'] = rfm['AvgOrderValue'] * discount
rfm['Expected_Value'] = rfm['Adjusted_CLV'] * rfm['Churn_Prob']
rfm['ROI'] = rfm['Expected_Value'] - rfm['Discount_Cost']

# Ranking customers: Highest ROI means best targets
rfm = rfm.sort_values(by='ROI', ascending=False)
print(rfm[['CustomerID','Segment','ROI']].head())

# Visualization
# Segment Distribution:=
rfm['Segment'].value_counts().plot(kind='bar')
plt.show()

# ROI Distribution
rfm_filtered = rfm[rfm['ROI'] < rfm['ROI'].quantile(0.95)]
plt.hist(rfm_filtered['ROI'], bins=30)
plt.title("ROI Distribution")
plt.show()


# Elasticity Curve

plt.plot(pricing_df['price'], pricing_df['elasticity'])
plt.title("Elasticity Curve")
plt.show()

rfm['Target_Flag'] = np.where(
    (rfm['ROI'] > 200) & (rfm['Income_Segment'] != 'Low'),
    1,
    0
)


#METRICS


# Total customers
total_customers = len(rfm)

# Target customers
target_customers = rfm[rfm['Target_Flag'] == 1].shape[0]

# % targeted
target_pct = (target_customers / total_customers) * 100

# Avg ROI
avg_roi = rfm['ROI'].mean()

# High ROI customers
high_roi = rfm[rfm['ROI'] > 500].shape[0]

print("Total Customers:", total_customers)
print("Target Customers:", target_customers)
print("Target %:", round(target_pct,2))
print("Avg ROI:", round(avg_roi,2))
print("High ROI Customers:", high_roi)
print(rfm[['CustomerID','Segment','Income_Segment','ROI']].head())



