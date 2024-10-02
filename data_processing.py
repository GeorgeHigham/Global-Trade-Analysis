import sqlite3
import csv

countries = []
codes = []

with open('data/trade_1988_2021.csv', mode='r') as file:
    reader = csv.reader(file)
    for row in reader:
        if row[0] == 'ReporterISO3':
            continue
        if row[0] not in codes:
            codes.append(row[0])
        if row[1] not in countries:
            countries.append(row[1])

conn = sqlite3.connect("trades.db")
curs = conn.cursor()

curs.execute("""
    CREATE TABLE CountryCodes (
        Country VARCHAR(50),
        Code CHAR(3),
        PRIMARY KEY(Country)
    )
""")

curs.execute("BEGIN TRANSACTION;")

for ind in range(len(countries)):
    try:
        curs.execute('INSERT INTO CountryCodes (Country, Code) VALUES (?, ?)', [countries[ind], codes[ind]])
    except Exception as e:
        print(f'Exception: {e}')
        print(f'Row: {row}')
        curs.execute("ROLLBACK")
        break
curs.execute("COMMIT")

curs.execute("""
    CREATE TABLE TradeStats (
        ISO3Year CHAR(10),
        ReporterISO3 CHAR(3),
        PartnerISO3 CHAR(3),
        Year INT,
        TradeFlowName VARCHAR(50),
        TradeValue FLOAT,
        PRIMARY KEY(ISO3Year)
    )
""")

curs.execute("BEGIN TRANSACTION;")

with open('data/trade_1988_2021.csv', mode='r') as file:
    reader = csv.reader(file)
    for row in reader:
        if row[0] == 'ReporterISO3':
            continue
        prim_key = f'{row[0]}{row[2]}{row[4]}'
        try:
            curs.execute('INSERT INTO TradeStats (ISO3Year, ReporterISO3, PartnerISO3, Year, TradeFlowName, TradeValue) VALUES (?, ?, ?, ?, ?, ?)', [prim_key, row[0], row[2], row[4], row[5], row[6]])
        except Exception as e:
            print(f'Exception: {e}')
            print(f'Row: {row}')
            curs.execute("ROLLBACK")
            break
    curs.execute("COMMIT")


curs.execute("""
    CREATE TABLE ContinentCountry (
        Continent VARCHAR(50),
        Country VARCHAR(50),
        PRIMARY KEY(Country)
    )
""")

curs.execute("BEGIN TRANSACTION;")

with open('data/Countries by continents.csv', mode='r') as file:
    reader = csv.reader(file)
    for row in reader:
        if row[0] == 'Continent':
            continue
        try:
            curs.execute('INSERT INTO ContinentCountry (Continent, Country) VALUES (?, ?)', row)
        except Exception as e:
            print(f'Exception: {e}')
            print(f'Row: {row}')
            curs.execute("ROLLBACK")
            break
    curs.execute("COMMIT")
