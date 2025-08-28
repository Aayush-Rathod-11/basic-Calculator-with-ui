import http.server
import socketserver
import socket
import threading
import webbrowser

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Menu-Based Beautiful Calculator</title>
  <style>
    :root{
      --bg1:#74ebd5;
      --bg2:#acb6e5;
      --card:rgba(255,255,255,0.14);
      --glass:rgba(255,255,255,0.18);
      --text:#1f2937;
      --accent:#6c63ff;
      --accent2:#ff6584;
      --warn:#fca311;
      --ok:#10b981;
    }
    .dark{
      --bg1:#0f172a;
      --bg2:#1f2937;
      --card:rgba(255,255,255,0.06);
      --glass:rgba(255,255,255,0.10);
      --text:#e5e7eb;
      --accent:#8b5cf6;
      --accent2:#fb7185;
      --warn:#f59e0b;
      --ok:#34d399;
    }

    *{box-sizing:border-box}
    body{
      margin:0;
      height:100vh;
      display:flex;
      justify-content:center;
      align-items:center;
      background:linear-gradient(135deg, var(--bg1) 0%, var(--bg2) 100%);
      font-family:system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, 'Segoe UI Symbol';
      color:var(--text);
      transition:background 0.5s ease;
    }
    .container{width: min(92vw, 380px); text-align:center;}
    .card{
      background:var(--card);
      backdrop-filter: blur(12px);
      border:1px solid rgba(255,255,255,0.25);
      border-radius:22px;
      padding:22px;
      box-shadow:0 12px 30px rgba(0,0,0,0.25);
      display:none;
      animation:fadeIn 300ms ease;
    }
    .card.active{display:block}
    @keyframes fadeIn{from{opacity:0; transform:translateY(8px)} to{opacity:1; transform:translateY(0)}}

    h2{margin:0 0 14px 0; color:white; text-shadow:0 2px 10px rgba(0,0,0,0.25)}

    .btn{
      width:100%;
      height:52px;
      border:none;
      border-radius:16px;
      font-size:1.05rem;
      font-weight:700;
      cursor:pointer;
      transition:transform 0.15s ease, box-shadow 0.2s ease, opacity 0.2s ease;
      box-shadow:0 8px 16px rgba(0,0,0,0.18);
      color:white;
      margin:8px 0;
    }
    .btn:hover{transform:translateY(-1px)}
    .btn:active{transform:translateY(0) scale(0.98)}
    .btn-primary{background:var(--accent)}
    .btn-danger{background:var(--accent2)}
    .btn-ok{background:var(--ok)}
    .btn-warn{background:var(--warn)}

    /* Header row with theme toggle */
    .topbar{
      display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;
    }
    .toggle{
      display:inline-flex; align-items:center; gap:8px; font-weight:600; color:white;
      user-select:none; cursor:pointer;
      background:var(--glass); padding:6px 10px; border-radius:12px;
    }

    /* Calculator */
    .display{
      width:100%; height:64px; background:rgba(255,255,255,0.2);
      border:none; border-radius:14px; margin:10px 0 18px 0; text-align:right;
      padding:14px; font-size:1.6rem; font-weight:800; color:#fff; letter-spacing:0.5px;
    }
    .grid{
      display:grid; grid-template-columns:repeat(4, 1fr); gap:12px;
    }
    .key{
      height:58px; border:none; border-radius:16px; font-size:1.15rem; font-weight:800;
      cursor:pointer; transition:transform 0.15s ease, opacity 0.2s ease;
      background:rgba(255,255,255,0.28); color:#111827;
      box-shadow:0 6px 14px rgba(0,0,0,0.15);
    }
    .key:hover{transform:translateY(-1px)}
    .op{background:var(--accent); color:white}
    .eq{background:var(--accent2); color:white; grid-column:span 2}
    .clr{background:var(--warn); color:white}
    .wide{grid-column:span 2}

    /* Small helper text */
    .hint{font-size:0.85rem; opacity:0.85; color:white; margin-top:8px}
    .footer{margin-top:10px; font-size:0.78rem; opacity:0.8; color:white}

    /* Link-styled back */
    .link-btn{
      display:inline-block; margin-top:12px; color:white; font-weight:700;
      text-decoration:none; background:var(--glass); padding:8px 12px; border-radius:12px;
      cursor:pointer;
    }
  </style>
