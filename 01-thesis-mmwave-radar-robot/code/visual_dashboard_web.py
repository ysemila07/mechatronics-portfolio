# Hosts local web-based dashboard for real-time visualisation, tuning and analysis of obstacle detection.
import time, threading, math, json
from flask import Flask, jsonify, Response, request
try:
    from flask_cors import CORS
except Exception:
    CORS = None

# Uses existing RadarThread from readData_AWR1642.py
from readData_AWR1642 import RadarThread

app = Flask(__name__)
if CORS:
    CORS(app)

# Radar thread glue
radar_thread = None
_last_pts = []
_last_ts = 0.0
_frame_ctr = 0

# Heading in radians for indicator (0 = +Y).
_heading_rad = 0.0

def _start_radar():
    global radar_thread
    if radar_thread is None:
        radar_thread = threading.Thread(target=_radar_loop, daemon=True)
        radar_thread.start()

def _radar_loop():
    global _last_pts, _last_ts, _frame_ctr
    rt = RadarThread()
    rt.start()
    time.sleep(2.0)
    print("[dashboard] radar thread started")
    try:
        while True:
            pts = rt.get_points()
            if pts:
                _last_pts = pts
                _last_ts = time.time()
                _frame_ctr += 1
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        try: rt.stop()
        except Exception: pass
        print("[dashboard] radar thread stopped")

# Range-band logic (meters)
# Base bands (for coloring)
R_MAX_COLOR = 1.50
def band_of(r):
    if r < 0.10:         return ("clutter",  "#666666")   # dark gray
    if r < 0.20:         return ("veryclose","#FF7F7F")   # light red
    if r < 0.25:         return ("stop",     "#FF0000")   # red
    if r < 0.35:         return ("caution",  "#FFA500")   # orange
    if r <= R_MAX_COLOR: return ("usable",   "#2ECC71")   # green
    return ("ignored",   "#333333")

# Live tuning parameters
_params = {
    "R_MIN": 0.40,
    "R_MAX": 1.00,
    "MIN_SNR": 15.0,
    "MIN_ABS_VEL": 0.0,
}
_params_lock = threading.Lock()

def get_params():
    with _params_lock:
        return dict(_params)

def set_params(update: dict):
    with _params_lock:
        for k, v in update.items():
            if k in _params:
                try:
                    _params[k] = float(v)
                except Exception:
                    pass

