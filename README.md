Voici le code complet du fichier `index.html` (1 397 lignes) :

---

```html
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BTC Analytics — 70 APIs</title>
<style>
:root {
  --bg: #0b0e14;
  --bg2: #12161f;
  --bg3: #1a1f2e;
  --card: #1e2438;
  --border: #2a3050;
  --orange: #f7931a;
  --orange2: #e8820a;
  --green: #00c896;
  --red: #ff4757;
  --blue: #4da6ff;
  --purple: #a78bfa;
  --yellow: #fbbf24;
  --text: #e8ecf4;
  --text2: #8892aa;
  --text3: #525c78;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--text); font-family: 'SF Mono', 'Fira Code', monospace; font-size: 13px; min-height: 100vh; }
a { color: var(--orange); text-decoration: none; }

/* ── HEADER ─────────────────────────────────────── */
.header { background: var(--bg2); border-bottom: 1px solid var(--border); padding: 12px 20px; display: flex; align-items: center; gap: 16px; position: sticky; top: 0; z-index: 100; }
.logo { font-size: 20px; font-weight: 900; color: var(--orange); letter-spacing: -1px; }
.logo span { color: var(--text2); font-weight: 400; font-size: 11px; margin-left: 4px; }
.price-hero { font-size: 22px; font-weight: 700; color: var(--text); }
.price-change { font-size: 13px; padding: 2px 8px; border-radius: 4px; font-weight: 600; }
.pos { background: rgba(0,200,150,.15); color: var(--green); }
.neg { background: rgba(255,71,87,.15); color: var(--red); }
.badge-apis { margin-left: auto; background: rgba(247,147,26,.1); border: 1px solid rgba(247,147,26,.3); color: var(--orange); padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; }
.last-update { color: var(--text3); font-size: 10px; }

/* ── TABS ───────────────────────────────────────── */
.tabs { background: var(--bg2); border-bottom: 1px solid var(--border); overflow-x: auto; white-space: nowrap; padding: 0 12px; }
.tab { display: inline-block; padding: 10px 14px; cursor: pointer; color: var(--text2); font-size: 11px; font-weight: 600; letter-spacing: .5px; border-bottom: 2px solid transparent; transition: all .2s; text-transform: uppercase; }
.tab:hover { color: var(--text); }
.tab.active { color: var(--orange); border-bottom-color: var(--orange); }

/* ── LAYOUT ─────────────────────────────────────── */
.content { padding: 16px; max-width: 1600px; margin: 0 auto; }
.screen { display: none; }
.screen.active { display: block; }
.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.grid-5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; }
.grid-6 { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; }
@media(max-width:1200px) { .grid-6 { grid-template-columns: repeat(4, 1fr); } }
@media(max-width:900px) { .grid-4,.grid-5,.grid-6 { grid-template-columns: repeat(2, 1fr); } .grid-3 { grid-template-columns: 1fr; } }
@media(max-width:600px) { .grid-2,.grid-3,.grid-4,.grid-5,.grid-6 { grid-template-columns: 1fr; } }

/* ── CARDS ─────────────────────────────────────── */
.card { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 14px; }
.card-sm { background: var(--card); border: 1px solid var(--border); border-radius: 6px; padding: 10px 12px; }
.section-title { color: var(--orange); font-size: 10px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin: 18px 0 8px; border-left: 3px solid var(--orange); padding-left: 8px; }
.kv { display: flex; justify-content: space-between; align-items: center; padding: 4px 0; border-bottom: 1px solid rgba(255,255,255,.04); }
.kv:last-child { border-bottom: none; }
.kv .k { color: var(--text2); font-size: 11px; }
.kv .v { font-weight: 600; font-size: 12px; text-align: right; }
.kv .v.pos { color: var(--green); }
.kv .v.neg { color: var(--red); }
.kv .v.blue { color: var(--blue); }
.kv .v.orange { color: var(--orange); }
.kv .v.purple { color: var(--purple); }
.metric-big { text-align: center; }
.metric-big .val { font-size: 24px; font-weight: 900; }
.metric-big .lbl { font-size: 10px; color: var(--text2); text-transform: uppercase; letter-spacing: 1px; margin-top: 2px; }
.metric-big .sub { font-size: 11px; color: var(--text3); margin-top: 2px; }

/* ── FEAR & GREED ───────────────────────────────── */
.fg-gauge { position: relative; width: 120px; height: 60px; margin: 0 auto 8px; }
.fg-gauge svg { width: 100%; height: 100%; }
.fg-val { text-align: center; font-size: 28px; font-weight: 900; line-height: 1; }
.fg-label { text-align: center; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-top: 2px; }

/* ── TABLE ──────────────────────────────────────── */
.tbl-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 11px; }
thead th { background: var(--bg3); color: var(--text2); padding: 8px 10px; text-align: left; font-weight: 700; font-size: 10px; letter-spacing: .5px; text-transform: uppercase; white-space: nowrap; border-bottom: 1px solid var(--border); }
tbody tr { border-bottom: 1px solid rgba(255,255,255,.04); transition: background .1s; }
tbody tr:hover { background: rgba(255,255,255,.03); }
td { padding: 7px 10px; white-space: nowrap; }
.rank { color: var(--text3); font-size: 10px; }
.ex-name { font-weight: 600; font-size: 12px; }
.ex-price { font-weight: 700; font-size: 13px; color: var(--text); }
.spread-bar { height: 4px; border-radius: 2px; background: var(--green); display: block; transition: width .5s; }

/* ── LOADING ─────────────────────────────────────── */
#loader { position: fixed; inset: 0; background: var(--bg); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 999; }
.loader-ring { width: 48px; height: 48px; border: 3px solid var(--border); border-top-color: var(--orange); border-radius: 50%; animation: spin .8s linear infinite; margin-bottom: 16px; }
@keyframes spin { to { transform: rotate(360deg); } }
.loader-text { color: var(--text2); font-size: 12px; }

/* ── COUNTRY FLAGS ───────────────────────────────── */
.region-title { font-size: 13px; font-weight: 700; color: var(--text); margin: 14px 0 8px; display: flex; align-items: center; gap: 8px; }

/* ── SIGNAL ─────────────────────────────────────── */
.signal { padding: 10px 14px; border-radius: 6px; border-left: 3px solid; margin-bottom: 8px; }
.signal.buy { background: rgba(0,200,150,.07); border-color: var(--green); }
.signal.sell { background: rgba(255,71,87,.07); border-color: var(--red); }
.signal.neutral { background: rgba(77,166,255,.07); border-color: var(--blue); }
.signal-title { font-weight: 700; font-size: 12px; }
.signal-desc { color: var(--text2); font-size: 11px; margin-top: 3px; }

/* ── SOURCE CARD ─────────────────────────────────── */
.src-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 10px; }
.src-card { background: var(--card); border: 1px solid var(--border); border-radius: 7px; padding: 12px 14px; display: flex; flex-direction: column; gap: 4px; transition: border-color .2s; }
.src-card:hover { border-color: var(--orange); }
.src-name { font-weight: 700; font-size: 13px; color: var(--text); display: flex; align-items: center; gap: 6px; }
.src-url { color: var(--text3); font-size: 10px; }
.src-data { color: var(--text2); font-size: 11px; line-height: 1.5; margin-top: 2px; }
.src-tag { display: inline-block; font-size: 9px; font-weight: 700; letter-spacing: .5px; padding: 2px 6px; border-radius: 3px; text-transform: uppercase; }
.tag-free { background: rgba(0,200,150,.15); color: var(--green); }
.tag-key { background: rgba(251,191,36,.15); color: var(--yellow); }
.tag-country { background: rgba(77,166,255,.15); color: var(--blue); }

/* ── MISC ─────────────────────────────────────────── */
.pill { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 700; }
.pill-orange { background: rgba(247,147,26,.15); color: var(--orange); }
.pill-green { background: rgba(0,200,150,.15); color: var(--green); }
.pill-red { background: rgba(255,71,87,.15); color: var(--red); }
.pill-blue { background: rgba(77,166,255,.15); color: var(--blue); }
.pill-purple { background: rgba(167,139,250,.15); color: var(--purple); }
.divider { border: none; border-top: 1px solid var(--border); margin: 14px 0; }
.err { color: var(--text3); font-style: italic; font-size: 11px; }
</style>
</head>
<body>
<div id="loader">
  <div class="loader-ring"></div>
  <div class="loader-text">Chargement des 70 APIs...</div>
</div>

<div class="header">
  <div class="logo">₿ BTC<span>Analytics</span></div>
  <div class="price-hero" id="h-price">---</div>
  <span class="price-change" id="h-change">--</span>
  <span class="price-change" id="h-vol" style="margin-left:4px;background:rgba(77,166,255,.1);color:var(--blue)"></span>
  <div class="badge-apis">70 APIs Gratuites</div>
  <div class="last-update" id="h-upd"></div>
</div>

<div class="tabs">
  <div class="tab active" onclick="setTab('dash')">Dashboard</div>
  <div class="tab" onclick="setTab('marche')">Marché</div>
  <div class="tab" onclick="setTab('onchain')">On-Chain</div>
  <div class="tab" onclick="setTab('tech')">Technique</div>
  <div class="tab" onclick="setTab('reseau')">Réseau</div>
  <div class="tab" onclick="setTab('ln')">Lightning</div>
  <div class="tab" onclick="setTab('exchanges')">Exchanges USD</div>
  <div class="tab" onclick="setTab('intl')">International</div>
  <div class="tab" onclick="setTab('etf')">ETF</div>
  <div class="tab" onclick="setTab('derivatifs')">Dérivés</div>
  <div class="tab" onclick="setTab('defi')">DeFi / Analytics</div>
  <div class="tab" onclick="setTab('alertes')">Alertes</div>
  <div class="tab" onclick="setTab('sources')">Sources (70)</div>
</div>

<div class="content">

  <!-- DASHBOARD -->
  <div id="s-dash" class="screen active">
    <div class="grid-4" style="margin-bottom:12px">
      <div class="card metric-big"><div class="val orange" id="d-price">---</div><div class="lbl">Prix BTC/USD</div><div class="sub" id="d-source">CoinGecko</div></div>
      <div class="card metric-big"><div class="val" id="d-chg24" style="color:var(--text)">--</div><div class="lbl">Variation 24h</div><div class="sub" id="d-chg7">7j: --</div></div>
      <div class="card metric-big"><div class="val" id="d-mcap" style="color:var(--blue)">---</div><div class="lbl">Market Cap</div><div class="sub" id="d-dom">Dom: --</div></div>
      <div class="card metric-big"><div class="val" id="d-vol" style="color:var(--purple)">---</div><div class="lbl">Volume 24h</div><div class="sub" id="d-supply">Supply: --</div></div>
    </div>
    <div class="grid-4" style="margin-bottom:12px">
      <div class="card" style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:16px">
        <div class="fg-gauge"><svg viewBox="0 0 120 60"><defs><linearGradient id="g1" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#ff4757"/><stop offset="25%" stop-color="#ffa502"/><stop offset="50%" stop-color="#ffd32a"/><stop offset="75%" stop-color="#2ed573"/><stop offset="100%" stop-color="#00c896"/></linearGradient></defs><path d="M10,55 A55,55 0 0,1 110,55" fill="none" stroke="var(--border)" stroke-width="10" stroke-linecap="round"/><path id="fg-arc" d="M10,55 A55,55 0 0,1 110,55" fill="none" stroke="url(#g1)" stroke-width="10" stroke-linecap="round" stroke-dasharray="173" stroke-dashoffset="173"/></svg></div>
        <div class="fg-val" id="fg-val" style="color:var(--yellow)">--</div>
        <div class="fg-label" id="fg-label" style="color:var(--text2)">Fear & Greed</div>
        <div style="color:var(--text3);font-size:10px;margin-top:4px" id="fg-prev"></div>
      </div>
      <div class="card"><div class="section-title" style="margin-top:0">On-Chain KPIs</div><div id="d-onchain-kpis"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">Réseau</div><div id="d-network-kpis"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">Lightning</div><div id="d-ln-kpis"></div></div>
    </div>
    <div class="grid-2">
      <div class="card"><div class="section-title" style="margin-top:0">Prix All-Time & Niveaux</div><div id="d-ath"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">Marché Comparatif</div><div id="d-market-comp"></div></div>
    </div>
  </div>

  <!-- MARCHE -->
  <div id="s-marche" class="screen">
    <div class="grid-3">
      <div class="card"><div class="section-title" style="margin-top:0">CoinGecko — Prix & Marché</div><div id="m-cg"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">Marché Global CoinGecko</div><div id="m-global"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">CoinPaprika</div><div id="m-cp"></div></div>
    </div>
    <div class="grid-3" style="margin-top:12px">
      <div class="card"><div class="section-title" style="margin-top:0">CoinLore</div><div id="m-cl"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">CoinRanking</div><div id="m-cr"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">Alternative.me Ticker</div><div id="m-alt"></div></div>
    </div>
    <div class="section-title">Stooq — Historique 30 Jours</div>
    <div class="card"><div id="m-stooq"></div></div>
  </div>

  <!-- ON-CHAIN -->
  <div id="s-onchain" class="screen">
    <div class="grid-3">
      <div class="card"><div class="section-title" style="margin-top:0">CoinMetrics — Valorisation</div><div id="oc-val"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">CoinMetrics — Adoption</div><div id="oc-adp"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">CoinMetrics — ROI & Mining</div><div id="oc-roi"></div></div>
    </div>
    <div class="grid-3" style="margin-top:12px">
      <div class="card"><div class="section-title" style="margin-top:0">BGR bitcoin-data.com — SOPR</div><div id="oc-sopr"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">BGR — Détenteurs & Baleines</div><div id="oc-whale"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">BGR — NRPL & Pertes Réalisées</div><div id="oc-nrpl"></div></div>
    </div>
    <div class="grid-3" style="margin-top:12px">
      <div class="card"><div class="section-title" style="margin-top:0">CoinMetrics Deep — Adresses & NVT</div><div id="oc-deep"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">Bitfinex — Positions Long/Short</div><div id="oc-positions"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">Deribit — Volatilité Implicite (DVol)</div><div id="oc-dvol"></div></div>
    </div>
  </div>

  <!-- TECHNIQUE -->
  <div id="s-tech" class="screen">
    <div class="grid-3">
      <div class="card"><div class="section-title" style="margin-top:0">Moyennes Mobiles — Kraken OHLC</div><div id="t-ma"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">Indicateurs Momentum</div><div id="t-ind"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">Risque & Volatilité</div><div id="t-risk"></div></div>
    </div>
    <div class="section-title">Kraken — Données OHLCV Complètes</div>
    <div class="card"><div id="t-kraken"></div></div>
  </div>

  <!-- RESEAU -->
  <div id="s-reseau" class="screen">
    <div class="grid-3">
      <div class="card"><div class="section-title" style="margin-top:0">Mempool.space — Fees & Mempool</div><div id="r-mempool"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">Blockchair — Blockchain Stats</div><div id="r-blockchair"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">Blockchain.info — Stats Globales</div><div id="r-bcinfo"></div></div>
    </div>
    <div class="grid-3" style="margin-top:12px">
      <div class="card"><div class="section-title" style="margin-top:0">Blockstream.info</div><div id="r-blockstream"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">Bitnodes.io — Nœuds P2P</div><div id="r-bitnodes"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">Blockchain.info — Pools Mining</div><div id="r-pools"></div></div>
    </div>
    <div class="grid-3" style="margin-top:12px">
      <div class="card"><div class="section-title" style="margin-top:0">Mempool.space — Derniers Blocs</div><div id="r-blocks"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">Blockchain.info Charts</div><div id="r-bcharts"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">WhatToMine — Mining Stats</div><div id="r-wtm"></div></div>
    </div>
  </div>

  <!-- LIGHTNING -->
  <div id="s-ln" class="screen">
    <div class="grid-4">
      <div class="card metric-big"><div class="val blue" id="ln-nodes">---</div><div class="lbl">Nœuds LN</div><div class="sub" id="ln-nodes-src"></div></div>
      <div class="card metric-big"><div class="val purple" id="ln-chan">---</div><div class="lbl">Canaux</div><div class="sub" id="ln-chan-src"></div></div>
      <div class="card metric-big"><div class="val orange" id="ln-cap-btc">---</div><div class="lbl">Capacité (BTC)</div><div class="sub" id="ln-cap-usd"></div></div>
      <div class="card metric-big"><div class="val green" id="ln-avg-cap">---</div><div class="lbl">Capacité Moy/Canal</div><div class="sub">satoshis</div></div>
    </div>
    <div class="grid-2" style="margin-top:12px">
      <div class="card"><div class="section-title" style="margin-top:0">Mempool.space Lightning</div><div id="ln-mempool"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">1ML.com — Statistiques 30j</div><div id="ln-1ml"></div></div>
    </div>
  </div>

  <!-- EXCHANGES USD -->
  <div id="s-exchanges" class="screen">
    <div class="grid-4" style="margin-bottom:12px">
      <div class="card metric-big"><div class="val orange" id="ex-count">--</div><div class="lbl">Exchanges actifs</div></div>
      <div class="card metric-big"><div class="val" id="ex-avg" style="color:var(--text)">---</div><div class="lbl">Prix moyen</div></div>
      <div class="card metric-big"><div class="val" id="ex-spread" style="color:var(--yellow)">--</div><div class="lbl">Spread arbitrage</div><div class="sub">Max - Min</div></div>
      <div class="card"><div class="kv"><span class="k">Plus haut</span><span class="v blue" id="ex-high"></span></div><div class="kv"><span class="k">Plus bas</span><span class="v blue" id="ex-low"></span></div></div>
    </div>
    <div class="card" style="margin-bottom:12px"><div class="tbl-wrap"><table id="ex-table"><thead><tr><th>#</th><th>Exchange</th><th>Prix USD</th><th>vs Moyen</th><th>Spread</th></tr></thead><tbody></tbody></table></div></div>
    <div class="grid-3">
      <div class="card"><div class="section-title" style="margin-top:0">Deribit — Dérivés</div><div id="ex-deribit"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">Poloniex</div><div id="ex-poloniex"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">Crypto.com</div><div id="ex-cdotcom"></div></div>
    </div>
    <div class="grid-3" style="margin-top:12px">
      <div class="card"><div class="section-title" style="margin-top:0">BitMart</div><div id="ex-bitmart"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">BTSE</div><div id="ex-btse"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">CoinLore — Données Marché</div><div id="ex-coinlore"></div></div>
    </div>
    <div class="section-title">WBTC DEX — Uniswap / DexScreener</div>
    <div class="card"><div id="ex-dex"></div></div>
  </div>

  <!-- INTERNATIONAL -->
  <div id="s-intl" class="screen">
    <div class="section-title">Taux de Change BTC (exchangerate-api + CoinGecko)</div>
    <div class="grid-6" id="intl-fx"></div>

    <div class="region-title">🇯🇵 JAPON</div>
    <div class="grid-3" id="intl-jp"></div>

    <div class="region-title">🇰🇷 CORÉE DU SUD</div>
    <div class="grid-3" id="intl-kr"></div>

    <div class="region-title">🇦🇺 AUSTRALIE &nbsp;·&nbsp; 🇷🇺 RUSSIE / EUROPE DE L'EST</div>
    <div class="grid-3" id="intl-au-ru"></div>

    <div class="region-title">🇹🇷 TURQUIE</div>
    <div class="grid-2" id="intl-tr"></div>

    <div class="region-title">🇧🇷 BRÉSIL</div>
    <div class="grid-3" id="intl-br"></div>

    <div class="region-title">🇿🇦 AFRIQUE DU SUD</div>
    <div class="grid-2" id="intl-za"></div>

    <div class="region-title">🇲🇽 MEXIQUE</div>
    <div class="grid-2" id="intl-mx"></div>

    <div class="region-title">🇮🇳 INDE</div>
    <div class="grid-2" id="intl-in"></div>

    <div class="region-title">🇮🇩 INDONÉSIE</div>
    <div class="grid-2" id="intl-id"></div>
  </div>

  <!-- ETF -->
  <div id="s-etf" class="screen">
    <div class="grid-4" style="margin-bottom:12px">
      <div class="card metric-big"><div class="val orange" id="etf-aum">---</div><div class="lbl">AUM Total ETF</div><div class="sub">USD (SoSoValue)</div></div>
      <div class="card metric-big"><div class="val" id="etf-flow-day" style="color:var(--text)">---</div><div class="lbl">Flux Net Jour</div><div class="sub">Millions USD</div></div>
      <div class="card metric-big"><div class="val blue" id="etf-flow-cum">---</div><div class="lbl">Flux Cumulé</div><div class="sub">Total depuis lancement</div></div>
      <div class="card metric-big"><div class="val green" id="etf-btc-held">---</div><div class="lbl">BTC Détenus</div><div class="sub">Total ETFs</div></div>
    </div>
    <div class="grid-2">
      <div class="card"><div class="section-title" style="margin-top:0">SoSoValue — Flux ETF BTC</div><div id="etf-soso"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">TwelveData — Prix ETF BTC</div><div id="etf-12d"></div></div>
    </div>
  </div>

  <!-- ALERTES -->
  <div id="s-alertes" class="screen">
    <div class="section-title">Signaux Actifs</div>
    <div id="al-signals"></div>
    <div class="section-title">Signaux Techniques</div>
    <div id="al-tech-signals"></div>
  </div>

  <!-- DERIVATIFS -->
  <div id="s-derivatifs" class="screen">
    <div class="grid-4" style="margin-bottom:12px">
      <div class="card metric-big"><div class="val orange" id="drv-funding">---</div><div class="lbl">Funding Rate Moyen</div><div class="sub">% / 8h agrégé</div></div>
      <div class="card metric-big"><div class="val" id="drv-ls" style="color:var(--text)">---</div><div class="lbl">Ratio Long/Short</div><div class="sub">Binance Global</div></div>
      <div class="card metric-big"><div class="val blue" id="drv-oi">---</div><div class="lbl">Open Interest BTC</div><div class="sub">Binance Futures</div></div>
      <div class="card metric-big"><div class="val purple" id="drv-dvol">---</div><div class="lbl">Bitcoin DVol</div><div class="sub">Deribit Volatility Index</div></div>
    </div>
    <div class="grid-3">
      <div class="card"><div class="section-title" style="margin-top:0">Binance USDT-M Futures (FAPI)</div><div id="drv-binance"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">Kraken Futures — PF_XBTUSD</div><div id="drv-kraken"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">BitMEX — XBTUSD Perpetual</div><div id="drv-bitmex"></div></div>
    </div>
    <div class="grid-3" style="margin-top:12px">
      <div class="card"><div class="section-title" style="margin-top:0">Hyperliquid DEX (décentralisé)</div><div id="drv-hyper"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">Bitget USDT-Futures</div><div id="drv-bitget"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">Bitfinex Stats — Positions</div><div id="drv-bfxstats"></div></div>
    </div>
    <div class="card" style="margin-top:12px;background:rgba(247,147,26,.05);border-color:rgba(247,147,26,.2)">
      <div style="font-size:11px;color:var(--text2);line-height:1.8">
        <strong style="color:var(--orange)">Note sur les métriques avancées de dérivés :</strong>
        Les données de liquidations cumulées en temps réel (Coinglass), les options Greeks complets, et les données de whale positions (Nansen, Glassnode) nécessitent des abonnements payants.
        Les sources ci-dessus représentent <strong>tout ce qui est disponible gratuitement</strong> sans clé API.
      </div>
    </div>
  </div>

  <!-- DEFI / ANALYTICS -->
  <div id="s-defi" class="screen">
    <div class="grid-4" style="margin-bottom:12px">
      <div class="card metric-big"><div class="val orange" id="defi-btc-tvl">---</div><div class="lbl">TVL Bitcoin Chain</div><div class="sub">DefiLlama (BTC natif)</div></div>
      <div class="card metric-big"><div class="val green" id="defi-wbtc">---</div><div class="lbl">WBTC TVL Ethereum</div><div class="sub">DefiLlama Protocol</div></div>
      <div class="card metric-big"><div class="val blue" id="defi-messari-price">---</div><div class="lbl">Prix (Messari)</div><div class="sub">Métriques analytiques</div></div>
      <div class="card metric-big"><div class="val purple" id="defi-cc-close">---</div><div class="lbl">Close (CryptoCompare)</div><div class="sub">30j high: <span id="defi-cc-high">---</span></div></div>
    </div>
    <div class="grid-3">
      <div class="card"><div class="section-title" style="margin-top:0">DefiLlama — Bitcoin Ecosystem TVL</div><div id="defi-llama"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">CoinPaprika Extended — Métriques BTC</div><div id="defi-messari"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">CryptoCompare — Historique 30j</div><div id="defi-cc"></div></div>
    </div>
    <div class="grid-3" style="margin-top:12px">
      <div class="card"><div class="section-title" style="margin-top:0">WhatToMine — Mining BTC</div><div id="defi-wtm"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">CoinMetrics Deep — Métriques On-Chain</div><div id="defi-cm-deep"></div></div>
      <div class="card"><div class="section-title" style="margin-top:0">Mempool.space — Derniers Blocs</div><div id="defi-blocks"></div></div>
    </div>
    <div class="section-title">Blockchain.info Charts — Hashrate &amp; Transactions Historique</div>
    <div class="grid-2">
      <div class="card"><div id="defi-bchart-hashrate"></div></div>
      <div class="card"><div id="defi-bchart-txcount"></div></div>
    </div>
    <div class="card" style="margin-top:12px;background:rgba(167,139,250,.05);border-color:rgba(167,139,250,.2)">
      <div style="font-size:11px;color:var(--text2);line-height:1.8">
        <strong style="color:var(--purple)">Métriques avancées non disponibles gratuitement :</strong>
        LTH/STH ratios détaillés (Glassnode Pro ~$30/mois), Whale cohorts précises (Nansen ~$150/mois), 
        Realized price par cohort (IntoTheBlock $299/mois), SOAB complet (Glassnode), 
        Santiment sentiment (Santiment API ~$50/mois). Ces données sont exclusivement derrière des paywalls.
      </div>
    </div>
  </div>

  <!-- SOURCES -->
  <div id="s-sources" class="screen">
    <div style="margin-bottom:16px">
      <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
        <div style="font-size:28px;font-weight:900;color:var(--orange)">70 APIs Gratuites</div>
        <div style="color:var(--text2);font-size:13px">toutes les sources Bitcoin disponibles dans le monde</div>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px" id="src-filters">
        <span class="pill pill-orange" onclick="filterSrc('all')" id="f-all" style="cursor:pointer">Toutes (70)</span>
        <span class="pill pill-blue" onclick="filterSrc('exchanges_usd')" id="f-usd" style="cursor:pointer">Exchanges USD (28)</span>
        <span class="pill pill-blue" onclick="filterSrc('exchanges_international')" id="f-intl" style="cursor:pointer">International (19)</span>
        <span class="pill pill-green" onclick="filterSrc('on_chain')" id="f-oc" style="cursor:pointer">On-Chain (7)</span>
        <span class="pill pill-purple" onclick="filterSrc('lightning')" id="f-ln" style="cursor:pointer">Lightning (2)</span>
        <span class="pill" style="background:rgba(251,191,36,.15);color:var(--yellow);cursor:pointer" onclick="filterSrc('etf_finance')">ETF (2)</span>
        <span class="pill" style="background:rgba(255,71,87,.15);color:var(--red);cursor:pointer" onclick="filterSrc('derivatives')">Dérivés (6)</span>
        <span class="pill" style="background:rgba(0,200,150,.15);color:var(--green);cursor:pointer" onclick="filterSrc('defi_tvl')">DeFi TVL (1)</span>
        <span class="pill" style="background:rgba(77,166,255,.15);color:var(--blue);cursor:pointer" onclick="filterSrc('analytics')">Analytics (2)</span>
        <span class="pill" style="background:rgba(247,147,26,.15);color:var(--orange);cursor:pointer" onclick="filterSrc('mining_stats')">Mining (2)</span>
        <span class="pill" style="background:rgba(82,92,120,.3);color:var(--text2);cursor:pointer" onclick="filterSrc('sentiment')">Sentiment (1)</span>
        <span class="pill" style="background:rgba(82,92,120,.3);color:var(--text2);cursor:pointer" onclick="filterSrc('historical')">Historique (2)</span>
      </div>
    </div>
    <div id="src-cards" class="src-grid"></div>
  </div>

</div><!-- /content -->

<script>
const API = '';
let DATA = {}, INTL = {}, EX = {}, STOOQ = {}, ALERTS = [], SOURCES = {}, NET = {}, LN = {};
let DRV = {}, DEFI = {};
let currentSrcFilter = 'all';

function fmt(v, dec=0) { if(v==null||v===undefined||isNaN(v)) return '<span class="err">N/A</span>'; return Number(v).toLocaleString('fr-FR',{minimumFractionDigits:dec,maximumFractionDigits:dec}); }
function fmtP(v) { if(v==null||isNaN(v)) return '<span class="err">N/A</span>'; const c=v>0?'pos':v<0?'neg':''; return `<span class="${c}">${v>0?'+':''}${Number(v).toFixed(2)}%</span>`; }
function fmtV(v) { if(!v) return '<span class="err">N/A</span>'; const b=1e9,m=1e6,k=1e3; if(v>=b) return (v/b).toFixed(2)+'B'; if(v>=m) return (v/m).toFixed(2)+'M'; if(v>=k) return (v/k).toFixed(1)+'K'; return v.toFixed(0); }
function kv(k,v,cls='') { return `<div class="kv"><span class="k">${k}</span><span class="v ${cls}">${v}</span></div>`; }
function colorNum(v) { if(v==null||isNaN(v)) return ''; return v>0?'pos':v<0?'neg':''; }

function setTab(name) {
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));
  document.querySelector(`.tab[onclick*="'${name}'"]`).classList.add('active');
  document.getElementById('s-'+name).classList.add('active');
}

// ══════ DASHBOARD ══════════════════════════════════════════
function renderDash() {
  const d = DATA;
  document.getElementById('d-price').innerHTML = d.price_usd!=null?'$'+fmt(d.price_usd):'<span class="err">N/A</span>';
  document.getElementById('d-chg24').innerHTML = fmtP(d.change_24h);
  document.getElementById('d-chg7').textContent = '7j: '+(d.change_7d!=null?((d.change_7d>0?'+':'')+Number(d.change_7d).toFixed(2)+'%'):'N/A');
  document.getElementById('d-mcap').innerHTML = d.market_cap_usd!=null?'$'+fmtV(d.market_cap_usd):'<span class="err">N/A</span>';
  document.getElementById('d-dom').textContent = 'Dom: '+(d.btc_dominance!=null?d.btc_dominance.toFixed(2)+'%':'N/A');
  document.getElementById('d-vol').innerHTML = d.volume_24h_usd!=null?'$'+fmtV(d.volume_24h_usd):'<span class="err">N/A</span>';
  document.getElementById('d-supply').textContent = 'Supply: '+(d.circulating_supply!=null?fmt(d.circulating_supply)+' BTC':'N/A');

  // Fear & Greed
  const fg = d.fear_greed_value;
  if(fg!=null) {
    document.getElementById('fg-val').textContent = fg;
    const color = fg<20?'var(--red)':fg<40?'#ff6348':fg<60?'var(--yellow)':fg<80?'#2ed573':'var(--green)';
    document.getElementById('fg-val').style.color = color;
    document.getElementById('fg-label').textContent = d.fear_greed_label||'';
    document.getElementById('fg-label').style.color = color;
    document.getElementById('fg-prev').textContent = 'Hier: '+(d.fear_greed_previous||'N/A');
    const arc = document.getElementById('fg-arc');
    const pct = fg/100; const total = 173;
    arc.setAttribute('stroke-dashoffset', total*(1-pct));
  }

  // On-Chain KPIs
  document.getElementById('d-onchain-kpis').innerHTML = [
    kv('MVRV', d.mvrv!=null?Number(d.mvrv).toFixed(3):'N/A', d.mvrv>3?'neg':d.mvrv<1?'pos':'orange'),
    kv('NUPL', d.nupl!=null?Number(d.nupl).toFixed(3):'N/A', d.nupl>0.75?'neg':d.nupl<0?'pos':'orange'),
    kv('aSOPR', d.asopr!=null?Number(d.asopr).toFixed(4):'N/A'),
    kv('RSI 14j', d.rsi_14!=null?Number(d.rsi_14).toFixed(1):'N/A', d.rsi_14>70?'neg':d.rsi_14<30?'pos':'blue'),
    kv('Realized Cap', d.realized_cap_usd!=null?'$'+fmtV(d.realized_cap_usd):'N/A'),
  ].join('');

  document.getElementById('d-network-kpis').innerHTML = [
    kv('Hashrate', d.hashrate_eh!=null?Number(d.hashrate_eh).toFixed(1)+' EH/s':'N/A'),
    kv('Difficulté', d.difficulty_t!=null?Number(d.difficulty_t).toFixed(2)+' T':'N/A'),
    kv('Blocs', d.blocks_total!=null?fmt(d.blocks_total):'N/A'),
    kv('Mempool TXs', d.mempool_count!=null?fmt(d.mempool_count):'N/A'),
    kv('Frais moyen', d.fee_avg_sat!=null?fmt(d.fee_avg_sat)+' sat/vB':'N/A'),
  ].join('');

  document.getElementById('d-ln-kpis').innerHTML = [
    kv('Nœuds LN', d.ln_nodes!=null?fmt(d.ln_nodes):'N/A', 'blue'),
    kv('Canaux', d.ln_channels!=null?fmt(d.ln_channels):'N/A', 'purple'),
    kv('Capacité BTC', d.ln_capacity_btc!=null?fmt(d.ln_capacity_btc)+' BTC':'N/A', 'orange'),
    kv('Capacité USD', d.ln_capacity_usd!=null?'$'+fmtV(d.ln_capacity_usd):'N/A', 'green'),
    kv('Avg Capacité', d.ln_avg_capacity!=null?fmt(d.ln_avg_capacity)+' sat':'N/A'),
  ].join('');

  document.getElementById('d-ath').innerHTML = [
    kv('ATH', d.ath_usd!=null?'$'+fmt(d.ath_usd):'N/A', 'orange'),
    kv('ATH Date', d.ath_date||'N/A'),
    kv('Distance ATH', d.ath_change_pct!=null?fmtP(d.ath_change_pct):'N/A'),
    kv('ATL', d.atl_usd!=null?'$'+fmt(d.atl_usd):'N/A'),
    kv('200j MA', d.ma200!=null?'$'+fmt(d.ma200):'N/A', 'blue'),
    kv('Prix vs 200j MA', d.price_to_ma200!=null?fmtP(d.price_to_ma200):'N/A'),
    kv('Mayer Multiple', d.mayer_multiple!=null?Number(d.mayer_multiple).toFixed(3):'N/A'),
  ].join('');

  document.getElementById('d-market-comp').innerHTML = [
    kv('Vol 30j Annualisée', d.volatility_30d!=null?Number(d.volatility_30d).toFixed(2)+'%':'N/A'),
    kv('Sharpe 30j', d.sharpe_30d!=null?Number(d.sharpe_30d).toFixed(3):'N/A', d.sharpe_30d>1?'pos':d.sharpe_30d<0?'neg':''),
    kv('Puell Multiple', d.puell_multiple!=null?Number(d.puell_multiple).toFixed(3):'N/A'),
    kv('Blocs Aujourd\'hui', d.blocks_today!=null?d.blocks_today:'N/A'),
    kv('Revenus Mineurs/j', d.miners_revenue!=null?'$'+fmtV(d.miners_revenue):'N/A'),
    kv('Supply Totale', d.supply_btc!=null?fmt(d.supply_btc)+' BTC':'N/A'),
    kv('Exchanges actifs', d.exchange_count||'N/A', 'orange'),
  ].join('');
}

// ══════ MARCHE ══════════════════════════════════════════════
function renderMarche() {
  const d = DATA;
  document.getElementById('m-cg').innerHTML = [
    kv('Prix USD', d.price_usd!=null?'<strong>$'+fmt(d.price_usd)+'</strong>':'N/A', 'orange'),
    kv('Change 24h', fmtP(d.change_24h)),
    kv('Change 7j', fmtP(d.change_7d)),
    kv('Change 30j', fmtP(d.change_30d)),
    kv('Market Cap', d.market_cap_usd!=null?'$'+fmtV(d.market_cap_usd):'N/A'),
    kv('Volume 24h', d.volume_24h_usd!=null?'$'+fmtV(d.volume_24h_usd):'N/A'),
    kv('Supply circulante', d.circulating_supply!=null?fmt(d.circulating_supply)+' BTC':'N/A'),
    kv('ATH', d.ath_usd!=null?'$'+fmt(d.ath_usd):'N/A'),
    kv('ATH Date', d.ath_date||'N/A'),
    kv('ATL', d.atl_usd!=null?'$'+fmt(d.atl_usd):'N/A'),
    kv('Source', 'CoinGecko API', 'blue'),
  ].join('');

  document.getElementById('m-global').innerHTML = [
    kv('Dominance BTC', d.btc_dominance!=null?Number(d.btc_dominance).toFixed(2)+'%':'N/A', 'orange'),
    kv('Dominance ETH', d.eth_dominance!=null?Number(d.eth_dominance).toFixed(2)+'%':'N/A'),
    kv('Market Cap Total', d.total_market_cap!=null?'$'+fmtV(d.total_market_cap):'N/A'),
    kv('Cryptos actives', d.active_cryptos!=null?fmt(d.active_cryptos):'N/A'),
    kv('Cap USDT', d.usdt_market_cap!=null?'$'+fmtV(d.usdt_market_cap):'N/A'),
    kv('Cap USDC', d.usdc_market_cap!=null?'$'+fmtV(d.usdc_market_cap):'N/A'),
    kv('Source', 'CoinGecko /global', 'blue'),
  ].join('');

  document.getElementById('m-cp').innerHTML = [
    kv('Prix CoinPaprika', d.price_coinpaprika!=null?'$'+fmt(d.price_coinpaprika):'N/A'),
    kv('Volume 24h', d.coinpaprika_vol!=null?'$'+fmtV(d.coinpaprika_vol):'N/A'),
    kv('Beta 30j', d.coinpaprika_beta!=null?Number(d.coinpaprika_beta).toFixed(3):'N/A'),
    kv('High 24h', d.coinpaprika_high!=null?'$'+fmt(d.coinpaprika_high):'N/A'),
    kv('Low 24h', d.coinpaprika_low!=null?'$'+fmt(d.coinpaprika_low):'N/A'),
    kv('Open 24h', d.coinpaprika_open!=null?'$'+fmt(d.coinpaprika_open):'N/A'),
    kv('Source', 'CoinPaprika API', 'blue'),
  ].join('');

  document.getElementById('m-cl').innerHTML = (()=>{
    const ex = EX;
    return [
      kv('Prix USD', ex.coinlore_price!=null?'$'+fmt(ex.coinlore_price):'N/A'),
      kv('Market Cap', ex.coinlore_market_cap!=null?'$'+fmtV(ex.coinlore_market_cap):'N/A'),
      kv('Volume 24h', ex.coinlore_vol_24h!=null?'$'+fmtV(ex.coinlore_vol_24h):'N/A'),
      kv('Change 24h', ex.coinlore_change_24h!=null?fmtP(ex.coinlore_change_24h):'N/A'),
      kv('Change 7j', ex.coinlore_change_7d!=null?fmtP(ex.coinlore_change_7d):'N/A'),
      kv('Rang', ex.coinlore_rank!=null?'#'+ex.coinlore_rank:'N/A'),
      kv('Source', 'CoinLore API (sans clé)', 'blue'),
    ].join('');
  })();

  document.getElementById('m-cr').innerHTML = [
    kv('Prix USD', EX.coinranking_price!=null?'$'+fmt(EX.coinranking_price):'N/A'),
    kv('Source', 'CoinRanking API (sans clé)', 'blue'),
  ].join('');

  document.getElementById('m-alt').innerHTML = [
    kv('Fear & Greed', d.fear_greed_value!=null?d.fear_greed_value+' — '+(d.fear_greed_label||''):'N/A'),
    kv('Hier (F&G)', d.fear_greed_previous!=null?d.fear_greed_previous+' — '+(d.fear_greed_prev_label||''):'N/A'),
    kv('Prix Alt.me', d.altme_price!=null?'$'+fmt(d.altme_price):'N/A'),
    kv('Change 24h', d.altme_change!=null?fmtP(d.altme_change):'N/A'),
    kv('Market Cap', d.altme_mcap!=null?'$'+fmtV(d.altme_mcap):'N/A'),
    kv('Source', 'Alternative.me', 'blue'),
  ].join('');

  const s = STOOQ;
  document.getElementById('m-stooq').innerHTML = !s || Object.keys(s).length<3 ? '<p class="err">Données Stooq non disponibles</p>' : [
    kv('Close actuel', s.close_latest!=null?'$'+fmt(s.close_latest,2):'N/A'),
    kv('High 30j', s.high_30d!=null?'$'+fmt(s.high_30d,2):'N/A'),
    kv('Low 30j', s.low_30d!=null?'$'+fmt(s.low_30d,2):'N/A'),
    kv('Open 30j ago', s.open_30d!=null?'$'+fmt(s.open_30d,2):'N/A'),
    kv('Performance 30j', s.perf_30d!=null?fmtP(s.perf_30d):'N/A'),
    kv('Vol moyen 30j', s.avg_vol!=null?fmtV(s.avg_vol):'N/A'),
    kv('Jours de données', s.days_available!=null?s.days_available:'N/A'),
    kv('Source', 'Stooq CSV', 'blue'),
  ].join('');
}

// ══════ ON-CHAIN ════════════════════════════════════════════
function renderOnchain() {
  const d = DATA;
  document.getElementById('oc-val').innerHTML = [
    kv('MVRV Ratio', d.mvrv!=null?Number(d.mvrv).toFixed(4):'N/A', d.mvrv>3?'neg':d.mvrv<1?'pos':'orange'),
    kv('Realized Cap USD', d.realized_cap_usd!=null?'$'+fmtV(d.realized_cap_usd):'N/A'),
    kv('NUPL', d.nupl!=null?Number(d.nupl).toFixed(4):'N/A', d.nupl>0.75?'neg':d.nupl<0?'pos':'orange'),
    kv('Puell Multiple', d.puell_multiple!=null?Number(d.puell_multiple).toFixed(4):'N/A'),
    kv('Mayer Multiple', d.mayer_multiple!=null?Number(d.mayer_multiple).toFixed(4):'N/A'),
    kv('Supply dans profit', d.supply_profit_pct!=null?Number(d.supply_profit_pct).toFixed(2)+'%':'N/A'),
    kv('ROI depuis 1an', d.roi_1y!=null?fmtP(d.roi_1y*100):'N/A'),
    kv('Flux net exchanges', d.net_flow!=null?fmtV(Math.abs(d.net_flow))+(d.net_flow<0?' sortie':' entrée'):'N/A'),
    kv('Source', 'CoinMetrics Community', 'blue'),
  ].join('');

  document.getElementById('oc-adp').innerHTML = [
    kv('Adresses actives', d.active_addresses!=null?fmtV(d.active_addresses):'N/A'),
    kv('TXs réseau', d.tx_count!=null?fmtV(d.tx_count):'N/A'),
    kv('Vol transferts USD', d.transfer_vol_usd!=null?'$'+fmtV(d.transfer_vol_usd):'N/A'),
    kv('Vol ajusté USD', d.adjusted_vol_usd!=null?'$'+fmtV(d.adjusted_vol_usd):'N/A'),
    kv('Supply achetée >1j', d.supply_1d!=null?fmtV(d.supply_1d)+'BTC':'N/A'),
    kv('Supply >1 an (HODL)', d.supply_1y!=null?fmtV(d.supply_1y)+'BTC':'N/A'),
    kv('Hash rate (TH/s)', d.hash_rate!=null?fmtV(d.hash_rate):'N/A'),
    kv('Difficulté', d.difficulty!=null?fmtV(d.difficulty):'N/A'),
    kv('Source', 'CoinMetrics Community', 'blue'),
  ].join('');

  document.getElementById('oc-roi').innerHTML = [
    kv('ROI 3 mois', d.roi_3m!=null?fmtP(d.roi_3m*100):'N/A'),
    kv('ROI 6 mois', d.roi_6m!=null?fmtP(d.roi_6m*100):'N/A'),
    kv('ROI 1 an', d.roi_1y!=null?fmtP(d.roi_1y*100):'N/A'),
    kv('Miners Revenue', d.miners_revenue!=null?'$'+fmtV(d.miners_revenue):'N/A'),
    kv('Récompense bloc actuelle', '3.125 BTC'),
    kv('Prochain halving ~', '2028'),
    kv('Source', 'CoinMetrics + Blockchain.info', 'blue'),
  ].join('');

  document.getElementById('oc-sopr').innerHTML = [
    kv('aSOPR', d.asopr!=null?Number(d.asopr).toFixed(5):'N/A', d.asopr>1.02?'pos':d.asopr<0.98?'neg':''),
    kv('SOPR', d.sopr!=null?Number(d.sopr).toFixed(5):'N/A'),
    kv('LTH Realized Price', d.lth_realized!=null?'$'+fmt(d.lth_realized):'N/A'),
    kv('STH Realized Price', d.sth_realized!=null?'$'+fmt(d.sth_realized):'N/A'),
    kv('Source', 'BGR bitcoin-data.com', 'blue'),
  ].join('');

  document.getElementById('oc-whale').innerHTML = [
    kv('Baleines >1000 BTC', d.whale_count!=null?fmt(d.whale_count):'N/A'),
    kv('Baleines variation 30j', d.whale_change_30d!=null?fmtP(d.whale_change_30d):'N/A'),
    kv('LTH MVRV proxy', d.lth_mvrv!=null?Number(d.lth_mvrv).toFixed(3):'N/A'),
    kv('STH MVRV proxy', d.sth_mvrv!=null?Number(d.sth_mvrv).toFixed(3):'N/A'),
    kv('Source', 'BGR bitcoin-data.com', 'blue'),
  ].join('');

  document.getElementById('oc-nrpl').innerHTML = [
    kv('NRPL USD', d.nrpl_usd!=null?'$'+fmtV(d.nrpl_usd):'N/A'),
    kv('NRPL BTC', d.nrpl_btc!=null?Number(d.nrpl_btc).toFixed(4)+'BTC':'N/A'),
    kv('Flux sorties exch', d.exchange_outflow!=null?fmtV(d.exchange_outflow):'N/A'),
    kv('Flux entrées exch', d.exchange_inflow!=null?fmtV(d.exchange_inflow):'N/A'),
    kv('Source', 'BGR bitcoin-data.com', 'blue'),
  ].join('');

  document.getElementById('oc-deep').innerHTML = [
    kv('Adresses actives', d.cm_active_addresses!=null?fmt(d.cm_active_addresses):'N/A', 'green'),
    kv('NVT Ratio ajusté', d.cm_nvt_adj!=null?Number(d.cm_nvt_adj).toFixed(2):'N/A', d.cm_nvt_adj>90?'neg':d.cm_nvt_adj<30?'pos':''),
    kv('Supply active 1an', d.cm_sply_act_1yr_btc!=null?fmtV(d.cm_sply_act_1yr_btc)+' BTC':'N/A'),
    kv('Vol transferts adj', d.cm_tx_tfr_val_adj_usd!=null?'$'+fmtV(d.cm_tx_tfr_val_adj_usd):'N/A'),
    kv('Supply actuelle', d.cm_supply_current!=null?fmtV(d.cm_supply_current)+' BTC':'N/A'),
    kv('Source', 'CoinMetrics Community', 'blue'),
  ].join('');

  document.getElementById('oc-positions').innerHTML = [
    kv('Longs BTC (Bitfinex)', d.bfx_longs_btc!=null?Number(d.bfx_longs_btc).toFixed(2)+' BTC':'N/A', 'pos'),
    kv('Shorts BTC (Bitfinex)', d.bfx_shorts_btc!=null?Number(d.bfx_shorts_btc).toFixed(2)+' BTC':'N/A', 'neg'),
    kv('Ratio L/S', d.bfx_ls_ratio!=null?Number(d.bfx_ls_ratio).toFixed(3):'N/A', d.bfx_ls_ratio>1?'pos':'neg'),
    kv('Longs/Shorts Binance', d.bnf_long_pct!=null?`${Number(d.bnf_long_pct).toFixed(1)}% / ${Number(d.bnf_short_pct).toFixed(1)}%`:'N/A'),
    kv('Signal L/S', d.bnf_ls_ratio>1.1?'Surbull':'Overbear':'Neutre'),
    kv('Source', 'Bitfinex Stats + Binance FAPI', 'blue'),
  ].join('');

  document.getElementById('oc-dvol').innerHTML = [
    kv('Deribit DVol (actuel)', d.deribit_dvol!=null?Number(d.deribit_dvol).toFixed(1)+'%':'N/A', d.deribit_dvol>80?'neg':d.deribit_dvol>60?'orange':'pos'),
    kv('Var DVol', d.deribit_dvol_change!=null?(d.deribit_dvol_change>0?'+':'')+Number(d.deribit_dvol_change).toFixed(1)+'%':'N/A'),
    kv('Interprétation', d.deribit_dvol>80?'Volatilité extrême':d.deribit_dvol>60?'Volatilité élevée':d.deribit_dvol>40?'Volatilité modérée':'Volatilité faible'),
    kv('Funding Rate moyen', d.avg_funding_rate_pct!=null?(d.avg_funding_rate_pct>0?'+':'')+Number(d.avg_funding_rate_pct).toFixed(4)+'%':'N/A'),
    kv('Source', 'Deribit DVol API', 'blue'),
  ].join('');
}

// ══════ TECHNIQUE ═══════════════════════════════════════════
function renderTech() {
  const d = DATA;
  document.getElementById('t-ma').innerHTML = [
    kv('Close actuel', d.close_latest!=null?'$'+fmt(d.close_latest,2):'N/A'),
    kv('VWAP (Kraken)', d.vwap!=null?'$'+fmt(d.vwap,2):'N/A'),
    kv('MA 7j', d.ma7!=null?'$'+fmt(d.ma7):'N/A'),
    kv('MA 30j', d.ma30!=null?'$'+fmt(d.ma30):'N/A'),
    kv('MA 200j', d.ma200!=null?'$'+fmt(d.ma200):'N/A'),
    kv('Prix vs MA 7j', d.price_to_ma7!=null?fmtP(d.price_to_ma7):'N/A'),
    kv('Prix vs MA 30j', d.price_to_ma30!=null?fmtP(d.price_to_ma30):'N/A'),
    kv('Prix vs MA 200j', d.price_to_ma200!=null?fmtP(d.price_to_ma200):'N/A'),
    kv('Source', 'Kraken OHLC + calcul', 'blue'),
  ].join('');

  document.getElementById('t-ind').innerHTML = [
    kv('RSI 14j', d.rsi_14!=null?Number(d.rsi_14).toFixed(2):'N/A', d.rsi_14>70?'neg':d.rsi_14<30?'pos':'blue'),
    kv('Interprétation RSI', d.rsi_14>70?'Suracheté':d.rsi_14<30?'Survendu':'Neutre'),
    kv('Mayer Multiple', d.mayer_multiple!=null?Number(d.mayer_multiple).toFixed(4):'N/A'),
    kv('Mayer Interprétation', d.mayer_multiple>2.4?'Bull extrême':d.mayer_multiple<0.8?'Achat':d.mayer_multiple>1?'Haussier':'Baissier'),
    kv('Source', 'Kraken OHLC calculé', 'blue'),
  ].join('');

  document.getElementById('t-risk').innerHTML = [
    kv('Volatilité 30j ann.', d.volatility_30d!=null?Number(d.volatility_30d).toFixed(2)+'%':'N/A'),
    kv('Sharpe 30j', d.sharpe_30d!=null?Number(d.sharpe_30d).toFixed(4):'N/A', d.sharpe_30d>2?'pos':d.sharpe_30d>1?'green':d.sharpe_30d<0?'neg':''),
    kv('Spread arbitrage', d.arbitrage_spread_pct!=null?Number(d.arbitrage_spread_pct).toFixed(4)+'%':'N/A'),
    kv('Plus haut exchange', d.highest_exchange||'N/A'),
    kv('Plus bas exchange', d.lowest_exchange||'N/A'),
    kv('Source', 'Calculs internes + Kraken', 'blue'),
  ].join('');

  const s = STOOQ;
  document.getElementById('t-kraken').innerHTML = [
    kv('Open 30j ago', s.open_30d!=null?'$'+fmt(s.open_30d,2):'N/A'),
    kv('High 30j', s.high_30d!=null?'$'+fmt(s.high_30d,2):'N/A'),
    kv('Low 30j', s.low_30d!=null?'$'+fmt(s.low_30d,2):'N/A'),
    kv('Close dernier', s.close_latest!=null?'$'+fmt(s.close_latest,2):'N/A'),
    kv('Volume moyen 30j', s.avg_vol!=null?fmtV(s.avg_vol):'N/A'),
    kv('Performance 30j', s.perf_30d!=null?fmtP(s.perf_30d):'N/A'),
    kv('Jours disponibles', s.days_available||'N/A'),
    kv('Source', 'Stooq CSV + Kraken OHLC', 'blue'),
  ].join('');
}

// ══════ RESEAU ══════════════════════════════════════════════
function renderReseau() {
  const d = DATA; const n = NET;
  document.getElementById('r-mempool').innerHTML = [
    kv('Frais fastest (sat/vB)', d.fee_fastest_sat!=null?d.fee_fastest_sat:'N/A'),
    kv('Frais moyen (sat/vB)', d.fee_avg_sat!=null?d.fee_avg_sat:'N/A'),
    kv('Frais économique', d.fee_eco_sat!=null?d.fee_eco_sat:'N/A'),
    kv('Frais minimum', d.fee_min_sat!=null?d.fee_min_sat:'N/A'),
    kv('TXs en attente', d.mempool_count!=null?fmt(d.mempool_count):'N/A'),
    kv('Taille mempool (MB)', d.mempool_size_mb!=null?Number(d.mempool_size_mb).toFixed(2):'N/A'),
    kv('Hashrate (EH/s)', d.hashrate_eh!=null?Number(d.hashrate_eh).toFixed(2):'N/A'),
    kv('Difficulté (T)', d.difficulty_t!=null?Number(d.difficulty_t).toFixed(2):'N/A'),
    kv('Prochain ajustement', d.blocks_till_adjust!=null?d.blocks_till_adjust+' blocs':'N/A'),
    kv('Source', 'Mempool.space API', 'blue'),
  ].join('');

  document.getElementById('r-blockchair').innerHTML = [
    kv('Blocs total', d.blocks_total!=null?fmt(d.blocks_total):'N/A'),
    kv('TXs total réseau', d.blockchain_tx_total!=null?fmtV(d.blockchain_tx_total):'N/A'),
    kv('UTXOs total', d.utxo_count!=null?fmtV(d.utxo_count):'N/A'),
    kv('Taille blockchain (GB)', d.blockchain_size_gb!=null?Number(d.blockchain_size_gb).toFixed(2):'N/A'),
    kv('TXs dernières 24h', d.transactions_24h!=null?fmtV(d.transactions_24h):'N/A'),
    kv('Vol on-chain 24h (sat)', d.bc_vol_24h_sat!=null?fmtV(d.bc_vol_24h_sat)+' sat':'N/A'),
    kv('Source', 'Blockchair API', 'blue'),
  ].join('');

  document.getElementById('r-bcinfo').innerHTML = [
    kv('Prix marché (USD)', d.bcinfo_price!=null?'$'+fmt(d.bcinfo_price):'N/A'),
    kv('Hash rate (GH/s)', d.bcinfo_hash!=null?fmtV(d.bcinfo_hash):'N/A'),
    kv('Blocs aujourd\'hui', d.blocks_today!=null?d.blocks_today:'N/A'),
    kv('Revenus mineurs/j', d.miners_revenue!=null?'$'+fmtV(d.miners_revenue):'N/A'),
    kv('TXs dernières 24h', d.tx_24h!=null?fmtV(d.tx_24h):'N/A'),
    kv('Difficulté', d.diff_raw!=null?fmtV(d.diff_raw):'N/A'),
    kv('Supply totale (BTC)', d.supply_btc!=null?fmt(d.supply_btc):'N/A'),
    kv('Taille (bytes)', d.blockchain_bytes!=null?fmtV(d.blockchain_bytes):'N/A'),
    kv('Source', 'Blockchain.info', 'blue'),
  ].join('');

  document.getElementById('r-blockstream').innerHTML = [
    kv('Hauteur de bloc', d.block_height!=null?fmt(d.block_height):'N/A'),
    kv('TXs dans mempool', d.mempool_count!=null?fmt(d.mempool_count):'N/A'),
    kv('Source', 'Blockstream.info', 'blue'),
  ].join('');

  document.getElementById('r-bitnodes').innerHTML = [
    kv('Nœuds P2P totaux', d.bitnodes_total!=null?fmt(d.bitnodes_total):'N/A'),
    kv('Source', 'Bitnodes.io', 'blue'),
  ].join('');

  const pools = d.mining_pools;
  if(pools && typeof pools === 'object') {
    const sorted = Object.entries(pools).sort((a,b)=>b[1]-a[1]).slice(0,6);
    document.getElementById('r-pools').innerHTML = sorted.map(([name,pct]) =>
      `<div class="kv"><span class="k">${name}</span><span class="v">${Number(pct).toFixed(1)}%</span></div>`
    ).join('')+'<div class="kv"><span class="k" style="color:var(--text3);font-size:10px">Source: Blockchain.info</span></div>';
  } else {
    document.getElementById('r-pools').innerHTML = '<p class="err">Données pools non disponibles</p>';
  }

  document.getElementById('r-blocks').innerHTML = [
    kv('Hauteur bloc', d.last_block_height!=null?fmt(d.last_block_height):'N/A', 'orange'),
    kv('TXs dans bloc', d.last_block_txcount!=null?fmt(d.last_block_txcount):'N/A'),
    kv('Taille bloc', d.last_block_size_kb!=null?Number(d.last_block_size_kb).toFixed(1)+' KB':'N/A'),
    kv('Frais médian', d.last_block_median_fee_rate!=null?d.last_block_median_fee_rate+' sat/vB':'N/A'),
    kv('Pool mineur', d.last_block_pool||'N/A', 'blue'),
    kv('Moy TXs (10 blocs)', d.blocks_avg_tx_count!=null?fmt(d.blocks_avg_tx_count):'N/A'),
    kv('Moy taille (10 blocs)', d.blocks_avg_size_kb!=null?Number(d.blocks_avg_size_kb).toFixed(1)+' KB':'N/A'),
    kv('Source', 'Mempool.space /v1/blocks', 'blue'),
  ].join('');

  document.getElementById('r-bcharts').innerHTML = [
    kv('Hashrate actuel', d.bchart_hashrate_now_eh!=null?Number(d.bchart_hashrate_now_eh).toFixed(2)+' EH/s':'N/A', 'orange'),
    kv('Hashrate moy 30j', d.bchart_hashrate_30d_avg_eh!=null?Number(d.bchart_hashrate_30d_avg_eh).toFixed(2)+' EH/s':'N/A'),
    kv('TXs aujourd\'hui', d.bchart_txcount_today!=null?fmt(d.bchart_txcount_today):'N/A'),
    kv('Moy TXs/j (30j)', d.bchart_txcount_30d_avg!=null?fmt(d.bchart_txcount_30d_avg):'N/A'),
    kv('Frais USD (7j)', d.bchart_fees_usd_today!=null?'$'+fmt(d.bchart_fees_usd_today,2):'N/A'),
    kv('Source', 'Blockchain.info Charts API', 'blue'),
  ].join('');

  document.getElementById('r-wtm').innerHTML = [
    kv('Profitabilité', d.wtm_btc_profitability!=null?Number(d.wtm_btc_profitability).toFixed(1)+'%':'N/A', d.wtm_btc_profitability>100?'pos':d.wtm_btc_profitability<80?'neg':''),
    kv('Nethash (EH/s)', d.wtm_btc_nethash_th!=null?(Number(d.wtm_btc_nethash_th)/1e18).toFixed(2)+' EH/s':'N/A'),
    kv('Difficulté', d.wtm_btc_difficulty!=null?fmtV(d.wtm_btc_difficulty):'N/A'),
    kv('Récompense bloc', d.wtm_btc_block_reward!=null?Number(d.wtm_btc_block_reward).toFixed(4)+' BTC':'N/A'),
    kv('Temps par bloc', d.wtm_btc_block_time!=null?Number(d.wtm_btc_block_time).toFixed(1)+' sec':'N/A'),
    kv('Source', 'WhatToMine.com API', 'blue'),
  ].join('');
}

// ══════ LIGHTNING ════════════════════════════════════════════
function renderLightning() {
  const d = DATA;
  document.getElementById('ln-nodes').textContent = d.ln_nodes!=null?fmt(d.ln_nodes):'---';
  document.getElementById('ln-chan').textContent = d.ln_channels!=null?fmt(d.ln_channels):'---';
  document.getElementById('ln-cap-btc').textContent = d.ln_capacity_btc!=null?fmt(d.ln_capacity_btc)+' BTC':'---';
  document.getElementById('ln-cap-usd').textContent = d.ln_capacity_usd!=null?'$'+fmtV(d.ln_capacity_usd):'---';
  document.getElementById('ln-avg-cap').textContent = d.ln_avg_capacity!=null?fmt(d.ln_avg_capacity):'---';
  document.getElementById('ln-nodes-src').textContent = 'Mempool.space';
  document.getElementById('ln-chan-src').textContent = 'Mempool.space';

  document.getElementById('ln-mempool').innerHTML = [
    kv('Nœuds', d.ln_nodes!=null?fmt(d.ln_nodes):'N/A', 'blue'),
    kv('Canaux', d.ln_channels!=null?fmt(d.ln_channels):'N/A', 'purple'),
    kv('Capacité totale (BTC)', d.ln_capacity_btc!=null?fmt(d.ln_capacity_btc):'N/A', 'orange'),
    kv('Capacité totale (USD)', d.ln_capacity_usd!=null?'$'+fmtV(d.ln_capacity_usd):'N/A'),
    kv('Capacité moy/canal (sat)', d.ln_avg_capacity!=null?fmt(d.ln_avg_capacity):'N/A'),
    kv('Source', 'Mempool.space Lightning API', 'blue'),
  ].join('');

  document.getElementById('ln-1ml').innerHTML = [
    kv('Nœuds 1ML', d.ln_1ml_nodes!=null?fmt(d.ln_1ml_nodes):'N/A', 'blue'),
    kv('Canaux 1ML', d.ln_1ml_channels!=null?fmt(d.ln_1ml_channels):'N/A'),
    kv('Var nœuds 30j', d.ln_1ml_node_growth!=null?fmtP(d.ln_1ml_node_growth):'N/A'),
    kv('Var canaux 30j', d.ln_1ml_chan_growth!=null?fmtP(d.ln_1ml_chan_growth):'N/A'),
    kv('Source', '1ML.com Statistics API', 'blue'),
  ].join('');
}

// ══════ EXCHANGES USD ═══════════════════════════════════════
function renderExchanges() {
  const ex = EX; const d = DATA;
  const count = ex.exchange_count || d.exchange_count;
  const avg = ex.avg_price || d.avg_price;
  const spread = ex.arbitrage_spread_pct || d.arbitrage_spread_pct;

  document.getElementById('ex-count').textContent = count||'--';
  document.getElementById('ex-avg').textContent = avg?'$'+fmt(avg,2):'---';
  document.getElementById('ex-spread').textContent = spread?Number(spread).toFixed(4)+'%':'--';
  document.getElementById('ex-high').textContent = (ex.highest_exchange||d.highest_exchange)||'--';
  document.getElementById('ex-low').textContent = (ex.lowest_exchange||d.lowest_exchange)||'--';

  const prices = (ex.exchange_prices||d.exchange_prices||[]);
  const tbody = document.querySelector('#ex-table tbody');
  tbody.innerHTML = prices.map((row,i)=> {
    const diff = avg&&row.price ? ((row.price-avg)/avg*100) : 0;
    const barW = Math.min(Math.abs(diff)*500, 100);
    return `<tr>
      <td class="rank">${i+1}</td>
      <td class="ex-name">${row.name}</td>
      <td class="ex-price">$${fmt(row.price,2)}</td>
      <td style="color:${diff>0?'var(--green)':diff<0?'var(--red)':'var(--text2)'};font-weight:600">${diff>0?'+':''}${diff.toFixed(4)}%</td>
      <td style="width:80px"><span class="spread-bar" style="width:${barW}%;background:${Math.abs(diff)<0.1?'var(--green)':Math.abs(diff)<0.5?'var(--yellow)':'var(--red)'}"></span></td>
    </tr>`;
  }).join('');

  document.getElementById('ex-deribit').innerHTML = [
    kv('Index Price', d.deribit_index_price!=null?'$'+fmt(d.deribit_index_price,2):'N/A'),
    kv('Perpétuel BTC', d.deribit_perp_price!=null?'$'+fmt(d.deribit_perp_price,2):'N/A'),
    kv('Funding Rate', d.deribit_funding!=null?Number(d.deribit_funding*100).toFixed(6)+'%':'N/A'),
    kv('Open Interest', d.deribit_oi!=null?'$'+fmtV(d.deribit_oi):'N/A'),
    kv('Source', 'Deribit.com API', 'blue'),
  ].join('');

  document.getElementById('ex-poloniex').innerHTML = [
    kv('Prix', ex.poloniex_price!=null?'$'+fmt(ex.poloniex_price,2):'N/A'),
    kv('High 24h', ex.poloniex_high_24h!=null?'$'+fmt(ex.poloniex_high_24h,2):'N/A'),
    kv('Low 24h', ex.poloniex_low_24h!=null?'$'+fmt(ex.poloniex_low_24h,2):'N/A'),
    kv('Volume USD 24h', ex.poloniex_vol_usd!=null?'$'+fmtV(ex.poloniex_vol_usd):'N/A'),
    kv('Variation 24h', ex.poloniex_change_24h!=null?fmtP(ex.poloniex_change_24h):'N/A'),
    kv('Source', 'Poloniex API', 'blue'),
  ].join('');

  document.getElementById('ex-cdotcom').innerHTML = [
    kv('Prix (Ask)', ex.cdotcom_price!=null?'$'+fmt(ex.cdotcom_price,2):'N/A'),
    kv('High 24h', ex.cdotcom_high_24h!=null?'$'+fmt(ex.cdotcom_high_24h,2):'N/A'),
    kv('Low 24h', ex.cdotcom_low_24h!=null?'$'+fmt(ex.cdotcom_low_24h,2):'N/A'),
    kv('Volume USD 24h', ex.cdotcom_vol_usd!=null?'$'+fmtV(ex.cdotcom_vol_usd):'N/A'),
    kv('Variation 24h', ex.cdotcom_change_24h!=null?fmtP(ex.cdotcom_change_24h):'N/A'),
    kv('Source', 'Crypto.com API v2', 'blue'),
  ].join('');

  document.getElementById('ex-bitmart').innerHTML = [
    kv('Prix', ex.bitmart_price!=null?'$'+fmt(ex.bitmart_price,2):'N/A'),
    kv('High 24h', ex.bitmart_high_24h!=null?'$'+fmt(ex.bitmart_high_24h,2):'N/A'),
    kv('Low 24h', ex.bitmart_low_24h!=null?'$'+fmt(ex.bitmart_low_24h,2):'N/A'),
    kv('Volume USD 24h', ex.bitmart_vol_usd!=null?'$'+fmtV(ex.bitmart_vol_usd):'N/A'),
    kv('Variation 24h', ex.bitmart_change_24h!=null?fmtP(ex.bitmart_change_24h):'N/A'),
    kv('Source', 'BitMart API', 'blue'),
  ].join('');

  document.getElementById('ex-btse').innerHTML = [
    kv('Prix Last', ex.btse_price!=null?'$'+fmt(ex.btse_price,2):'N/A'),
    kv('Index Price', ex.btse_index_price!=null?'$'+fmt(ex.btse_index_price,2):'N/A'),
    kv('Source', 'BTSE Exchange API', 'blue'),
  ].join('');

  document.getElementById('ex-coinlore').innerHTML = [
    kv('Prix USD', ex.coinlore_price!=null?'$'+fmt(ex.coinlore_price,2):'N/A'),
    kv('Market Cap', ex.coinlore_market_cap!=null?'$'+fmtV(ex.coinlore_market_cap):'N/A'),
    kv('Volume 24h', ex.coinlore_vol_24h!=null?'$'+fmtV(ex.coinlore_vol_24h):'N/A'),
    kv('Variation 24h', ex.coinlore_change_24h!=null?fmtP(ex.coinlore_change_24h):'N/A'),
    kv('Variation 7j', ex.coinlore_change_7d!=null?fmtP(ex.coinlore_change_7d):'N/A'),
    kv('Rang global', ex.coinlore_rank!=null?'#'+ex.coinlore_rank:'N/A'),
    kv('Source', 'CoinLore API', 'blue'),
  ].join('');

  document.getElementById('ex-dex').innerHTML = [
    kv('Prix WBTC/USD', d.dex_wbtc_price_usd!=null?'$'+fmt(d.dex_wbtc_price_usd,2):'N/A'),
    kv('Liquidité USD', d.dex_liquidity!=null?'$'+fmtV(d.dex_liquidity):'N/A'),
    kv('Volume 24h USD', d.dex_volume_24h!=null?'$'+fmtV(d.dex_volume_24h):'N/A'),
    kv('Pool Uniswap', d.dex_pair||'WBTC/ETH'),
    kv('Réseau', 'Ethereum Mainnet'),
    kv('Source', 'DexScreener API', 'blue'),
  ].join('');
}

// ══════ INTERNATIONAL ═══════════════════════════════════════
function renderIntl() {
  const i = INTL; const d = DATA;

  const fxPairs = [
    {cur:'JPY',flag:'🇯🇵',ref:i.btc_jpy_ref},
    {cur:'KRW',flag:'🇰🇷',ref:i.btc_krw_ref},
    {cur:'AUD',flag:'🇦🇺',ref:i.btc_aud_ref},
    {cur:'BRL',flag:'🇧🇷',ref:i.btc_brl_ref},
    {cur:'ZAR',flag:'🇿🇦',ref:i.btc_zar_ref},
    {cur:'MXN',flag:'🇲🇽',ref:i.btc_mxn_ref},
    {cur:'INR',flag:'🇮🇳',ref:i.btc_inr_ref},
    {cur:'IDR',flag:'🇮🇩',ref:i.btc_idr_ref},
    {cur:'TRY',flag:'🇹🇷',ref:i.btc_try_ref||i.btc_try},
    {cur:'EUR',flag:'🇪🇺',ref:i.btc_eur_ref||i.btc_eur},
    {cur:'GBP',flag:'🇬🇧',ref:i.btc_gbp_ref||i.btc_gbp},
  ];
  document.getElementById('intl-fx').innerHTML = fxPairs.map(f=>
    `<div class="card-sm"><div style="font-size:18px">${f.flag}</div><div style="font-weight:700;color:var(--orange);font-size:12px">${f.cur}</div><div style="font-size:11px">${f.ref!=null?'₿ = '+fmt(f.ref)+' '+f.cur:'N/A'}</div></div>`
  ).join('');

  document.getElementById('intl-jp').innerHTML = [
    mkExCard('bitFlyer', '🇯🇵', i.bitflyer_price_jpy, 'JPY', i.bitflyer_price_usd, i.bitflyer_vol_jpy, i.bitflyer_ask_jpy, i.bitflyer_bid_jpy),
    mkExCard('Coincheck', '🇯🇵', i.coincheck_price_jpy, 'JPY', i.coincheck_price_usd, i.coincheck_vol_jpy),
    mkExCard('Zaif', '🇯🇵', i.zaif_price_jpy, 'JPY', i.zaif_price_usd, null, null, null, i.zaif_vwap_jpy),
  ].join('');

  document.getElementById('intl-kr').innerHTML = [
    mkExCard('Upbit', '🇰🇷', i.upbit_price_krw, 'KRW', i.upbit_price_usd, i.upbit_vol_krw),
    mkExCard('Bithumb', '🇰🇷', i.bithumb_price_krw, 'KRW', i.bithumb_price_usd, null, i.bithumb_ask_krw, i.bithumb_bid_krw),
    mkExCard('Korbit', '🇰🇷', i.korbit_price_krw, 'KRW', i.korbit_price_usd, i.korbit_vol_btc),
  ].join('');

  document.getElementById('intl-au-ru').innerHTML = [
    mkExCard('BTCMarkets', '🇦🇺', i.btcmarkets_price_aud, 'AUD', i.btcmarkets_price_usd, i.btcmarkets_vol_btc, i.btcmarkets_ask_aud, i.btcmarkets_bid_aud),
    mkExCard('Exmo', '🇷🇺', i.exmo_price_usd, 'USD', i.exmo_price_usd, i.exmo_vol_btc, null, null, null, 'Russie/Europe de l\'Est'),
    `<div class="card"><div class="kv"><span class="k">Source</span><span class="v blue">Exmo + BTCMarkets API</span></div></div>`,
  ].join('');

  document.getElementById('intl-tr').innerHTML = [
    mkExCard('BtcTurk', '🇹🇷', i.btcturk_price_usdt, 'USDT', i.btcturk_price_usd, i.btcturk_vol_btc),
    mkExCard('Paribu', '🇹🇷', i.paribu_price_try, 'TRY', i.paribu_price_usd),
  ].join('');

  document.getElementById('intl-br').innerHTML = [
    mkExCard('Mercado Bitcoin', '🇧🇷', i.mercado_price_brl, 'BRL', i.mercado_price_usd, i.mercado_vol_brl),
    mkExCard('Foxbit', '🇧🇷', i.foxbit_price_brl||i.foxbit_price_usd, i.foxbit_price_brl?'BRL':'USD', i.foxbit_price_usd, null, null, null, null, 'foxbit.com.br'),
    mkExCard('NovaDax', '🇧🇷', i.novadax_price_brl, 'BRL', i.novadax_price_usd, i.novadax_vol_brl),
  ].join('');

  document.getElementById('intl-za').innerHTML = [
    mkExCard('Luno', '🇿🇦', i.luno_price_zar, 'ZAR', i.luno_price_usd, i.luno_vol_24h, i.luno_ask_zar, i.luno_bid_zar),
    mkExCard('VALR', '🇿🇦', i.valr_price_zar, 'ZAR', i.valr_price_usd, null, i.valr_ask_zar, i.valr_bid_zar),
  ].join('');

  document.getElementById('intl-mx').innerHTML = [
    mkExCard('Bitso', '🇲🇽', i.bitso_price_mxn, 'MXN', i.bitso_price_usd, i.bitso_vol, i.bitso_ask_mxn, i.bitso_bid_mxn),
    `<div class="card"><div class="section-title" style="margin-top:0">Bitso — Données Extra</div>${[
      kv('High 24h', i.bitso_high_mxn!=null?fmt(i.bitso_high_mxn,2)+' MXN':'N/A'),
      kv('Low 24h', i.bitso_low_mxn!=null?fmt(i.bitso_low_mxn,2)+' MXN':'N/A'),
      kv('Source', 'Bitso.com REST API', 'blue'),
    ].join('')}</div>`,
  ].join('');

  document.getElementById('intl-in').innerHTML = [
    mkExCard('CoinDCX', '🇮🇳', i.coindcx_price_inr, 'INR', i.coindcx_price_usd, i.coindcx_vol, null, null, null, 'coindcx.com'),
    mkExCard('WazirX', '🇮🇳', i.wazirx_price_inr, 'INR', i.wazirx_price_usd, i.wazirx_vol),
  ].join('');

  document.getElementById('intl-id').innerHTML = [
    mkExCard('Indodax', '🇮🇩', i.indodax_price_idr, 'IDR', i.indodax_price_usd, i.indodax_vol_btc),
    `<div class="card"><div class="section-title" style="margin-top:0">Indodax — Données Extra</div>${[
      kv('High IDR', i.indodax_high_idr!=null?fmt(i.indodax_high_idr)+' IDR':'N/A'),
      kv('Low IDR', i.indodax_low_idr!=null?fmt(i.indodax_low_idr)+' IDR':'N/A'),
      kv('Vol BTC', i.indodax_vol_btc!=null?i.indodax_vol_btc+' BTC':'N/A'),
      kv('Source', 'Indodax.com API', 'blue'),
    ].join('')}</div>`,
  ].join('');
}

function mkExCard(name, flag, nativePrice, nativeCur, usdPrice, vol, ask, bid, extra, sub) {
  return `<div class="card">
    <div style="display:flex;align-items:center;gap:6px;margin-bottom:8px">
      <span style="font-size:16px">${flag}</span>
      <span style="font-weight:700;font-size:13px">${name}</span>
      ${sub?`<span style="color:var(--text3);font-size:10px">${sub}</span>`:''}
    </div>
    ${kv(`Prix (${nativeCur})`, nativePrice!=null?fmt(nativePrice,2)+' '+nativeCur:'N/A', 'orange')}
    ${usdPrice!=null?kv('≈ USD', '$'+fmt(usdPrice,2)):''}
    ${vol!=null?kv('Volume', fmtV(Number(vol))):''}
    ${ask!=null?kv('Ask', fmt(ask,2)+' '+nativeCur):''}
    ${bid!=null?kv('Bid', fmt(bid,2)+' '+nativeCur):''}
    ${extra!=null?kv('Extra', extra):''}
  </div>`;
}

// ══════ ETF ════════════════════════════════════════════════
function renderEtf() {
  const d = DATA;
  document.getElementById('etf-aum').innerHTML = d.etf_total_aum_usd!=null?'$'+fmtV(d.etf_total_aum_usd):'<span class="err">---</span>';
  const flow = d.etf_daily_inflow_usd;
  document.getElementById('etf-flow-day').innerHTML = flow!=null?`<span class="${flow>0?'pos':'neg'}">${flow>0?'+':''}${fmtV(flow)}</span>`:'<span class="err">---</span>';
  document.getElementById('etf-flow-cum').innerHTML = d.etf_cum_inflow_usd!=null?'$'+fmtV(d.etf_cum_inflow_usd):'<span class="err">---</span>';
  document.getElementById('etf-btc-held').innerHTML = d.etf_total_btc_held!=null?fmt(d.etf_total_btc_held)+' BTC':'<span class="err">---</span>';

  document.getElementById('etf-soso').innerHTML = [
    kv('AUM Total', d.etf_total_aum_usd!=null?'$'+fmtV(d.etf_total_aum_usd):'N/A (clé non configurée)', 'orange'),
    kv('Flux net jour', d.etf_daily_inflow_usd!=null?'$'+fmtV(d.etf_daily_inflow_usd):'N/A', d.etf_daily_inflow_usd>0?'pos':d.etf_daily_inflow_usd<0?'neg':''),
    kv('Flux net cumulé', d.etf_cum_inflow_usd!=null?'$'+fmtV(d.etf_cum_inflow_usd):'N/A', 'blue'),
    kv('BTC détenus total', d.etf_total_btc_held!=null?fmt(d.etf_total_btc_held)+' BTC':'N/A', 'green'),
    kv('Volume journalier', d.etf_daily_vol_usd!=null?'$'+fmtV(d.etf_daily_vol_usd):'N/A'),
    kv('Signal', d.etf_signal||'N/A'),
    kv('Données date', d.etf_date||'N/A'),
    kv('Source', 'SoSoValue ETF API (clé)', 'yellow'),
  ].join('');

  document.getElementById('etf-12d').innerHTML = [
    kv('IBIT (BlackRock)', d.etf_ibit_price!=null?'$'+fmt(d.etf_ibit_price,2)+(d.etf_ibit_change!=null?' ('+fmtP(d.etf_ibit_change)+')'):'N/A'),
    kv('IBIT Volume', d.etf_ibit_vol!=null?fmtV(d.etf_ibit_vol):'N/A'),
    kv('FBTC (Fidelity)', d.etf_fbtc_price!=null?'$'+fmt(d.etf_fbtc_price,2)+(d.etf_fbtc_change!=null?' ('+fmtP(d.etf_fbtc_change)+')'):'N/A'),
    kv('ARKB (ARK)', d.etf_arkb_price!=null?'$'+fmt(d.etf_arkb_price,2)+(d.etf_arkb_change!=null?' ('+fmtP(d.etf_arkb_change)+')'):'N/A'),
    kv('GBTC (Grayscale)', d.etf_gbtc_price!=null?'$'+fmt(d.etf_gbtc_price,2)+(d.etf_gbtc_change!=null?' ('+fmtP(d.etf_gbtc_change)+')'):'N/A'),
    kv('HODL (VanEck)', d.etf_hodl_price!=null?'$'+fmt(d.etf_hodl_price,2)+(d.etf_hodl_change!=null?' ('+fmtP(d.etf_hodl_change)+')'):'N/A'),
    kv('Source', 'TwelveData ETF API (clé)', 'yellow'),
  ].join('');
}

// ══════ ALERTES ═════════════════════════════════════════════
function renderAlertes() {
  const signals = Array.isArray(ALERTS) ? ALERTS : (DATA.alerts||[]);
  const buyS = signals.filter(a=>a.type==='buy');
  const sellS = signals.filter(a=>a.type==='sell');
  const neutS = signals.filter(a=>a.type==='neutral');
  const all = [...buyS,...neutS,...sellS];
  document.getElementById('al-signals').innerHTML = all.length
    ? all.map(s=>`<div class="signal ${s.type}"><div class="signal-title">${s.indicator||s.title||s.type.toUpperCase()}</div><div class="signal-desc">${s.message||s.description||''}</div></div>`).join('')
    : '<p class="err">Aucun signal disponible (données on-chain non chargées)</p>';

  document.getElementById('al-tech-signals').innerHTML = [
    `<div class="signal ${DATA.rsi_14>70?'sell':DATA.rsi_14<30?'buy':'neutral'}">
      <div class="signal-title">RSI 14j = ${DATA.rsi_14!=null?Number(DATA.rsi_14).toFixed(1):'N/A'}</div>
      <div class="signal-desc">${DATA.rsi_14>70?'RSI suracheté — Attention':DATA.rsi_14<30?'RSI survendu — Opportunité':'RSI neutre'}</div>
    </div>`,
    `<div class="signal ${DATA.mvrv>3.7?'sell':DATA.mvrv<1?'buy':'neutral'}">
      <div class="signal-title">MVRV = ${DATA.mvrv!=null?Number(DATA.mvrv).toFixed(3):'N/A'}</div>
      <div class="signal-desc">${DATA.mvrv>3.7?'MVRV élevé — Zone de vente historique':DATA.mvrv<1?'MVRV < 1 — Zone d\'achat historique':'MVRV neutre'}</div>
    </div>`,
    `<div class="signal ${DATA.fear_greed_value>80?'sell':DATA.fear_greed_value<20?'buy':'neutral'}">
      <div class="signal-title">Fear & Greed = ${DATA.fear_greed_value||'N/A'} (${DATA.fear_greed_label||''})</div>
      <div class="signal-desc">${DATA.fear_greed_value>80?'Greed extrême — Prudence':DATA.fear_greed_value<20?'Fear extrême — Opportunité historique':'Zone neutre'}</div>
    </div>`,
  ].join('');
}

// ══════ DÉRIVÉS ══════════════════════════════════════════════
function renderDerivatives() {
  const d = DRV;
  const fr = d.avg_funding_rate_pct;
  document.getElementById('drv-funding').innerHTML = fr!=null
    ? `<span class="${fr>0?'neg':fr<-0.01?'pos':''}">${fr>0?'+':''}${Number(fr).toFixed(4)}%</span>`
    : '<span class="err">---</span>';
  document.getElementById('drv-ls').innerHTML = d.bnf_ls_ratio!=null
    ? (d.bnf_long_pct!=null?`<span class="pos">${Number(d.bnf_long_pct).toFixed(1)}% L</span> / <span class="neg">${Number(d.bnf_short_pct).toFixed(1)}% S</span>`:'---')
    : '<span class="err">---</span>';
  document.getElementById('drv-oi').innerHTML = d.bnf_oi_btc!=null
    ? fmt(d.bnf_oi_btc,0)+' BTC'
    : '<span class="err">---</span>';
  document.getElementById('drv-dvol').innerHTML = d.deribit_dvol!=null
    ? Number(d.deribit_dvol).toFixed(1)+'%'
    : '<span class="err">---</span>';

  document.getElementById('drv-binance').innerHTML = [
    kv('Mark Price', d.bnf_mark_price!=null?'$'+fmt(d.bnf_mark_price,2):'N/A', 'orange'),
    kv('Index Price', d.bnf_index_price!=null?'$'+fmt(d.bnf_index_price,2):'N/A'),
    kv('Funding Rate', d.bnf_funding_rate!=null?(d.bnf_funding_rate>0?'+':'')+Number(d.bnf_funding_rate).toFixed(6)+'%':'N/A', d.bnf_funding_rate>0.1?'neg':d.bnf_funding_rate<-0.05?'pos':''),
    kv('Open Interest (BTC)', d.bnf_oi_btc!=null?fmt(d.bnf_oi_btc,0)+' BTC':'N/A', 'blue'),
    kv('Volume 24h USD', d.bnf_vol_usd!=null?'$'+fmtV(d.bnf_vol_usd):'N/A'),
    kv('Longs / Shorts', d.bnf_long_pct!=null?`${Number(d.bnf_long_pct).toFixed(1)}% / ${Number(d.bnf_short_pct).toFixed(1)}%`:'N/A'),
    kv('Signal Funding', d.funding_signal||'N/A'),
    kv('Source', 'Binance FAPI (gratuit)', 'blue'),
  ].join('');

  document.getElementById('drv-kraken').innerHTML = [
    kv('Last Price', d.krf_last_price!=null?'$'+fmt(d.krf_last_price,2):'N/A', 'orange'),
    kv('Mark Price', d.krf_mark_price!=null?'$'+fmt(d.krf_mark_price,2):'N/A'),
    kv('Bid / Ask', (d.krf_bid&&d.krf_ask)?'$'+fmt(d.krf_bid,2)+' / $'+fmt(d.krf_ask,2):'N/A'),
    kv('Funding Rate', d.krf_funding_rate!=null?(d.krf_funding_rate>0?'+':'')+Number(d.krf_funding_rate).toFixed(6)+'%':'N/A'),
    kv('OI (contrats)', d.krf_oi_contracts!=null?fmt(d.krf_oi_contracts):'N/A'),
    kv('Volume 24h', d.krf_vol_24h!=null?fmtV(d.krf_vol_24h):'N/A'),
    kv('Source', 'Kraken Futures API (gratuit)', 'blue'),
  ].join('');

  document.getElementById('drv-bitmex').innerHTML = [
    kv('Last Price', d.bitmex_last_price!=null?'$'+fmt(d.bitmex_last_price,2):'N/A', 'orange'),
    kv('Mark Price', d.bitmex_mark_price!=null?'$'+fmt(d.bitmex_mark_price,2):'N/A'),
    kv('Funding Rate', d.bitmex_funding_rate!=null?(d.bitmex_funding_rate>0?'+':'')+Number(d.bitmex_funding_rate).toFixed(6)+'%':'N/A'),
    kv('OI (contrats USD)', d.bitmex_oi_contracts!=null?fmt(d.bitmex_oi_contracts):'N/A'),
    kv('Volume 24h (BTC)', d.bitmex_vol_24h_btc!=null?Number(d.bitmex_vol_24h_btc).toFixed(2)+' BTC':'N/A'),
    kv('Source', 'BitMEX API v1 (gratuit)', 'blue'),
  ].join('');

  document.getElementById('drv-hyper').innerHTML = [
    kv('Mark Price', d.hyper_mark_price!=null?'$'+fmt(d.hyper_mark_price,2):'N/A', 'orange'),
    kv('Mid Price', d.hyper_mid_price!=null?'$'+fmt(d.hyper_mid_price,2):'N/A'),
    kv('Funding Rate', d.hyper_funding_rate!=null?(d.hyper_funding_rate>0?'+':'')+Number(d.hyper_funding_rate).toFixed(6)+'%':'N/A'),
    kv('OI (USD)', d.hyper_oi_usd!=null?'$'+fmtV(d.hyper_oi_usd):'N/A', 'blue'),
    kv('Volume 24h USD', d.hyper_vol_24h_usd!=null?'$'+fmtV(d.hyper_vol_24h_usd):'N/A'),
    kv('Type', 'DEX (décentralisé)'),
    kv('Source', 'Hyperliquid API (gratuit)', 'blue'),
  ].join('');

  document.getElementById('drv-bitget').innerHTML = [
    kv('Last Price', d.bgf_last_price!=null?'$'+fmt(d.bgf_last_price,2):'N/A', 'orange'),
    kv('Mark Price', d.bgf_mark_price!=null?'$'+fmt(d.bgf_mark_price,2):'N/A'),
    kv('Index Price', d.bgf_index_price!=null?'$'+fmt(d.bgf_index_price,2):'N/A'),
    kv('Funding Rate', d.bgf_funding_rate!=null?(d.bgf_funding_rate>0?'+':'')+Number(d.bgf_funding_rate).toFixed(6)+'%':'N/A'),
    kv('OI (USD)', d.bgf_oi_usd!=null?'$'+fmtV(d.bgf_oi_usd):'N/A'),
    kv('Volume 24h USD', d.bgf_vol_usd!=null?'$'+fmtV(d.bgf_vol_usd):'N/A'),
    kv('Source', 'Bitget Futures API (gratuit)', 'blue'),
  ].join('');

  document.getElementById('drv-bfxstats').innerHTML = [
    kv('Longs BTC (Bitfinex)', d.bfx_longs_btc!=null?Number(d.bfx_longs_btc).toFixed(2)+' BTC':'N/A', 'pos'),
    kv('Shorts BTC (Bitfinex)', d.bfx_shorts_btc!=null?Number(d.bfx_shorts_btc).toFixed(2)+' BTC':'N/A', 'neg'),
    kv('Ratio L/S', d.bfx_ls_ratio!=null?Number(d.bfx_ls_ratio).toFixed(3):'N/A', d.bfx_ls_ratio>1?'pos':'neg'),
    kv('Deribit DVol', d.deribit_dvol!=null?Number(d.deribit_dvol).toFixed(1)+'%':'N/A', 'purple'),
    kv('Var DVol', d.deribit_dvol_change!=null?(d.deribit_dvol_change>0?'+':'')+Number(d.deribit_dvol_change).toFixed(1)+'%':'N/A'),
    kv('Source', 'Bitfinex Stats + Deribit DVol', 'blue'),
  ].join('');
}

// ══════ DEFI / ANALYTICS ════════════════════════════════════
function renderDefi() {
  const d = DEFI;
  document.getElementById('defi-btc-tvl').innerHTML = d.btc_chain_tvl_usd!=null?'$'+fmtV(d.btc_chain_tvl_usd):'<span class="err">---</span>';
  document.getElementById('defi-wbtc').innerHTML = d.wbtc_tvl_usd!=null?'$'+fmtV(d.wbtc_tvl_usd):'<span class="err">---</span>';
  document.getElementById('defi-messari-price').innerHTML = d.messari_price!=null?'$'+fmt(d.messari_price,2):'<span class="err">---</span>';
  document.getElementById('defi-cc-close').innerHTML = d.cc_close!=null?'$'+fmt(d.cc_close,2):'<span class="err">---</span>';
  document.getElementById('defi-cc-high').textContent = d.cc_high_30d!=null?'$'+fmt(d.cc_high_30d,0):'---';

  document.getElementById('defi-llama').innerHTML = [
    kv('TVL Bitcoin Chain (natif)', d.btc_chain_tvl_usd!=null?'$'+fmtV(d.btc_chain_tvl_usd):'N/A', 'orange'),
    kv('WBTC TVL (Ethereum)', d.wbtc_tvl_usd!=null?'$'+fmtV(d.wbtc_tvl_usd):'N/A', 'green'),
    kv('tBTC TVL', d.tbtc_tvl_usd!=null?'$'+fmtV(d.tbtc_tvl_usd):'N/A'),
    kv('Babylon (BTC staking)', d.babylon_tvl_usd!=null?'$'+fmtV(d.babylon_tvl_usd):'N/A', 'blue'),
    kv('Lombard Finance (LBTC)', d.lombard_tvl_usd!=null?'$'+fmtV(d.lombard_tvl_usd):'N/A'),
    kv('Source', 'DefiLlama API (gratuit)', 'blue'),
  ].join('');

  document.getElementById('defi-messari').innerHTML = [
    kv('Prix USD', d.messari_price!=null?'$'+fmt(d.messari_price,2):'N/A', 'orange'),
    kv('Volume 24h', d.messari_vol_24h!=null?'$'+fmtV(d.messari_vol_24h):'N/A'),
    kv('Market Cap', d.messari_market_cap!=null?'$'+fmtV(d.messari_market_cap):'N/A'),
    kv('ATH Prix', d.messari_ath_price!=null?'$'+fmt(d.messari_ath_price,0):'N/A', 'purple'),
    kv('Distance ATH', d.messari_pct_from_ath!=null?Number(d.messari_pct_from_ath).toFixed(1)+'%':'N/A', d.messari_pct_from_ath<-50?'neg':d.messari_pct_from_ath>-10?'pos':''),
    kv('Variation 7j', d.messari_chg_7d!=null?(d.messari_chg_7d>0?'+':'')+Number(d.messari_chg_7d).toFixed(2)+'%':'N/A', d.messari_chg_7d>0?'pos':'neg'),
    kv('Variation 30j', d.messari_chg_30d!=null?(d.messari_chg_30d>0?'+':'')+Number(d.messari_chg_30d).toFixed(2)+'%':'N/A', d.messari_chg_30d>0?'pos':'neg'),
    kv('Variation 1an', d.messari_chg_1y!=null?(d.messari_chg_1y>0?'+':'')+Number(d.messari_chg_1y).toFixed(1)+'%':'N/A', d.messari_chg_1y>0?'pos':'neg'),
    kv('Supply minée', d.messari_supply_mined!=null?fmt(d.messari_supply_mined)+' BTC':'N/A'),
    kv('% Supply émise', d.messari_supply_pct!=null?Number(d.messari_supply_pct).toFixed(2)+'%':'N/A'),
    kv('Source', 'CoinPaprika Extended (gratuit)', 'blue'),
  ].join('');

  document.getElementById('defi-cc').innerHTML = [
    kv('Close (hier)', d.cc_close!=null?'$'+fmt(d.cc_close,2):'N/A', 'orange'),
    kv('High (hier)', d.cc_high!=null?'$'+fmt(d.cc_high,2):'N/A'),
    kv('Low (hier)', d.cc_low!=null?'$'+fmt(d.cc_low,2):'N/A'),
    kv('Volume USD 24h', d.cc_vol_usd_24h!=null?'$'+fmtV(d.cc_vol_usd_24h):'N/A'),
    kv('High 30j', d.cc_high_30d!=null?'$'+fmt(d.cc_high_30d,0):'N/A', 'green'),
    kv('Low 30j', d.cc_low_30d!=null?'$'+fmt(d.cc_low_30d,0):'N/A', 'red'),
    kv('Volume moyen 30j', d.cc_avg_vol_30d!=null?'$'+fmtV(d.cc_avg_vol_30d):'N/A'),
    kv('Source', 'CryptoCompare (gratuit)', 'blue'),
  ].join('');

  document.getElementById('defi-wtm').innerHTML = [
    kv('Profitabilité Mining', d.wtm_btc_profitability!=null?Number(d.wtm_btc_profitability).toFixed(1)+'%':'N/A', d.wtm_btc_profitability>100?'pos':d.wtm_btc_profitability<80?'neg':''),
    kv('Hashrate réseau', d.wtm_btc_nethash_th!=null?(Number(d.wtm_btc_nethash_th)/1e18).toFixed(2)+' EH/s':'N/A'),
    kv('Difficulté réseau', d.wtm_btc_difficulty!=null?fmtV(d.wtm_btc_difficulty):'N/A'),
    kv('Récompense bloc', d.wtm_btc_block_reward!=null?Number(d.wtm_btc_block_reward).toFixed(4)+' BTC':'N/A'),
    kv('Temps par bloc', d.wtm_btc_block_time!=null?Number(d.wtm_btc_block_time).toFixed(2)+' min':'N/A'),
    kv('Dernier bloc', d.wtm_btc_last_block!=null?fmt(d.wtm_btc_last_block):'N/A'),
    kv('Source', 'WhatToMine.com (gratuit)', 'blue'),
  ].join('');

  document.getElementById('defi-cm-deep').innerHTML = [
    kv('Adresses actives', d.cm_active_addresses!=null?fmt(d.cm_active_addresses):'N/A', 'green'),
    kv('NVT Ratio ajusté', d.cm_nvt_adj!=null?Number(d.cm_nvt_adj).toFixed(2):'N/A', d.cm_nvt_adj>90?'neg':d.cm_nvt_adj<30?'pos':''),
    kv('Supply active 1an', d.cm_sply_act_1yr_btc!=null?fmtV(d.cm_sply_act_1yr_btc)+' BTC':'N/A'),
    kv('Vol transferts (USD)', d.cm_tx_tfr_val_adj_usd!=null?'$'+fmtV(d.cm_tx_tfr_val_adj_usd):'N/A'),
    kv('Hashrate (EH/s)', d.cm_hashrate_eh!=null?Number(d.cm_hashrate_eh).toFixed(2)+' EH/s':'N/A'),
    kv('Supply actuelle', d.cm_supply_current!=null?fmtV(d.cm_supply_current)+' BTC':'N/A'),
    kv('Date données', d.cm_deep_date||'N/A'),
    kv('Source', 'CoinMetrics Community API', 'blue'),
  ].join('');

  document.getElementById('defi-blocks').innerHTML = [
    kv('Hauteur actuelle', d.last_block_height!=null?fmt(d.last_block_height):'N/A', 'orange'),
    kv('TXs dans bloc', d.last_block_txcount!=null?fmt(d.last_block_txcount):'N/A'),
    kv('Taille', d.last_block_size_kb!=null?Number(d.last_block_size_kb).toFixed(1)+' KB':'N/A'),
    kv('Frais médian', d.last_block_median_fee_rate!=null?d.last_block_median_fee_rate+' sat/vB':'N/A'),
    kv('Pool mineur', d.last_block_pool||'N/A', 'blue'),
    kv('Moy TXs (10 blocs)', d.blocks_avg_tx_count!=null?fmt(d.blocks_avg_tx_count):'N/A'),
    kv('Source', 'Mempool.space (gratuit)', 'blue'),
  ].join('');

  document.getElementById('defi-bchart-hashrate').innerHTML =
    `<div class="section-title" style="margin-top:0">Hashrate Réseau — 30 Jours</div>` +
    (d.bchart_hashrate_history ? d.bchart_hashrate_history.slice(-10).map(r =>
      `<div class="kv"><span class="k" style="font-size:10px">${r.date}</span><span class="v orange">${Number(r.eh).toFixed(2)} EH/s</span></div>`
    ).join('') : '<p class="err">Données non disponibles</p>');

  document.getElementById('defi-bchart-txcount').innerHTML =
    `<div class="section-title" style="margin-top:0">Transactions / Jour — 10 derniers jours</div>` +
    [
      kv('TXs aujourd\'hui', d.bchart_txcount_today!=null?fmt(d.bchart_txcount_today):'N/A', 'blue'),
      kv('Moy TXs/j (30j)', d.bchart_txcount_30d_avg!=null?fmt(d.bchart_txcount_30d_avg):'N/A'),
      kv('Frais réseau USD', d.bchart_fees_usd_today!=null?'$'+fmt(d.bchart_fees_usd_today,2):'N/A'),
      kv('Hashrate moy 30j', d.bchart_hashrate_30d_avg_eh!=null?Number(d.bchart_hashrate_30d_avg_eh).toFixed(2)+' EH/s':'N/A'),
      kv('Source', 'Blockchain.info Charts API', 'blue'),
    ].join('');
}

function filterSrc(cat) {
  currentSrcFilter = cat;
  renderSources(SOURCES);
}

function renderSources(src) {
  if(!src || !src.categories) { document.getElementById('src-cards').innerHTML = '<p class="err">Sources non chargées</p>'; return; }
  const catOrder = ['exchanges_usd','exchanges_international','on_chain','lightning','sentiment','historical','etf_finance','derivatives','defi_tvl','analytics','mining_stats'];
  const catLabels = {
    'exchanges_usd':'Exchanges USD','exchanges_international':'Exchanges Internationaux',
    'on_chain':'On-Chain','lightning':'Lightning Network','sentiment':'Sentiment',
    'historical':'Données Historiques','etf_finance':'ETF & Finance',
    'derivatives':'Dérivés & Futures','defi_tvl':'DeFi TVL','analytics':'Analytics',
    'mining_stats':'Mining Stats'
  };
  let html = '';
  for(const catKey of catOrder) {
    const cat = src.categories[catKey];
    if(!cat) continue;
    if(currentSrcFilter !== 'all' && currentSrcFilter !== catKey) continue;
    const catLabel = catLabels[catKey]||catKey;
    html += `<div style="grid-column:1/-1;margin:8px 0 4px"><span class="pill pill-orange">${catLabel} — ${cat.count} sources</span></div>`;
    for(const s of (cat.sources||[])) {
      const tags = [];
      if(!s.key) tags.push('<span class="src-tag tag-free">Gratuit</span>');
      else tags.push('<span class="src-tag tag-key">Clé API</span>');
      if(s.country) tags.push(`<span class="src-tag tag-country">${s.country}</span>`);
      html += `<div class="src-card">
        <div class="src-name">${s.name} ${tags.join(' ')}</div>
        <div class="src-url">🔗 ${s.url}</div>
        <div class="src-data">${s.data}</div>
      </div>`;
    }
  }
  document.getElementById('src-cards').innerHTML = html;
}

// ══════ HEADER UPDATE ════════════════════════════════════════
function updateHeader() {
  const d = DATA;
  const p = d.price_usd;
  if(p) {
    document.getElementById('h-price').textContent = '$'+fmt(p,2);
    const chg = d.change_24h;
    const chgEl = document.getElementById('h-change');
    if(chg!=null) { chgEl.textContent=(chg>0?'+':'')+Number(chg).toFixed(2)+'%'; chgEl.className='price-change '+(chg>0?'pos':'neg'); }
    const vol = d.volume_24h_usd;
    if(vol) document.getElementById('h-vol').textContent = 'Vol: $'+fmtV(vol);
  }
  const upd = DATA.updated_at||EX.updated_at;
  if(upd) document.getElementById('h-upd').textContent = 'Mis à jour: '+new Date(upd).toLocaleTimeString('fr-FR');
}

// ══════ MAIN LOAD ═════════════════════════════════════════════
async function load() {
  try {
    const [sumR, intlR, exR, stooqR, alertsR, sourcesR, drvR, defiR] = await Promise.allSettled([
      fetch(API+'/api/summary').then(r=>r.json()),
      fetch(API+'/api/international').then(r=>r.json()),
      fetch(API+'/api/exchanges').then(r=>r.json()),
      fetch(API+'/api/stooq').then(r=>r.json()),
      fetch(API+'/api/alerts').then(r=>r.json()),
      fetch(API+'/api/sources').then(r=>r.json()),
      fetch(API+'/api/derivatives').then(r=>r.json()),
      fetch(API+'/api/defi').then(r=>r.json()),
    ]);

    DATA   = sumR.status==='fulfilled'    ? sumR.value    : {};
    INTL   = intlR.status==='fulfilled'   ? intlR.value   : {};
    EX     = exR.status==='fulfilled'     ? exR.value     : {};
    STOOQ  = stooqR.status==='fulfilled'  ? stooqR.value  : {};
    ALERTS = alertsR.status==='fulfilled' ? alertsR.value : [];
    SOURCES= sourcesR.status==='fulfilled'? sourcesR.value: {};
    DRV    = drvR.status==='fulfilled'    ? drvR.value    : {};
    DEFI   = defiR.status==='fulfilled'   ? defiR.value   : {};

    // Merge EX data into DATA for easy access
    Object.assign(DATA, EX);
    Object.assign(DATA, STOOQ);
    // Also merge network data from DRV for Réseau tab
    Object.assign(DATA, DRV);
    Object.assign(DATA, DEFI);

    document.getElementById('loader').style.display = 'none';
    updateHeader();
    renderDash();
    renderMarche();
    renderOnchain();
    renderTech();
    renderReseau();
    renderLightning();
    renderExchanges();
    renderIntl();
    renderEtf();
    renderDerivatives();
    renderDefi();
    renderAlertes();
    renderSources(SOURCES);
  } catch(e) {
    console.error('Load error:', e);
    document.getElementById('loader').innerHTML = '<div class="loader-text" style="color:var(--red)">Erreur de chargement: '+e.message+'</div>';
  }
}

load();
setInterval(load, 5*60*1000);
</script>
</body>
</html>
```

