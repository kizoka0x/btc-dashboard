"""
BTC On-Chain Analytics API — v9.0.0 (Vercel Edition)
Toutes les APIs BTC gratuites disponibles dans le monde — 70 sources.

Structure Vercel : ce fichier est servi comme serverless function.
GET /         → index.html
GET /api/*    → endpoints FastAPI

APIs intégrées (sans clé) :
  EXCHANGES USD : CoinGecko, Binance, Coinbase, Kraken, Bitfinex, Bitstamp,
                  OKX, Bybit, Gemini, KuCoin, Gate.io, HTX, MEXC, Bitget,
                  CoinEx, LBank, WhiteBit, CoinCap, Deribit, CoinPaprika
  EXCHANGES INTL: bitFlyer/Coincheck/Zaif(JP), Upbit/Bithumb/Korbit(KR),
                  BTCMarkets(AU), BtcTurk/Paribu(TR), Mercado Bitcoin(BR),
                  Exmo(RU/EU)
  DEX ON-CHAIN  : DexScreener (WBTC Uniswap Ethereum)
  ON-CHAIN      : CoinMetrics, BGR/bitcoin-data.com, Mempool.space,
                  Blockchair, Blockchain.info, Blockstream.info, Bitnodes.io
  HISTORIQUE    : Stooq (CSV 30j)
  SENTIMENT     : Alternative.me Fear & Greed + ticker
  LIGHTNING     : Mempool.space + 1ML.com
  MINING        : Blockchain.info pools
  ETF (clés)    : SoSoValue, TwelveData

APIs supplémentaires v8 (+14 sources) :
  EXCHANGES USD+ : Poloniex, Crypto.com, BitMart, BTSE, CoinLore, CoinRanking, XT.com
  EXCHANGES INTL+: Foxbit(BR), NovaDax(BR), Luno(ZA), VALR(ZA),
                   Bitso(MX), CoinDCX(IN), WazirX(IN), Indodax(ID)
  DÉRIVÉS (v9)   : Binance FAPI (BTC-Perp), Kraken Futures, BitMEX,
                   Hyperliquid DEX, Bitget Futures, Deribit DVol
  DEFI/TVL (v9)  : DefiLlama (Bitcoin Ecosystem TVL)
  ANALYTICS (v9) : CryptoCompare (historique OHLCV), Messari (métriques BTC)
  MINING+ (v9)   : WhatToMine (profitabilité mining BTC)
  STATS (v9)     : Bitfinex Stats (positions long/short)
"""

import os, time, math, requests, logging
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# ── load .env if present (dev local) ───────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="BTC Analytics — 70 APIs Gratuites", version="9.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BGR_BASE    = "https://bitcoin-data.com"
SOSO_BASE   = "https://api.sosovalue.xyz"
TWELVE_BASE = "https://api.twelvedata.com"

# ── Caches globaux ─────────────────────────────────────────────
_bgr_cache         = {"data": {}, "ts": 0}
_bgr_holders_cache = {"data": {}, "ts": 0}
_cm_ext_cache      = {"data": {}, "ts": 0}
_pools_cache       = {"data": {}, "ts": 0}
_soso_cache        = {"data": {}, "ts": 0}
_twelve_cache      = {"data": {}, "ts": 0}
_puell_cache       = {"data": {}, "ts": 0}
_cg_cache          = {"data": {}, "ts": 0}
_cb_cache          = {"data": {}, "ts": 0}
_fx_cache          = {"data": {}, "ts": 0}
_ex_cache          = {"data": {}, "ts": 0}
_1ml_cache         = {"data": {}, "ts": 0}
_dex_cache         = {"data": {}, "ts": 0}
_stooq_cache       = {"data": {}, "ts": 0}
_intl_cache        = {"data": {}, "ts": 0}
_defillama_cache   = {"data": {}, "ts": 0}
_mempool_deep_cache= {"data": {}, "ts": 0}
_bcinfo_chart_cache= {"data": {}, "ts": 0}
_cm_deep_cache     = {"data": {}, "ts": 0}
# ── Caches nouvelles sources v8 ────────────────────────────
_poloniex_cache    = {"data": {}, "ts": 0}
_cdotcom_cache     = {"data": {}, "ts": 0}
_bitmart_cache     = {"data": {}, "ts": 0}
_btse_cache        = {"data": {}, "ts": 0}
_coinlore_cache    = {"data": {}, "ts": 0}
_coinranking_cache = {"data": {}, "ts": 0}
_foxbit_cache      = {"data": {}, "ts": 0}
_novadax_cache     = {"data": {}, "ts": 0}
_luno_cache        = {"data": {}, "ts": 0}
_valr_cache        = {"data": {}, "ts": 0}
_bitso_cache       = {"data": {}, "ts": 0}
_coindcx_cache     = {"data": {}, "ts": 0}
_wazirx_cache      = {"data": {}, "ts": 0}
_indodax_cache     = {"data": {}, "ts": 0}
# ── Caches nouvelles sources v9 (dérivés, DeFi, analytics) ──────────────
_bnf_cache         = {"data": {}, "ts": 0}   # Binance FAPI Futures
_krf_cache         = {"data": {}, "ts": 0}   # Kraken Futures
_bitmex_cache      = {"data": {}, "ts": 0}   # BitMEX XBTUSD
_hyper_cache       = {"data": {}, "ts": 0}   # Hyperliquid DEX
_xtcom_cache       = {"data": {}, "ts": 0}   # XT.com Exchange
_bgf_cache         = {"data": {}, "ts": 0}   # Bitget Futures
_messari_cache     = {"data": {}, "ts": 0}   # Messari Analytics
_cc_cache          = {"data": {}, "ts": 0}   # CryptoCompare
_bfxstats_cache    = {"data": {}, "ts": 0}   # Bitfinex Stats
_dvol_cache        = {"data": {}, "ts": 0}   # Deribit DVol
_wtm_cache         = {"data": {}, "ts": 0}   # WhatToMine

BGR_TTL    = 3600
SOSO_TTL   = 86400
TWELVE_TTL = 3600
EX_TTL     = 60
INTL_TTL   = 90
FX_TTL     = 300

# ══════════════════════════════════════════════════════════════
# UTILITAIRES
# ══════════════════════════════════════════════════════════════
def safe(v, d=6):
    try:
        f = float(v)
        return None if (math.isnan(f) or math.isinf(f)) else round(f, d)
    except:
        return None

def get(url, params=None, timeout=9, headers=None):
    # 🛑 On bloque les sites qui détestent Vercel
    if "bitcoin-data.com" in url or "fapi.binance.com" in url:
        return None

    try:
        # 🟢 HACK INFAILLIBLE : On force l'activation de 'requests' ici !
        import requests 
        
        h = {
            "Accept": "application/json", 
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
        }
        if headers:
            h.update(headers)
            
        r = requests.get(url, params=params or {}, timeout=timeout, headers=h)
        
        if r.status_code == 200:
            return r.json()
            
    except Exception as e:
        # On enlève le silencieux : si un site plante, Vercel l'écrira dans les logs
        print(f"Erreur sur {url}: {e}")
        
    return None

def sf(fn):
    """safe_fetch — attrape les exceptions d'une fonction fetch"""
    try:
        return fn()
    except Exception as e:
        log.warning(f"sf {fn.__name__}: {e}")
        return {}

# ══════════════════════════════════════════════════════════════
# FX RATES — taux de change via exchangerate-api + CoinGecko BTC
# ══════════════════════════════════════════════════════════════
def fetch_fx():
    global _fx_cache
    now = time.time()
    if now - _fx_cache["ts"] < FX_TTL and _fx_cache["data"]:
        return _fx_cache["data"]

    # Taux USD→devises via exchangerate-api (sans clé, fiable)
    result = {}
    d_fx = get("https://api.exchangerate-api.com/v4/latest/USD", timeout=6)
    rates_raw = d_fx.get("rates", {}) if d_fx else {}

    # Récupération prix BTC/USD depuis CoinGecko (ou cache)
    cg = get("https://api.coingecko.com/api/v3/simple/price", {
        "ids": "bitcoin",
        "vs_currencies": "usd"
    }, timeout=6)
    btc_usd = None
    if cg and cg.get("bitcoin", {}).get("usd"):
        btc_usd = cg["bitcoin"]["usd"]

    # Fallback pour BTC/USD si CoinGecko rate-limité
    if not btc_usd and _cg_cache.get("data", {}).get("price_usd"):
        btc_usd = _cg_cache["data"]["price_usd"]

    result["btc_usd_cg"] = safe(btc_usd, 2) if btc_usd else None

    # Construction des taux et prix BTC dans chaque devise
    currencies = {
        "jpy": "JPY", "krw": "KRW", "aud": "AUD", "brl": "BRL",
        "try": "TRY", "eur": "EUR", "gbp": "GBP",
        "zar": "ZAR", "mxn": "MXN", "inr": "INR", "idr": "IDR"
    }
    for cur_lower, cur_upper in currencies.items():
        rate = rates_raw.get(cur_upper)  # 1 USD = rate devises
        if rate and float(rate) > 0:
            result[f"rate_{cur_lower}"] = round(float(rate), 6)
            if btc_usd:
                result[f"btc_{cur_lower}"] = safe(btc_usd * float(rate), 2)

    if result:
        _fx_cache = {"data": result, "ts": now}
    return result

def to_usd(native_price, currency_rate):
    """Convertit un prix natif en USD via le taux (unités par USD)"""
    if native_price and currency_rate and currency_rate > 0:
        return round(native_price / currency_rate, 2)
    return None

# ══════════════════════════════════════════════════════════════
# COINGECKO
# ══════════════════════════════════════════════════════════════
def fetch_coingecko():
    global _cg_cache
    now = time.time()
    if now - _cg_cache["ts"] < 90 and _cg_cache["data"]:
        return _cg_cache["data"]
    d = get("https://api.coingecko.com/api/v3/coins/bitcoin", {
        "localization": "false", "tickers": "false",
        "community_data": "false", "developer_data": "false", "sparkline": "false"
    })
    if not d:
        return _cg_cache.get("data", {})
    md = d.get("market_data", {})
    result = {
        "price_usd":          safe(md.get("current_price", {}).get("usd"), 2),
        "price_change_1d":    safe(md.get("price_change_percentage_24h"), 4),
        "price_change_7d":    safe(md.get("price_change_percentage_7d"), 4),
        "price_change_30d":   safe(md.get("price_change_percentage_30d"), 4),
        "volume_usd":         safe(md.get("total_volume", {}).get("usd"), 0),
        "market_cap":         safe(md.get("market_cap", {}).get("usd"), 0),
        "ath_usd":            safe(md.get("ath", {}).get("usd"), 2),
        "ath_pct":            safe(md.get("ath_change_percentage", {}).get("usd"), 2),
        "high_24h":           safe(md.get("high_24h", {}).get("usd"), 2),
        "low_24h":            safe(md.get("low_24h", {}).get("usd"), 2),
        "circulating_supply": safe(md.get("circulating_supply"), 0),
        "max_supply":         21_000_000,
    }
    if result.get("price_usd"):
        _cg_cache = {"data": result, "ts": now}
    return result

def fetch_coingecko_global():
    d = get("https://api.coingecko.com/api/v3/global")
    if not d:
        return {}
    data  = d.get("data", {})
    mcaps = data.get("market_cap_percentage", {})
    return {
        "btc_dominance":         safe(mcaps.get("btc"), 2),
        "eth_dominance":         safe(mcaps.get("eth"), 2),
        "total_market_cap_usd":  safe(data.get("total_market_cap", {}).get("usd"), 0),
        "total_volume_24h_usd":  safe(data.get("total_volume", {}).get("usd"), 0),
        "market_cap_change_24h": safe(data.get("market_cap_change_percentage_24h_usd"), 2),
        "active_cryptos":        data.get("active_cryptocurrencies"),
    }

def fetch_stablecoins():
    d = get("https://api.coingecko.com/api/v3/simple/price", {
        "ids": "tether,usd-coin,dai", "vs_currencies": "usd", "include_market_cap": "true"
    })
    if not d:
        return {}
    usdt  = safe(d.get("tether", {}).get("usd_market_cap"), 0)
    usdc  = safe(d.get("usd-coin", {}).get("usd_market_cap"), 0)
    dai   = safe(d.get("dai", {}).get("usd_market_cap"), 0)
    total = sum(x for x in [usdt, usdc, dai] if x)
    return {"usdt_market_cap": usdt, "usdc_market_cap": usdc, "dai_market_cap": dai,
            "stablecoin_total": safe(total, 0)}

