"""
api/main.py — API BTC On-Chain v4.7.4
Date    : 2026-03-21

FIX CRITIQUE v4.7.0 :
  fetch_technicals() inexistant remplace par fetch_kraken_ohlc() + compute_technicals(ohlc)
  Causait 500 Internal Server Error sur /api/onchain

Nouveautés v4.7.0 :
  CoinMetrics Extended 14 métriques, Mining Pools, Mayer Multiple, bgr_probe
"""
import os, time, math, requests, logging
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

log = logging.getLogger(__name__)
app = FastAPI(title="BTC On-Chain Analytics API", version="4.7.4")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

try:
    from api.test import router as test_router
    app.include_router(test_router)
except:
    try:
        from test import router as test_router
        app.include_router(test_router)
    except:
        pass

BGR_BASE    = "https://bitcoin-data.com"
SOSO_BASE   = "https://api.sosovalue.xyz"
TWELVE_BASE = "https://api.twelvedata.com"

# ══════════════════════════════════════════════════════════
# CACHE BGR MUTUALISÉ — résout le rate limit 8 req/h
# Un seul appel réel par heure, partagé entre tous les endpoints
# ══════════════════════════════════════════════════════════
_bgr_cache = {"data": {}, "ts": 0}
_bgr_holders_cache = {"data": {}, "ts": 0}
_cm_ext_cache = {"data": {}, "ts": 0}
_pools_cache = {"data": {}, "ts": 0}
BGR_TTL = 3600  # 1 heure

# ══════════════════════════════════════════════════════════
# CACHE SOSOVALUE — plan Demo = 10 appels/mois → TTL 24h
# ══════════════════════════════════════════════════════════
_soso_cache = {"data": {}, "ts": 0}
SOSO_TTL = 86400  # 24 heures

# ══════════════════════════════════════════════════════════
# CACHE TWELVE DATA — plan Basic = 800 req/jour → TTL 1h
# ══════════════════════════════════════════════════════════
_twelve_cache = {"data": {}, "ts": 0}

# ══════════════════════════════════════════════════════════
# CACHE PUELL MULTIPLE — CoinMetrics 365j → TTL 24h
# ══════════════════════════════════════════════════════════
_puell_cache  = {"data": {}, "ts": 0}
_cg_cache     = {"data": {}, "ts": 0}  # CoinGecko cache 60s anti-429
_cb_cache     = {"data": {}, "ts": 0}  # Coinbase cache 60s
TWELVE_TTL = 3600  # 1 heure

def safe(v, d=6):
    try:
        f = float(v)
        return None if (math.isnan(f) or math.isinf(f)) else round(f, d)
    except:
        return None

def get(url, params=None, timeout=10, headers=None):
    try:
        h = {"Accept": "application/json"}
        if headers: h.update(headers)
        r = requests.get(url, params=params or {}, timeout=timeout, headers=h)
        if r.status_code == 200:
            return r.json()
        log.warning(f"GET {url} -> HTTP {r.status_code}")
    except Exception as e:
        log.error(f"GET {url} -> {e}")
    return None

# ══════════════════════════════════════════════════════════
# COINGECKO
# ══════════════════════════════════════════════════════════

def fetch_coingecko():
    global _cg_cache
    now=time.time()
    if now-_cg_cache["ts"]<60 and _cg_cache["data"]: return _cg_cache["data"]
    d = get("https://api.coingecko.com/api/v3/coins/bitcoin", {
        "localization":"false","tickers":"false",
        "community_data":"false","developer_data":"false","sparkline":"false"
    })
    if not d: return _cg_cache.get("data", {})
    md = d.get("market_data", {})
    result = {
        "price_usd":          safe(md.get("current_price",{}).get("usd"), 2),
        "price_change_1d":    safe(md.get("price_change_percentage_24h"), 4),
        "price_change_7d":    safe(md.get("price_change_percentage_7d"), 4),
        "price_change_30d":   safe(md.get("price_change_percentage_30d"), 4),
        "volume_usd":         safe(md.get("total_volume",{}).get("usd"), 0),
        "market_cap":         safe(md.get("market_cap",{}).get("usd"), 0),
        "ath_usd":            safe(md.get("ath",{}).get("usd"), 2),
        "ath_pct":            safe(md.get("ath_change_percentage",{}).get("usd"), 2),
        "high_24h":           safe(md.get("high_24h",{}).get("usd"), 2),
        "low_24h":            safe(md.get("low_24h",{}).get("usd"), 2),
        "circulating_supply": safe(md.get("circulating_supply"), 0),
        "max_supply":         21_000_000,
    }
    if result.get("price_usd"): _cg_cache = {"data": result, "ts": now}
    return result

def fetch_coingecko_global():
    d = get("https://api.coingecko.com/api/v3/global")
    if not d: return {}
    data  = d.get("data", {})
    mcaps = data.get("market_cap_percentage", {})
    return {
        "btc_dominance":         safe(mcaps.get("btc"), 2),
        "eth_dominance":         safe(mcaps.get("eth"), 2),
        "total_market_cap_usd":  safe(data.get("total_market_cap",{}).get("usd"), 0),
        "total_volume_24h_usd":  safe(data.get("total_volume",{}).get("usd"), 0),
        "market_cap_change_24h": safe(data.get("market_cap_change_percentage_24h_usd"), 2),
        "active_cryptos":        data.get("active_cryptocurrencies"),
    }

def fetch_stablecoins():
    d = get("https://api.coingecko.com/api/v3/simple/price", {
        "ids":"tether,usd-coin,dai","vs_currencies":"usd","include_market_cap":"true"
    })
    if not d: return {}
    usdt  = safe(d.get("tether",{}).get("usd_market_cap"), 0)
    usdc  = safe(d.get("usd-coin",{}).get("usd_market_cap"), 0)
    dai   = safe(d.get("dai",{}).get("usd_market_cap"), 0)
    total = sum(x for x in [usdt, usdc, dai] if x)
    return {"usdt_market_cap":usdt,"usdc_market_cap":usdc,"dai_market_cap":dai,
            "stablecoin_total":safe(total,0)}

