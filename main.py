""" BTC On-Chain Analytics API — v9.0.0 (Vercel Edition) Toutes les APIs BTC gratuites disponibles dans le monde — 70 sources.

Structure Vercel : ce fichier est servi comme serverless function. GET / → index.html GET /api/* → endpoints FastAPI

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
    try:
        h = {"Accept": "application/json", "User-Agent": "btc-analytics/7.0"}
        if headers:
            h.update(headers)
        r = requests.get(url, params=params or {}, timeout=timeout, headers=h)
        if r.status_code == 200:
            return r.json()
        log.warning(f"GET {url} -> HTTP {r.status_code}")
    except Exception as e:
        log.error(f"GET {url} -> {e}")
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
    result = {}
    d = get("https://community-api.coinmetrics.io/v4/timeseries/asset-metrics", {
        "assets": "btc", "metrics": "CapMVRVCur,CapRealUSD",
        "page_size": "1", "paging_from": "end"
    })
    if d and d.get("data"):
        row  = d["data"][-1]
        mvrv = safe(row.get("CapMVRVCur"), 4)
        rc   = safe(row.get("CapRealUSD"), 2)
        nupl = round(1 - 1/mvrv, 4) if mvrv and mvrv > 0 else None
        result.update({"mvrv": mvrv, "realized_cap": rc, "nupl": nupl,
                        "coinmetrics_date": row.get("time", "")[:10]})
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
Exit code: 0

Action: $ sed -n '401,900p' /app/vercel/main.py
Observation: if ln:
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
Exit code: 0

Action: $ sed -n '900,1400p' /app/vercel/main.py
Observation: chg = data.get("c")
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
Exit code: 0