---

Je mets maintenant à jour la documentation et le PRD en parallèle.
Action: file_editor create /app/vercel/README.md --file-text "# BTC Analytics Dashboard — v9.0.0

Dashboard Bitcoin agrégeant **70 APIs gratuites** dans le monde, déployable sur Vercel.

## Structure du projet (déploiement Vercel)

```
/app/vercel/
├── main.py          # FastAPI backend — 70 APIs (2364 lignes)
├── index.html       # Frontend vanilla JS — 13 onglets (1397 lignes)
├── requirements.txt # Dépendances Python
├── vercel.json      # Configuration Vercel serverless
└── README.md        # Ce fichier
```

> **Important** : Tous les fichiers doivent être à la **racine** du repo GitHub (structure plate).

---

## APIs Intégrées — 70 Sources

### Exchanges USD (28)
CoinGecko, Binance, Coinbase, Kraken, Bitfinex, Bitstamp, OKX, Bybit, Gemini, KuCoin, Gate.io, HTX, MEXC, Bitget, CoinEx, LBank, WhiteBit, CoinCap, Deribit, CoinPaprika, WBTC DEX (DexScreener), Poloniex, Crypto.com, BitMart, BTSE, CoinLore, CoinRanking, XT.com

### Exchanges Internationaux (19)
🇯🇵 bitFlyer, Coincheck, Zaif  
🇰🇷 Upbit, Bithumb, Korbit  
🇦🇺 BTCMarkets  
🇧🇷 Mercado Bitcoin, Foxbit, NovaDax  
🇷🇺 Exmo  
🇿🇦 Luno, VALR  
🇲🇽 Bitso  
🇮🇳 CoinDCX, WazirX  
🇮🇩 Indodax  
🇹🇷 BtcTurk, Paribu  