# ══════════════════════════════════════════════════════════
# COINMETRICS (C6 : NVT retiré — plan payant, toujours null)
# ══════════════════════════════════════════════════════════

def fetch_coinmetrics():
    """CoinMetrics Community — v4.7.4
    HTTP 403 permanent depuis Vercel iad1 — fallback proxy dans get_onchain().
    hashrate_cm supprimé (doublon hashrate_eh Mempool).
    tx_count supprimé (remplacé par tx_24h Blockchair).
    active_addresses supprimé (remplacé par adr_bal_cnt BGeometrics).
    """
    result = {}
    d = get("https://community-api.coinmetrics.io/v4/timeseries/asset-metrics", {
        "assets":"btc","metrics":"CapMVRVCur,CapRealUSD",
        "page_size":"1","paging_from":"end"
    })
    if d and d.get("data"):
        row          = d["data"][-1]
        mvrv         = safe(row.get("CapMVRVCur"), 4)
        realized_cap = safe(row.get("CapRealUSD"), 2)
        nupl         = round(1 - 1/mvrv, 4) if mvrv and mvrv > 0 else None
        result.update({
            "mvrv":             mvrv,
            "realized_cap":     realized_cap,
            "nupl":             nupl,
            "coinmetrics_date": row.get("time","")[:10],
        })
        log.info(f"CoinMetrics OK: mvrv={mvrv} realized_cap={realized_cap}")
    else:
        log.warning("CoinMetrics 403/vide — fallback proxy actif dans get_onchain()")
    return result

# ══════════════════════════════════════════════════════════
# PUELL MULTIPLE — CoinMetrics IssTotUSD × 365j (v4.7.3)
# Formule : IssTotUSD_jour / MA365(IssTotUSD)
# Validé : Glassnode Academy, David Puell, CryptoQuant
# Zones : <0.5 accumulation | 0.5-3.0 neutre | >3.0 distribution
# ══════════════════════════════════════════════════════════
def fetch_puell_multiple():
    """Puell Multiple via CoinMetrics IssTotUSD 365 jours"""
    global _puell_cache
    now = time.time()
    if now - _puell_cache["ts"] < 86400 and _puell_cache["data"]:
        log.info("Puell: cache hit")
        return _puell_cache["data"]
    try:
        d = get("https://community-api.coinmetrics.io/v4/timeseries/asset-metrics", {
            "assets": "btc",
            "metrics": "IssTotUSD",
            "page_size": "365",
            "paging_from": "end"
        })
        if not d or not d.get("data") or len(d["data"]) < 30:
            log.warning("Puell: donnees insuffisantes")
            return {}
        values = [float(row["IssTotUSD"]) for row in d["data"]
                  if row.get("IssTotUSD") and float(row["IssTotUSD"]) > 0]
        if not values:
            return {}
        today_val = values[-1]
        ma365     = sum(values) / len(values)
        puell     = round(today_val / ma365, 4) if ma365 > 0 else None
        result = {
            "puell_multiple":      puell,
            "puell_iss_today_usd": round(today_val, 2),
            "puell_ma365_usd":     round(ma365, 2),
        }
        _puell_cache = {"data": result, "ts": now}
        log.info(f"Puell: {puell} ({len(values)} pts)")
        return result
    except Exception as e:
        log.warning(f"fetch_puell_multiple: {e}")
        return {}

# ══════════════════════════════════════════════════════════
# BGEOMETRICS — CACHE MUTUALISÉ (C1)
# Un seul appel réel toutes les BGR_TTL secondes
# Résout le double-appel qui épuisait le rate limit 8/h
# ══════════════════════════════════════════════════════════

def fetch_coinmetrics_extended():
    """CoinMetrics Community — métriques étendues (flux exchanges, émission, adresses)"""
    global _cm_ext_cache
    now = time.time()
    if now - _cm_ext_cache["ts"] < 3600 and _cm_ext_cache["data"]:
        return _cm_ext_cache["data"]

    result = {}
    base = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
    metrics = [
        "FlowInExNtv", "FlowOutExNtv", "FlowInExUSD", "FlowOutExUSD",
        "SplyExNtv", "SplyExUSD", "IssTotNtv", "IssTotUSD",
        "TxTfrCnt", "AdrBalCnt", "ROI30d", "ROI1yr",
        "BlkCnt", "FeeTotNtv"
    ]
    url = f"{base}?assets=btc&metrics={','.join(metrics)}&page_size=1"
    d = get(url)
    if d and isinstance(d, dict) and d.get("data"):
        row = d["data"][0] if isinstance(d["data"], list) else {}
        result["flow_in_ex_btc"]   = safe(row.get("FlowInExNtv"), 2)
        result["flow_out_ex_btc"]  = safe(row.get("FlowOutExNtv"), 2)
        result["flow_in_ex_usd"]   = safe(row.get("FlowInExUSD"), 2)
        result["flow_out_ex_usd"]  = safe(row.get("FlowOutExUSD"), 2)
        result["sply_ex_btc"]      = safe(row.get("SplyExNtv"), 2)
        result["sply_ex_usd"]      = safe(row.get("SplyExUSD"), 2)
        result["iss_tot_btc"]      = safe(row.get("IssTotNtv"), 2)
        result["iss_tot_usd"]      = safe(row.get("IssTotUSD"), 2)
        result["tx_transfer_cnt"]  = safe(row.get("TxTfrCnt"), 0)
        result["adr_bal_cnt"]      = safe(row.get("AdrBalCnt"), 0)
        result["roi_30d"]          = safe(row.get("ROI30d"), 4)
        result["roi_1yr"]          = safe(row.get("ROI1yr"), 4)
        result["blk_cnt_cm"]       = safe(row.get("BlkCnt"), 0)
        result["fee_tot_btc_cm"]   = safe(row.get("FeeTotNtv"), 4)

    if result:
        _cm_ext_cache = {"data": result, "ts": now}
    return result