# ══════════════════════════════════════════════════════════════
# COINMETRICS
# ══════════════════════════════════════════════════════════════
def fetch_coinmetrics():
    """MVRV/NUPL via Kraken OHLC MA200 proxy (CoinMetrics blocks serverless)"""
    result = {}
    try:
        since = int(time.time()) - 400 * 86400
        d = get("https://api.kraken.com/0/public/OHLC",
                {"pair": "XBTUSD", "interval": "1440", "since": since})
        if not d or d.get("error"): return result
        candles = d.get("result", {}).get("XXBTZUSD", [])
        if len(candles) < 200: return result
        closes = [float(c[4]) for c in candles]
        price = closes[-1]
        ma200 = sum(closes[-200:]) / 200
        if ma200 > 0 and price > 0:
            mvrv = round(price / ma200, 4)
            nupl = round(1 - 1/mvrv, 4)
            supply = 19700000
            realized_cap = round(ma200 * supply, 0)
            result.update({
                "mvrv": mvrv,
                "realized_cap": realized_cap,
                "nupl": nupl,
                "coinmetrics_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            })
    except Exception as e:
        log.warning(f"fetch_coinmetrics proxy: {e}")
    return result

def fetch_coinmetrics_extended():
    global _cm_ext_cache
    now = time.time()
    if now - _cm_ext_cache["ts"] < 3600 and _cm_ext_cache["data"]:
        return _cm_ext_cache["data"]
    metrics = "FlowInExNtv,FlowOutExNtv,FlowInExUSD,FlowOutExUSD,SplyExNtv,SplyExUSD,IssTotNtv,IssTotUSD,TxTfrCnt,AdrBalCnt,ROI30d,ROI1yr,BlkCnt,FeeTotNtv"
    d = get(f"https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=btc&metrics={metrics}&page_size=1")
    result = {}
    if d and d.get("data"):
        row = d["data"][0] if isinstance(d["data"], list) else {}
        result = {
            "flow_in_ex_btc":  safe(row.get("FlowInExNtv"), 2),
            "flow_out_ex_btc": safe(row.get("FlowOutExNtv"), 2),
            "flow_in_ex_usd":  safe(row.get("FlowInExUSD"), 2),
            "flow_out_ex_usd": safe(row.get("FlowOutExUSD"), 2),
            "sply_ex_btc":     safe(row.get("SplyExNtv"), 2),
            "tx_transfer_cnt": safe(row.get("TxTfrCnt"), 0),
            "adr_bal_cnt":     safe(row.get("AdrBalCnt"), 0),
            "roi_30d":         safe(row.get("ROI30d"), 4),
            "roi_1yr":         safe(row.get("ROI1yr"), 4),
            "fee_tot_btc_cm":  safe(row.get("FeeTotNtv"), 4),
        }
    if result:
        _cm_ext_cache = {"data": result, "ts": now}
    return result

def fetch_puell_multiple():
    global _puell_cache
    now = time.time()
    if now - _puell_cache["ts"] < 86400 and _puell_cache["data"]:
        return _puell_cache["data"]
    try:
        d = get("https://community-api.coinmetrics.io/v4/timeseries/asset-metrics", {
            "assets": "btc", "metrics": "IssTotUSD", "page_size": "365", "paging_from": "end"
        })
        if not d or not d.get("data") or len(d["data"]) < 30:
            return {}
        values = [float(r["IssTotUSD"]) for r in d["data"]
                  if r.get("IssTotUSD") and float(r["IssTotUSD"]) > 0]
        if not values:
            return {}
        today = values[-1]
        ma365 = sum(values) / len(values)
        puell = round(today / ma365, 4) if ma365 > 0 else None
        result = {"puell_multiple": puell, "puell_iss_today_usd": round(today, 2), "puell_ma365_usd": round(ma365, 2)}
        _puell_cache = {"data": result, "ts": now}
        return result
    except Exception as e:
        log.warning(f"fetch_puell: {e}")
        return {}

# ══════════════════════════════════════════════════════════════
# BGR / bitcoin-data.com
# ══════════════════════════════════════════════════════════════
def fetch_bgeometrics():
    return {}
    global _bgr_cache
    now = time.time()
    if now - _bgr_cache["ts"] < BGR_TTL and _bgr_cache["data"]:
        return _bgr_cache["data"]
    result = {}
    B = BGR_BASE
    for name, url, key, field in [
        ("asopr",      f"{B}/api-block/v1/asopr/1",       "asopr",      "asopr"),
        ("sopr_block", f"{B}/api-block/v1/sopr-block/1",  "soprBlock",  "sopr_block"),
        ("nrpl_usd",   f"{B}/api-block/v1/nrpl-usd/1",   "nrplUsd",    "nrpl_usd"),
        ("nrpl_btc",   f"{B}/api-block/v1/nrpl-btc/1",   "nrplBtc",    "nrpl_btc"),
    ]:
        d = get(url)
        if d and isinstance(d, dict):
            result[field] = safe(d.get(key), 4)
    if result:
        _bgr_cache = {"data": result, "ts": now}
    return result

def fetch_bgr_holders():
    return {}
    global _bgr_holders_cache
    now = time.time()
    if now - _bgr_holders_cache["ts"] < BGR_TTL and _bgr_holders_cache["data"]:
        return _bgr_holders_cache["data"]
    result = {}
    d = get(f"{BGR_BASE}/api-block/v1/btc-price/1")
    if d and isinstance(d, dict):
        rp = d.get("realizedPrice") or d.get("realized_price") or d.get("btcPrice")
        if rp:
            result["lth_realized_price"] = safe(rp, 2)
    d3 = get(f"{BGR_BASE}/api-block/v1/btc-1000/1")
    if d3 and isinstance(d3, dict):
        result["whale_1000_count"] = safe(d3.get("btc1000"), 0)
    if result:
        _bgr_holders_cache = {"data": result, "ts": now}
    return result
  
# ══════════════════════════════════════════════════════════════
# MEMPOOL.SPACE
# ══════════════════════════════════════════════════════════════
def fetch_mempool():
    result = {}
    fees = get("https://mempool.space/api/v1/fees/recommended")
    if fees:
        result.update({"fee_high": safe(fees.get("fastestFee"), 0),
                       "fee_med": safe(fees.get("halfHourFee"), 0),
                       "fee_low": safe(fees.get("hourFee"), 0),
                       "fee_min": safe(fees.get("minimumFee"), 0)})
    mem = get("https://mempool.space/api/mempool")
    if mem:
        result.update({"pending_txs": safe(mem.get("count"), 0),
                       "pending_mb": safe((mem.get("vsize") or 0) / 1e6, 2),
                       "pending_fees_btc": safe((mem.get("total_fee") or 0) / 1e8, 4)})
    mining = get("https://mempool.space/api/v1/mining/hashrate/1m")
    if mining:
        hrs = mining.get("hashrates", [])
        dfs = mining.get("difficulty", [])
        if hrs:
            result["hashrate_eh"] = safe(hrs[-1].get("avgHashrate", 0) / 1e18, 2)
        if dfs:
            result["difficulty"] = safe(dfs[-1].get("difficulty"), 0)
    da = get("https://mempool.space/api/v1/difficulty-adjustment")
    if da:
        result.update({"diff_progress_pct": safe(da.get("progressPercent"), 2),
                       "diff_change_pct": safe(da.get("difficultyChange"), 4),
                       "diff_remaining_blocks": safe(da.get("remainingBlocks"), 0),
                       "previous_retarget_pct": safe(da.get("previousRetarget"), 4)})
    ln = get("https://mempool.space/api/v1/lightning/statistics/latest")
    if ln:
        l = ln.get("latest", {})
        result.update({"ln_channels": safe(l.get("channel_count"), 0),
                       "ln_nodes": safe(l.get("node_count"), 0),
                       "ln_capacity_btc": safe((l.get("total_capacity") or 0) / 1e8, 2),
                       "ln_avg_capacity_sat": safe(l.get("avg_capacity"), 0)})
    return result

# ══════════════════════════════════════════════════════════════
# BLOCKCHAIN.INFO
# ══════════════════════════════════════════════════════════════
def fetch_blockchain_info():
    d = get("https://blockchain.info/stats?format=json", timeout=8)
    if not d:
        return {}
    miners_rev_raw = d.get("miners_revenue_btc") or d.get("n_btc_mined") or 0
    miners_rev_btc = round(float(miners_rev_raw) / 1e8, 4) if miners_rev_raw else None
    return {
        "blockchain_market_price":  safe(d.get("market_price_usd"), 2),
        "blockchain_minutes_btw_blocks": safe(d.get("minutes_between_blocks"), 2),
        "blockchain_n_tx":          safe(d.get("n_tx"), 0),
        "blockchain_blocks_today":  safe(d.get("n_blocks_mined"), 0),
        "blockchain_miners_rev_usd":safe(d.get("miners_revenue_usd"), 2),
        "blockchain_hash_rate_gh":  safe(d.get("hash_rate"), 2),
    }

def fetch_blockchain_query():
    result = {}
    try:
        r = requests.get("https://blockchain.info/q/getblockcount", timeout=6,
                         headers={"User-Agent": "btc-analytics/7.0"})
        if r.status_code == 200:
            result["bi_block_height"] = int(r.text.strip())
    except: pass
    try:
        r = requests.get("https://blockchain.info/q/totalbc", timeout=6,
                         headers={"User-Agent": "btc-analytics/7.0"})
        if r.status_code == 200:
            sats = int(r.text.strip())
            result["bi_supply_btc"]  = round(sats / 1e8, 2)
            result["bi_supply_sats"] = sats
    except: pass
    try:
        r = requests.get("https://blockchain.info/q/latesthash", timeout=6,
                         headers={"User-Agent": "btc-analytics/7.0"})
        if r.status_code == 200:
            h = r.text.strip()
            result["bi_latest_hash"] = h[:20] + "..." if len(h) > 20 else h
    except: pass
    return result

# ══════════════════════════════════════════════════════════════
# BLOCKCHAIR
# ══════════════════════════════════════════════════════════════
def fetch_blockchair():
    d = get("https://api.blockchair.com/bitcoin/stats")
    if not d:
        return {}
    data = d.get("data", {})
    return {
        "blocks_total":          safe(data.get("blocks"), 0),
        "blockchain_tx_total":   safe(data.get("transactions"), 0),
        "utxo_count":            safe(data.get("outputs"), 0),
        "blockchain_size_gb":    safe((data.get("blockchain_size") or 0) / 1e9, 2),
        "transactions_24h":      safe(data.get("transactions_24h"), 0),
        "bc_vol_24h_sat":        safe(data.get("volume_24h"), 0),   # en satoshis
        "mempool_tps":           safe(data.get("mempool_tps"), 2),
    }

# ══════════════════════════════════════════════════════════════
# BLOCKSTREAM.INFO
# ══════════════════════════════════════════════════════════════
def fetch_blockstream():
    result = {}
    try:
        r = requests.get("https://blockstream.info/api/blocks/tip/height", timeout=8,
                         headers={"User-Agent": "btc-analytics/7.0"})
        if r.status_code == 200:
            result["blockstream_block_height"] = int(r.text.strip())
    except: pass
    try:
        d = get("https://blockstream.info/api/mempool", timeout=8)
        if d:
            result["blockstream_mempool_count"]    = safe(d.get("count"), 0)
            result["blockstream_mempool_vsize_mb"] = safe((d.get("vsize") or 0) / 1e6, 2)
    except: pass
    return result

# ══════════════════════════════════════════════════════════════
# BITNODES.IO
# ══════════════════════════════════════════════════════════════
def fetch_bitnodes():
    d = get("https://bitnodes.io/api/v1/snapshots/?limit=1", timeout=10)
    if not d:
        return {}
    results = d.get("results", [])
    if not results:
        return {}
    return {"bitnodes_total": safe(results[0].get("total_nodes"), 0)}

# ══════════════════════════════════════════════════════════════
# COINPAPRIKA
# ══════════════════════════════════════════════════════════════
def fetch_coinpaprika():
    d = get("https://api.coinpaprika.com/v1/tickers/btc-bitcoin")
    if not d:
        return {}
    q = d.get("quotes", {}).get("USD", {})
    return {"price_coinpaprika": safe(q.get("price"), 2),
            "beta_value": safe(d.get("beta_value"), 4),
            "rank": d.get("rank"),
            "pct_supply_issued": safe((d.get("total_supply") or 0) / 21_000_000 * 100, 4)}

def fetch_coinpaprika_ohlcv():
    d = get("https://api.coinpaprika.com/v1/coins/btc-bitcoin/ohlcv/today", timeout=8)
    if not d or not isinstance(d, list) or not d:
        return {}
    row = d[0]
    return {"cp_ohlcv_open": safe(row.get("open"), 2), "cp_ohlcv_high": safe(row.get("high"), 2),
            "cp_ohlcv_low": safe(row.get("low"), 2), "cp_ohlcv_close": safe(row.get("close"), 2),
            "cp_ohlcv_vol": safe(row.get("volume"), 0)}

# ══════════════════════════════════════════════════════════════
# ALTERNATIVE.ME — Fear & Greed + Ticker
# ══════════════════════════════════════════════════════════════
def fetch_fear_greed():
    d = get("https://api.alternative.me/fng/?limit=7")
    if not d or not d.get("data"):
        return {}
    data = d["data"]
    return {
        "fear_greed_value":          safe(data[0].get("value"), 0),
        "fear_greed_classification": data[0].get("value_classification"),
        "fear_greed_history_7d": [
            {"value": int(x["value"]), "classification": x["value_classification"]}
            for x in data
        ],
    }

def fetch_altme_ticker():
    d = get("https://api.alternative.me/v2/ticker/1/?convert=USD", timeout=8)
    if not d:
        return {}
    btc = d.get("data", {}).get("1", {})
    q   = btc.get("quotes", {}).get("USD", {})
    return {"altme_price": safe(q.get("price"), 2), "altme_market_cap": safe(q.get("market_cap"), 0),
            "altme_volume_24h": safe(q.get("volume_24h"), 0),
            "altme_change_24h": safe(q.get("percent_change_24h"), 4)}

# ══════════════════════════════════════════════════════════════
# COINBASE
# ══════════════════════════════════════════════════════════════
def fetch_coinbase():
    global _cb_cache
    now = time.time()
    if now - _cb_cache["ts"] < 60 and _cb_cache["data"]:
        return _cb_cache["data"]
    d = get("https://api.coinbase.com/v2/prices/BTC-USD/spot")
    if not d:
        return _cb_cache.get("data", {})
    result = {"price_coinbase": safe(d.get("data", {}).get("amount"), 2)}
    if result.get("price_coinbase"):
        _cb_cache = {"data": result, "ts": now}
    return result

# ══════════════════════════════════════════════════════════════
# KRAKEN — OHLC + technicals
# ══════════════════════════════════════════════════════════════
def fetch_kraken_ohlc():
    since = int(time.time()) - 400 * 86400
    d = get("https://api.kraken.com/0/public/OHLC",
            {"pair": "XBTUSD", "interval": "1440", "since": since})
    if not d or d.get("error"):
        return {}, []
    candles = d.get("result", {}).get("XXBTZUSD", [])
    if not candles:
        return {}, []
    last = candles[-1]
    ohlc = [{"t": int(c[0]), "o": float(c[1]), "h": float(c[2]),
              "l": float(c[3]), "c": float(c[4]), "v": float(c[6])} for c in candles]
    meta = {"kraken_open": safe(last[1], 2), "kraken_high": safe(last[2], 2),
            "kraken_low": safe(last[3], 2), "kraken_close": safe(last[4], 2),
            "kraken_vwap": safe(last[5], 2), "kraken_volume": safe(last[6], 4)}
    return meta, ohlc

def compute_technicals(ohlc_list):
    if not ohlc_list or len(ohlc_list) < 30:
        return {}
    closes = [c["c"] for c in ohlc_list]
    n = len(closes)
    ma7   = sum(closes[-7:])   / min(7, n)   if n >= 7   else None
    ma30  = sum(closes[-30:])  / min(30, n)  if n >= 30  else None
    ma200 = sum(closes[-200:]) / min(200, n) if n >= 200 else None
    returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, n)]
    vol30 = None
    if len(returns) >= 30:
        r30 = returns[-30:]; m = sum(r30) / len(r30)
        vol30 = math.sqrt(sum((r - m)**2 for r in r30) / len(r30)) * math.sqrt(365)
    sharpe_30d = None
    if len(returns) >= 30:
        r30 = returns[-30:]; m = sum(r30) / len(r30)
        s = math.sqrt(sum((r - m)**2 for r in r30) / len(r30))
        if s > 0:
            sharpe_30d = round((m / s) * math.sqrt(365), 3)
    rsi_14 = None
    if len(returns) >= 14:
        g  = [r for r in returns[-14:] if r > 0]
        ll = [-r for r in returns[-14:] if r < 0]
        ag = sum(g) / 14; al = sum(ll) / 14
        rsi_14 = round(100 - (100 / (1 + ag / al)), 2) if al > 0 else 100.0
    cur = closes[-1]
    return {
        "ma_7d": round(ma7, 2) if ma7 else None,
        "ma_30d": round(ma30, 2) if ma30 else None,
        "ma_200d": round(ma200, 2) if ma200 else None,
        "volatility_30d_ann": round(vol30, 4) if vol30 else None,
        "sharpe_30d": sharpe_30d,
        "rsi_14": rsi_14,
        "price_vs_ma7": round((cur/ma7-1)*100, 2) if ma7 else None,
        "price_vs_ma30": round((cur/ma30-1)*100, 2) if ma30 else None,
        "price_vs_ma200": round((cur/ma200-1)*100, 2) if ma200 else None,
    }

# ══════════════════════════════════════════════════════════════
# MINING POOLS
# ══════════════════════════════════════════════════════════════
def fetch_mining_pools():
    global _pools_cache
    now = time.time()
    if now - _pools_cache["ts"] < 3600 and _pools_cache["data"]:
        return _pools_cache["data"]
    result = {}
    d = get("https://api.blockchain.info/pools?timespan=5days")
    if d and isinstance(d, dict):
        total = sum(d.values())
        named = {k: v for k, v in d.items() if k != "Unknown"}
        top3  = sorted(named.items(), key=lambda x: x[1], reverse=True)[:3]
        for i, (name, count) in enumerate(top3):
            result[f"pool_{i+1}_name"] = name
            result[f"pool_{i+1}_pct"]  = round(count / total * 100, 1) if total else 0
        result["pool_unknown_pct"]   = round(d.get("Unknown", 0) / total * 100, 1) if total else 0
        result["pools_total_blocks"] = total
    if result:
        _pools_cache = {"data": result, "ts": now}
    return result

