"""Exercise the observation helper in a real local headless browser when available."""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/gx-design/scripts/observe-ui.js"


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
const examples=''' + examples_json + ''';
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
            proc = subprocess.run([node, str(ROOT / "tests/browser_probe.cjs"), browser, str(fixture)],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=55)
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


if __name__ == "__main__":
    unittest.main()