def fetch_mining_pools():
    """Blockchain.info — distribution des pools miniers"""
    global _pools_cache
    now = time.time()
    if now - _pools_cache["ts"] < 3600 and _pools_cache["data"]:
        return _pools_cache["data"]

    result = {}
    d = get("https://api.blockchain.info/pools?timespan=5days")
    if d and isinstance(d, dict):
        total = sum(d.values())
        # Unknown exclu du top3 — affiché séparément via pool_unknown_pct
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


def fetch_bgeometrics():
    """Cache 1h — résout rate limit BGR 8 req/h"""
    global _bgr_cache
    now = time.time()
    if now - _bgr_cache["ts"] < BGR_TTL and _bgr_cache["data"]:
        return _bgr_cache["data"]

    result = {}
    B = BGR_BASE

    d = get(f"{B}/api-block/v1/asopr/1")
    if d and isinstance(d, dict):
        result["asopr"]      = safe(d.get("asopr"), 4)
        result["asopr_date"] = d.get("d", "")

    d2 = get(f"{B}/api-block/v1/sopr-block/1")
    if d2 and isinstance(d2, dict):
        result["sopr_block"] = safe(d2.get("soprBlock"), 4)

    d3 = get(f"{B}/api-block/v1/nrpl-usd/1")
    if d3 and isinstance(d3, dict):
        result["nrpl_usd"] = safe(d3.get("nrplUsd"), 2)

    d4 = get(f"{B}/api-block/v1/nrpl-btc/1")
    if d4 and isinstance(d4, dict):
        result["nrpl_btc"] = safe(d4.get("nrplBtc"), 4)

    if result:  # Ne mettre en cache que si au moins 1 valeur reçue
        _bgr_cache = {"data": result, "ts": now}
    return result

def fetch_bgr_holders():
    """Cache 1h séparé pour les données holders BGR"""
    global _bgr_holders_cache
    now = time.time()
    if now - _bgr_holders_cache["ts"] < BGR_TTL and _bgr_holders_cache["data"]:
        return _bgr_holders_cache["data"]

    result = {}
    B = BGR_BASE

    # LTH Realized Price
    d = get(f"{B}/api-block/v1/btc-price/1")
    if d and isinstance(d, dict):
        rp = d.get("realizedPrice") or d.get("realized_price") or d.get("btcPrice")
        if rp: result["lth_realized_price"] = safe(rp, 2)

    if not result.get("lth_realized_price"):
        d_alt = get(f"{B}/v1/realized-price/1")
        if d_alt and isinstance(d_alt, dict):
            rp = d_alt.get("realizedPrice") or d_alt.get("value") or d_alt.get("v")
            if rp: result["lth_realized_price"] = safe(rp, 2)

    # Whales > 1000 BTC
    d3 = get(f"{B}/api-block/v1/btc-1000/1")
    if d3 and isinstance(d3, dict):
        result["whale_1000_count"] = safe(d3.get("btc1000"), 0)

    if result:
        _bgr_holders_cache = {"data": result, "ts": now}
    return result

def fetch_sosovalue_etf():
    """D1 : SoSoValue ETF — flux nets réels BTC spot ETF
    URL: https://api.sosovalue.xyz | Header: x-soso-api-key
    Plan Demo = 10 appels/mois → cache 24h SOSO_TTL
    Endpoint: POST /openapi/v2/etf/currentEtfDataMetrics
    Données confirmées en live (20 mars 2026):
      totalNetAssets=$90.8B, dailyNetInflow=-$90M, 12 ETF individuels
    """
    global _soso_cache
    now = time.time()
    if now - _soso_cache["ts"] < SOSO_TTL and _soso_cache["data"]:
        log.info("SoSoValue: cache hit")
        return _soso_cache["data"]

    key = os.environ.get("SOSOVALUE_KEY", "")
    if not key:
        log.warning("SOSOVALUE_KEY manquant")
        return {}

    try:
        # verify=False : api.sosovalue.xyz utilise un certificat intermédiaire
        # non inclus dans le bundle SSL de Python/Vercel (SSLCertVerificationError)
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        r = requests.post(
            f"{SOSO_BASE}/openapi/v2/etf/currentEtfDataMetrics",
            json={"type": "us-btc-spot"},
            headers={"x-soso-api-key": key, "Content-Type": "application/json"},
            timeout=10,
            verify=False
        )
        if r.status_code != 200:
            log.error(f"SoSoValue HTTP {r.status_code}")
            return {}
        d = r.json()
        if d.get("code") != 0:
            log.error(f"SoSoValue code={d.get('code')} msg={d.get('msg')}")
            return {}
        data = d.get("data", {})

        # Agrégats globaux
        result = {
            "etf_date":           data.get("totalNetAssets", {}).get("lastUpdateDate"),
            "etf_total_aum_usd":  safe(data.get("totalNetAssets", {}).get("value"), 2),
            "etf_aum_pct_mcap":   safe(data.get("totalNetAssetsPercentage", {}).get("value"), 6),
            "etf_daily_inflow_usd": safe(data.get("dailyNetInflow", {}).get("value"), 2),
            "etf_cum_inflow_usd": safe(data.get("cumNetInflow", {}).get("value"), 2),
            "etf_daily_volume_usd": safe(data.get("dailyTotalValueTraded", {}).get("value"), 2),
            "etf_total_btc_held": safe(data.get("totalTokenHoldings", {}).get("value"), 4),
        }

        # ETF individuels — top 4 par AUM
        etf_list = data.get("list", [])
        # Trier par netAssets décroissant
        etf_sorted = sorted(
            etf_list,
            key=lambda x: float(x.get("netAssets", {}).get("value", 0) or 0),
            reverse=True
        )
        # Stocker les 4 premiers
        for i, etf in enumerate(etf_sorted[:4]):
            ticker = etf.get("ticker", f"ETF{i}")
            result[f"etf_{ticker.lower()}_aum"]          = safe(etf.get("netAssets", {}).get("value"), 2)
            result[f"etf_{ticker.lower()}_daily_inflow"]  = safe(etf.get("dailyNetInflow", {}).get("value"), 2)
            result[f"etf_{ticker.lower()}_cum_inflow"]    = safe(etf.get("cumNetInflow", {}).get("value"), 2)

        # Signal macro ETF
        daily = result.get("etf_daily_inflow_usd")
        if daily is not None:
            if daily > 500_000_000:
                result["etf_signal"] = "Entrées massives 🟢"
            elif daily > 0:
                result["etf_signal"] = "Entrées positives 🟢"
            elif daily > -500_000_000:
                result["etf_signal"] = "Sorties modérées 🟡"
            else:
                result["etf_signal"] = "Sorties massives 🔴"

        if result:
            _soso_cache = {"data": result, "ts": now}
            log.info(f"SoSoValue: AUM={result.get('etf_total_aum_usd')} daily={result.get('etf_daily_inflow_usd')}")
        return result

    except Exception as e:
        log.error(f"SoSoValue ERR: {e}")
        return {}