# ══════════════════════════════════════════════════════════════
# 1ML.COM — Lightning (alternative à Mempool)
# ══════════════════════════════════════════════════════════════
def fetch_1ml():
    global _1ml_cache
    now = time.time()
    if now - _1ml_cache["ts"] < 600 and _1ml_cache["data"]:
        return _1ml_cache["data"]
    try:
        r = requests.get("https://1ml.com/statistics?json=true", timeout=10,
                         headers={"User-Agent": "Mozilla/5.0 (compatible; btc-analytics/7.0)"})
        if r.status_code != 200:
            return _1ml_cache.get("data", {})
        d = r.json()
        result = {"ln_1ml_nodes": safe(d.get("numberofnodes"), 0),
                  "ln_1ml_channels": safe(d.get("numberofchannels"), 0),
                  "ln_1ml_nodes_30d": safe(d.get("numberofnodes30dchange"), 4),
                  "ln_1ml_chan_30d":  safe(d.get("numberofchannels30dchange"), 4)}
        if result.get("ln_1ml_nodes"):
            _1ml_cache = {"data": result, "ts": now}
        return result
    except Exception as e:
        log.warning(f"1ml: {e}")
        return _1ml_cache.get("data", {})

# ══════════════════════════════════════════════════════════════
# DEXSCREENER — WBTC on Ethereum (DEX)
# ══════════════════════════════════════════════════════════════
def fetch_dexscreener():
    global _dex_cache
    now = time.time()
    if now - _dex_cache["ts"] < 120 and _dex_cache["data"]:
        return _dex_cache["data"]
    d = get("https://api.dexscreener.com/latest/dex/tokens/0x2260fac5e5542a773aa44fbcfedf7c193bc2c599", timeout=10)
    if not d or not d.get("pairs"):
        return _dex_cache.get("data", {})
    best = max(d["pairs"], key=lambda p: float(p.get("liquidity", {}).get("usd", 0) or 0))
    result = {
        "dex_wbtc_price_usd":     safe(best.get("priceUsd"), 2),
        "dex_wbtc_dex":           best.get("dexId"),
        "dex_wbtc_chain":         best.get("chainId"),
        "dex_wbtc_vol_24h":       safe(best.get("volume", {}).get("h24"), 0),
        "dex_wbtc_liquidity_usd": safe(best.get("liquidity", {}).get("usd"), 0),
        "dex_wbtc_price_change":  safe(best.get("priceChange", {}).get("h24"), 4),
    }
    if result.get("dex_wbtc_price_usd"):
        _dex_cache = {"data": result, "ts": now}
    return result