### On-Chain (7)
CoinMetrics Community, BGR bitcoin-data.com, Mempool.space, Blockchair, Blockchain.info, Blockstream.info, Bitnodes.io

### Dérivés & Futures (6)
Binance FAPI (USDT-M Perp), Kraken Futures, BitMEX, Hyperliquid DEX, Bitget Futures, Deribit DVol

### DeFi TVL (1)
DefiLlama (Bitcoin Ecosystem : BTC natif, WBTC, tBTC, Babylon, Lombard)

### Analytics (2)
CoinPaprika Extended (remplace Messari), CryptoCompare (historique OHLCV 30j)

### Mining (2)
Blockchain.info Mining Pools, WhatToMine (profitabilité BTC)

### Lightning (2)
Mempool.space Lightning, 1ML.com

### Sentiment (1)
Alternative.me Fear & Greed

### Historique (2)
Stooq CSV (30j), Kraken OHLC

### ETF (2, clés API requises)
SoSoValue, TwelveData

---

## Onglets Frontend (13)
Dashboard | Marché | On-Chain | Technique | Réseau | Lightning | Exchanges USD | International | ETF | Dérivés | DeFi/Analytics | Alertes | Sources (70)

---

## Déploiement sur Vercel

### Étape 1 — Préparer le repo GitHub
1. Créer un nouveau repo GitHub (ex: `btc-dashboard`)
2. Uploader **uniquement** les fichiers du dossier `/app/vercel/` **à la racine** du repo :
   - `main.py`
   - `index.html`
   - `requirements.txt`
   - `vercel.json`