def fetch_twelvedata_etf():
    """D2 : Twelve Data — prix/volume ETF BTC en temps réel
    Plan Basic = 800 req/jour → cache 1h TWELVE_TTL
    Endpoint: GET /quote?symbol=IBIT,FBTC,ARKB,GBTC,HODL
    Données confirmées en live (20 mars 2026)
    """
    global _twelve_cache
    now = time.time()
    if now - _twelve_cache["ts"] < TWELVE_TTL and _twelve_cache["data"]:
        log.info("TwelveData: cache hit")
        return _twelve_cache["data"]

    key = os.environ.get("TWELVE_DATA_KEY", "")
    if not key:
        log.warning("TWELVE_DATA_KEY manquant")
        return {}

    TICKERS = ["IBIT", "FBTC", "ARKB", "GBTC", "HODL"]
    d = get(
        f"{TWELVE_BASE}/quote",
        params={"symbol": ",".join(TICKERS), "apikey": key},
        timeout=10
    )
    if not d:
        return {}

    result = {}
    total_volume = 0
    price_changes = []

    for ticker in TICKERS:
        etf = d.get(ticker, {})
        if not etf or etf.get("status") == "error":
            continue
        t = ticker.lower()
        close  = safe(etf.get("close"), 4)
        volume = safe(etf.get("volume"), 0)
        change = safe(etf.get("percent_change"), 4)
        result[f"etf_{t}_price"]      = close
        result[f"etf_{t}_volume"]     = volume
        result[f"etf_{t}_change_pct"] = change
        result[f"etf_{t}_date"]       = etf.get("datetime")
        if volume: total_volume += float(volume)
        if change is not None: price_changes.append(float(change))

    if total_volume > 0:
        result["etf_total_market_volume"] = safe(total_volume, 0)
    if price_changes:
        result["etf_avg_price_change"] = safe(sum(price_changes)/len(price_changes), 4)

    if result:
        _twelve_cache = {"data": result, "ts": now}
        log.info(f"TwelveData ETF: {len(result)} champs")
    return result

# ══════════════════════════════════════════════════════════
# BLOCKCHAIN.INFO + MEMPOOL + BLOCKCHAIR
# (inchangés — fonctionnent depuis iad1)
# ══════════════════════════════════════════════════════════

def fetch_blockchain_info():
    d = get("https://blockchain.info/stats?format=json", timeout=8)
    if not d: return {}
    miners_rev_raw = d.get("miners_revenue_btc") or d.get("n_btc_mined") or 0
    miners_rev_btc = round(float(miners_rev_raw) / 1e8, 4) if miners_rev_raw else None
    fees_raw = d.get("total_fees_btc") or 0
    fees_btc = round(abs(float(fees_raw)) / 1e8, 8) if fees_raw else None
    return {
        "blockchain_market_price":           safe(d.get("market_price_usd"), 2),
        "blockchain_minutes_between_blocks": safe(d.get("minutes_between_blocks"), 2),
        "blockchain_n_tx":                   safe(d.get("n_tx"), 0),
        "blockchain_blocks_today":           safe(d.get("n_blocks_mined"), 0),
        "blockchain_total_fees_btc":         fees_btc,
        "blockchain_miners_revenue_usd":     safe(d.get("miners_revenue_usd"), 2),
        "blockchain_nextretarget":           safe(d.get("nextretarget"), 0),
        "blockchain_hash_rate_gh":           safe(d.get("hash_rate"), 2),
    }

def fetch_mempool():
    result = {}
    fees = get("https://mempool.space/api/v1/fees/recommended")
    if fees:
        result.update({
            "fee_high": safe(fees.get("fastestFee"), 0),
            "fee_med":  safe(fees.get("halfHourFee"), 0),
            "fee_low":  safe(fees.get("hourFee"), 0),
            "fee_min":  safe(fees.get("minimumFee"), 0),
        })
    mem = get("https://mempool.space/api/mempool")
    if mem:
        result.update({
            "pending_txs":      safe(mem.get("count"), 0),
            "pending_mb":       safe((mem.get("vsize") or 0) / 1e6, 2),
            "pending_fees_btc": safe((mem.get("total_fee") or 0) / 1e8, 4),
        })
    mining = get("https://mempool.space/api/v1/mining/hashrate/1m")
    if mining:
        hrs = mining.get("hashrates", []); dfs = mining.get("difficulty", [])
        if hrs: result["hashrate_eh"] = safe(hrs[-1].get("avgHashrate", 0) / 1e18, 2)
        if dfs: result["difficulty"]  = safe(dfs[-1].get("difficulty"), 0)
    da = get("https://mempool.space/api/v1/difficulty-adjustment")
    if da:
        result.update({
            "diff_progress_pct":     safe(da.get("progressPercent"), 2),
            "diff_change_pct":       safe(da.get("difficultyChange"), 4),
            "diff_remaining_blocks": safe(da.get("remainingBlocks"), 0),
            "previous_retarget_pct": safe(da.get("previousRetarget"), 4),
        })
    ln = get("https://mempool.space/api/v1/lightning/statistics/latest")
    if ln:
        l = ln.get("latest", {})
        result.update({
            "ln_channels":         safe(l.get("channel_count"), 0),
            "ln_nodes":            safe(l.get("node_count"), 0),
            "ln_capacity_btc":     safe((l.get("total_capacity") or 0) / 1e8, 2),
            "ln_avg_capacity_sat": safe(l.get("avg_capacity"), 0),
        })
    return result