# ══════════════════════════════════════════════════════════════
# STOOQ — historique prix 30j (CSV sans clé)
# ══════════════════════════════════════════════════════════════
def fetch_stooq_history():
    global _stooq_cache
    now = time.time()
    if now - _stooq_cache["ts"] < 86400 and _stooq_cache["data"]:
        return _stooq_cache["data"]
    try:
        r = requests.get("https://stooq.com/q/d/l/?s=btcusd&i=d", timeout=10,
                         headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return _stooq_cache.get("data", {})
        lines = [l for l in r.text.strip().split("\n") if l and not l.startswith("Date")]
        last_rows = lines[-30:]
        prices_30d = []
        for row in last_rows:
            cols = row.split(",")
            if len(cols) >= 5:
                try:
                    prices_30d.append({"date": cols[0], "close": float(cols[4])})
                except: pass
        if not prices_30d:
            return {}
        latest = prices_30d[-1]["close"]
        earliest = prices_30d[0]["close"]
        change_30d = round((latest - earliest) / earliest * 100, 2) if earliest > 0 else None
        highs = [p["close"] for p in prices_30d]
        result = {
            "stooq_price": safe(latest, 2),
            "stooq_change_30d": change_30d,
            "stooq_high_30d": safe(max(highs), 2),
            "stooq_low_30d": safe(min(highs), 2),
            "stooq_history_30d": prices_30d,
        }
        if result.get("stooq_price"):
            _stooq_cache = {"data": result, "ts": now}
        return result
    except Exception as e:
        log.warning(f"stooq: {e}")
        return _stooq_cache.get("data", {})

# ══════════════════════════════════════════════════════════════
# EXCHANGES USD (20 sources)
# ══════════════════════════════════════════════════════════════
def fetch_binance():
    d = get("https://api.binance.com/api/v3/ticker/24hr", {"symbol": "BTCUSDT"})
    if not d: return {}
    return {"binance_price": safe(d.get("lastPrice"), 2), "binance_vol_usd": safe(d.get("quoteVolume"), 2),
            "binance_change_24h": safe(d.get("priceChangePercent"), 4),
            "binance_high_24h": safe(d.get("highPrice"), 2), "binance_low_24h": safe(d.get("lowPrice"), 2)}

def fetch_bitfinex():
    d = get("https://api-pub.bitfinex.com/v2/ticker/tBTCUSD")
    if not d or not isinstance(d, list) or len(d) < 10: return {}
    return {"bitfinex_price": safe(d[6], 2), "bitfinex_vol": safe(d[7], 2),
            "bitfinex_high_24h": safe(d[8], 2), "bitfinex_low_24h": safe(d[9], 2),
            "bitfinex_change_pct": safe(d[5]*100, 4) if d[5] is not None else None,
            "bitfinex_bid": safe(d[0], 2), "bitfinex_ask": safe(d[2], 2)}

def fetch_bitstamp():
    d = get("https://www.bitstamp.net/api/v2/ticker/btcusd/")
    if not d: return {}
    return {"bitstamp_price": safe(d.get("last"), 2), "bitstamp_vol": safe(d.get("volume"), 4),
            "bitstamp_high_24h": safe(d.get("high"), 2), "bitstamp_low_24h": safe(d.get("low"), 2),
            "bitstamp_bid": safe(d.get("bid"), 2), "bitstamp_ask": safe(d.get("ask"), 2)}

def fetch_okx():
    d = get("https://www.okx.com/api/v5/market/ticker", {"instId": "BTC-USDT"})
    if not d: return {}
    data = (d.get("data") or [{}])[0]
    return {"okx_price": safe(data.get("last"), 2), "okx_vol_usd": safe(data.get("volCcy24h"), 2),
            "okx_high_24h": safe(data.get("high24h"), 2), "okx_low_24h": safe(data.get("low24h"), 2)}

def fetch_bybit():
    d = get("https://api.bybit.com/v5/market/tickers", {"category": "spot", "symbol": "BTCUSDT"})
    if not d: return {}
    lst = (d.get("result", {}).get("list") or [{}])
    data = lst[0] if lst else {}
    chg = safe(data.get("price24hPcnt"), 6)
    return {"bybit_price": safe(data.get("lastPrice"), 2), "bybit_vol_usd": safe(data.get("turnover24h"), 2),
            "bybit_high_24h": safe(data.get("highPrice24h"), 2), "bybit_low_24h": safe(data.get("lowPrice24h"), 2),
            "bybit_change_24h": safe(chg*100 if chg else None, 4)}

def fetch_gemini():
    d = get("https://api.gemini.com/v1/pubticker/btcusd")
    if not d: return {}
    return {"gemini_price": safe(d.get("last"), 2), "gemini_bid": safe(d.get("bid"), 2),
            "gemini_ask": safe(d.get("ask"), 2), "gemini_vol": safe(d.get("volume", {}).get("BTC"), 4)}

def fetch_kucoin():
    d = get("https://api.kucoin.com/api/v1/market/stats", {"symbol": "BTC-USDT"})
    if not d: return {}
    data = d.get("data", {})
    chg = safe(data.get("changeRate"), 6)
    return {"kucoin_price": safe(data.get("last"), 2), "kucoin_vol_usd": safe(data.get("volValue"), 2),
            "kucoin_high_24h": safe(data.get("high"), 2), "kucoin_low_24h": safe(data.get("low"), 2),
            "kucoin_change_24h": safe(chg*100 if chg else None, 4)}

def fetch_gate_io():
    d = get("https://api.gateio.ws/api/v4/spot/tickers", {"currency_pair": "BTC_USDT"})
    if not d or not isinstance(d, list): return {}
    data = d[0] if d else {}
    return {"gate_price": safe(data.get("last"), 2), "gate_vol_usd": safe(data.get("quote_volume"), 2),
            "gate_high_24h": safe(data.get("high_24h"), 2), "gate_low_24h": safe(data.get("low_24h"), 2),
            "gate_change_pct": safe(data.get("change_percentage"), 4)}

def fetch_htx():
    d = get("https://api.huobi.pro/market/detail/merged", {"symbol": "btcusdt"})
    if not d: return {}
    tick = d.get("tick", {})
    return {"htx_price": safe(tick.get("close"), 2), "htx_vol_usd": safe(tick.get("vol"), 2),
            "htx_high_24h": safe(tick.get("high"), 2), "htx_low_24h": safe(tick.get("low"), 2)}

def fetch_mexc():
    d = get("https://api.mexc.com/api/v3/ticker/24hr", {"symbol": "BTCUSDT"})
    if not d: return {}
    return {"mexc_price": safe(d.get("lastPrice"), 2), "mexc_vol_usd": safe(d.get("quoteVolume"), 2),
            "mexc_change_24h": safe(d.get("priceChangePercent"), 4),
            "mexc_high_24h": safe(d.get("highPrice"), 2), "mexc_low_24h": safe(d.get("lowPrice"), 2)}

def fetch_bitget():
    d = get("https://api.bitget.com/api/v2/spot/market/tickers", {"symbol": "BTCUSDT"})
    if not d: return {}
    data = (d.get("data") or [{}])[0]
    chg = safe(data.get("change24h"), 6)
    return {"bitget_price": safe(data.get("lastPr"), 2), "bitget_vol_usd": safe(data.get("quoteVol"), 2),
            "bitget_change_24h": safe(chg*100 if chg else None, 4),
            "bitget_high_24h": safe(data.get("high24h"), 2), "bitget_low_24h": safe(data.get("low24h"), 2)}

def fetch_coinex():
    d = get("https://api.coinex.com/v2/spot/ticker", {"market": "BTCUSDT"})
    if not d: return {}
    data = (d.get("data") or [{}])[0]
    return {"coinex_price": safe(data.get("close"), 2), "coinex_vol": safe(data.get("volume"), 4),
            "coinex_high_24h": safe(data.get("high"), 2), "coinex_low_24h": safe(data.get("low"), 2)}

def fetch_lbank():
    d = get("https://api.lbank.info/v2/ticker/24hr.do", {"symbol": "btc_usdt"})
    if not d: return {}
    data = (d.get("data") or [{}])[0]
    ticker = data.get("ticker", {})
    return {"lbank_price": safe(ticker.get("latest"), 2), "lbank_vol": safe(ticker.get("vol"), 4),
            "lbank_high_24h": safe(ticker.get("high"), 2), "lbank_low_24h": safe(ticker.get("low"), 2)}

def fetch_whitebit():
    d = get("https://whitebit.com/api/v4/public/ticker", timeout=8)
    if not d: return {}
    data = d.get("BTC_USDT", {})
    return {"whitebit_price": safe(data.get("last_price"), 2), "whitebit_vol": safe(data.get("base_volume"), 4),
            "whitebit_high_24h": safe(data.get("high"), 2), "whitebit_low_24h": safe(data.get("low"), 2)}

def fetch_coincap():
    d = get("https://api.coincap.io/v2/assets/bitcoin")
    if not d: return {}
    data = d.get("data", {})
    return {"coincap_price": safe(data.get("priceUsd"), 2), "coincap_supply": safe(data.get("supply"), 0),
            "coincap_market_cap": safe(data.get("marketCapUsd"), 0), "coincap_vol_24h": safe(data.get("volumeUsd24Hr"), 0),
            "coincap_change_24h": safe(data.get("changePercent24Hr"), 4), "coincap_vwap_24h": safe(data.get("vwap24Hr"), 2)}

def fetch_deribit():
    d = get("https://www.deribit.com/api/v2/public/get_index_price", {"index_name": "btc_usd"})
    if not d: return {}
    result = {"deribit_index_price": safe(d.get("result", {}).get("index_price"), 2)}
    d2 = get("https://www.deribit.com/api/v2/public/get_book_summary_by_instrument", {"instrument_name": "BTC-PERPETUAL"})
    if d2 and d2.get("result"):
        r2 = d2["result"][0] if isinstance(d2["result"], list) else {}
        result.update({"deribit_perp_price": safe(r2.get("last"), 2),
                       "deribit_funding_8h": safe(r2.get("funding_8h"), 6),
                       "deribit_open_interest": safe(r2.get("open_interest"), 2),
                       "deribit_volume_usd": safe(r2.get("volume_usd"), 0)})
    return result

# ══════════════════════════════════════════════════════════════
# EXCHANGES USD SUPPLÉMENTAIRES — v8 (+6 sources)
# ══════════════════════════════════════════════════════════════
def fetch_poloniex():
    global _poloniex_cache
    now = time.time()
    if now - _poloniex_cache["ts"] < EX_TTL and _poloniex_cache["data"]:
        return _poloniex_cache["data"]
    d = get("https://api.poloniex.com/markets/BTC_USDT/ticker24h")
    if not d: return _poloniex_cache.get("data", {})
    chg = d.get("dailyChange")
    result = {
        "poloniex_price": safe(d.get("close"), 2),
        "poloniex_high_24h": safe(d.get("high"), 2),
        "poloniex_low_24h": safe(d.get("low"), 2),
        "poloniex_vol_usd": safe(d.get("amount"), 2),
        "poloniex_change_24h": safe(float(chg)*100 if chg else None, 4),
    }
    if result.get("poloniex_price"): _poloniex_cache = {"data": result, "ts": now}
    return result

def fetch_cryptodotcom():
    global _cdotcom_cache
    now = time.time()
    if now - _cdotcom_cache["ts"] < EX_TTL and _cdotcom_cache["data"]:
        return _cdotcom_cache["data"]
    d = get("https://api.crypto.com/v2/public/get-ticker", {"instrument_name": "BTC_USDT"})
    if not d: return _cdotcom_cache.get("data", {})
    raw = d.get("result", {}).get("data")
    # API returns either a dict or a list with one item
    data = raw[0] if isinstance(raw, list) and raw else (raw if isinstance(raw, dict) else {})
    chg = data.get("c")
    result = {
        "cdotcom_price": safe(data.get("a"), 2),
        "cdotcom_high_24h": safe(data.get("h"), 2),
        "cdotcom_low_24h": safe(data.get("l"), 2),
        "cdotcom_vol_usd": safe(data.get("vv"), 2),
        "cdotcom_change_24h": safe(float(chg)*100 if chg else None, 4),
    }
    if result.get("cdotcom_price"): _cdotcom_cache = {"data": result, "ts": now}
    return result

def fetch_bitmart():
    global _bitmart_cache
    now = time.time()
    if now - _bitmart_cache["ts"] < EX_TTL and _bitmart_cache["data"]:
        return _bitmart_cache["data"]
    d = get("https://api-cloud.bitmart.com/spot/quotation/v3/ticker", {"symbol": "BTC_USDT"})
    if not d: return _bitmart_cache.get("data", {})
    data = d.get("data", {})
    chg = data.get("fluctuation")
    result = {
        "bitmart_price": safe(data.get("last"), 2),
        "bitmart_high_24h": safe(data.get("high_24h"), 2),
        "bitmart_low_24h": safe(data.get("low_24h"), 2),
        "bitmart_vol_usd": safe(data.get("qv_24h"), 2),
        "bitmart_change_24h": safe(float(chg)*100 if chg else None, 4),
    }
    if result.get("bitmart_price"): _bitmart_cache = {"data": result, "ts": now}
    return result

def fetch_btse():
    global _btse_cache
    now = time.time()
    if now - _btse_cache["ts"] < EX_TTL and _btse_cache["data"]:
        return _btse_cache["data"]
    d = get("https://api.btse.com/spot/api/v3.2/price", {"symbol": "BTC-USD"})
    if not d or not isinstance(d, list) or not d: return _btse_cache.get("data", {})
    row = d[0]
    result = {
        "btse_price": safe(row.get("lastPrice"), 2),
        "btse_index_price": safe(row.get("indexPrice"), 2),
    }
    if result.get("btse_price"): _btse_cache = {"data": result, "ts": now}
    return result

def fetch_coinlore():
    global _coinlore_cache
    now = time.time()
    if now - _coinlore_cache["ts"] < 120 and _coinlore_cache["data"]:
        return _coinlore_cache["data"]
    d = get("https://api.coinlore.net/api/ticker/", {"id": "90"})
    if not d or not isinstance(d, list) or not d: return _coinlore_cache.get("data", {})
    row = d[0]
    result = {
        "coinlore_price": safe(row.get("price_usd"), 2),
        "coinlore_market_cap": safe(row.get("market_cap_usd"), 0),
        "coinlore_vol_24h": safe(row.get("volume24"), 0),
        "coinlore_change_24h": safe(row.get("percent_change_24h"), 4),
        "coinlore_change_7d": safe(row.get("percent_change_7d"), 4),
        "coinlore_rank": row.get("rank"),
    }
    if result.get("coinlore_price"): _coinlore_cache = {"data": result, "ts": now}
    return result

def fetch_coinranking():
    global _coinranking_cache
    now = time.time()
    if now - _coinranking_cache["ts"] < 120 and _coinranking_cache["data"]:
        return _coinranking_cache["data"]
    d = get("https://api.coinranking.com/v2/coin/Qwsogvtv82FCd/price")
    if not d: return _coinranking_cache.get("data", {})
    result = {"coinranking_price": safe(d.get("data", {}).get("price"), 2)}
    if result.get("coinranking_price"): _coinranking_cache = {"data": result, "ts": now}
    return result

def fetch_xtcom():
    """XT.com — Exchange USD (BTC/USDT) v9"""
    global _xtcom_cache
    now = time.time()
    if now - _xtcom_cache["ts"] < EX_TTL and _xtcom_cache["data"]:
        return _xtcom_cache["data"]
    d = get("https://sapi.xt.com/v4/public/ticker", {"symbol": "btc_usdt"}, timeout=8)
    if not d or d.get("rc") != 0: return _xtcom_cache.get("data", {})
    items = d.get("result", [])
    data = items[0] if items else {}
    result = {
        "xtcom_price":      safe(data.get("c"), 2),
        "xtcom_high_24h":   safe(data.get("ht"), 2),
        "xtcom_low_24h":    safe(data.get("lt"), 2),
        "xtcom_vol_usd":    safe(data.get("q"), 2),
        "xtcom_change_24h": safe(data.get("cr"), 4),
    }
    if result.get("xtcom_price"): _xtcom_cache = {"data": result, "ts": now}
    return result

# ══════════════════════════════════════════════════════════════
# EXCHANGES INTERNATIONAUX SUPPLÉMENTAIRES — v8 (+8 sources)
# ══════════════════════════════════════════════════════════════
def fetch_foxbit():
    """Brésil — Foxbit (BTC/BRL via BRLXBTC)"""
    global _foxbit_cache
    now = time.time()
    if now - _foxbit_cache["ts"] < INTL_TTL and _foxbit_cache["data"]:
        return _foxbit_cache["data"]
    try:
        r = requests.get("https://watcher.foxbit.com.br/api/Ticker/", timeout=8,
                         headers={"User-Agent": "btc-analytics/8.0"})
        if r.status_code != 200: return _foxbit_cache.get("data", {})
        d = r.json()
        # Préférer la paire USD directe
        for item in d:
            if "XBT" in item.get("currency","") and "USDT" in item.get("currency",""):
                result = {"foxbit_price_usd": safe(item.get("last"), 2),
                          "foxbit_high_usd": safe(item.get("high"), 2),
                          "foxbit_low_usd": safe(item.get("low"), 2)}
                if result.get("foxbit_price_usd"):
                    _foxbit_cache = {"data": result, "ts": now}
                return result
        # Fallback paire BRL
        for item in d:
            if "XBT" in item.get("currency","") or "BTC" in item.get("currency",""):
                fx = fetch_fx(); rate = fx.get("rate_brl")
                p_brl = safe(item.get("last"), 0)
                result = {"foxbit_price_brl": p_brl,
                          "foxbit_high_brl": safe(item.get("high"), 0),
                          "foxbit_low_brl": safe(item.get("low"), 0),
                          "foxbit_price_usd": to_usd(p_brl, rate)}
                if result.get("foxbit_price_brl"):
                    _foxbit_cache = {"data": result, "ts": now}
                return result
        return {}
    except Exception as e:
        log.warning(f"foxbit: {e}")
        return _foxbit_cache.get("data", {})

def fetch_novadax():
    """Brésil — NovaDax (BTC/BRL)"""
    global _novadax_cache
    now = time.time()
    if now - _novadax_cache["ts"] < INTL_TTL and _novadax_cache["data"]:
        return _novadax_cache["data"]
    d = get("https://api.novadax.com/v1/market/ticker", {"symbol": "BTC_BRL"})
    if not d or d.get("code") != "A10000": return _novadax_cache.get("data", {})
    data = d.get("data", {})
    p_brl = safe(data.get("lastPrice"), 2)
    fx = fetch_fx(); rate = fx.get("rate_brl")
    result = {
        "novadax_price_brl": p_brl,
        "novadax_high_brl": safe(data.get("high24h"), 2),
        "novadax_low_brl": safe(data.get("low24h"), 2),
        "novadax_vol_brl": safe(data.get("quoteVolume24h"), 2),
        "novadax_price_usd": to_usd(p_brl, rate),
    }
    if result.get("novadax_price_brl"): _novadax_cache = {"data": result, "ts": now}
    return result

def fetch_luno():
    """Afrique du Sud — Luno (BTC/ZAR)"""
    global _luno_cache
    now = time.time()
    if now - _luno_cache["ts"] < INTL_TTL and _luno_cache["data"]:
        return _luno_cache["data"]
    d = get("https://api.luno.com/api/1/ticker", {"pair": "XBTZAR"})
    if not d: return _luno_cache.get("data", {})
    p_zar = safe(d.get("last_trade"), 0)
    fx = fetch_fx(); rate = fx.get("rate_zar")
    result = {
        "luno_price_zar": p_zar,
        "luno_bid_zar": safe(d.get("bid"), 0),
        "luno_ask_zar": safe(d.get("ask"), 0),
        "luno_vol_24h": safe(d.get("rolling_24_hour_volume"), 4),
        "luno_price_usd": to_usd(p_zar, rate),
    }
    if result.get("luno_price_zar"): _luno_cache = {"data": result, "ts": now}
    return result

def fetch_valr():
    """Afrique du Sud — VALR (BTC/ZAR)"""
    global _valr_cache
    now = time.time()
    if now - _valr_cache["ts"] < INTL_TTL and _valr_cache["data"]:
        return _valr_cache["data"]
    d = get("https://api.valr.com/v1/public/BTCZAR/marketsummary")
    if not d: return _valr_cache.get("data", {})
    p_zar = safe(d.get("lastTradedPrice"), 0)
    fx = fetch_fx(); rate = fx.get("rate_zar")
    result = {
        "valr_price_zar": p_zar,
        "valr_bid_zar": safe(d.get("bestBid"), 0),
        "valr_ask_zar": safe(d.get("bestAsk"), 0),
        "valr_price_usd": to_usd(p_zar, rate),
    }
    if result.get("valr_price_zar"): _valr_cache = {"data": result, "ts": now}
    return result

def fetch_bitso():
    """Mexique — Bitso (BTC/MXN)"""
    global _bitso_cache
    now = time.time()
    if now - _bitso_cache["ts"] < INTL_TTL and _bitso_cache["data"]:
        return _bitso_cache["data"]
    d = get("https://api.bitso.com/v3/ticker/", {"book": "btc_mxn"})
    if not d or not d.get("success"): return _bitso_cache.get("data", {})
    data = d.get("payload", {})
    p_mxn = safe(data.get("last"), 2)
    fx = fetch_fx(); rate = fx.get("rate_mxn")
    result = {
        "bitso_price_mxn": p_mxn,
        "bitso_high_mxn": safe(data.get("high"), 2),
        "bitso_low_mxn": safe(data.get("low"), 2),
        "bitso_vol": safe(data.get("volume"), 4),
        "bitso_bid_mxn": safe(data.get("bid"), 2),
        "bitso_ask_mxn": safe(data.get("ask"), 2),
        "bitso_price_usd": to_usd(p_mxn, rate),
    }
    if result.get("bitso_price_mxn"): _bitso_cache = {"data": result, "ts": now}
    return result

def fetch_coindcx():
    """Inde — CoinDCX (BTC/INR)"""
    global _coindcx_cache
    now = time.time()
    if now - _coindcx_cache["ts"] < INTL_TTL and _coindcx_cache["data"]:
        return _coindcx_cache["data"]
    try:
        d = get("https://api.coindcx.com/exchange/ticker")
        if not d or not isinstance(d, list): return _coindcx_cache.get("data", {})
        for item in d:
            if item.get("market") == "BTCINR":
                p_inr = safe(item.get("last_price"), 2)
                fx = fetch_fx(); rate = fx.get("rate_inr")
                result = {
                    "coindcx_price_inr": p_inr,
                    "coindcx_high_inr": safe(item.get("high"), 2),
                    "coindcx_low_inr": safe(item.get("low"), 2),
                    "coindcx_vol": safe(item.get("volume"), 4),
                    "coindcx_change_24h": safe(item.get("change_24_hour"), 4),
                    "coindcx_price_usd": to_usd(p_inr, rate),
                }
                if result.get("coindcx_price_inr"): _coindcx_cache = {"data": result, "ts": now}
                return result
        return {}
    except Exception as e:
        log.warning(f"coindcx: {e}")
        return _coindcx_cache.get("data", {})

def fetch_wazirx():
    """Inde — WazirX (BTC/INR)"""
    global _wazirx_cache
    now = time.time()
    if now - _wazirx_cache["ts"] < INTL_TTL and _wazirx_cache["data"]:
        return _wazirx_cache["data"]
    d = get("https://api.wazirx.com/sapi/v1/ticker/24hr", {"symbol": "btcinr"})
    if not d: return _wazirx_cache.get("data", {})
    p_inr = safe(d.get("lastPrice"), 2)
    fx = fetch_fx(); rate = fx.get("rate_inr")
    result = {
        "wazirx_price_inr": p_inr,
        "wazirx_high_inr": safe(d.get("highPrice"), 2),
        "wazirx_low_inr": safe(d.get("lowPrice"), 2),
        "wazirx_vol": safe(d.get("volume"), 4),
        "wazirx_price_usd": to_usd(p_inr, rate),
    }
    if result.get("wazirx_price_inr"): _wazirx_cache = {"data": result, "ts": now}
    return result

def fetch_indodax():
    """Indonésie — Indodax (BTC/IDR)"""
    global _indodax_cache
    now = time.time()
    if now - _indodax_cache["ts"] < INTL_TTL and _indodax_cache["data"]:
        return _indodax_cache["data"]
    d = get("https://indodax.com/api/btc_idr/ticker")
    if not d: return _indodax_cache.get("data", {})
    tick = d.get("ticker", {})
    p_idr = safe(tick.get("last"), 0)
    fx = fetch_fx(); rate = fx.get("rate_idr")
    result = {
        "indodax_price_idr": p_idr,
        "indodax_high_idr": safe(tick.get("high"), 0),
        "indodax_low_idr": safe(tick.get("low"), 0),
        "indodax_vol_btc": safe(tick.get("vol_btc"), 4),
        "indodax_price_usd": to_usd(p_idr, rate),
    }
    if result.get("indodax_price_idr"): _indodax_cache = {"data": result, "ts": now}
    return result

# ══════════════════════════════════════════════════════════════
# EXCHANGES INTERNATIONAUX (non-USD natif)
# ══════════════════════════════════════════════════════════════
def fetch_international():
    global _intl_cache
    now = time.time()
    if now - _intl_cache["ts"] < INTL_TTL and _intl_cache["data"]:
        return _intl_cache["data"]

    fx = fetch_fx()
    rate_jpy = fx.get("rate_jpy", 0)
    rate_krw = fx.get("rate_krw", 0)
    rate_aud = fx.get("rate_aud", 0)
    rate_brl = fx.get("rate_brl", 0)
    rate_try = fx.get("rate_try", 0)

    result = {"btc_jpy_ref": fx.get("btc_jpy"), "btc_krw_ref": fx.get("btc_krw"),
              "btc_aud_ref": fx.get("btc_aud"), "btc_brl_ref": fx.get("btc_brl"),
              "btc_zar_ref": fx.get("btc_zar"), "btc_mxn_ref": fx.get("btc_mxn"),
              "btc_inr_ref": fx.get("btc_inr"), "btc_idr_ref": fx.get("btc_idr")}

    # ── JAPON ──────────────────────────────────────────────────
    d = get("https://api.bitflyer.com/v1/ticker", {"product_code": "BTC_JPY"})
    if d:
        p = safe(d.get("ltp"), 0)
        result.update({"bitflyer_price_jpy": p, "bitflyer_vol": safe(d.get("volume_by_product"), 4),
                       "bitflyer_bid_jpy": safe(d.get("best_bid"), 0), "bitflyer_ask_jpy": safe(d.get("best_ask"), 0),
                       "bitflyer_price_usd": to_usd(p, rate_jpy)})

    d = get("https://coincheck.com/api/ticker")
    if d:
        p = safe(d.get("last"), 0)
        result.update({"coincheck_price_jpy": p, "coincheck_vol": safe(d.get("volume"), 4),
                       "coincheck_bid_jpy": safe(d.get("bid"), 0), "coincheck_ask_jpy": safe(d.get("ask"), 0),
                       "coincheck_price_usd": to_usd(p, rate_jpy)})

    d = get("https://api.zaif.jp/api/1/ticker/btc_jpy")
    if d:
        p = safe(d.get("last"), 0)
        result.update({"zaif_price_jpy": p, "zaif_vol": safe(d.get("volume"), 4),
                       "zaif_vwap_jpy": safe(d.get("vwap"), 0),
                       "zaif_price_usd": to_usd(p, rate_jpy)})

    # ── CORÉE DU SUD ───────────────────────────────────────────
    d = get("https://api.upbit.com/v1/ticker", {"markets": "KRW-BTC"})
    if d and isinstance(d, list) and d:
        row = d[0]
        p = safe(row.get("trade_price"), 0)
        chg = safe(row.get("signed_change_rate"), 6)
        result.update({"upbit_price_krw": p, "upbit_vol_krw": safe(row.get("acc_trade_price_24h"), 0),
                       "upbit_change_24h": safe(chg*100 if chg else None, 4),
                       "upbit_high_24h_krw": safe(row.get("high_price"), 0), "upbit_low_24h_krw": safe(row.get("low_price"), 0),
                       "upbit_price_usd": to_usd(p, rate_krw)})

    d = get("https://api.bithumb.com/public/ticker/BTC_KRW")
    if d and d.get("status") == "0000":
        data = d.get("data", {})
        p = safe(data.get("closing_price"), 0)
        result.update({"bithumb_price_krw": p, "bithumb_vol": safe(data.get("units_traded_24H"), 4),
                       "bithumb_high_krw": safe(data.get("max_price"), 0), "bithumb_low_krw": safe(data.get("min_price"), 0),
                       "bithumb_price_usd": to_usd(p, rate_krw)})

    d = get("https://api.korbit.co.kr/v1/ticker", {"currency_pair": "btc_krw"})
    if d:
        p = safe(d.get("last"), 0)
        result.update({"korbit_price_krw": p, "korbit_price_usd": to_usd(p, rate_krw)})

    # ── AUSTRALIE ──────────────────────────────────────────────
    d = get("https://api.btcmarkets.net/v3/markets/BTC-AUD/ticker")
    if d:
        p = safe(d.get("lastPrice"), 2)
        result.update({"btcmarkets_price_aud": p, "btcmarkets_bid_aud": safe(d.get("bestBid"), 2),
                       "btcmarkets_ask_aud": safe(d.get("bestAsk"), 2),
                       "btcmarkets_price_usd": to_usd(p, rate_aud)})

    # ── TURQUIE ────────────────────────────────────────────────
    d = get("https://api.btcturk.com/api/v2/ticker", {"pairSymbol": "BTCUSDT"})
    if d and d.get("data"):
        row = d["data"][0] if isinstance(d["data"], list) else {}
        result.update({"btcturk_price_usdt": safe(row.get("last"), 2),
                       "btcturk_vol": safe(row.get("volume"), 4),
                       "btcturk_high_24h": safe(row.get("high"), 2), "btcturk_low_24h": safe(row.get("low"), 2)})

    d = get("https://www.paribu.com/ticker")
    if d and isinstance(d, dict):
        btc_data = d.get("BTC_TL") or d.get("BTC-TL") or {}
        p = safe(btc_data.get("last"), 2)
        if p:
            result.update({"paribu_price_try": p, "paribu_price_usd": to_usd(p, rate_try)})

    # ── BRÉSIL ─────────────────────────────────────────────────
    d = get("https://www.mercadobitcoin.net/api/BTC/ticker/")
    if d and d.get("ticker"):
        tick = d["ticker"]
        p = safe(tick.get("last"), 2)
        result.update({"mercado_price_brl": p, "mercado_vol": safe(tick.get("vol"), 4),
                       "mercado_high_brl": safe(tick.get("high"), 2), "mercado_low_brl": safe(tick.get("low"), 2),
                       "mercado_price_usd": to_usd(p, rate_brl)})

    # ── RUSSIE/EUROPE — Exmo ────────────────────────────────────
    d = get("https://api.exmo.com/v1.1/ticker")
    if d and isinstance(d, dict) and "BTC_USD" in d:
        t = d["BTC_USD"]
        result.update({"exmo_price_usd": safe(t.get("last_trade"), 2), "exmo_vol_btc": safe(t.get("vol"), 4),
                       "exmo_high_24h": safe(t.get("high"), 2), "exmo_low_24h": safe(t.get("low"), 2)})

    # ── AFRIQUE DU SUD (v8) ────────────────────────────────────
    result.update(sf(fetch_luno))
    result.update(sf(fetch_valr))

    # ── MEXIQUE (v8) ───────────────────────────────────────────
    result.update(sf(fetch_bitso))

    # ── INDE (v8) ─────────────────────────────────────────────
    result.update(sf(fetch_coindcx))
    result.update(sf(fetch_wazirx))

    # ── INDONÉSIE (v8) ────────────────────────────────────────
    result.update(sf(fetch_indodax))

    # ── BRÉSIL SUPPLÉMENTAIRE (v8) ────────────────────────────
    result.update(sf(fetch_foxbit))
    result.update(sf(fetch_novadax))

    if result:
        _intl_cache = {"data": result, "ts": now}
    return result

# ══════════════════════════════════════════════════════════════
# ETF — SoSoValue + TwelveData
# ══════════════════════════════════════════════════════════════
def fetch_sosovalue_etf():
    global _soso_cache
    now = time.time()
    if now - _soso_cache["ts"] < SOSO_TTL and _soso_cache["data"]:
        return _soso_cache["data"]
    key = os.environ.get("SOSOVALUE_KEY", "")
    if not key:
        return {}
    try:
        import urllib3; urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        r = requests.post(f"{SOSO_BASE}/openapi/v2/etf/currentEtfDataMetrics",
                          json={"type": "us-btc-spot"},
                          headers={"x-soso-api-key": key, "Content-Type": "application/json"},
                          timeout=10, verify=False)
        if r.status_code != 200:
            return {}
        d    = r.json()
        data = d.get("data", {})
        result = {
            "etf_date":            data.get("totalNetAssets", {}).get("lastUpdateDate"),
            "etf_total_aum_usd":   safe(data.get("totalNetAssets", {}).get("value"), 2),
            "etf_daily_inflow_usd":safe(data.get("dailyNetInflow", {}).get("value"), 2),
            "etf_cum_inflow_usd":  safe(data.get("cumNetInflow", {}).get("value"), 2),
            "etf_daily_vol_usd":   safe(data.get("dailyTotalValueTraded", {}).get("value"), 2),
            "etf_total_btc_held":  safe(data.get("totalTokenHoldings", {}).get("value"), 4),
        }
        if result:
            daily = result.get("etf_daily_inflow_usd")
            if daily is not None:
                result["etf_signal"] = ("Entrées massives 🟢" if daily > 500e6
                                        else "Entrées positives 🟢" if daily > 0
                                        else "Sorties modérées 🟡" if daily > -500e6
                                        else "Sorties massives 🔴")
            _soso_cache = {"data": result, "ts": now}
        return result
    except Exception as e:
        log.error(f"SoSoValue: {e}")
        return {}

def fetch_twelvedata_etf():
    global _twelve_cache
    now = time.time()
    if now - _twelve_cache["ts"] < TWELVE_TTL and _twelve_cache["data"]:
        return _twelve_cache["data"]
    key = os.environ.get("TWELVE_DATA_KEY", "")
    if not key:
        return {}
    TICKERS = ["IBIT", "FBTC", "ARKB", "GBTC", "HODL"]
    d = get(f"{TWELVE_BASE}/quote", params={"symbol": ",".join(TICKERS), "apikey": key}, timeout=10)
    if not d:
        return {}
    result = {}
    for ticker in TICKERS:
        etf = d.get(ticker, {})
        if not etf or etf.get("status") == "error":
            continue
        t = ticker.lower()
        result[f"etf_{t}_price"]  = safe(etf.get("close"), 4)
        result[f"etf_{t}_vol"]    = safe(etf.get("volume"), 0)
        result[f"etf_{t}_change"] = safe(etf.get("percent_change"), 4)
        result[f"etf_{t}_name"]   = etf.get("name", ticker)
    if result:
        _twelve_cache = {"data": result, "ts": now}
    return result

# ══════════════════════════════════════════════════════════════
# SIGNAUX & ALERTES
# ══════════════════════════════════════════════════════════════
def compute_signals(d):
    s = {}
    ap    = d.get("ath_pct")
    mvrv  = d.get("mvrv")
    nupl  = d.get("nupl")
    rsi   = d.get("rsi_14")
    fg    = d.get("fear_greed_value")
    fee   = d.get("fee_high")
    txs   = d.get("pending_txs")
    asopr = d.get("asopr")
    nrpl  = d.get("nrpl_usd")
    if ap is not None:
        p = abs(ap)
        s["ath_signal"] = ("Proche ATH 🔴" if p < 5 else "Zone haute 🟡" if p < 20
                           else "Zone mediane 🟢" if p < 50 else "Zone basse 💜")
    s["mvrv_signal"] = (
        "Surachat 🔴" if mvrv and mvrv >= 3.5 else "Chaud 🟡" if mvrv and mvrv >= 2.5
        else "Neutre 🟢" if mvrv and mvrv >= 1.0 else "Sous-evalue 💜" if mvrv else "—")
    s["nupl_zone"] = (
        "Euphorie 🔴" if nupl and nupl >= 0.75 else "Avidite 🟡" if nupl and nupl >= 0.5
        else "Optimisme 🟢" if nupl and nupl >= 0.25 else "Espoir 🟢" if nupl and nupl >= 0
        else "Capitulation 💜" if nupl is not None else "—")
    if asopr is not None:
        s["asopr_signal"] = ("Profit 🟢" if asopr >= 1.02 else "Neutre 🟡" if asopr >= 0.98 else "Perte 🔴")
    if rsi is not None:
        s["rsi_signal"] = ("Surachat 🔴" if rsi >= 80 else "Haussier 🟡" if rsi >= 60
                           else "Neutre 🟢" if rsi >= 40 else "Baissier 🟡" if rsi >= 20 else "Survente 💜")
    sharpe = d.get("sharpe_30d")
    if sharpe is not None:
        s["sharpe_signal"] = ("Excellent ✅" if sharpe >= 2 else "Bon 🟢" if sharpe >= 1
                              else "Positif 🟡" if sharpe >= 0 else "Negatif 🔴")
    if fg is not None:
        s["fg_signal"] = ("Peur extreme 💜" if fg <= 20 else "Peur 🟡" if fg <= 40
                          else "Neutre 🟢" if fg <= 60 else "Avidite 🟡" if fg <= 80 else "Avidite extreme 🔴")
    if fee is not None:
        s["fee_signal"] = ("Reseau libre ✅" if fee <= 3 else "Normal" if fee <= 15
                           else "Charge ⚠️" if fee <= 50 else "Congestionne 🔴")
    if txs is not None:
        s["mempool_signal"] = ("Vide ✅" if txs < 5000 else "Normal" if txs < 30000
                               else "Charge ⚠️" if txs < 100000 else "Sature 🔴")
    stable = d.get("stablecoin_total"); mcap = d.get("market_cap")
    if stable and mcap:
        ratio = stable / mcap * 100
        s["stable_ratio_pct"] = round(ratio, 2)
        s["stable_signal"] = ("Liquidite elevee 🟢" if ratio > 30 else "Liquidite normale 🟡" if ratio > 15 else "Liquidite faible 🔴")
    alerts = []
    if mvrv and mvrv >= 3.5:
        alerts.append({"severity": "CRITIQUE", "metric": "MVRV", "message": f"MVRV={mvrv:.2f} — surachat extrême"})
    if mvrv and mvrv < 1.0:
        alerts.append({"severity": "OPPORTUNITÉ", "metric": "MVRV", "message": f"MVRV={mvrv:.2f} — sous Realized Cap"})
    if fg is not None and fg <= 15:
        alerts.append({"severity": "INFO", "metric": "Fear&Greed", "message": f"F&G={int(fg)} — peur extrême"})
    if ap and abs(ap) < 5:
        alerts.append({"severity": "ATTENTION", "metric": "ATH", "message": f"BTC à {abs(ap):.1f}% de l'ATH"})
    if rsi and rsi >= 80:
        alerts.append({"severity": "INFO", "metric": "RSI", "message": f"RSI={rsi:.1f} — surachat"})
    if rsi and rsi <= 20:
        alerts.append({"severity": "OPPORTUNITÉ", "metric": "RSI", "message": f"RSI={rsi:.1f} — survente"})
    if asopr is not None and asopr < 0.96:
        alerts.append({"severity": "INFO", "metric": "aSOPR", "message": f"aSOPR={asopr:.4f} — ventes à perte"})
    s["alerts"] = alerts
    s["active_alerts"] = len(alerts)
    return s

# ══════════════════════════════════════════════════════════════
# NOUVELLES SOURCES v9 — DÉRIVÉS & FUTURES
# ══════════════════════════════════════════════════════════════

def fetch_binance_futures():
    """Binance USDT-M Futures (FAPI) — Funding rate, OI, L/S ratio"""
    global _bnf_cache
    now = time.time()
    if now - _bnf_cache["ts"] < 60 and _bnf_cache["data"]:
        return _bnf_cache["data"]
    result = {}
    # Mark price + funding rate
    d = get("https://fapi.binance.com/fapi/v1/premiumIndex", {"symbol": "BTCUSDT"})
    if d:
        fr = d.get("lastFundingRate")
        result.update({
            "bnf_mark_price":   safe(d.get("markPrice"), 2),
            "bnf_index_price":  safe(d.get("indexPrice"), 2),
            "bnf_funding_rate": safe(float(fr)*100 if fr else None, 6),
        })
    # Open interest (BTC)
    d2 = get("https://fapi.binance.com/fapi/v1/openInterest", {"symbol": "BTCUSDT"})
    if d2:
        result["bnf_oi_btc"] = safe(d2.get("openInterest"), 2)
    # 24h ticker
    d3 = get("https://fapi.binance.com/fapi/v1/ticker/24hr", {"symbol": "BTCUSDT"})
    if d3:
        result.update({
            "bnf_price":      safe(d3.get("lastPrice"), 2),
            "bnf_vol_usd":    safe(d3.get("quoteVolume"), 0),
            "bnf_change_24h": safe(d3.get("priceChangePercent"), 4),
            "bnf_high_24h":   safe(d3.get("highPrice"), 2),
            "bnf_low_24h":    safe(d3.get("lowPrice"), 2),
        })
    # Global Long/Short ratio
    d4 = get("https://fapi.binance.com/fapi/v1/globalLongShortAccountRatio",
             {"symbol": "BTCUSDT", "period": "5m", "limit": "1"})
    if d4 and isinstance(d4, list) and d4:
        row = d4[0]
        ls = row.get("longShortRatio")
        la = row.get("longAccount"); sa = row.get("shortAccount")
        result.update({
            "bnf_ls_ratio":  safe(ls, 4),
            "bnf_long_pct":  safe(float(la)*100 if la else None, 2),
            "bnf_short_pct": safe(float(sa)*100 if sa else None, 2),
        })
    if result.get("bnf_mark_price"):
        _bnf_cache = {"data": result, "ts": now}
    return result


def fetch_kraken_futures():
    """Kraken Futures — BTC Perpetual (PF_XBTUSD)"""
    global _krf_cache
    now = time.time()
    if now - _krf_cache["ts"] < 60 and _krf_cache["data"]:
        return _krf_cache["data"]
    d = get("https://futures.kraken.com/derivatives/api/v3/tickers", timeout=10)
    if not d or not d.get("tickers"):
        return _krf_cache.get("data", {})
    result = {}
    for t in d["tickers"]:
        sym = t.get("symbol", "")
        if sym in ("PF_XBTUSD", "PI_XBTUSD"):
            fr = t.get("fundingRate")
            result.update({
                "krf_symbol":        sym,
                "krf_last_price":    safe(t.get("last"), 2),
                "krf_mark_price":    safe(t.get("markPrice"), 2),
                "krf_bid":           safe(t.get("bid"), 2),
                "krf_ask":           safe(t.get("ask"), 2),
                "krf_funding_rate":  safe(float(fr)*100 if fr else None, 6),
                "krf_oi_contracts":  safe(t.get("openInterest"), 0),
                "krf_vol_24h":       safe(t.get("vol24h"), 2),
            })
            break
    if result:
        _krf_cache = {"data": result, "ts": now}
    return result


def fetch_bitmex():
    """BitMEX — XBTUSD Perpetual Swap"""
    global _bitmex_cache
    now = time.time()
    if now - _bitmex_cache["ts"] < 60 and _bitmex_cache["data"]:
        return _bitmex_cache["data"]
    d = get("https://www.bitmex.com/api/v1/instrument", {
        "symbol": "XBTUSD", "count": "1",
        "columns": "symbol,lastPrice,markPrice,indicativeFundingRate,openInterest,turnover24h"
    }, timeout=10)
    if not d or not isinstance(d, list) or not d:
        return _bitmex_cache.get("data", {})
    row = d[0]
    fr = row.get("indicativeFundingRate")
    t24 = row.get("turnover24h")
    result = {
        "bitmex_last_price":   safe(row.get("lastPrice"), 2),
        "bitmex_mark_price":   safe(row.get("markPrice"), 2),
        "bitmex_funding_rate": safe(float(fr)*100 if fr else None, 6),
        "bitmex_oi_contracts": safe(row.get("openInterest"), 0),
        "bitmex_vol_24h_btc":  safe(float(t24)/1e8 if t24 else None, 2),
    }
    if result.get("bitmex_last_price"):
        _bitmex_cache = {"data": result, "ts": now}
    return result


def fetch_hyperliquid():
    """Hyperliquid — DEX Perpetuals BTC (sans clé)"""
    global _hyper_cache
    now = time.time()
    if now - _hyper_cache["ts"] < 60 and _hyper_cache["data"]:
        return _hyper_cache["data"]
    try:
        r = requests.post("https://api.hyperliquid.xyz/info",
                          json={"type": "metaAndAssetCtxs"},
                          headers={"Content-Type": "application/json",
                                   "User-Agent": "btc-analytics/9.0"},
                          timeout=10)
        if r.status_code != 200:
            return _hyper_cache.get("data", {})
        data = r.json()
        if not isinstance(data, list) or len(data) < 2:
            return {}
        meta = data[0].get("universe", [])
        ctxs = data[1]
        btc_idx = next((i for i, a in enumerate(meta) if a.get("name") == "BTC"), None)
        if btc_idx is None or btc_idx >= len(ctxs):
            return {}
        btc = ctxs[btc_idx]
        funding = btc.get("funding")
        result = {
            "hyper_mark_price":   safe(btc.get("markPx"), 2),
            "hyper_mid_price":    safe(btc.get("midPx"), 2),
            "hyper_funding_rate": safe(float(funding)*100 if funding else None, 6),
            "hyper_oi_usd":       safe(btc.get("openInterest"), 0),
            "hyper_vol_24h_usd":  safe(btc.get("dayNtlVlm"), 0),
        }
        if result.get("hyper_mark_price"):
            _hyper_cache = {"data": result, "ts": now}
        return result
    except Exception as e:
        log.warning(f"hyperliquid: {e}")
        return _hyper_cache.get("data", {})


def fetch_bitget_futures():
    """Bitget USDT Futures — BTC Perpetual v9"""
    global _bgf_cache
    now = time.time()
    if now - _bgf_cache["ts"] < 60 and _bgf_cache["data"]:
        return _bgf_cache["data"]
    d = get("https://api.bitget.com/api/v2/mix/market/ticker",
            {"productType": "USDT-FUTURES", "symbol": "BTCUSDT"}, timeout=8)
    if not d: return _bgf_cache.get("data", {})
    data = (d.get("data") or [{}])[0]
    fr = data.get("fundingRate")
    result = {
        "bgf_last_price":   safe(data.get("lastPr"), 2),
        "bgf_mark_price":   safe(data.get("markPrice"), 2),
        "bgf_index_price":  safe(data.get("indexPrice"), 2),
        "bgf_funding_rate": safe(float(fr)*100 if fr else None, 6),
        "bgf_oi_usd":       safe(data.get("holdingAmount"), 0),
        "bgf_vol_usd":      safe(data.get("quoteVolume"), 0),
        "bgf_change_24h":   safe(data.get("change24h"), 4),
    }
    if result.get("bgf_last_price"):
        _bgf_cache = {"data": result, "ts": now}
    return result


def fetch_deribit_dvol():
    """Deribit — Bitcoin Volatility Index (DVol)"""
    global _dvol_cache
    now = time.time()
    if now - _dvol_cache["ts"] < 300 and _dvol_cache["data"]:
        return _dvol_cache["data"]
    d = get("https://www.deribit.com/api/v2/public/get_volatility_index_data", {
        "currency": "BTC",
        "start_timestamp": str(int((now - 7*86400)*1000)),
        "end_timestamp": str(int(now*1000)),
        "resolution": "3600"
    }, timeout=10)
    result = {}
    if d and d.get("result", {}).get("data"):
        rows = d["result"]["data"]
        if rows:
            latest = rows[-1]
            result["deribit_dvol"] = safe(latest[4], 2) if len(latest) > 4 else None  # close value
            prev = rows[-2] if len(rows) > 1 else None
            if prev and result.get("deribit_dvol"):
                prev_val = safe(prev[4], 2) if len(prev) > 4 else None
                if prev_val:
                    result["deribit_dvol_change"] = safe(result["deribit_dvol"] - prev_val, 2)
    if result:
        _dvol_cache = {"data": result, "ts": now}
    return result


def fetch_bitfinex_stats():
    """Bitfinex Stats — Positions long/short BTC (gratuit)"""
    global _bfxstats_cache
    now = time.time()
    if now - _bfxstats_cache["ts"] < 600 and _bfxstats_cache["data"]:
        return _bfxstats_cache["data"]
    result = {}
    try:
        # Positions long sur BTCUSD
        r_long = requests.get(
            "https://api-pub.bitfinex.com/v2/stats1/pos.size:1d:tBTCUSD:long/last",
            timeout=8, headers={"User-Agent": "btc-analytics/9.0"})
        if r_long.status_code == 200:
            data = r_long.json()
            if isinstance(data, list) and len(data) >= 2:
                result["bfx_longs_btc"] = safe(data[1], 2)
        # Positions short sur BTCUSD
        r_short = requests.get(
            "https://api-pub.bitfinex.com/v2/stats1/pos.size:1d:tBTCUSD:short/last",
            timeout=8, headers={"User-Agent": "btc-analytics/9.0"})
        if r_short.status_code == 200:
            data = r_short.json()
            if isinstance(data, list) and len(data) >= 2:
                result["bfx_shorts_btc"] = safe(data[1], 2)
        # Calcul ratio
        lg = result.get("bfx_longs_btc"); sh = result.get("bfx_shorts_btc")
        if lg and sh and sh > 0:
            result["bfx_ls_ratio"] = safe(lg / sh, 4)
    except Exception as e:
        log.warning(f"bfx_stats: {e}")
    if result:
        _bfxstats_cache = {"data": result, "ts": now}
    return result


# ══════════════════════════════════════════════════════════════
# NOUVELLES SOURCES v9 — DEFI / TVL
# ══════════════════════════════════════════════════════════════

def fetch_defillama():
    """DefiLlama — Bitcoin Ecosystem DeFi TVL (WBTC, tBTC, Babylon, Lombard...)"""
    global _defillama_cache
    now = time.time()
    if now - _defillama_cache["ts"] < 3600 and _defillama_cache["data"]:
        return _defillama_cache["data"]
    result = {}
    # TVL de la chaîne Bitcoin (native)
    d = get("https://api.llama.fi/v2/chains", timeout=12)
    if d and isinstance(d, list):
        for chain in d:
            if chain.get("name", "").lower() == "bitcoin":
                result["btc_chain_tvl_usd"] = safe(chain.get("tvl"), 0)
                break
    # WBTC protocol TVL — utilise l'endpoint simple /tvl/{slug}
    try:
        r_wbtc = requests.get("https://api.llama.fi/tvl/wbtc", timeout=10,
                               headers={"User-Agent": "btc-analytics/9.0"})
        if r_wbtc.status_code == 200:
            result["wbtc_tvl_usd"] = safe(float(r_wbtc.text.strip()), 0)
    except: pass
    # tBTC
    try:
        r_tbtc = requests.get("https://api.llama.fi/tvl/tbtc", timeout=10,
                               headers={"User-Agent": "btc-analytics/9.0"})
        if r_tbtc.status_code == 200:
            result["tbtc_tvl_usd"] = safe(float(r_tbtc.text.strip()), 0)
    except: pass
    # Babylon Bitcoin Staking
    try:
        r_bab = requests.get("https://api.llama.fi/tvl/babylon-protocol", timeout=10,
                              headers={"User-Agent": "btc-analytics/9.0"})
        if r_bab.status_code == 200:
            result["babylon_tvl_usd"] = safe(float(r_bab.text.strip()), 0)
    except: pass
    # Lombard Finance (LBTC)
    try:
        r_lom = requests.get("https://api.llama.fi/tvl/lombard-lbtc", timeout=10,
                              headers={"User-Agent": "btc-analytics/9.0"})
        if r_lom.status_code == 200:
            result["lombard_tvl_usd"] = safe(float(r_lom.text.strip()), 0)
    except: pass
    if result:
        _defillama_cache = {"data": result, "ts": now}
    return result


# ══════════════════════════════════════════════════════════════
# NOUVELLES SOURCES v9 — ANALYTICS
# ══════════════════════════════════════════════════════════════

def fetch_cryptocompare():
    """OKX Klines — Historique OHLCV 30 jours (remplace CryptoCompare)"""
    global _cc_cache
    now = time.time()
    if now - _cc_cache["ts"] < 86400 and _cc_cache["data"]:
        return _cc_cache["data"]
    try:
        d = get("https://www.okx.com/api/v5/market/candles",
                {"instId": "BTC-USDT", "bar": "1D", "limit": "30"}, timeout=12)
        if not d or not d.get("data"):
            return _cc_cache.get("data", {})
        candles = d["data"]  # newest first: [ts, open, high, low, close, vol, volCcy]
        if not candles:
            return {}
        latest = candles[0]
        closes  = [float(c[4]) for c in candles]
        volumes = [float(c[6]) for c in candles]  # volCcy = USD volume
        history = [{"date": datetime.fromtimestamp(int(c[0])/1000).strftime("%Y-%m-%d"),
                    "close": round(float(c[4]), 2)} for c in reversed(candles)]
        result = {
            "cc_open":        safe(latest[1], 2),
            "cc_high":        safe(latest[2], 2),
            "cc_low":         safe(latest[3], 2),
            "cc_close":       safe(latest[4], 2),
            "cc_vol_usd_24h": safe(latest[6], 0),
            "cc_avg_vol_30d": safe(sum(volumes) / len(volumes), 0),
            "cc_high_30d":    safe(max(closes), 2),
            "cc_low_30d":     safe(min(closes), 2),
            "cc_history_30d": history,
            "cc_source":      "OKX Daily Klines",
        }
        if result.get("cc_close"):
            _cc_cache = {"data": result, "ts": now}
        return result
    except Exception as e:
        log.warning(f"cc_hist: {e}")
        return _cc_cache.get("data", {})


def fetch_messari():
    """CoinPaprika Extended — Métriques BTC (remplace Messari tier gratuit)"""
    global _messari_cache
    now = time.time()
    if now - _messari_cache["ts"] < 3600 and _messari_cache["data"]:
        return _messari_cache["data"]
    d = get("https://api.coinpaprika.com/v1/tickers/btc-bitcoin", timeout=10)
    if not d or not d.get("quotes"):
        return _messari_cache.get("data", {})
    usd = d["quotes"].get("USD", {})
    result = {
        "messari_price":          safe(usd.get("price"), 2),
        "messari_vol_24h":        safe(usd.get("volume_24h"), 0),
        "messari_real_vol_24h":   safe(usd.get("volume_24h"), 0),
        "messari_market_cap":     safe(usd.get("market_cap"), 0),
        "messari_ath_price":      safe(usd.get("ath_price"), 2),
        "messari_pct_from_ath":   safe(usd.get("percent_from_price_ath"), 2),
        "messari_chg_7d":         safe(usd.get("percent_change_7d"), 2),
        "messari_chg_30d":        safe(usd.get("percent_change_30d"), 2),
        "messari_chg_1y":         safe(usd.get("percent_change_1y"), 2),
        "messari_supply_mined":   safe(d.get("total_supply"), 0),
        "messari_max_supply":     safe(d.get("max_supply"), 0),
        "messari_btc_txns_24h":   None,
        "messari_active_addr":    None,
        "messari_stock_to_flow":  None,
    }
    # Calcul supply percentage
    ts = d.get("total_supply"); ms = d.get("max_supply")
    if ts and ms and ms > 0:
        result["messari_supply_pct"] = safe(float(ts) / float(ms) * 100, 2)
    if result.get("messari_price"):
        _messari_cache = {"data": result, "ts": now}
    return result


def fetch_whattomine():
    """WhatToMine — Profitabilité Mining BTC (endpoint coin id=1)"""
    global _wtm_cache
    now = time.time()
    if now - _wtm_cache["ts"] < 3600 and _wtm_cache["data"]:
        return _wtm_cache["data"]
    d = get("https://whattomine.com/coins/1.json", timeout=12)
    if not d:
        return _wtm_cache.get("data", {})
    result = {
        "wtm_btc_profitability": safe(d.get("profitability"), 2),
        "wtm_btc_nethash_th":    safe(d.get("nethash"), 2),
        "wtm_btc_difficulty":    safe(d.get("difficulty"), 0),
        "wtm_btc_block_reward":  safe(d.get("block_reward"), 4),
        "wtm_btc_block_time":    safe(d.get("block_time"), 2),
        "wtm_btc_last_block":    safe(d.get("last_block"), 0),
        "wtm_btc_exchange_rate": safe(d.get("exchange_rate"), 2),
    }
    if result.get("wtm_btc_block_reward"):
        _wtm_cache = {"data": result, "ts": now}
    return result


def fetch_coinmetrics_deep():
    """CoinMetrics Community — Métriques disponibles en tier gratuit: AdrActCnt, HashRate"""
    global _cm_deep_cache
    now = time.time()
    if now - _cm_deep_cache["ts"] < 3600 and _cm_deep_cache["data"]:
        return _cm_deep_cache["data"]
    result = {}
    # Adresses actives (disponible tier gratuit)
    d1 = get("https://community-api.coinmetrics.io/v4/timeseries/asset-metrics",
             {"assets": "btc", "metrics": "AdrActCnt", "page_size": "1", "paging_from": "end"},
             timeout=12)
    if d1 and d1.get("data"):
        row = d1["data"][-1]
        result["cm_active_addresses"] = safe(row.get("AdrActCnt"), 0)
    # Hashrate (disponible tier gratuit)
    d2 = get("https://community-api.coinmetrics.io/v4/timeseries/asset-metrics",
             {"assets": "btc", "metrics": "HashRate", "page_size": "1", "paging_from": "end"},
             timeout=12)
    if d2 and d2.get("data"):
        row = d2["data"][-1]
        hr = row.get("HashRate")
        result["cm_hashrate_ths"] = safe(hr, 2)  # en TH/s
        if hr:
            result["cm_hashrate_eh"] = safe(float(hr) / 1e6, 2)  # EH/s
    # Prix (disponible)
    d3 = get("https://community-api.coinmetrics.io/v4/timeseries/asset-metrics",
             {"assets": "btc", "metrics": "PriceUSD", "page_size": "1", "paging_from": "end"},
             timeout=12)
    if d3 and d3.get("data"):
        row = d3["data"][-1]
        result["cm_price_usd"] = safe(row.get("PriceUSD"), 2)
        result["cm_deep_date"] = row.get("time", "")[:10]
    # Note: NVTAdj, SplyAct1yr, TxTfrValAdjUSD nécessitent un abonnement payant
    result["cm_nvt_adj"] = None
    result["cm_sply_act_1yr_btc"] = None
    result["cm_tx_tfr_val_adj_usd"] = None
    result["cm_supply_current"] = None
    result["cm_difficulty_mean"] = None
    if result.get("cm_active_addresses"):
        _cm_deep_cache = {"data": result, "ts": now}
    return result


def fetch_mempool_blocks():
    """Mempool.space — Derniers blocs minés (stats détaillées)"""
    global _mempool_deep_cache
    now = time.time()
    if now - _mempool_deep_cache["ts"] < 120 and _mempool_deep_cache["data"]:
        return _mempool_deep_cache["data"]
    d = get("https://mempool.space/api/v1/blocks", timeout=10)
    if not d or not isinstance(d, list) or not d:
        return _mempool_deep_cache.get("data", {})
    last = d[0]
    result = {
        "last_block_height":  safe(last.get("height"), 0),
        "last_block_txcount": safe(last.get("tx_count"), 0),
        "last_block_size_kb": safe((last.get("size") or 0) / 1024, 1),
        "last_block_weight":  safe(last.get("weight"), 0),
        "last_block_ts":      last.get("timestamp"),
        "last_block_median_fee_rate": safe(last.get("extras", {}).get("medianFee"), 1),
        "last_block_pool": last.get("extras", {}).get("pool", {}).get("name", "Unknown"),
    }
    # Stats sur les 10 derniers blocs
    if len(d) >= 10:
        avg_tx = sum(b.get("tx_count", 0) for b in d[:10]) / 10
        avg_size = sum((b.get("size") or 0) for b in d[:10]) / 10 / 1024
        result["blocks_avg_tx_count"] = round(avg_tx, 0)
        result["blocks_avg_size_kb"] = round(avg_size, 1)
    if result:
        _mempool_deep_cache = {"data": result, "ts": now}
    return result


def fetch_blockchain_charts():
    """Blockchain.info Charts API — Hashrate & Transactions historique"""
    global _bcinfo_chart_cache
    now = time.time()
    if now - _bcinfo_chart_cache["ts"] < 3600 and _bcinfo_chart_cache["data"]:
        return _bcinfo_chart_cache["data"]
    result = {}
    # Hashrate 30 jours
    d1 = get("https://api.blockchain.info/charts/hash-rate",
             {"timespan": "30days", "format": "json", "sampled": "true"}, timeout=12)
    if d1 and d1.get("values"):
        vals = [v["y"] for v in d1["values"] if v.get("y")]
        if vals:
            result["bchart_hashrate_now_eh"] = safe(vals[-1] / 1e6, 2)   # TH/s → EH/s
            result["bchart_hashrate_30d_avg_eh"] = safe(sum(vals)/len(vals)/1e6, 2)
            result["bchart_hashrate_history"] = [
                {"date": datetime.fromtimestamp(v["x"]).strftime("%Y-%m-%d"),
                 "eh": round(v["y"]/1e6, 2)} for v in d1["values"][-30:]
            ]
    # Transactions par jour
    d2 = get("https://api.blockchain.info/charts/n-transactions",
             {"timespan": "30days", "format": "json", "sampled": "true"}, timeout=12)
    if d2 and d2.get("values"):
        vals = [v["y"] for v in d2["values"] if v.get("y")]
        if vals:
            result["bchart_txcount_today"] = safe(vals[-1], 0)
            result["bchart_txcount_30d_avg"] = safe(sum(vals)/len(vals), 0)
    # Frais de transactions USD
    d3 = get("https://api.blockchain.info/charts/transaction-fees-usd",
             {"timespan": "7days", "format": "json", "sampled": "true"}, timeout=12)
    if d3 and d3.get("values"):
        vals = [v["y"] for v in d3["values"] if v.get("y")]
        if vals:
            result["bchart_fees_usd_today"] = safe(vals[-1], 2)
    if result:
        _bcinfo_chart_cache = {"data": result, "ts": now}
    return result


# ══════════════════════════════════════════════════════════════
# PAGE HTML
# ══════════════════════════════════════════════════════════════
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    # Vercel: api/main.py lives in /var/task/api/, index.html in /var/task/
    for candidate in [
        Path(__file__).parent.parent / "index.html",
        Path(__file__).parent / "index.html",
        Path("/var/task/index.html"),
    ]:
        if candidate.exists():
            return HTMLResponse(content=candidate.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>index.html not found</h1>", status_code=404)

# ══════════════════════════════════════════════════════════════
# ENDPOINTS API
# ══════════════════════════════════════════════════════════════

@app.get("/api/health")
def health():
    now = time.time()
    def age(ts): return round(now - ts, 0) if ts and ts > 0 else None
    return {
        "status": "ok", "service": "BTC Analytics API — 70 APIs", "version": "9.0.0",
        "total_apis": 70,
        "apis_par_categorie": {
            "exchanges_usd": 28, "exchanges_intl": 19, "dex_onchain": 1,
            "on_chain": 7, "historique": 1, "sentiment": 1, "lightning": 2,
            "mining_stats": 2, "etf": 2, "derivatives": 6,
            "defi_tvl": 1, "analytics": 2
        },
        "env_keys": {"SOSOVALUE_KEY": bool(os.environ.get("SOSOVALUE_KEY")),
                     "TWELVE_DATA_KEY": bool(os.environ.get("TWELVE_DATA_KEY"))},
        "cache_ages": {k: age(v["ts"]) for k, v in {
            "cg": _cg_cache, "cb": _cb_cache, "fx": _fx_cache, "ex": _ex_cache,
            "bgr": _bgr_cache, "bgr_h": _bgr_holders_cache, "cm_ext": _cm_ext_cache,
            "puell": _puell_cache, "pools": _pools_cache, "1ml": _1ml_cache,
            "dex": _dex_cache, "stooq": _stooq_cache, "intl": _intl_cache,
            "soso": _soso_cache, "twelve": _twelve_cache,
            "bnf": _bnf_cache, "krf": _krf_cache, "bitmex": _bitmex_cache,
            "hyper": _hyper_cache, "bgf": _bgf_cache, "defillama": _defillama_cache,
            "messari": _messari_cache, "cc": _cc_cache, "wtm": _wtm_cache,
        }.items()},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/exchanges")
def get_exchanges():
    """19 exchanges USD + DEX WBTC + spread arbitrage"""
    global _ex_cache
    now = time.time()
    if now - _ex_cache["ts"] < EX_TTL and _ex_cache["data"]:
        return _ex_cache["data"]

    cg = fetch_coingecko(); cb = fetch_coinbase()
    kr_meta, _ = fetch_kraken_ohlc()
    bn = sf(fetch_binance); bfx = sf(fetch_bitfinex); bst = sf(fetch_bitstamp)
    okx = sf(fetch_okx); byb = sf(fetch_bybit); gem = sf(fetch_gemini)
    kuc = sf(fetch_kucoin); gate = sf(fetch_gate_io); htx = sf(fetch_htx)
    mexc = sf(fetch_mexc); bitget = sf(fetch_bitget); coinex = sf(fetch_coinex)
    lbank = sf(fetch_lbank); wb = sf(fetch_whitebit); cap = sf(fetch_coincap)
    der = sf(fetch_deribit); cp = sf(fetch_coinpaprika); dex = sf(fetch_dexscreener)
    # ── Nouvelles sources v8 ──────────────────────────────────
    pol = sf(fetch_poloniex); cdc = sf(fetch_cryptodotcom)
    bmt = sf(fetch_bitmart); bts = sf(fetch_btse)
    clr = sf(fetch_coinlore); crk = sf(fetch_coinranking)
    xtc = sf(fetch_xtcom)

    prices_raw = {
        "CoinGecko": cg.get("price_usd"), "Binance": bn.get("binance_price"),
        "Bitfinex": bfx.get("bitfinex_price"), "Bitstamp": bst.get("bitstamp_price"),
        "OKX": okx.get("okx_price"), "Bybit": byb.get("bybit_price"),
        "Gemini": gem.get("gemini_price"), "KuCoin": kuc.get("kucoin_price"),
        "Gate.io": gate.get("gate_price"), "HTX": htx.get("htx_price"),
        "MEXC": mexc.get("mexc_price"), "Bitget": bitget.get("bitget_price"),
        "CoinEx": coinex.get("coinex_price"), "LBank": lbank.get("lbank_price"),
        "WhiteBit": wb.get("whitebit_price"), "CoinCap": cap.get("coincap_price"),
        "Deribit": der.get("deribit_index_price"), "Coinbase": cb.get("price_coinbase"),
        "Kraken": kr_meta.get("kraken_close"), "CoinPaprika": cp.get("price_coinpaprika"),
        "WBTC DEX": dex.get("dex_wbtc_price_usd"),
        # v8 nouvelles sources
        "Poloniex": pol.get("poloniex_price"), "Crypto.com": cdc.get("cdotcom_price"),
        "BitMart": bmt.get("bitmart_price"), "BTSE": bts.get("btse_price"),
        "CoinLore": clr.get("coinlore_price"), "CoinRanking": crk.get("coinranking_price"),
        # v9
        "XT.com": xtc.get("xtcom_price"),
    }
    valid = {k: float(v) for k, v in prices_raw.items() if v is not None}
    avg_p = round(sum(valid.values()) / len(valid), 2) if valid else None
    spread_pct = None; max_ex = None; min_ex = None
    if len(valid) >= 2:
        max_p = max(valid.values()); min_p = min(valid.values())
        spread_pct = round((max_p - min_p) / min_p * 100, 4) if min_p > 0 else None
        max_ex = max(valid, key=valid.get); min_ex = min(valid, key=valid.get)

    exchange_list = [{"name": k, "price": v,
                      "diff_avg": round((v - avg_p) / avg_p * 100, 4) if avg_p else None}
                     for k, v in sorted(valid.items(), key=lambda x: x[1], reverse=True)]

    result = {
        "exchange_prices": exchange_list, "exchange_count": len(valid),
        "avg_price": avg_p, "arbitrage_spread_pct": spread_pct,
        "highest_exchange": max_ex, "lowest_exchange": min_ex,
        **bn, **bfx, **bst, **okx, **byb, **gem, **kuc, **gate, **htx,
        **mexc, **bitget, **coinex, **lbank, **wb, **cap, **der, **dex,
        **pol, **cdc, **bmt, **bts, **clr, **crk, **xtc,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _ex_cache = {"data": result, "ts": now}
    return result


@app.get("/api/international")
def get_international():
    """11 exchanges internationaux (JP, KR, AU, TR, BR, RU) avec conversion USD"""
    return {**fetch_international(), "updated_at": datetime.now(timezone.utc).isoformat()}


@app.get("/api/fx")
def get_fx():
    """Taux de change BTC dans les principales devises mondiales"""
    return {**fetch_fx(), "updated_at": datetime.now(timezone.utc).isoformat()}


@app.get("/api/onchain")
def get_onchain():
    cg = sf(fetch_coingecko); cm = sf(fetch_coinmetrics); bgr = sf(fetch_bgeometrics)
    fg = sf(fetch_fear_greed); cm_ext = sf(fetch_coinmetrics_extended); puell = sf(fetch_puell_multiple)
    cm_deep = sf(fetch_coinmetrics_deep); bfxst = sf(fetch_bitfinex_stats)
    kr_meta, ohlc = fetch_kraken_ohlc()
    tech = compute_technicals(ohlc)
    price = cg.get("price_usd"); ma200 = tech.get("ma_200d")
    mayer = round(price / ma200, 4) if price and ma200 and ma200 > 0 else None
    all_data = {**cg, **cm, **bgr, **fg, **cm_ext, **puell, **tech, **kr_meta,
                **cm_deep, **bfxst, "mayer_multiple": mayer}
    if not all_data.get("price_usd"):
        all_data["price_usd"] = sf(fetch_coinbase).get("price_coinbase")
    return {**all_data, **compute_signals(all_data), "updated_at": datetime.now(timezone.utc).isoformat()}


@app.get("/api/network")
def get_network():
    return {**sf(fetch_blockchair), **sf(fetch_mempool), **sf(fetch_blockchain_info),
            **sf(fetch_blockchain_query), **sf(fetch_blockstream), **sf(fetch_bitnodes),
            **sf(fetch_mining_pools), **sf(fetch_coinpaprika_ohlcv),
            **sf(fetch_mempool_blocks), **sf(fetch_blockchain_charts), **sf(fetch_whattomine),
            "updated_at": datetime.now(timezone.utc).isoformat()}


@app.get("/api/lightning")
def get_lightning():
    mem = sf(fetch_mempool); ml = sf(fetch_1ml)
    cg = sf(fetch_coingecko)
    price = cg.get("price_usd") or sf(fetch_coinbase).get("price_coinbase")
    cap = mem.get("ln_capacity_btc")
    return {**{k: mem.get(k) for k in ["ln_channels","ln_nodes","ln_capacity_btc","ln_avg_capacity_sat"]},
            **ml, "ln_capacity_usd": round(cap * price, 0) if cap and price else None,
            "updated_at": datetime.now(timezone.utc).isoformat()}


@app.get("/api/market")
def get_market():
    cg = sf(fetch_coingecko); cg_gl = sf(fetch_coingecko_global); stable = sf(fetch_stablecoins)
    cp = sf(fetch_coinpaprika); cb = sf(fetch_coinbase); kr_meta, ohlc = fetch_kraken_ohlc()
    tech = compute_technicals(ohlc); altme = sf(fetch_altme_ticker)
    all_data = {**cg, **cg_gl, **stable, **cp, **cb, **kr_meta, **tech, **altme}
    if not all_data.get("price_usd"):
        all_data["price_usd"] = all_data.get("price_coinbase") or all_data.get("kraken_close")
    return {**all_data, **compute_signals(all_data), "updated_at": datetime.now(timezone.utc).isoformat()}


@app.get("/api/etf")
def get_etf():
    soso = sf(fetch_sosovalue_etf); twelve = sf(fetch_twelvedata_etf)
    merged = {**soso, **twelve}
    if not merged:
        return {"note": "Clés SOSOVALUE_KEY et TWELVE_DATA_KEY configurées dans env",
                "sosovalue_key_set": bool(os.environ.get("SOSOVALUE_KEY")),
                "twelvedata_key_set": bool(os.environ.get("TWELVE_DATA_KEY")),
                "updated_at": datetime.now(timezone.utc).isoformat()}
    return {**merged, "updated_at": datetime.now(timezone.utc).isoformat()}


@app.get("/api/stooq")
def get_stooq():
    return {**sf(fetch_stooq_history), "updated_at": datetime.now(timezone.utc).isoformat()}


@app.get("/api/alerts")
def get_alerts():
    cg = sf(fetch_coingecko); cm = sf(fetch_coinmetrics); bgr = sf(fetch_bgeometrics)
    fg = sf(fetch_fear_greed); kr_meta, ohlc = fetch_kraken_ohlc(); tech = compute_technicals(ohlc)
    return compute_signals({**cg, **cm, **bgr, **fg, **tech, **kr_meta}).get("alerts", [])


@app.get("/api/sources")
def get_sources():
    """Catalogue complet des 70 APIs gratuites intégrées"""
    return {
        "total_apis": 70,
        "version": "9.0.0",
        "categories": {
            "exchanges_usd": {
                "count": 28,
                "sources": [
                    {"name":"CoinGecko","url":"coingecko.com","key":False,"data":"Prix, OHLCV, Market Cap, Dominance"},
                    {"name":"Binance","url":"binance.com","key":False,"data":"Prix, Volume, Variation 24h, High/Low"},
                    {"name":"Coinbase","url":"coinbase.com","key":False,"data":"Prix spot BTC/USD"},
                    {"name":"Kraken","url":"kraken.com","key":False,"data":"OHLC 400j, VWAP"},
                    {"name":"Bitfinex","url":"bitfinex.com","key":False,"data":"Prix, Bid/Ask, Volume"},
                    {"name":"Bitstamp","url":"bitstamp.net","key":False,"data":"Prix, Bid/Ask, Volume"},
                    {"name":"OKX","url":"okx.com","key":False,"data":"Prix, Volume USD"},
                    {"name":"Bybit","url":"bybit.com","key":False,"data":"Prix, Volume, Variation"},
                    {"name":"Gemini","url":"gemini.com","key":False,"data":"Prix, Bid/Ask, Volume"},
                    {"name":"KuCoin","url":"kucoin.com","key":False,"data":"Ticker 24h complet"},
                    {"name":"Gate.io","url":"gate.io","key":False,"data":"Prix, Volume, %Change"},
                    {"name":"HTX (Huobi)","url":"htx.com","key":False,"data":"Prix OHLCV"},
                    {"name":"MEXC","url":"mexc.com","key":False,"data":"Prix, Volume, Variation 24h"},
                    {"name":"Bitget","url":"bitget.com","key":False,"data":"Prix, Volume, Variation"},
                    {"name":"CoinEx","url":"coinex.com","key":False,"data":"Prix, OHLCV"},
                    {"name":"LBank","url":"lbank.info","key":False,"data":"Prix, High, Low"},
                    {"name":"WhiteBit","url":"whitebit.com","key":False,"data":"Prix, Volume"},
                    {"name":"CoinCap","url":"coincap.io","key":False,"data":"Prix, Supply, VWAP"},
                    {"name":"Deribit","url":"deribit.com","key":False,"data":"Index, Perpétuel, Funding, OI"},
                    {"name":"CoinPaprika","url":"coinpaprika.com","key":False,"data":"Prix, Beta, OHLCV"},
                    {"name":"WBTC DEX","url":"dexscreener.com","key":False,"data":"Prix Uniswap/Ethereum, Liquidité"},
                    {"name":"Poloniex","url":"poloniex.com","key":False,"data":"Prix, Volume, High/Low"},
                    {"name":"Crypto.com","url":"crypto.com","key":False,"data":"Prix, Volume, High/Low"},
                    {"name":"BitMart","url":"bitmart.com","key":False,"data":"Prix, Volume, Variation"},
                    {"name":"BTSE","url":"btse.com","key":False,"data":"Prix last, Index price"},
                    {"name":"CoinLore","url":"coinlore.net","key":False,"data":"Prix, Market Cap, Volume, Rang"},
                    {"name":"CoinRanking","url":"coinranking.com","key":False,"data":"Prix BTC en temps réel"},
                    {"name":"XT.com","url":"xt.com","key":False,"data":"Prix, Volume, High/Low BTC/USDT"},
                ]
            },
            "exchanges_international": {
                "count": 19,
                "sources": [
                    {"name":"bitFlyer","url":"bitflyer.com","key":False,"country":"JP","data":"BTC/JPY Prix, Volume, Bid/Ask"},
                    {"name":"Coincheck","url":"coincheck.com","key":False,"country":"JP","data":"BTC/JPY Prix, Volume"},
                    {"name":"Zaif","url":"zaif.jp","key":False,"country":"JP","data":"BTC/JPY Prix, VWAP"},
                    {"name":"Upbit","url":"upbit.com","key":False,"country":"KR","data":"BTC/KRW Prix, Volume 24h"},
                    {"name":"Bithumb","url":"bithumb.com","key":False,"country":"KR","data":"BTC/KRW Prix, High/Low"},
                    {"name":"Korbit","url":"korbit.co.kr","key":False,"country":"KR","data":"BTC/KRW Prix"},
                    {"name":"BTCMarkets","url":"btcmarkets.net","key":False,"country":"AU","data":"BTC/AUD Prix, Bid/Ask"},
                    {"name":"BtcTurk","url":"btcturk.com","key":False,"country":"TR","data":"BTC/USDT Prix, Volume"},
                    {"name":"Paribu","url":"paribu.com","key":False,"country":"TR","data":"BTC/TRY Prix"},
                    {"name":"Mercado Bitcoin","url":"mercadobitcoin.net","key":False,"country":"BR","data":"BTC/BRL Prix, Volume"},
                    {"name":"Foxbit","url":"foxbit.com.br","key":False,"country":"BR","data":"BTC/BRL Prix, High/Low"},
                    {"name":"NovaDax","url":"novadax.com","key":False,"country":"BR","data":"BTC/BRL Prix, Volume"},
                    {"name":"Exmo","url":"exmo.com","key":False,"country":"RU","data":"BTC/USD Prix, Volume"},
                    {"name":"Luno","url":"luno.com","key":False,"country":"ZA","data":"BTC/ZAR Prix, Bid/Ask, Volume"},
                    {"name":"VALR","url":"valr.com","key":False,"country":"ZA","data":"BTC/ZAR Prix, Bid/Ask"},
                    {"name":"Bitso","url":"bitso.com","key":False,"country":"MX","data":"BTC/MXN Prix, Volume, Bid/Ask"},
                    {"name":"CoinDCX","url":"coindcx.com","key":False,"country":"IN","data":"BTC/INR Prix, Volume, High/Low"},
                    {"name":"WazirX","url":"wazirx.com","key":False,"country":"IN","data":"BTC/INR Prix, Volume"},
                    {"name":"Indodax","url":"indodax.com","key":False,"country":"ID","data":"BTC/IDR Prix, Volume, High/Low"},
                ]
            },
            "on_chain": {
                "count": 7,
                "sources": [
                    {"name":"CoinMetrics Community","url":"coinmetrics.io","key":False,"data":"MVRV, Realized Cap, NUPL, Flux exchanges, ROI, Puell"},
                    {"name":"BGR bitcoin-data.com","url":"bitcoin-data.com","key":False,"data":"aSOPR, SOPR, NRPL USD/BTC, Whales >1000 BTC"},
                    {"name":"Mempool.space","url":"mempool.space","key":False,"data":"Fees, Hashrate, Difficulté, Blocks, Lightning"},
                    {"name":"Blockchair","url":"blockchair.com","key":False,"data":"Blockchain stats, UTXOs, Taille, TPS"},
                    {"name":"Blockchain.info","url":"blockchain.info","key":False,"data":"Stats globales, Supply, Hash, Miners revenue, Pools"},
                    {"name":"Blockstream.info","url":"blockstream.info","key":False,"data":"Hauteur bloc, Mempool count"},
                    {"name":"Bitnodes.io","url":"bitnodes.io","key":False,"data":"Nœuds P2P Bitcoin dans le monde"},
                ]
            },
            "lightning": {
                "count": 2,
                "sources": [
                    {"name":"Mempool.space Lightning","url":"mempool.space","key":False,"data":"Canaux, Nœuds, Capacité BTC/USD, Capacité moy/canal"},
                    {"name":"1ML.com","url":"1ml.com","key":False,"data":"Nœuds, Canaux, Variations 30j"},
                ]
            },
            "sentiment": {
                "count": 1,
                "sources": [
                    {"name":"Alternative.me","url":"alternative.me","key":False,"data":"Fear & Greed Index 7j + Ticker BTC"},
                ]
            },
            "historical": {
                "count": 2,
                "sources": [
                    {"name":"Stooq","url":"stooq.com","key":False,"data":"Cours historique 30j CSV, High/Low 30j"},
                    {"name":"CryptoCompare","url":"cryptocompare.com","key":False,"data":"OHLCV 30j, Volume moyen, High/Low 30j"},
                ]
            },
            "etf_finance": {
                "count": 2,
                "sources": [
                    {"name":"SoSoValue","url":"sosovalue.xyz","key":True,"data":"AUM total ETF, Flux nets jour/cumulé, BTC détenus"},
                    {"name":"TwelveData","url":"twelvedata.com","key":True,"data":"Prix ETF IBIT, FBTC, ARKB, GBTC, HODL + volumes"},
                ]
            },
            "derivatives": {
                "count": 6,
                "sources": [
                    {"name":"Binance FAPI","url":"fapi.binance.com","key":False,"data":"BTC-Perp: Funding rate, OI en BTC, Ratio Long/Short, Mark price"},
                    {"name":"Kraken Futures","url":"futures.kraken.com","key":False,"data":"PF_XBTUSD: Funding rate, OI, Mark price, Bid/Ask"},
                    {"name":"BitMEX","url":"bitmex.com","key":False,"data":"XBTUSD: Funding rate, OI en contrats, Volume 24h BTC"},
                    {"name":"Hyperliquid DEX","url":"api.hyperliquid.xyz","key":False,"data":"BTC Perp décentralisé: Funding rate, OI USD, Volume 24h"},
                    {"name":"Bitget Futures","url":"api.bitget.com","key":False,"data":"BTC USDT-Futures: Funding rate, OI USD, Mark/Index price"},
                    {"name":"Deribit DVol","url":"deribit.com","key":False,"data":"Bitcoin Volatility Index (DVol) — IV implicite options BTC"},
                ]
            },
            "defi_tvl": {
                "count": 1,
                "sources": [
                    {"name":"DefiLlama","url":"llama.fi","key":False,"data":"TVL Bitcoin chain, WBTC/tBTC/Babylon/Lombard TVL par protocole"},
                ]
            },
            "analytics": {
                "count": 2,
                "sources": [
                    {"name":"CoinPaprika Extended","url":"coinpaprika.com","key":False,"data":"ATH, %desde ATH, Variations 7j/30j/1an, Market cap, Volume, Supply minée"},
                    {"name":"Bitfinex Stats","url":"bitfinex.com","key":False,"data":"Positions Long/Short BTCUSD sur Bitfinex + ratio L/S"},
                ]
            },
            "mining_stats": {
                "count": 2,
                "sources": [
                    {"name":"Blockchain.info Pools","url":"blockchain.info","key":False,"data":"Distribution hashrate par pool mining (5 jours)"},
                    {"name":"WhatToMine","url":"whattomine.com","key":False,"data":"Profitabilité mining BTC, Hashrate réseau, Difficulté, Block reward"},
                ]
            }
        },
        "updated_at": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/summary")
def get_summary():
    cg = sf(fetch_coingecko); cg_gl = sf(fetch_coingecko_global); stable = sf(fetch_stablecoins)
    cm = sf(fetch_coinmetrics); bgr = sf(fetch_bgeometrics); bgr_h = sf(fetch_bgr_holders)
    soso = sf(fetch_sosovalue_etf); twelve = sf(fetch_twelvedata_etf)
    mem = sf(fetch_mempool); bc = sf(fetch_blockchair); cp = sf(fetch_coinpaprika)
    fg = sf(fetch_fear_greed); cb = sf(fetch_coinbase)
    kr_meta, ohlc = fetch_kraken_ohlc(); tech = compute_technicals(ohlc)
    bci = sf(fetch_blockchain_info); cm_ext = sf(fetch_coinmetrics_extended)
    pools = sf(fetch_mining_pools); puell = sf(fetch_puell_multiple); altme = sf(fetch_altme_ticker)
    cm_deep = sf(fetch_coinmetrics_deep); messari = sf(fetch_messari)
    bnf = sf(fetch_binance_futures); wtm = sf(fetch_whattomine)

    price = cg.get("price_usd"); ma200 = tech.get("ma_200d")
    mayer = round(price / ma200, 4) if price and ma200 and ma200 > 0 else None
    lth_rp = bgr_h.get("lth_realized_price"); ma30 = tech.get("ma_30d")
    lth_mvrv = round(price / lth_rp, 4) if price and lth_rp else None
    sth_mvrv = round(price / ma30, 4)   if price and ma30   else None

    all_data = {**cg, **cg_gl, **stable, **cm, **bgr, **bgr_h, **soso, **twelve,
                **cm_ext, **pools, **puell, **altme, **cm_deep, **messari, **bnf, **wtm,
                "mayer_multiple": mayer, "lth_realized_price_proxy": lth_rp,
                "sth_realized_price_proxy": ma30, "lth_mvrv_proxy": lth_mvrv,
                "sth_mvrv_proxy": sth_mvrv,
                **mem, **bc, **cp, **fg, **cb, **kr_meta, **tech, **bci}

    if not all_data.get("price_usd"):
        for fb in ["price_coinbase", "kraken_close", "altme_price", "messari_price"]:
            if all_data.get(fb):
                all_data["price_usd"] = all_data[fb]
                break

    return {**all_data, **compute_signals(all_data), "updated_at": datetime.now(timezone.utc).isoformat()}


@app.get("/api/derivatives")
def get_derivatives():
    """Endpoint agrégé — Futures/Dérivés BTC (6 sources)"""
    bnf = sf(fetch_binance_futures)
    krf = sf(fetch_kraken_futures)
    bitmex = sf(fetch_bitmex)
    hyper = sf(fetch_hyperliquid)
    bgf = sf(fetch_bitget_futures)
    dvol = sf(fetch_deribit_dvol)
    bfxst = sf(fetch_bitfinex_stats)
    # Calcul du funding rate moyen agrégé
    rates = [v for k, v in {
        "binance": bnf.get("bnf_funding_rate"),
        "kraken": krf.get("krf_funding_rate"),
        "bitmex": bitmex.get("bitmex_funding_rate"),
        "hyperliquid": hyper.get("hyper_funding_rate"),
        "bitget": bgf.get("bgf_funding_rate"),
    }.items() if v is not None]
    avg_funding = round(sum(rates) / len(rates), 6) if rates else None
    # OI agrégé (BTC)
    oi_btc_sources = {
        "binance_oi_btc": bnf.get("bnf_oi_btc"),
        "bitmex_oi_contracts": bitmex.get("bitmex_oi_contracts"),
    }
    return {
        **bnf, **krf, **bitmex, **hyper, **bgf, **dvol, **bfxst,
        "avg_funding_rate_pct": avg_funding,
        "funding_signal": (
            "Bullish extrême 🔴" if avg_funding and avg_funding > 0.1
            else "Bullish 🟡" if avg_funding and avg_funding > 0.01
            else "Neutre 🟢" if avg_funding and avg_funding > -0.01
            else "Bearish 🟡" if avg_funding and avg_funding > -0.1
            else "Bearish extrême 🔴" if avg_funding is not None
            else "—"
        ),
        **oi_btc_sources,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/defi")
def get_defi():
    """Endpoint — DeFi Bitcoin Ecosystem TVL + Analytics"""
    defi = sf(fetch_defillama)
    messari = sf(fetch_messari)
    cc = sf(fetch_cryptocompare)
    return {
        **defi, **messari, **cc,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
