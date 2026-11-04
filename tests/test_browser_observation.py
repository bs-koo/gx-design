"""Exercise the observation helper in a real local headless browser when available."""
import importlib.util
import json
import os
import shutil
import signal
import subprocess
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/gx-design/scripts/observe-ui.js"


def load_eval_runner():
    spec = importlib.util.spec_from_file_location("browser_probe_eval_runner", ROOT / "evals/run_eval.py")
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def stop_owned_process_tree(pid):
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
    else:
        try:
            os.killpg(pid, signal.SIGTERM)
            for _ in range(10):
                time.sleep(0.05)
                os.killpg(pid, 0)
            os.killpg(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def cleanup_browser_profiles(profile_parent):
    parent = profile_parent.resolve(strict=True)
    for profile in parent.glob("gx-browser-test-*"):
        target = profile.resolve()
        if target.parent != parent or not target.is_dir():
            raise RuntimeError("Browser profile escaped its owned parent directory")
        try:
            pid = int((target / "gx-browser-pid").read_text())
        except FileNotFoundError:
            pid = None
        if pid is not None:
            if pid < 1:
                raise RuntimeError("Invalid owned browser process ID")
            stop_owned_process_tree(pid)
        for attempt in range(12):
            try:
                shutil.rmtree(target)
                break
            except FileNotFoundError:
                break
            except OSError:
                if attempt == 11:
                    raise
                time.sleep(0.2 * (attempt + 1))


def run_browser_probe(node, browser, fixture, profile_parent, timeout=55):
    env = dict(os.environ, GX_BROWSER_PROFILE_PARENT=str(profile_parent.resolve()))
    command = [node, str(ROOT / "tests/browser_probe.cjs"), browser, str(fixture)]
    if os.name == "nt":
        # Keep Node and every Chrome descendant in one Job Object. Unlike
        # taskkill /T, this still tracks children after their parent exits.
        eval_runner = load_eval_runner()
        try:
            returncode, stdout, stderr = eval_runner._run_turn(command, "", env, ROOT, timeout)
            if returncode == -1:
                raise subprocess.TimeoutExpired(command, timeout, stdout.encode(), stderr.encode())
            return subprocess.CompletedProcess(command, returncode, stdout.encode(), stderr.encode())
        finally:
            cleanup_browser_profiles(profile_parent)
    options = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {"start_new_session": True}
    proc = subprocess.Popen(command,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, **options)
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        return subprocess.CompletedProcess(proc.args, proc.returncode, stdout, stderr)
    except subprocess.TimeoutExpired:
        # Stop the still-owned tree before losing the Node parent PID.
        stop_owned_process_tree(proc.pid)
        proc.communicate(timeout=5)
        raise
    finally:
        if proc.poll() is None:
            stop_owned_process_tree(proc.pid)
            proc.wait(timeout=5)
        # TerminateProcess/SIGKILL cannot run Node's finally block.
        cleanup_browser_profiles(profile_parent)


class BrowserObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.environ.get("GX_BROWSER_TESTS") != "1" and not os.environ.get("GX_BROWSER_BIN"):
            raise unittest.SkipTest("Opt-in browser integration: set GX_BROWSER_TESTS=1")
        candidates = [os.environ.get("GX_BROWSER_BIN"), shutil.which("chromium"),
                      shutil.which("google-chrome"), shutil.which("chromium-browser"),
                      "C:/Program Files/Google/Chrome/Application/chrome.exe",
                      "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"]
        browser = next((p for p in candidates if p and Path(p).is_file()), None)
        node = shutil.which("node")
        if not browser or not node:
            raise unittest.SkipTest("No local Chrome/Chromium; real DOM checks unverified")
        if not SCRIPT.exists():
            raise AssertionError("Bundled observation helper is missing")
        examples = {name: (ROOT / "skills/gx-design/examples" / (name + ".html")).read_text(encoding="utf-8")
                    for name in ("list-filter", "form-errors")}
        examples_json = json.dumps(examples).replace("<", "\\u003c")
        with tempfile.TemporaryDirectory(prefix="gx-observation-") as task_tmp:
            folder = Path(task_tmp)
            fixture = folder / "fixture.html"
            fixture.write_text('''<!doctype html><meta charset="utf-8">
<style>.item{padding:8px;color:rgb(10,20,30)} .hidden{display:none}
.overflow{width:800px} #subject{width:320px}</style>
<main id="subject"><h1>Example</h1><section>
<div id="duplicate" class="item">PRIVATE_TEXT_ONE</div><div id="duplicate" class="item">PRIVATE_TEXT_TWO</div>
</section><input type="password" value="SECRET_VALUE"><div class="hidden">HIDDEN</div>
<div class="overflow">wide</div></main><aside id="outside"><div class="target"><span>OTHER</span></div></aside>
<script src="''' + SCRIPT.as_uri() + '''"></script><script>
const before=document.documentElement.outerHTML;
const normal=gxObserveUI({root:'#subject'});
const unchanged=before===document.documentElement.outerHTML;
const bounded=gxObserveUI({root:'#subject',maxElements:2,maxScan:3});
let invalid=false;try{gxObserveUI({root:'#missing'})}catch(e){invalid=true}
const anonymous=gxObserveUI({root:'.target'});
const anonymousRoundTrip=anonymous.elements.every(item=>document.querySelectorAll(item.selector).length===1&&document.querySelector('.target').contains(document.querySelector(item.selector)));
const duplicateIdRoundTrip=normal.elements.every(item=>document.querySelectorAll(item.selector).length===1&&document.querySelector('#subject').contains(document.querySelector(item.selector)));
const payload={normal,unchanged,bounded,invalid,anonymousRoundTrip,duplicateIdRoundTrip};
const transparentFixture=document.createElement('section');transparentFixture.id='transparency';
transparentFixture.innerHTML='<div id="ghost" style="opacity:0">'+'<button>Hidden</button>'.repeat(300)+'</div><button id="visible-task">Visible task</button><div style="opacity:.5"><button id="half-child" style="opacity:.5">Partial</button></div>';
document.body.append(transparentFixture);
const opaque=gxObserveUI({root:'#transparency'});
const transparent=gxObserveUI({root:'#ghost',includeTransparent:true,maxElements:2});
payload.opacity={visibleCaptured:opaque.elements.some(item=>item.selector==='#visible-task'),
 transparentCaptured:opaque.elements.some(item=>item.selector==='#ghost'),coverage:opaque.coverage,
 partial:opaque.elements.find(item=>item.selector==='#half-child'),included:transparent.elements};
const examples=''' + examples_json + ''';
payload.axScenarios=[
 {name:'initial',expression:'document.open();document.write('+JSON.stringify(examples['form-errors'])+');document.close();'},
 {name:'invalid',expression:"document.getElementById('name').value='Valid';document.getElementById('email').value='bad';document.getElementById('request').dispatchEvent(new Event('submit',{cancelable:true}));"},
 {name:'before',expression:"document.getElementById('view').click();"},
 {name:'after',expression:"document.getElementById('view').click();"},
 {name:'recovered',expression:"document.getElementById('email').value='name@example.com';document.getElementById('request').dispatchEvent(new Event('submit',{cancelable:true}));"}
];
Promise.all(Object.entries(examples).map(([name,markup])=>new Promise(resolve=>{
 const frame=document.createElement('iframe');frame.onload=()=>{
  const d=frame.contentDocument;const w=frame.contentWindow;
  if(name==='list-filter'){
   d.getElementById('status').value='late';d.getElementById('status').dispatchEvent(new w.Event('change'));
   const filtered=d.querySelectorAll('#rows tr').length;
   d.getElementById('stress').click();d.getElementById('view').click();
   payload.list={filtered,after:d.querySelectorAll('#rows tr').length,filter:d.getElementById('status').value,
    stressed:d.querySelector('#rows td').textContent.includes('여러 부서')};
  }else{
   d.getElementById('name').value='Example';d.getElementById('email').value='bad';d.getElementById('message').value='KEEP';
   const submit=()=>d.getElementById('request').dispatchEvent(new w.Event('submit',{cancelable:true}));submit();
   const error=!d.getElementById('errors').hidden;const focus=d.activeElement.id;
   d.getElementById('email').value='name@example.com';submit();
   payload.form={error,focus,recovered:d.getElementById('errors').hidden,
    preserved:d.getElementById('message').value,completed:d.getElementById('result').textContent.length>0};
  }resolve();
 };frame.srcdoc=markup;document.body.append(frame);
}))).then(()=>{document.body.innerHTML='<pre id="result"></pre>';
 document.getElementById('result').textContent=JSON.stringify(payload)});
</script>''', encoding="utf-8")
            profiles = folder / "profiles"
            profiles.mkdir()
            proc = run_browser_probe(node, browser, fixture, profiles)
            rendered = proc.stdout.decode("utf-8", "replace")
            if proc.returncode or not rendered:
                raise AssertionError("Browser observation failed: " + proc.stderr.decode("utf-8", "replace")[-1200:])
            cls.payload = json.loads(rendered)

    def test_observer_does_not_mutate_dom_or_capture_content(self):
        self.assertTrue(self.payload["unchanged"])
        encoded = json.dumps(self.payload["normal"])
        for private in ("SECRET_VALUE", "PRIVATE_TEXT_ONE", "PRIVATE_TEXT_TWO", "HIDDEN", "OTHER"):
            self.assertNotIn(private, encoded)

    def test_scope_styles_and_repeat_candidates_are_observed(self):
        result = self.payload["normal"]
        self.assertEqual(result["scope"], "#subject")
        self.assertGreater(result["viewport"]["width"], 0)
        self.assertTrue(any(item["tag"] == "h1" for item in result["elements"]))
        self.assertFalse(any("outside" in item["selector"] for item in result["elements"]))
        self.assertTrue(any(group["count"] == 2 for group in result["repeatCandidates"]))
        self.assertTrue(any(item["styles"]["color"] == "rgb(10, 20, 30)" for item in result["elements"]))

    def test_limits_and_missing_scope_are_explicit(self):
        self.assertTrue(self.payload["invalid"])
        bounded = self.payload["bounded"]
        self.assertLessEqual(len(bounded["elements"]), 2)
        self.assertTrue(bounded["coverage"]["truncated"])
        self.assertEqual(self.payload["normal"]["claims"], "observation-only")

    def test_list_example_preserves_filter_across_comparison_and_long_data(self):
        self.assertEqual(self.payload["list"], {"filtered": 2, "after": 2, "filter": "late", "stressed": True})

    def test_form_example_recovers_without_losing_input(self):
        self.assertEqual(self.payload["form"], {"error": True, "focus": "email", "recovered": True,
                                               "preserved": "KEEP", "completed": True})

    def test_anonymous_scope_selectors_resolve_uniquely_inside_scope(self):
        self.assertTrue(self.payload["anonymousRoundTrip"])
        self.assertTrue(self.payload["duplicateIdRoundTrip"])

    def test_transparent_subtrees_do_not_consume_capture_budget(self):
        result = self.payload["opacity"]
        self.assertTrue(result["visibleCaptured"])
        self.assertFalse(result["transparentCaptured"])
        self.assertEqual(result["coverage"]["transparentSkipped"], 301)
        self.assertFalse(result["coverage"]["truncated"])
        self.assertEqual(result["partial"]["visibility"]["effectiveOpacity"], 0.25)

    def test_transparent_opt_in_reports_ancestor_opacity(self):
        included = self.payload["opacity"]["included"]
        self.assertEqual(len(included), 2)
        self.assertTrue(all(item.get("visibility", {}).get("effectiveOpacity") == 0 for item in included))
        self.assertEqual(included[1]["styles"]["opacity"], "1")

    def test_form_accessible_descriptions_follow_error_and_comparison_state(self):
        self.assertTrue("accessibility" in self.payload, "Probe must capture real Chrome AX descriptions")
        def description(state, name):
            nodes = self.payload["accessibility"][state]
            field = next(node for node in nodes if node.get("role", {}).get("value") == "textbox"
                         and node.get("name", {}).get("value") == name)
            return field.get("description", {}).get("value", "")
        help_text = "접수 결과를 받을 주소를 입력하세요."
        error_text = "이메일 주소를 확인해 주세요."
        for state in ("initial", "invalid", "before", "after", "recovered"):
            self.assertEqual(description(state, "이름"), "", state)
            self.assertIn(help_text, description(state, "이메일"), state)
        for state in ("initial", "before", "recovered"):
            self.assertNotIn(error_text, description(state, "이메일"), state)
        for state in ("invalid", "after"):
            self.assertIn(error_text, description(state, "이메일"), state)


class BrowserProbeTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.environ.get("GX_BROWSER_TESTS") != "1" and not os.environ.get("GX_BROWSER_BIN"):
            raise unittest.SkipTest("Opt-in browser transport checks: set GX_BROWSER_TESTS=1")
        cls.node = shutil.which("node")
        if not cls.node:
            raise unittest.SkipTest("Node.js 22+ is unavailable")

    def run_node(self, source):
        proc = subprocess.run([self.node, "-e", source], cwd=ROOT, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=12)
        self.assertEqual(proc.returncode, 0, proc.stderr.decode("utf-8", "replace")[-2000:])

    def test_devtools_http_response_has_a_deadline(self):
        self.run_node(r'''
const assert=require('node:assert/strict'),http=require('node:http');
const {connectDevTools}=require('./tests/browser_probe.cjs');
(async()=>{
 const sockets=new Set();const server=http.createServer(()=>{});
 server.on('connection',socket=>{sockets.add(socket);socket.on('close',()=>sockets.delete(socket))});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 try{await assert.rejects(connectDevTools('http://127.0.0.1:'+server.address().port,{timeoutMs:100}),/DevTools HTTP.*timed out/)}
 finally{for(const socket of sockets)socket.destroy();await new Promise(resolve=>server.close(resolve))}
})().catch(error=>{console.error(error);process.exitCode=1});
''')

    def test_devtools_websocket_handshake_has_a_deadline(self):
        self.run_node(r'''
const assert=require('node:assert/strict'),http=require('node:http');
const {connectDevTools}=require('./tests/browser_probe.cjs');
(async()=>{
 const sockets=new Set();const server=http.createServer((request,response)=>{
  response.setHeader('Content-Type','application/json');
  response.end(JSON.stringify([{type:'page',webSocketDebuggerUrl:'ws://127.0.0.1:'+server.address().port+'/socket'}]));
 });
 server.on('connection',socket=>{sockets.add(socket);socket.on('close',()=>sockets.delete(socket))});
 server.on('upgrade',()=>{});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 try{await assert.rejects(connectDevTools('http://127.0.0.1:'+server.address().port,{timeoutMs:1000}),/DevTools WebSocket.*timed out/)}
 finally{for(const socket of sockets)socket.destroy();await new Promise(resolve=>server.close(resolve))}
})().catch(error=>{console.error(error);process.exitCode=1});
''')

    def test_spawn_failure_cleans_its_owned_profile(self):
        self.run_node(r'''
const assert=require('node:assert/strict'),fs=require('node:fs/promises'),os=require('node:os'),path=require('node:path');
const {runProbe}=require('./tests/browser_probe.cjs');
(async()=>{
 const parent=await fs.mkdtemp(path.join(os.tmpdir(),'gx-probe-failure-'));
 try{
  await assert.rejects(runProbe({browser:path.join(parent,'missing-browser'),fixture:__filename,profileParent:parent}),/Browser launch failed/);
  assert.deepEqual(await fs.readdir(parent),[]);
 }finally{await fs.rm(parent,{recursive:true,force:true})}
})().catch(error=>{console.error(error);process.exitCode=1});
''')

    def test_outer_timeout_cleans_browser_after_forced_node_exit(self):
        browser = os.environ.get("GX_BROWSER_BIN") or shutil.which("chromium") or shutil.which("google-chrome")
        if not browser and Path("C:/Program Files/Google/Chrome/Application/chrome.exe").is_file():
            browser = "C:/Program Files/Google/Chrome/Application/chrome.exe"
        if not browser:
            self.skipTest("Local Chrome/Chromium is unavailable")
        with tempfile.TemporaryDirectory(prefix="gx-forced-probe-") as task_tmp:
            folder = Path(task_tmp)
            fixture = folder / "waiting.html"
            fixture.write_text("<!doctype html><p>Wait without a result</p>", encoding="utf-8")
            profiles = folder / "profiles"
            profiles.mkdir()
            observed = {}
            stop = threading.Event()
            def observe_start():
                while not stop.wait(0.05):
                    for profile in profiles.glob("gx-browser-test-*"):
                        try:
                            observed["pid"] = int((profile / "gx-browser-pid").read_text())
                            observed["port"] = int((profile / "DevToolsActivePort").read_text().splitlines()[0])
                            return
                        except (OSError, ValueError, IndexError):
                            pass
            watcher = threading.Thread(target=observe_start, daemon=True)
            watcher.start()
            try:
                with self.assertRaises(subprocess.TimeoutExpired):
                    run_browser_probe(self.node, browser, fixture, profiles, timeout=5)
                self.assertIn("port", observed, "The real browser must have started before forced termination")
                with self.assertRaises((urllib.error.URLError, TimeoutError, ConnectionError)):
                    urllib.request.urlopen(f"http://127.0.0.1:{observed['port']}/json/version", timeout=1)
                self.assertEqual(list(profiles.iterdir()), [])
            finally:
                stop.set()
                watcher.join(timeout=1)
                # Also clean up a regression run where the assertion above detects a leak.
                if "pid" in observed and any(profiles.iterdir()):
                    if os.name == "nt":
                        subprocess.run(["taskkill", "/PID", str(observed["pid"]), "/T", "/F"],
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
                    else:
                        try:
                            os.killpg(observed["pid"], signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                for attempt in range(20):
                    try:
                        shutil.rmtree(profiles)
                        break
                    except FileNotFoundError:
                        break
                    except OSError:
                        if attempt == 19:
                            raise
                        time.sleep(0.1)


if __name__ == "__main__":
    unittest.main()