def fetch_blockchair():
    d = get("https://api.blockchair.com/bitcoin/stats")
    if not d: return {}
    data = d.get("data", {})
    return {
        "blocks_total":       safe(data.get("blocks"), 0),
        "tx_total":           safe(data.get("transactions"), 0),
        "utxo_count":         safe(data.get("outputs"), 0),
        "blockchain_size_gb": safe((data.get("blockchain_size") or 0) / 1e9, 2),
        "tx_24h":             safe(data.get("transactions_24h"), 0),
        "volume_24h_usd":     safe(data.get("volume_24h"), 0),
        "mempool_tps":        safe(data.get("mempool_tps"), 2),
    }

def fetch_coinpaprika():
    d = get("https://api.coinpaprika.com/v1/tickers/btc-bitcoin")
    if not d: return {}
    q = d.get("quotes", {}).get("USD", {})
    return {
        "price_coinpaprika": safe(q.get("price"), 2),
        "beta_value":        safe(d.get("beta_value"), 4),
        "rank":              d.get("rank"),
        "pct_supply_issued": safe((d.get("total_supply") or 0) / 21_000_000 * 100, 4),
    }

def fetch_fear_greed():
    d = get("https://api.alternative.me/fng/?limit=7")
    if not d or not d.get("data"): return {}
    data = d["data"]
    return {
        "fear_greed_value":          safe(data[0].get("value"), 0),
        "fear_greed_classification": data[0].get("value_classification"),
        "fear_greed_history_7d":     [{"value":int(x["value"]),"classification":x["value_classification"]} for x in data],
    }

def fetch_coinbase():
    global _cb_cache
    now=time.time()
    if now-_cb_cache["ts"]<60 and _cb_cache["data"]: return _cb_cache["data"]
    d = get("https://api.coinbase.com/v2/prices/BTC-USD/spot")
    if not d: return _cb_cache.get("data", {})
    result = {"price_coinbase": safe(d.get("data", {}).get("amount"), 2)}
    if result.get("price_coinbase"): _cb_cache = {"data": result, "ts": now}
    return result

def fetch_kraken_ohlc():
    since = int(time.time()) - 400 * 86400
    d = get("https://api.kraken.com/0/public/OHLC",
            {"pair":"XBTUSD","interval":"1440","since":since})
    if not d or d.get("error"): return {}, []
    candles = d.get("result", {}).get("XXBTZUSD", [])
    if not candles: return {}, []
    last = candles[-1]
    ohlc_list = [{"t":int(c[0]),"o":float(c[1]),"h":float(c[2]),
                  "l":float(c[3]),"c":float(c[4]),"v":float(c[6])} for c in candles]
    meta = {
        "kraken_open":   safe(last[1], 2),
        "kraken_high":   safe(last[2], 2),
        "kraken_low":    safe(last[3], 2),
        "kraken_close":  safe(last[4], 2),
        "kraken_vwap":   safe(last[5], 2),
        "kraken_volume": safe(last[6], 4),
    }
    return meta, ohlc_list

def compute_technicals(ohlc_list):
    """Calculs techniques purs — sans proxy fields"""
    if not ohlc_list or len(ohlc_list) < 30: return {}
    closes = [c["c"] for c in ohlc_list]
    n      = len(closes)
    ma7    = sum(closes[-7:])   / min(7, n)   if n >= 7   else None
    ma30   = sum(closes[-30:])  / min(30, n)  if n >= 30  else None
    ma200  = sum(closes[-200:]) / min(200, n) if n >= 200 else None
    returns = [(closes[i]-closes[i-1])/closes[i-1] for i in range(1, n)]
    vol30 = None
    if len(returns) >= 30:
        r30 = returns[-30:]; m = sum(r30)/len(r30)
        vol30 = math.sqrt(sum((r-m)**2 for r in r30)/len(r30)) * math.sqrt(365)
    sharpe_30d = None
    if len(returns) >= 30:
        r30 = returns[-30:]; m = sum(r30)/len(r30)
        s = math.sqrt(sum((r-m)**2 for r in r30)/len(r30))
        if s > 0: sharpe_30d = round((m/s)*math.sqrt(365), 3)
    sharpe_1y = None
    if len(returns) >= 200:
        r1 = returns[-200:]; m = sum(r1)/len(r1)
        s = math.sqrt(sum((r-m)**2 for r in r1)/len(r1))
        if s > 0: sharpe_1y = round((m/s)*math.sqrt(365), 3)
    rsi_14 = None
    if len(returns) >= 14:
        g = [r for r in returns[-14:] if r > 0]
        l = [-r for r in returns[-14:] if r < 0]
        ag = sum(g)/14; al = sum(l)/14
        rsi_14 = round(100-(100/(1+ag/al)), 2) if al > 0 else 100.0
    cur = closes[-1]
    return {
        "ma_7d":              round(ma7, 2)   if ma7   else None,
        "ma_30d":             round(ma30, 2)  if ma30  else None,
        "ma_200d":            round(ma200, 2) if ma200 else None,
        "volatility_30d_ann": round(vol30, 4) if vol30 else None,
        "sharpe_30d":         sharpe_30d,
        "sharpe_1y":          sharpe_1y,
        "rsi_14":             rsi_14,
        "price_vs_ma7":       round((cur/ma7-1)*100, 2)   if ma7   else None,
        "price_vs_ma30":      round((cur/ma30-1)*100, 2)  if ma30  else None,
        "price_vs_ma200":     round((cur/ma200-1)*100, 2) if ma200 else None,
    }