# Web routes
@app.route("/")
def index():
    _start_radar()
    html = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>mmWave Live Viewer</title>
  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
  <style>
    :root {{
      --bg:#111; --panel:#181818; --fg:#eee; --muted:#aaa; --grid:#333; --zero:#555;
    }}
    body {{ margin:0; background:var(--bg); color:var(--fg); font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif; }}
    .topbar {{ display:flex; gap:16px; align-items:center; padding:10px 14px; background:var(--panel); flex-wrap:wrap; }}
    .dot {{ width:10px; height:10px; border-radius:50%; background:#d33; }}
    .dot.ok {{ background:#2ecc71; }}
    .stat {{ opacity:.85; font-size:13px; }}
    .panel {{ display:flex; gap:10px; align-items:center; flex-wrap:wrap; }}
    .ctrl {{ display:flex; align-items:center; gap:6px; background:#202020; padding:6px 8px; border-radius:6px; }}
    .ctrl label {{ font-size:12px; color:var(--muted); }}
    .ctrl input[type=range] {{ width:160px; }}
    .ctrl input[type=number] {{ width:70px; background:#2a2a2a; color:var(--fg); border:1px solid #333; border-radius:4px; padding:2px 4px; }}
    #graph {{ width:100vw; height: calc(100vh - 110px); }}
    .legend-chip {{ display:inline-block; width:10px; height:10px; margin-right:6px; vertical-align:middle; }}
  </style>
</head>
<body>
  <div class="topbar">
    <div class="panel">
      <div id="dot" class="dot"></div>
      <div class="stat">Frames: <span id="frames">0</span></div>
      <div class="stat">Last: <span id="last">—</span></div>
      <div class="stat">
        <span class="legend-chip" style="background:#666"></span>Clutter
        <span class="legend-chip" style="background:#FF7F7F"></span>Very close
        <span class="legend-chip" style="background:#F00"></span>Stop
        <span class="legend-chip" style="background:#FFA500"></span>Caution
        <span class="legend-chip" style="background:#2ECC71"></span>Usable
      </div>
    </div>
    <div class="panel" id="controls">
      <!-- controls injected by JS after /get_params -->
    </div>
  </div>

  <div id="graph"></div>

  <script>
    const dot = document.getElementById('dot');
    const framesEl = document.getElementById('frames');
    const lastEl = document.getElementById('last');
    const controls = document.getElementById('controls');
    const W = 1.6; // +/- 1.6 m window

    const layout = {{
      paper_bgcolor: '#111', plot_bgcolor:'#111',
      xaxis: {{ title:'X (m)', range:[-W, W], gridcolor:'#333', zerolinecolor:'#555' }},
      yaxis: {{ title:'Y (m)', range:[-0.2, W], gridcolor:'#333', zerolinecolor:'#555', scaleanchor:'x', scaleratio:1 }},
      margin: {{ l:60, r:20, t:10, b:60 }},
      showlegend:false,
      shapes: [
        {{ type:'circle', xref:'x', yref:'y', x0:-0.25, y0:-0.25, x1:0.25, y1:0.25, line:{{color:'#333'}} }},
        {{ type:'circle', xref:'x', yref:'y', x0:-0.5,  y0:-0.5,  x1:0.5,  y1:0.5,  line:{{color:'#333'}} }},
        {{ type:'circle', xref:'x', yref:'y', x0:-1.0,  y0:-1.0,  x1:1.0,  y1:1.0,  line:{{color:'#333'}} }},
        {{ type:'circle', xref:'x', yref:'y', x0:-1.5,  y0:-1.5,  x1:1.5,  y1:1.5,  line:{{color:'#333'}} }},
      ]
    }};

    // Traces: points + robot marker + heading line
    const data = [
      {{ x:[], y:[], mode:'markers', type:'scattergl',
         marker:{{ size:6, color:[] }} }},
      {{ x:[0], y:[0], mode:'markers', type:'scatter',
         marker:{{ size:10, symbol:'x', color:'#eee' }} }},
      {{ x:[0,0], y:[0,1.2], mode:'lines', type:'scatter',
         line:{{ width:2, color:'#4FC3F7' }} }}
    ];

    Plotly.newPlot('graph', data, layout, {{displayModeBar:false}});

    // Build controls UI from /get_params
    function buildControls(p) {{
      controls.innerHTML = '';
      const defs = [
        {{key:'R_MIN', min:0.00, max:0.50, step:0.01, label:'R_MIN (m)'}},
        {{key:'R_MAX', min:0.30, max:2.00, step:0.01, label:'R_MAX (m)'}},
        {{key:'MIN_SNR', min:0, max:15, step:0.5, label:'MIN_SNR'}},
        {{key:'MIN_ABS_VEL', min:0.0, max:0.5, step:0.01, label:'MIN_ABS_VEL (m/s)'}},
      ];
      defs.forEach(d => {{
        const wrap = document.createElement('div'); wrap.className='ctrl';
        const lab = document.createElement('label'); lab.textContent = d.label;
        const rng = document.createElement('input'); rng.type='range';
        rng.min=d.min; rng.max=d.max; rng.step=d.step; rng.value=p[d.key];
        rng.oninput = () => {{ num.value = rng.value; sendParams({{[d.key]: rng.value}}); }};
        const num = document.createElement('input'); num.type='number';
        num.min=d.min; num.max=d.max; num.step=d.step; num.value=p[d.key];
        num.onchange = () => {{ rng.value = num.value; sendParams({{[d.key]: num.value}}); }};
        wrap.appendChild(lab); wrap.appendChild(rng); wrap.appendChild(num);
        controls.appendChild(wrap);
      }});
    }}

    function sendParams(obj) {{
      fetch('/set_params', {{
        method:'POST',
        headers:{{'Content-Type':'application/json'}},
        body: JSON.stringify(obj)
      }}).catch(()=>{{}});
    }}

    function loadParams() {{
      fetch('/get_params').then(r=>r.json()).then(p=>buildControls(p));
    }}

    function fetchData() {{
      fetch('/data').then(r => r.json()).then(j => {{
        dot.className = j.alive ? 'dot ok' : 'dot';
        framesEl.textContent = j.frames.toString();
        lastEl.textContent = new Date().toLocaleTimeString();

        // Update points
        Plotly.restyle('graph', {{ x: [j.x], y: [j.y], 'marker.color': [j.c] }}, [0]);

        // Update heading line
        Plotly.restyle('graph', {{ x:[[0, j.hx]], y:[[0, j.hy]] }}, [2]);
      }}).catch(e => {{
        dot.className = 'dot';
      }});
    }}

    loadParams();
    setInterval(fetchData, 400); // ~2.5 Hz
  </script>
</body>
</html>
"""
    return Response(html, mimetype="text/html")

@app.route("/get_params")
def get_params_route():
    return jsonify(get_params())

@app.route("/set_params", methods=["POST"])
def set_params_route():
    try:
        data = request.get_json(force=True, silent=True) or {}
        set_params(data)
        return jsonify({"ok": True, "params": get_params()})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

@app.route("/data")
def data():
    # Build coloured point arrays + heading vector using live params
    p = get_params()
    R_MIN = p["R_MIN"]; R_MAX = p["R_MAX"]
    MIN_SNR = p["MIN_SNR"]; MIN_ABS_VEL = p["MIN_ABS_VEL"]

    pts = _last_pts
    xs, ys, cs = [], [], []
    bands = {"clutter":0, "veryclose":0, "stop":0, "caution":0, "usable":0, "ignored":0}

    for (x, y, z, v, snr) in pts[-2500:]:  # cap payload size
        r = math.hypot(x, y)
        key, col = band_of(r)
        bands[key] += 1

        # Filtering for display:
        if r < R_MIN or r > R_MAX:
            continue
        if snr < MIN_SNR:
            continue
        if MIN_ABS_VEL > 0 and abs(v) < MIN_ABS_VEL:
            continue
        if key in ("ignored", "clutter"):
            continue

        xs.append(float(x))
        ys.append(float(y))
        cs.append(col)

    # Heading indicator: a 1.2 m arrow in current heading (0 rad default = +Y)
    hx = 1.2 * math.sin(_heading_rad)
    hy = 1.2 * math.cos(_heading_rad)

    alive = (time.time() - _last_ts) < 2.0
    return jsonify({
        "x": xs, "y": ys, "c": cs,
        "frames": _frame_ctr,
        "alive": alive,
        "bands": bands,
        "hx": hx, "hy": hy
    })

@app.route("/health")
def health():
    return "ok", 200

if __name__ == "__main__":
    print("[dashboard] Starting web server at http://0.0.0.0:8080")
    _start_radar()
    app.run(host="0.0.0.0", port=8080, debug=False, threaded=True)