# BTC Analytics Dashboard — PRD

## Problème Original
Créer un dashboard BTC agrégeant toutes les APIs Bitcoin gratuites disponibles dans le monde, déployable sur Vercel via GitHub.

## Architecture Finale (v9.0.0)
```
/app/vercel/
├── main.py        # FastAPI backend — 70 APIs (2365 lignes)
├── index.html     # Frontend vanilla JS — 13 onglets (1397 lignes)
├── requirements.txt
├── vercel.json
└── README.md
```

## APIs Intégrées — 70 Sources

### Exchanges USD (28)
CoinGecko, Binance, Coinbase, Kraken, Bitfinex, Bitstamp, OKX, Bybit, Gemini, KuCoin, Gate.io, HTX, MEXC, Bitget, CoinEx, LBank, WhiteBit, CoinCap, Deribit, CoinPaprika, WBTC DEX, Poloniex, Crypto.com, BitMart, BTSE, CoinLore, CoinRanking, XT.com

### Exchanges Internationaux (19)
🇯🇵 bitFlyer, Coincheck, Zaif | 🇰🇷 Upbit, Bithumb, Korbit | 🇦🇺 BTCMarkets | 🇧🇷 Mercado Bitcoin, Foxbit, NovaDax | 🇷🇺 Exmo | 🇿🇦 Luno, VALR | 🇲🇽 Bitso | 🇮🇳 CoinDCX, WazirX | 🇮🇩 Indodax | 🇹🇷 BtcTurk, Paribu

### On-Chain (7)
CoinMetrics, BGR bitcoin-data.com, Mempool.space, Blockchair, Blockchain.info, Blockstream.info, Bitnodes.io

### Dérivés & Futures (6)
Binance FAPI, Kraken Futures, BitMEX, Hyperliquid DEX, Bitget Futures, Deribit DVol

### DeFi TVL (1)
DefiLlama

### Analytics (2)
CoinPaprika Extended, Bitfinex Stats

### Mining (2)
Blockchain.info Pools, WhatToMine

### Lightning (2)
Mempool.space Lightning, 1ML.com

### Sentiment (1)
Alternative.me Fear & Greed

### Historique (2)
Stooq CSV, CryptoCompare (via OKX Klines)

### ETF (2, clés requises)
SoSoValue, TwelveData

## Clés API Utilisateur
- SOSOVALUE_KEY: SOSO-486d78fe180c417e91c3d0a0894c36ea
- TWELVE_DATA_KEY: eb28a9e2191d40feafbaafebd4f9429c

## Onglets Frontend (13)
Dashboard | Marché | On-Chain | Technique | Réseau | Lightning | Exchanges USD | International | ETF | Dérivés | DeFi/Analytics | Alertes | Sources (70)

## FX Rates Supportées
USD, JPY, KRW, AUD, BRL, TRY, EUR, GBP, ZAR, MXN, INR, IDR

## Déploiement Vercel
1. Upload /app/vercel/* dans GitHub (structure plate, tous fichiers à la racine)
2. Connecter repo à Vercel, Framework: Other
3. Variables d'env: SOSOVALUE_KEY + TWELVE_DATA_KEY
4. Deploy

## Métriques avancées payantes (non intégrées)
- LTH/STH ratios détaillés → Glassnode Pro (~$30/mois)
- Whale cohorts précises → Nansen (~$150/mois)
- Realized Price par cohort → IntoTheBlock ($299/mois)
- SOAB complet → Glassnode
- Santiment sentiment → Santiment API (~$50/mois)
- Liquidations temps réel → Coinglass (payant)

## Changelog
- 2026: v9.0.0 — +11 APIs (Dérivés: Binance FAPI, Kraken Futures, BitMEX, Hyperliquid, Bitget Futures, Deribit DVol; DeFi: DefiLlama; Mining: WhatToMine; Analytics: CoinPaprika Extended, CryptoCompare/OKX, Bitfinex Stats). 70 sources total. Livraison code complète main.py + index.html
- 2026-03-22: v8.0.0 — +14 APIs (Poloniex, Crypto.com, BitMart, BTSE, CoinLore, CoinRanking, XT.com, Foxbit, NovaDax, Luno, VALR, Bitso, CoinDCX, WazirX, Indodax). FX ZAR/MXN/INR/IDR. 59 sources
- 2026-03: v7.0.0 — Architecture Vercel serverless, 44 APIs initiales


