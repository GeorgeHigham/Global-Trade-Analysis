import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import dataframe_image as dfi


conn = sqlite3.connect("trades.db")
curs = conn.cursor()

# WLD is World for Total Trade

# minimum years in place
top_old_values_countries = np.array(curs.execute("""
    SELECT country, ROUND(AVG(TradeValue*1000),2)
    FROM TradeStats
    LEFT JOIN CountryCodes ON CountryCodes.Code = TradeStats.ReporterISO3
    WHERE TradeStats.PartnerISO3 = 'WLD' 
    AND country NOT IN ('European Union', 'Other Asia, nes')
    AND Year < 2010
    GROUP BY country
    HAVING COUNT(DISTINCT TradeStats.Year) > 15
    ORDER BY AVG(TradeValue) DESC
    LIMIT 10
""").fetchall())

top_recent_values_countries = np.array(curs.execute("""
    SELECT country, ROUND(AVG(TradeValue*1000),2)
    FROM TradeStats
    LEFT JOIN CountryCodes ON CountryCodes.Code = TradeStats.ReporterISO3
    WHERE TradeStats.PartnerISO3 = 'WLD' 
    AND country NOT IN ('European Union', 'Other Asia, nes')
    AND Year >= 2010
    GROUP BY country
    HAVING COUNT(DISTINCT TradeStats.Year) > 10
    ORDER BY AVG(TradeValue) DESC
    LIMIT 10
""").fetchall())

old_years_trade_df = pd.DataFrame(top_old_values_countries, columns=['Country', 'Average Yearly Exports 1988-2010 (USD)'])
recent_years_trade_df = pd.DataFrame(top_recent_values_countries, columns=['Country', 'Average Yearly Exports 2010-2021 (USD)'])

combined_df = pd.concat([old_years_trade_df, recent_years_trade_df], axis=1)
combined_df.insert(0, 'Rank', [i for i in range(1,11)])
combined_df['Average Yearly Exports 1988-2010 (USD)'] = pd.to_numeric(combined_df['Average Yearly Exports 1988-2010 (USD)'])
combined_df['Average Yearly Exports 2010-2021 (USD)'] = pd.to_numeric(combined_df['Average Yearly Exports 2010-2021 (USD)'])

recent_years_total = sum([x for x in combined_df['Average Yearly Exports 2010-2021 (USD)']])
old_years_total = sum([x for x in combined_df['Average Yearly Exports 1988-2010 (USD)']])

combined_df.loc[len(combined_df)] = ['', 'Sum Total', old_years_total, 'Sum Total', recent_years_total]
combined_df['Average Yearly Exports 1988-2010 (USD)'] = combined_df['Average Yearly Exports 1988-2010 (USD)'].apply(lambda x: f"{int(x):,}")
combined_df['Average Yearly Exports 2010-2021 (USD)'] = combined_df['Average Yearly Exports 2010-2021 (USD)'].apply(lambda x: f"{int(x):,}")
dfi.export(combined_df.style.hide(axis='index'), 'visualisations/Country Trade Years Comparison.png', dpi=400)


annual_value_top_trading = np.array(curs.execute("""
WITH top_trading_1998_2010 AS 
(
SELECT CountryCodes.country
FROM TradeStats
LEFT JOIN CountryCodes ON CountryCodes.Code = TradeStats.ReporterISO3
WHERE TradeStats.PartnerISO3 = 'WLD' 
AND country NOT IN ('European Union', 'Other Asia, nes')
AND Year < 2010
GROUP BY country
HAVING COUNT(DISTINCT TradeStats.Year) > 15
ORDER BY AVG(TradeValue) DESC
LIMIT 10
)
SELECT Year, country, SUM(TradeValue)
FROM TradeStats
LEFT JOIN CountryCodes ON CountryCodes.Code = TradeStats.ReporterISO3
WHERE country IN top_trading_1998_2010 
AND TradeStats.PartnerISO3 = 'WLD' 
AND country NOT IN ('European Union', 'Other Asia, nes')
GROUP BY country, Year
ORDER BY country, Year
""").fetchall())

