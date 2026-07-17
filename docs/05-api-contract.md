# API Contract

Frontend communicates only through REST APIs.

Base URL

/api/v1

Examples

GET /companies

GET /companies/{symbol}

GET /companies/{symbol}/financials

GET /companies/{symbol}/news

GET /companies/{symbol}/recommendation

GET /market/overview

GET /market/top-gainers

GET /market/top-losers

GET /portfolio

POST /portfolio

GET /watchlist

POST /watchlist

Response Format

{
    "success": true,
    "data": {}
}

Errors

{
    "success": false,
    "message": "..."
}