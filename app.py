import os,sys,time,subprocess,tempfile
from pathlib import Path
from collections import defaultdict,deque
from threading import Lock
from flask import Flask,request,jsonify,send_from_directory
ROOT=Path(__file__).resolve().parent
ENGINE=ROOT/"obscura"
app=Flask(__name__)
app.config["MAX_CONTENT_LENGTH"]=512*1024
hits=defaultdict(deque); lock=Lock()
def ensure_engine():
    if (ENGINE/"main.py").exists(): return
    subprocess.run(["git","clone","--depth","1","https://github.com/vo3pal/obscura.git",str(ENGINE)],check=True,timeout=180)
    req=ENGINE/"requirements.txt"
    if req.exists(): subprocess.run([sys.executable,"-m","pip","install","-r",str(req)],check=True,timeout=300)
@app.get("/")
def home(): return send_from_directory(ROOT/"static","index.html")
@app.get("/health")
def health(): return jsonify(ok=True,engine_ready=(ENGINE/"main.py").exists())
@app.post("/api/obfuscate")
def obfuscate():
    ip=request.headers.get("X-Forwarded-For",request.remote_addr or "?").split(",")[0].strip()
    now=time.time()
    with lock:
        q=hits[ip]
        while q and now-q[0]>60: q.popleft()
        if len(q)>=int(os.getenv("RATE_LIMIT_PER_MINUTE","10")): return jsonify(error="تجاوزت الحد؛ حاول بعد دقيقة."),429
        q.append(now)
    data=request.get_json(silent=True) or {}; code=data.get("code",""); mode=data.get("mode","vm")
    if not isinstance(code,str) or not code.strip(): return jsonify(error="الصق كود Luau أولًا."),400
    if len(code.encode())>256*1024: return jsonify(error="الحد الأقصى 256 KB."),413
    if mode not in {"lightweight","rename","native","vm"}: return jsonify(error="وضع غير صالح."),400
    try:
        ensure_engine()
        with tempfile.TemporaryDirectory(prefix="ozone_") as td:
            inp=Path(td)/"input.luau"; out=Path(td)/"output.luau"; inp.write_text(code,encoding="utf-8")
            p=subprocess.run([sys.executable,str(ENGINE/"main.py"),str(inp),"--mode",mode,"-o",str(out),"--quiet"],cwd=ENGINE,capture_output=True,text=True,timeout=45)
            if p.returncode or not out.exists(): return jsonify(error=(p.stderr or p.stdout or "تعذر التشفير.")[-1500:]),422
            return jsonify(ok=True,mode=mode,result=out.read_text(encoding="utf-8"))
    except subprocess.TimeoutExpired: return jsonify(error="انتهى وقت المعالجة؛ جرّب كودًا أصغر أو وضعًا أخف."),504
    except Exception:
        app.logger.exception("backend error")
        return jsonify(error="تعذر تشغيل المحرك. تأكد أن الاستضافة تدعم Git والاتصال الخارجي."),500
@app.errorhandler(413)
def large(_): return jsonify(error="حجم الطلب أكبر من المسموح."),413
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.getenv("PORT","8000")))