years = annual_value_top_trading[:,0].astype(int)
countries = annual_value_top_trading[:,1]
annual_value = (annual_value_top_trading[:,2].astype(float) * 1000)/1000000000000


plot_df = pd.DataFrame({
    'years': years,
    'countries': countries,
    'annual_value': annual_value
})

groups = plot_df.groupby('countries')

plt.figure(figsize=(10,6))
for name, group in groups:
    plt.plot(group['years'], group['annual_value'], label=name)
plt.grid()
plt.xlabel('Year')
plt.ylabel('Exports (USD Trillion)')
plt.title('Export Value of Trade in Goods by Country')
plt.legend()
plt.savefig('visualisations/Yearly Exports by Country', dpi=400)



top_old_trading_relationships= np.array(curs.execute("""
SELECT cc1.Country AS ReporterCountry, cc2.Country AS PartnerCountry, AVG(TradeValue)
FROM TradeStats
LEFT JOIN CountryCodes cc1 ON cc1.Code = TradeStats.ReporterISO3
LEFT JOIN CountryCodes cc2 ON cc2.Code = TradeStats.PartnerISO3
WHERE TradeValue != ''
AND ReporterCountry NOT IN ('European Union', 'Other Asia, nes')
AND PartnerCountry != 'None'
AND Year < 2010
GROUP BY ReporterCountry, PartnerCountry
ORDER BY AVG(TradeValue) DESC
LIMIT 10
""").fetchall())

top_old_trading_relationships = np.column_stack(([' -> '.join(sublist) for sublist in top_old_trading_relationships[:,[0, 1]]], top_old_trading_relationships[:,2].astype(float) * 1000))

top_new_trading_relationships= np.array(curs.execute("""
SELECT cc1.Country AS ReporterCountry, cc2.Country AS PartnerCountry, AVG(TradeValue)
FROM TradeStats
LEFT JOIN CountryCodes cc1 ON cc1.Code = TradeStats.ReporterISO3
LEFT JOIN CountryCodes cc2 ON cc2.Code = TradeStats.PartnerISO3
WHERE TradeValue != ''
AND ReporterCountry NOT IN ('European Union', 'Other Asia, nes')
AND PartnerCountry != 'None'
AND Year > 2010
GROUP BY ReporterCountry, PartnerCountry
ORDER BY AVG(TradeValue) DESC
LIMIT 10
""").fetchall())

top_new_trading_relationships = np.column_stack(([' -> '.join(sublist) for sublist in top_new_trading_relationships[:,[0, 1]]], top_new_trading_relationships[:,2].astype(float) * 1000))

old_years_trade_relationship_df = pd.DataFrame(top_old_trading_relationships, columns=['Exporter -> Importer', 'Average Yearly Exports 1988-2010 (USD)'])
recent_years_trade_relationship_df = pd.DataFrame(top_new_trading_relationships, columns=['Exporter -> Importer', 'Average Yearly Exports 2010-2021 (USD)'])
trading_countries_combined_table = pd.concat([old_years_trade_relationship_df, recent_years_trade_relationship_df], axis=1)
trading_countries_combined_table.insert(0, 'Rank', [i for i in range(1,11)])
trading_countries_combined_table['Average Yearly Exports 1988-2010 (USD)'] = pd.to_numeric(trading_countries_combined_table['Average Yearly Exports 1988-2010 (USD)']).apply(lambda x: f"{int(x):,}")
trading_countries_combined_table['Average Yearly Exports 2010-2021 (USD)'] = pd.to_numeric(trading_countries_combined_table['Average Yearly Exports 2010-2021 (USD)']).apply(lambda x: f"{int(x):,}")
dfi.export(trading_countries_combined_table.style.hide(axis='index'), 'visualisations/Country Trade Relationships Comparison.png', dpi=400)

plt.show()
