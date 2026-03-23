
Action: {"type": "mcp_tool", "tool_name": "mcp_view_bulk", "tool_arguments": {"paths": ["/app/memory/PRD.md", "/app/vercel"]}}
Observation: ===FILE: /app/memory/PRD.md
/app/memory/PRD.md:
1|# BTC Analytics Dashboard — PRD
2|
3|## Problème Original
4|Créer un dashboard BTC agrégeant toutes les APIs Bitcoin gratuites disponibles dans le monde, déployable sur Vercel via GitHub.
5|
6|## Architecture Finale (v9.0.0)
7|```
8|/app/vercel/
9|├── main.py        # FastAPI backend — 70 APIs (2365 lignes)
10|├── index.html     # Frontend vanilla JS — 13 onglets (1397 lignes)
11|├── requirements.txt
12|├── vercel.json
13|└── README.md
14|```
15|
16|## APIs Intégrées — 70 Sources
17|
18|### Exchanges USD (28)
19|CoinGecko, Binance, Coinbase, Kraken, Bitfinex, Bitstamp, OKX, Bybit, Gemini, KuCoin, Gate.io, HTX, MEXC, Bitget, CoinEx, LBank, WhiteBit, CoinCap, Deribit, CoinPaprika, WBTC DEX, Poloniex, Crypto.com, BitMart, BTSE, CoinLore, CoinRanking, XT.com
20|
21|### Exchanges Internationaux (19)
22|🇯🇵 bitFlyer, Coincheck, Zaif | 🇰🇷 Upbit, Bithumb, Korbit | 🇦🇺 BTCMarkets | 🇧🇷 Mercado Bitcoin, Foxbit, NovaDax | 🇷🇺 Exmo | 🇿🇦 Luno, VALR | 🇲🇽 Bitso | 🇮🇳 CoinDCX, WazirX | 🇮🇩 Indodax | 🇹🇷 BtcTurk, Paribu
23|
24|### On-Chain (7)
25|CoinMetrics, BGR bitcoin-data.com, Mempool.space, Blockchair, Blockchain.info, Blockstream.info, Bitnodes.io
26|
27|### Dérivés & Futures (6)
28|Binance FAPI, Kraken Futures, BitMEX, Hyperliquid DEX, Bitget Futures, Deribit DVol
29|
30|### DeFi TVL (1)
31|DefiLlama
32|
33|### Analytics (2)
34|CoinPaprika Extended, Bitfinex Stats
35|
36|### Mining (2)
37|Blockchain.info Pools, WhatToMine
38|
39|### Lightning (2)
40|Mempool.space Lightning, 1ML.com
41|
42|### Sentiment (1)
43|Alternative.me Fear & Greed
44|
45|### Historique (2)
46|Stooq CSV, CryptoCompare (via OKX Klines)
47|
48|### ETF (2, clés requises)
49|SoSoValue, TwelveData
50|
51|## Clés API Utilisateur
52|- SOSOVALUE_KEY: SOSO-486d78fe180c417e91c3d0a0894c36ea
53|- TWELVE_DATA_KEY: eb28a9e2191d40feafbaafebd4f9429c
54|
55|## Onglets Frontend (13)
56|Dashboard | Marché | On-Chain | Technique | Réseau | Lightning | Exchanges USD | International | ETF | Dérivés | DeFi/Analytics | Alertes | Sources (70)
57|
58|## FX Rates Supportées
59|USD, JPY, KRW, AUD, BRL, TRY, EUR, GBP, ZAR, MXN, INR, IDR
60|
61|## Déploiement Vercel
62|1. Upload /app/vercel/* dans GitHub (structure plate, tous fichiers à la racine)
63|2. Connecter repo à Vercel, Framework: Other
64|3. Variables d'env: SOSOVALUE_KEY + TWELVE_DATA_KEY
65|4. Deploy
66|
67|## Métriques avancées payantes (non intégrées)
68|- LTH/STH ratios détaillés → Glassnode Pro (~$30/mois)
69|- Whale cohorts précises → Nansen (~$150/mois)
70|- Realized Price par cohort → IntoTheBlock ($299/mois)
71|- SOAB complet → Glassnode
72|- Santiment sentiment → Santiment API (~$50/mois)
73|- Liquidations temps réel → Coinglass (payant)
74|
75|## Changelog
76|- 2026: v9.0.0 — +11 APIs (Dérivés: Binance FAPI, Kraken Futures, BitMEX, Hyperliquid, Bitget Futures, Deribit DVol; DeFi: DefiLlama; Mining: WhatToMine; Analytics: CoinPaprika Extended, CryptoCompare/OKX, Bitfinex Stats). 70 sources total. Livraison code complète main.py + index.html
77|- 2026-03-22: v8.0.0 — +14 APIs (Poloniex, Crypto.com, BitMart, BTSE, CoinLore, CoinRanking, XT.com, Foxbit, NovaDax, Luno, VALR, Bitso, CoinDCX, WazirX, Indodax). FX ZAR/MXN/INR/IDR. 59 sources
78|- 2026-03: v7.0.0 — Architecture Vercel serverless, 44 APIs initiales
79|

===END

===DIR: /app/vercel
/app/vercel/ (depth=2):
/app/vercel/README.md
/app/vercel/__pycache__/
/app/vercel/__pycache__/main.cpython-311.pyc
/app/vercel/index.html
/app/vercel/main.py
/app/vercel/requirements.txt
/app/vercel/vercel.json

===END
