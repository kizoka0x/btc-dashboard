# BTC Analytics Dashboard — PRD

## Problème Original
Créer un dashboard BTC agrégeant toutes les APIs Bitcoin gratuites disponibles dans le monde, déployable sur Vercel via GitHub.

## Architecture Finale (v8.0.0)
```
/app/vercel/
├── main.py        # FastAPI backend — 59 APIs (1726 lignes)
├── index.html     # Frontend vanilla JS — 11 onglets (1076 lignes)
├── requirements.txt
├── vercel.json
└── README.md
```

## APIs Intégrées — 59 Sources

### Exchanges USD (27)
CoinGecko, Binance, Coinbase, Kraken, Bitfinex, Bitstamp, OKX, Bybit, Gemini, KuCoin, Gate.io, HTX, MEXC, Bitget, CoinEx, LBank, WhiteBit, CoinCap, Deribit, CoinPaprika, WBTC DEX, Poloniex, Crypto.com, BitMart, BTSE, CoinLore, CoinRanking

### Exchanges Internationaux (19)
🇯🇵 bitFlyer, Coincheck, Zaif | 🇰🇷 Upbit, Bithumb, Korbit | 🇦🇺 BTCMarkets | 🇧🇷 Mercado Bitcoin, Foxbit, NovaDax | 🇷🇺 Exmo | 🇿🇦 Luno, VALR | 🇲🇽 Bitso | 🇮🇳 CoinDCX, WazirX | 🇮🇩 Indodax | 🇹🇷 BtcTurk, Paribu

### On-Chain (7)
CoinMetrics, BGR bitcoin-data.com, Mempool.space, Blockchair, Blockchain.info, Blockstream.info, Bitnodes.io

### Lightning (2), Sentiment (1), Historique (1)
Mempool.space LN, 1ML.com | Alternative.me | Stooq CSV

### ETF (2, clés)
SoSoValue, TwelveData

## Clés API Utilisateur
- SOSOVALUE_KEY: SOSO-486d78fe180c417e91c3d0a0894c36ea
- TWELVE_DATA_KEY: eb28a9e2191d40feafbaafebd4f9429c

## Onglets Frontend (11)
Dashboard | Marché | On-Chain | Technique | Réseau | Lightning | Exchanges USD | International | ETF | Alertes | Sources (59)

## FX Rates Supportées
USD, JPY, KRW, AUD, BRL, TRY, EUR, GBP, ZAR, MXN, INR, IDR (via exchangerate-api.com + CoinGecko)

## Déploiement Vercel
1. Upload /app/vercel/* dans GitHub (structure plate, tous fichiers à la racine)
2. Connecter repo à Vercel, Framework: Other
3. Variables d'env: SOSOVALUE_KEY + TWELVE_DATA_KEY
4. Deploy

## Changelog
- 2026-03-22: v8.0.0 — +14 nouvelles APIs (6 USD, 8 international), FX ZAR/MXN/INR/IDR, onglet Sources, ETF corrigé, 59 sources total
- 2026-03: v7.0.0 — Architecture Vercel serverless, 44 APIs initiales