### Étape 2 — Connecter à Vercel
1. Aller sur [vercel.com](https://vercel.com) → \"New Project\"
2. Importer le repo GitHub
3. **Framework Preset** : `Other`
4. Laisser tous les autres paramètres par défaut

### Étape 3 — Variables d'environnement
Dans Vercel → Settings → Environment Variables, ajouter :

| Variable | Valeur |
|----------|--------|
| `SOSOVALUE_KEY` | `SOSO-486d78fe180c417e91c3d0a0894c36ea` |
| `TWELVE_DATA_KEY` | `eb28a9e2191d40feafbaafebd4f9429c` |

### Étape 4 — Deploy
Cliquer \"Deploy\" → attendre ~2 minutes → ✅ Dashboard en ligne !

---

## Variables d'environnement

```bash
SOSOVALUE_KEY=SOSO-486d78fe180c417e91c3d0a0894c36ea   # ETF flux (SoSoValue)
TWELVE_DATA_KEY=eb28a9e2191d40feafbaafebd4f9429c       # Prix ETF (TwelveData)
```

---

## Endpoints API

| Endpoint | Description |
|----------|-------------|
| `GET /` | Sert index.html |
| `GET /api/health` | Health check |
| `GET /api/summary` | Prix, on-chain, réseau, lightning agrégés |
| `GET /api/exchanges` | Tous les prix USD + arbitrage |
| `GET /api/international` | Prix en devises locales + taux FX |
| `GET /api/network` | Données réseau Bitcoin |
| `GET /api/onchain` | Métriques on-chain (CoinMetrics, BGR) |
| `GET /api/lightning` | Lightning Network stats |
| `GET /api/etf` | Flux ETF BTC (SoSoValue + TwelveData) |
| `GET /api/stooq` | Historique 30j (Stooq CSV) |
| `GET /api/alerts` | Signaux buy/sell/neutral |
| `GET /api/derivatives` | Futures perp : Binance, Kraken, BitMEX, Hyperliquid, Bitget, Deribit DVol |
| `GET /api/defi` | TVL DefiLlama, analytics CoinPaprika, CryptoCompare, WhatToMine |
| `GET /api/sources` | Catalogue des 70 sources avec métadonnées |

---

## Métriques avancées (payantes — non intégrées)

Ces données sont **exclusivement disponibles via abonnement payant** :
- **LTH/STH Holder ratios détaillés** → Glassnode Pro (~$30/mois)
- **Whale cohorts précises** → Nansen (~$150/mois)
- **Realized Price par cohort** → IntoTheBlock ($299/mois)
- **SOAB complet** → Glassnode
- **Santiment sentiment** → Santiment API (~$50/mois)
- **Liquidations temps réel** → Coinglass (plan payant)

---

## Changelog

| Version | Date | Description |
|---------|------|-------------|
| v9.0.0 | 2026 | +11 APIs : Dérivés (Binance FAPI, Kraken Futures, BitMEX, Hyperliquid, Bitget, Deribit DVol), DeFi (DefiLlama), Mining (WhatToMine), Analytics (CoinPaprika Extended, CryptoCompare, OKX) — 70 sources total |
| v8.0.0 | 2026-03-22 | +14 APIs : Poloniex, Crypto.com, BitMart, BTSE, CoinLore, CoinRanking, XT.com, Foxbit, NovaDax, Luno, VALR, Bitso, CoinDCX, WazirX, Indodax — FX ZAR/MXN/INR/IDR — 59 sources |
| v7.0.0 | 2026-03 | Architecture Vercel serverless — 44 APIs initiales |
"
Observation: Overwrite successful: /app/vercel/README.md
