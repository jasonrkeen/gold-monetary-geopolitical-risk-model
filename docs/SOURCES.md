# Source register

| Dataset | Provider | Frequency | Model use | Access |
|---|---|---:|---|---|
| Adjusted market prices | Yahoo Finance chart endpoint | Daily | Gold, ETF, miner, and market returns | Public web endpoint |
| 10-year real yield (`DFII10`) | Federal Reserve Board via FRED | Daily | Monetary opportunity-cost channel | Public CSV |
| Broad U.S. dollar (`DTWEXBGS`) | Federal Reserve Board via FRED | Daily | Currency channel | Public CSV |
| VIX (`VIXCLS`) | CBOE via FRED | Daily | Market-stress channel | Public CSV |
| 10-year breakeven inflation (`T10YIE`) | Federal Reserve Bank of St. Louis | Daily | Inflation-expectations channel | Public CSV |
| AI Geopolitical Risk Index | Matteo Iacoviello | Daily | Geopolitical threats and acts | Public CSV |
| Central-bank purchases | World Gold Council or reviewed official source | Monthly/quarterly | Strategic official-sector demand | Optional manual import |
| Gold production and reserves | U.S. Geological Survey | Annual | Supply-security context | Methodology/source register |
| COMEX positioning | U.S. CFTC | Weekly | Positioning/crowding extension | Planned extension |

## Primary references

- FRED: <https://fred.stlouisfed.org/>
- AI-GPR data: <https://www.matteoiacoviello.com/ai_gpr.html>
- World Gold Council Gold Demand Trends: <https://www.gold.org/goldhub/research/gold-demand-trends>
- USGS Mineral Commodity Summaries: <https://www.usgs.gov/centers/national-minerals-information-center/mineral-commodity-summaries>
- CFTC Commitments of Traders: <https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm>

Market prices are used for research and demonstration. Users should review the
terms of each data provider before redistribution or commercial deployment.