def compute_signals(d):
    s = {}
    ap = d.get("ath_pct"); mvrv = d.get("mvrv"); nupl = d.get("nupl")
    rsi = d.get("rsi_14"); fg = d.get("fear_greed_value")
    fee = d.get("fee_high"); txs = d.get("pending_txs")

    if ap is not None:
        p = abs(ap)
        s["ath_signal"] = ("Proche ATH 🔴" if p < 5 else "Zone haute 🟡" if p < 20
                           else "Zone mediane 🟢" if p < 50 else "Zone basse 💜")
    s["mvrv_signal"] = (
        "Surachat 🔴" if mvrv and mvrv >= 3.5 else "Chaud 🟡" if mvrv and mvrv >= 2.5
        else "Neutre 🟢" if mvrv and mvrv >= 1.0 else "Sous-evalue 💜" if mvrv else "—"
    )
    if nupl is not None:
        s["nupl_zone"] = (
            "Euphorie 🔴" if nupl >= 0.75 else "Avidite 🟡" if nupl >= 0.5
            else "Optimisme 🟢" if nupl >= 0.25 else "Espoir 🟢" if nupl >= 0
            else "Capitulation 💜"
        )
    else:
        s["nupl_zone"] = "—"

    asopr = d.get("asopr")
    if asopr is not None:
        s["asopr_signal"] = "Profit 🟢" if asopr >= 1.02 else "Neutre 🟡" if asopr >= 0.98 else "Perte 🔴"

    nrpl = d.get("nrpl_usd")
    if nrpl is not None:
        s["nrpl_signal"] = ("Profit net 🟢" if nrpl > 0
                            else "Perte moderee 🟡" if nrpl > -500_000_000
                            else "Capitulation 💜")
    if rsi is not None:
        s["rsi_signal"] = (
            "Surachat 🔴" if rsi >= 80 else "Haussier 🟡" if rsi >= 60
            else "Neutre 🟢" if rsi >= 40 else "Baissier 🟡" if rsi >= 20
            else "Survente 💜"
        )
    sharpe = d.get("sharpe_30d")
    if sharpe is not None:
        s["sharpe_signal"] = ("Excellent ✅" if sharpe >= 2 else "Bon 🟢" if sharpe >= 1
                              else "Positif 🟡" if sharpe >= 0 else "Negatif 🔴")
    if fg is not None:
        s["fg_signal"] = (
            "Peur extreme 💜" if fg <= 20 else "Peur 🟡" if fg <= 40
            else "Neutre 🟢" if fg <= 60 else "Avidite 🟡" if fg <= 80
            else "Avidite extreme 🔴"
        )
    if fee is not None:
        s["fee_signal"] = ("Reseau libre ✅" if fee <= 3 else "Charge normale" if fee <= 15
                           else "Charge ⚠️" if fee <= 50 else "Congestionne 🔴")
    if txs is not None:
        s["mempool_signal"] = ("Vide ✅" if txs < 5000 else "Normal" if txs < 30000
                               else "Charge ⚠️" if txs < 100000 else "Sature 🔴")

    stable = d.get("stablecoin_total"); mcap = d.get("market_cap")
    if stable and mcap:
        ratio = stable / mcap * 100
        s["stable_ratio_pct"] = round(ratio, 2)
        s["stable_signal"] = ("Liquidite elevee 🟢" if ratio > 30
                              else "Liquidite normale 🟡" if ratio > 15
                              else "Liquidite faible 🔴")

    alerts = []
    if mvrv and mvrv >= 3.5:    alerts.append({"severity":"CRITIQUE",    "metric":"MVRV",      "message":f"MVRV={mvrv:.2f} surachat extreme"})
    if mvrv and mvrv < 1.0:     alerts.append({"severity":"OPPORTUNITE", "metric":"MVRV",      "message":f"MVRV={mvrv:.2f} sous Realized Cap"})
    if fg is not None and fg <= 15: alerts.append({"severity":"INFO",    "metric":"Fear&Greed","message":f"F&G={int(fg)} peur extreme"})
    if ap and abs(ap) < 5:      alerts.append({"severity":"ATTENTION",   "metric":"ATH",       "message":f"BTC a {abs(ap):.1f}% ATH"})
    if rsi and rsi >= 80:       alerts.append({"severity":"INFO",        "metric":"RSI",       "message":f"RSI={rsi:.1f} surachat"})
    if rsi and rsi <= 20:       alerts.append({"severity":"OPPORTUNITE", "metric":"RSI",       "message":f"RSI={rsi:.1f} survente"})
    if asopr is not None and asopr < 0.96:
        alerts.append({"severity":"INFO","metric":"aSOPR","message":f"aSOPR={asopr:.4f} ventes a perte"})
    if nrpl is not None and nrpl < -1_000_000_000:
        alerts.append({"severity":"INFO","metric":"NRPL","message":f"NRPL={nrpl:,.0f} capitulation"})

    s["alerts"] = alerts
    s["active_alerts"] = len(alerts)
    return s

