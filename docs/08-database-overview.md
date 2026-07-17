# Database Overview

## Database

Database Engine

- PostgreSQL

The database is designed to support both historical and real-time market data.

---

# Core Tables

## Companies

Stores all listed companies.

Fields

- id
- symbol
- company_name
- market
- sector
- industry
- description
- website
- logo
- exchange

---

## Financial Statements

Stores annual and quarterly reports.

Fields

- company_id
- period
- income_statement
- balance_sheet
- cash_flow
- financial_ratios

---

## Market Prices

Stores historical market prices.

Fields

- company_id
- date
- open
- high
- low
- close
- volume

---

## News

Stores financial news.

Fields

- id
- company_id
- title
- source
- published_date
- url
- summary
- sentiment

---

## AI Recommendations

Stores AI generated recommendations.

Fields

- company_id
- recommendation
- confidence
- explanation
- generated_at

---

## Users

Stores user accounts.

Fields

- id
- email
- name
- password_hash

---

## Portfolio

Stores user holdings.

Fields

- user_id
- company_id
- quantity
- average_price

---

## Watchlist

Stores bookmarked companies.

Fields

- user_id
- company_id

---

# Relationships

Company

↓

Financial Statements

↓

Market Prices

↓

News

↓

AI Recommendations

Users

↓

Portfolio

↓

Watchlist