</head>
<body>
  <div class="container">
    <!-- MENU -->
    <section id="menu" class="card active">
      <div class="topbar">
        <h2>Basic Calculator</h2>
        <span id="themeToggle" class="toggle" title="Toggle theme">🌗 Theme</span>
      </div>
      <p class="hint">Choose an option:</p>
      <button class="btn btn-primary" onclick="openCalc()">1. Perform Calculation</button>
      <button class="btn btn-danger" onclick="exitApp()">2. Exit</button>
      <div class="footer">Supports + − × ÷ ^ (power) • Keyboard input</div>
    </section>

    <!-- CALCULATOR -->
    <section id="calc" class="card">
      <div class="topbar">
        <h2>Calculator</h2>
        <span id="themeToggle2" class="toggle" title="Toggle theme">🌗 Theme</span>
      </div>

      <input id="display" class="display" placeholder="0" disabled />
      <div class="grid">
        <button class="key clr" onclick="clearDisplay()">C</button>
        <button class="key op"  onclick="append('^')">^</button>
        <button class="key op"  onclick="append('/')">÷</button>
        <button class="key op"  onclick="append('*')">×</button>

        <button class="key" onclick="append('7')">7</button>
        <button class="key" onclick="append('8')">8</button>
        <button class="key" onclick="append('9')">9</button>
        <button class="key op" onclick="append('-')">−</button>

        <button class="key" onclick="append('4')">4</button>
        <button class="key" onclick="append('5')">5</button>
        <button class="key" onclick="append('6')">6</button>
        <button class="key op" onclick="append('+')">+</button>

        <button class="key" onclick="append('1')">1</button>
        <button class="key" onclick="append('2')">2</button>
        <button class="key" onclick="append('3')">3</button>
        <button class="key" onclick="append('(')">(</button>

        <button class="key" onclick="append('0')">0</button>
        <button class="key" onclick="append('.')">.</button>
        <button class="key" onclick="append(')')">)</button>
        <button class="key eq" onclick="calculate()">=</button>
      </div>

      <div>
        <span class="link-btn" onclick="backToMenu()">← Back to Menu</span>
      </div>
      <p class="hint">Tip: Use keyboard numbers and + - * / ^ ( ) . Enter = equals, Backspace = delete last.</p>
    </section>

    <!-- EXIT -->
    <section id="exit" class="card">
      <h2>Goodbye 👋</h2>
      <p class="hint">Thanks for using the calculator.</p>
      <button class="btn btn-ok" onclick="restart()">Restart Program</button>
    </section>
  </div>

  <script>
    const body = document.body;
    const menu = document.getElementById('menu');
    const calc = document.getElementById('calc');
    const exitV = document.getElementById('exit');
    const display = document.getElementById('display');

    // Theme toggle
    const toggleTheme = () => body.classList.toggle('dark');
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
    document.getElementById('themeToggle2').addEventListener('click', toggleTheme);

    // Menu navigation
    function openCalc(){ menu.classList.remove('active'); exitV.classList.remove('active'); calc.classList.add('active'); }
    function backToMenu(){ calc.classList.remove('active'); exitV.classList.remove('active'); menu.classList.add('active'); clearDisplay(); }
    function exitApp(){ menu.classList.remove('active'); calc.classList.remove('active'); exitV.classList.add('active'); }
    function restart(){ exitApp(); backToMenu(); }

    // Calculator logic
    function append(ch){ display.value += ch; }
    function clearDisplay(){ display.value = ''; }

    function calculate(){
      try{
        const expr = display.value.replace(/\^/g, '**');
        // Basic guard: only allow valid characters
        if(!/^[0-9+\-*/().\s*]*([*]{2})?[0-9+\-*/().\s*]*$/.test(expr)){
          throw new Error('Invalid characters');
        }
        // eslint-disable-next-line no-eval
        const result = eval(expr);
        if (result === Infinity || Number.isNaN(result)) throw new Error('Math error');
        display.value = result;
      }catch(e){
        display.value = 'Error';
      }
    }

    // Keyboard support
    window.addEventListener('keydown', (e)=>{
      const k = e.key;
      if(/[0-9+\-*/().]/.test(k)){ append(k); }
      else if(k === '^'){ append('^'); }
      else if(k === 'Enter'){ e.preventDefault(); calculate(); }
      else if(k === 'Backspace'){ display.value = display.value.slice(0, -1); }
      else if(k.toLowerCase() === 'c' && (e.ctrlKey || e.metaKey)){ clearDisplay(); }
    });

    // Show menu by default
    menu.classList.add('active');
  </script>
</body>
</html>"""

class SinglePageHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve only our single page for any GET request
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode("utf-8"))

    # Silence logging
    def log_message(self, format, *args):
        pass

def _find_free_port(start=8000, max_tries=50):
    port = start
    for _ in range(max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                s.close()
                return port
            except OSError:
                port += 1
    return 0  # fall back to 0 (random)

def run_server():
    port = _find_free_port()
    if port == 0:
        port = 0  # let OS choose
    with socketserver.TCPServer(("", port), SinglePageHandler) as httpd:
        actual_port = httpd.server_address[1]
        url = f"http://localhost:{actual_port}"
        print(f"Calculator running at {url}")
        # Open browser in a separate thread to avoid blocking
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