# ══════════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "index.html"),
        "/var/task/index.html",
        "index.html",
    ]
    for path in candidates:
        try:
            with open(os.path.abspath(path), "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read(), status_code=200)
        except FileNotFoundError:
            continue
    return HTMLResponse(
        content='<h1 style="color:#f7931a">API v4.6 OK</h1><a href="/api/summary">/api/summary</a>',
        status_code=200)

@app.get("/api/health")
def health():
    now = time.time()
    def age(ts): return round(now - ts, 0) if ts and ts > 0 else None
    return {
        "status":   "ok",
        "service":  "BTC On-Chain Analytics API v4.7.4",
        "version":  "4.7.4",
        "cache_ages": {
            "bgr_s":          age(_bgr_cache["ts"]),
            "bgr_holders_s":  age(_bgr_holders_cache["ts"]),
            "cm_ext_s":       age(_cm_ext_cache["ts"]),
            "puell_s":        age(_puell_cache["ts"]),
            "cg_s":           age(_cg_cache["ts"]),
            "cb_s":           age(_cb_cache["ts"]),
            "pools_s":        age(_pools_cache["ts"]),
            "sosovalue_s":    age(_soso_cache["ts"]),
            "twelvedata_s":   age(_twelve_cache["ts"]),
        },
        "env_keys": {
            "SOSOVALUE_KEY":   bool(os.environ.get("SOSOVALUE_KEY")),
            "TWELVE_DATA_KEY": bool(os.environ.get("TWELVE_DATA_KEY")),
        },
        "note": "v4.7.4: CG cache 60s, CB cache 60s, CoinMetrics fallback proxy mvrv/realized_cap si 403.",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@app.get("/api/price")
def get_price():
    """Prix: CoinGecko + Coinbase + Kraken uniquement (Binance/Bybit bloqués iad1 → côté client)"""
    cg = fetch_coingecko(); cb = fetch_coinbase()
    kr_meta, _ = fetch_kraken_ohlc()
    return {
        **cg, **cb, **kr_meta,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

@app.get("/api/onchain")
def get_onchain():
    # Chaque fetch protégé individuellement — cold start Vercel ne cause plus de 500
    def safe_fetch(fn, *args):
        try: return fn(*args) if args else fn()
        except Exception as e: log.warning(f"safe_fetch {fn.__name__}: {e}"); return {}

    cm     = safe_fetch(fetch_coinmetrics)
    bgr    = safe_fetch(fetch_bgeometrics)
    fg     = safe_fetch(fetch_fear_greed)
    cg     = safe_fetch(fetch_coingecko)
    cm_ext = safe_fetch(fetch_coinmetrics_extended)
    try:
        _, ohlc = fetch_kraken_ohlc()
        tech = compute_technicals(ohlc)
    except Exception as e:
        log.warning(f"get_onchain kraken: {e}"); tech = {}
    puell  = safe_fetch(fetch_puell_multiple)
    price  = cg.get("price_usd")
    ma200  = tech.get("ma_200d")
    mayer  = round(price / ma200, 4) if price and ma200 and ma200 > 0 else None

    # Coinbase Premium Index — source CryptoQuant
    # (Coinbase_price - ref_price) / ref_price * 100
    cb_price  = cg.get("price_coinbase")
    ref_price = price
    coinbase_premium = None
    if cb_price and ref_price and ref_price > 0:
        coinbase_premium = round((cb_price - ref_price) / ref_price * 100, 6)

    # Fallback mvrv/realized_cap/nupl si CoinMetrics 403
    # realized_cap = market_cap / mvrv (proxy exact)
    mvrv_val = cm.get("mvrv") or bgr.get("mvrv")
    market_cap_val = cg.get("market_cap")
    fallback_rc = None
    if not cm.get("realized_cap") and market_cap_val and mvrv_val and mvrv_val > 0:
        fallback_rc = round(market_cap_val / mvrv_val, 2)
        log.info(f"realized_cap proxy: {fallback_rc}")
    fallback_nupl = None
    if not cm.get("nupl") and mvrv_val and mvrv_val > 0:
        fallback_nupl = round(1 - 1/mvrv_val, 4)

    all_data = {
        **cm, **bgr, **fg, **cg, **cm_ext, **puell,
        "mayer_multiple":   mayer,
        "coinbase_premium": coinbase_premium,
    }
    # Injecter les fallbacks si métriques manquantes
    if fallback_rc and not all_data.get("realized_cap"): all_data["realized_cap"] = fallback_rc
    if fallback_nupl and not all_data.get("nupl"): all_data["nupl"] = fallback_nupl
    return {**all_data, **compute_signals(all_data),
            "updated_at": datetime.now(timezone.utc).isoformat()}

@app.get("/api/derivatives")
def get_derivatives():
    """C4 : Binance Futures + Bybit bloqués iad1 → données gérées côté client dashboard"""
    bgr = fetch_bgeometrics()   # cache mutualisé
    return {
        "note": "Binance Futures et Bybit accessibles uniquement depuis le navigateur client (bloqués AWS iad1)",
        "asopr":      bgr.get("asopr"),
        "sopr_block": bgr.get("sopr_block"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

@app.get("/api/technicals")
def get_technicals():
    kr_meta, ohlc = fetch_kraken_ohlc()
    tech = compute_technicals(ohlc)
    cg = fetch_coingecko(); cm = fetch_coinmetrics()
    all_data = {**tech, **kr_meta, **cg, **cm}
    return {**all_data, **compute_signals(all_data),
            "updated_at": datetime.now(timezone.utc).isoformat()}

@app.get("/api/market")
def get_market():
    cg = fetch_coingecko(); cg_gl = fetch_coingecko_global()
    stable = fetch_stablecoins(); cp = fetch_coinpaprika()
    cb = fetch_coinbase(); kr_meta, ohlc = fetch_kraken_ohlc()
    tech = compute_technicals(ohlc)
    all_data = {**cg, **cg_gl, **stable, **cp, **cb, **kr_meta, **tech}
    return {**all_data, **compute_signals(all_data),
            "updated_at": datetime.now(timezone.utc).isoformat()}

@app.get("/api/network")
def get_network():
    pools = fetch_mining_pools()
    return {
        **fetch_blockchair(),
        **fetch_mempool(),
        **fetch_blockchain_info(),
        **pools,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

@app.get("/api/lightning")
def get_lightning():
    mem = fetch_mempool()
    return {k: mem.get(k) for k in
            ["ln_channels","ln_nodes","ln_capacity_btc","ln_avg_capacity_sat"]
            } | {"updated_at": datetime.now(timezone.utc).isoformat()}

@app.get("/api/holders")
def get_holders():
    """C5 : utilise fetch_bgeometrics() depuis le cache mutualisé — plus de double-appel"""
    bgr_h = fetch_bgr_holders()         # cache séparé pour realized price + whales
    bgr   = fetch_bgeometrics()         # cache mutualisé — asopr/nrpl/sopr déjà fetchés
    kr_meta, ohlc = fetch_kraken_ohlc()
    cm = fetch_coinmetrics()
    price   = ohlc[-1]["c"] if ohlc else None
    lth_rp  = bgr_h.get("lth_realized_price")
    lth_mvrv = round(price / lth_rp, 4) if price and lth_rp else None
    return {
        "lth_realized_price":  lth_rp,
        "lth_mvrv":            lth_mvrv,
        "mvrv":                cm.get("mvrv"),
        "asopr":               bgr.get("asopr"),
        "sopr_block":          bgr.get("sopr_block"),
        "nrpl_usd":            bgr.get("nrpl_usd"),
        "nrpl_btc":            bgr.get("nrpl_btc"),
        "whale_1000_count":    bgr_h.get("whale_1000_count"),


        "updated_at":          datetime.now(timezone.utc).isoformat(),
    }

@app.get("/api/etf")
def get_etf():
    """D1+D2 : SoSoValue (flux nets réels) + Twelve Data (prix/volume marché)"""
    soso   = fetch_sosovalue_etf()
    twelve = fetch_twelvedata_etf()
    merged = {**soso, **twelve}
    if merged:
        return {**merged, "updated_at": datetime.now(timezone.utc).isoformat()}
    return {
        "note": "ETF: SOSOVALUE_KEY et TWELVE_DATA_KEY requis comme variables env Vercel",
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/alerts")
def get_alerts():
    cg = fetch_coingecko(); cm = fetch_coinmetrics()
    bgr = fetch_bgeometrics()   # cache mutualisé
    fg = fetch_fear_greed(); kr_meta, ohlc = fetch_kraken_ohlc()
    tech = compute_technicals(ohlc)
    return compute_signals({**cg,**cm,**bgr,**fg,**tech,**kr_meta}).get("alerts", [])

@app.get("/api/summary")
def get_summary():
    cg = fetch_coingecko(); cg_gl = fetch_coingecko_global(); stable = fetch_stablecoins()
    cm = fetch_coinmetrics()
    bgr   = fetch_bgeometrics()     # cache 1h mutualisé
    bgr_h = fetch_bgr_holders()     # cache 1h séparé
    soso  = fetch_sosovalue_etf()   # cache 24h — plan Demo 10/mois
    twelve= fetch_twelvedata_etf()  # cache 1h — plan Basic 800/jour
    mem = fetch_mempool(); bc = fetch_blockchair()
    cp = fetch_coinpaprika(); fg = fetch_fear_greed()
    cb = fetch_coinbase(); kr_meta, ohlc = fetch_kraken_ohlc()
    tech = compute_technicals(ohlc); bci = fetch_blockchain_info()
    cm_ext = fetch_coinmetrics_extended()
    pools   = fetch_mining_pools()
    _, ohlc_s = fetch_kraken_ohlc()
    tech_s  = compute_technicals(ohlc_s)
    price_s = cg.get("price_usd")
    ma200_s = tech_s.get("ma_200d")
    mayer_s = round(price_s / ma200_s, 4) if price_s and ma200_s and ma200_s > 0 else None
    all_data = {**cg,**cg_gl,**stable,**cm,**bgr,**bgr_h,**soso,**twelve,**cm_ext,**pools,
        "mayer_multiple": mayer_s,
                **mem,**bc,**cp,**fg,**cb,**kr_meta,**tech,**bci}
    return {**all_data, **compute_signals(all_data),
            "updated_at": datetime.now(timezone.utc).isoformat()}


@app.get("/api/bgr_probe")
def bgr_probe():
    """Sonde les endpoints BGR — résultat attendu : 429 (rate limit Vercel iad1)."""
    B = BGR_BASE
    results = {}
    endpoints = [
        ("sth_realized_price_v1",  f"{B}/api-block/v1/sth-price/1"),
        ("sth_realized_price_v2",  f"{B}/api-block/v1/sth-realized-price/1"),
        ("sth_price_v3",           f"{B}/v1/short-term-holder-price/1"),
        ("sth_price_v4",           f"{B}/v1/sth-realized-price/1"),
        ("lth_sopr_v1",            f"{B}/api-block/v1/lth-sopr/1"),
        ("lth_sopr_v2",            f"{B}/v1/long-term-holder-sopr/1"),
        ("sth_sopr_v1",            f"{B}/api-block/v1/sth-sopr/1"),
        ("sth_sopr_v2",            f"{B}/v1/short-term-holder-sopr/1"),
        ("lth_nupl_v1",            f"{B}/api-block/v1/lth-nupl/1"),
        ("sth_nupl_v1",            f"{B}/api-block/v1/sth-nupl/1"),
        ("puell_v1",               f"{B}/api-block/v1/puell-multiple/1"),
        ("mayer_v1",               f"{B}/api-block/v1/mayer-multiple/1"),
        ("thermocap_v1",           f"{B}/api-block/v1/thermocap-multiple/1"),
        ("rhodl_v1",               f"{B}/api-block/v1/rhodl-ratio/1"),
        ("cdd_v1",                 f"{B}/api-block/v1/cdd/1"),
        ("lth_supply_v1",          f"{B}/api-block/v1/lth-supply/1"),
        ("sth_supply_v1",          f"{B}/api-block/v1/sth-supply/1"),
        ("exch_reserve_v1",        f"{B}/api-block/v1/exchange-reserve/1"),
        ("mvrv_v1",                f"{B}/api-block/v1/mvrv/1"),
        ("nupl_v1",                f"{B}/api-block/v1/nupl/1"),
    ]
    for name, url in endpoints:
        try:
            import requests as rq
            r = rq.get(url, timeout=6)
            if r.status_code == 200:
                j = r.json()
                d = j[-1] if isinstance(j, list) else j
                results[name] = {"status": 200, "keys": list(d.keys()) if isinstance(d, dict) else [], "sample": str(d)[:100]}
            else:
                results[name] = {"status": r.status_code}
        except Exception as e:
            results[name] = {"status": "error", "msg": str(e)[:60]}
    ok  = {k:v for k,v in results.items() if v.get("status")==200}
    fail= {k:v for k,v in results.items() if v.get("status")!=200}
    return {"ok_count": len(ok), "fail_count": len(fail), "ok": ok, "fail": fail}
