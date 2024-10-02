import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd

conn = sqlite3.connect("trades.db")
curs = conn.cursor()

# WLD is just World for Total Trade

# 166 countries matched with continents for continents analysis, countries by continents manually edited to include some of the larger countries

annual_value_continents = np.array(curs.execute("""
    SELECT Year, Continent, SUM(TradeValue)
    FROM TradeStats
    LEFT JOIN CountryCodes ON CountryCodes.Code = TradeStats.ReporterISO3
    LEFT JOIN ContinentCountry ON ContinentCountry.Country = CountryCodes.Country
    WHERE TradeStats.PartnerISO3 = 'WLD' AND continent NOT NULL
    GROUP BY Continent, Year
""").fetchall())

years = annual_value_continents[:,0].astype(int)
continents = annual_value_continents[:,1]
annual_value = (annual_value_continents[:,2].astype(float) * 1000)/1000000000000

plot_df = pd.DataFrame({
    'years': years,
    'continents': continents,
    'annual_value': annual_value})

groups = plot_df.groupby('continents')

plt.figure(figsize=(10,6))
for continent, group in groups:
    plt.plot(group['years'], group['annual_value'], label=continent)
plt.grid()
plt.xlabel('Year')
plt.ylabel('Exports Value (USD Trillion)')
plt.title('Export Value of Trade in Goods by Continent 1988-2021')
plt.legend()
plt.savefig('visualisations/Total Exports by Continent', dpi=400)

base_100_df = pd.DataFrame()

for continent, group in groups:
    base_value = group['annual_value'].iloc[0]
    group['base_values'] = (group['annual_value'] / base_value) * 100
    base_100_df = pd.concat([base_100_df, group])

new_groups = base_100_df.groupby('continents')

plt.figure(figsize=(10,6))
for continent, group in new_groups:
    plt.plot(group['years'], group['base_values'], label=continent)
plt.xlabel('Year')
plt.ylabel('Exports Value Change from 1988 (Base 100)')
plt.grid()
plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(500))
plt.ylim(0,6000)
plt.title('Changes in Export Value of Trade in Goods by Continent 1988-2021')
plt.legend()
plt.savefig('visualisations/Base 100 Exports by Continent', dpi=400)

timeframe_perc = 1

annual_value_continents_perc = np.array(curs.execute("""
WITH continent_trade AS 
(
SELECT Year, Continent, SUM(TradeValue) AS TotalTradeValue
FROM TradeStats
LEFT JOIN CountryCodes ON CountryCodes.Code = TradeStats.ReporterISO3
LEFT JOIN ContinentCountry ON ContinentCountry.Country = CountryCodes.Country
WHERE TradeStats.PartnerISO3 ='WLD' AND continent NOT NULL
GROUP BY Continent, Year
)

SELECT Year, Continent,
ROUND((TotalTradeValue - LAG(TotalTradeValue, ?) OVER (PARTITION BY Continent ORDER BY Year)) / LAG(TotalTradeValue, ?) OVER (PARTITION BY Continent ORDER BY Year) * 100, 2)
FROM continent_trade                               
""", (timeframe_perc,timeframe_perc)).fetchall())

years_perc = annual_value_continents_perc [:,0].astype(int)
continents_perc  = annual_value_continents_perc [:,1]
annual_value_change_perc = (annual_value_continents_perc [:,2].astype(float))

plot_df_perc = pd.DataFrame({
    'years': years_perc,
    'continents': continents_perc,
    'annual_value': annual_value_change_perc})

groups_perc = plot_df_perc.groupby('continents')

plt.figure(figsize=(10,6))
for name, group in groups_perc:
    plt.plot(group['years'], group['annual_value'], label=name, linewidth=1.7)
plt.xlabel('Year')
plt.ylabel('Exports Value % Change')
plt.ylim(-40,80)
plt.grid()
plt.axhline(y = 0, color = 'black', linestyle = '--') 
plt.title('Export Value of Trade in Goods Yearly Percentage Change 1988-2021')
plt.legend()
plt.savefig('visualisations/Yearly Export Percentage Change by Continent', dpi=400)

plt.show()
