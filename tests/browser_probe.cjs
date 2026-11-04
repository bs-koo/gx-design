// Opt-in test transport: observe the DOM result rather than waiting for all Chrome children to exit.
const fs = require('node:fs/promises');
const os = require('node:os');
const path = require('node:path');
const {spawn, spawnSync} = require('node:child_process');
const {pathToFileURL} = require('node:url');
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
async function main() {
 const profile = await fs.mkdtemp(path.join(os.tmpdir(), 'gx-browser-test-'));
 const child = spawn(process.argv[2], ['--headless=new','--disable-gpu','--no-first-run',
  '--disable-extensions','--disable-background-networking','--remote-debugging-port=0',
  '--user-data-dir='+profile,'about:blank'], {stdio:'ignore', windowsHide:true});
 let ws;
 try {
  let port;
  for(let i=0;i<250;i++){
   if(child.exitCode !== null)throw Error('Browser exited before DevTools started');
   try{port=(await fs.readFile(path.join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0];break}catch{}
   await delay(100);
  }
  if(!port)throw Error('Browser startup timed out');
  const targets=await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  ws=new WebSocket(targets.find(t=>t.type==='page').webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject});
  const waiting=new Map(), errors=[]; let serial=0;
  ws.onmessage=event=>{
   const msg=JSON.parse(event.data);
   if(msg.method==='Runtime.exceptionThrown')errors.push(msg.params.exceptionDetails);
   const pending=waiting.get(msg.id);if(!pending)return;
   waiting.delete(msg.id);clearTimeout(pending.timeout);
   msg.error?pending.reject(Error(JSON.stringify(msg.error))):pending.resolve(msg.result);
  };
  const send=(method,params={})=>new Promise((resolve,reject)=>{
   const id=++serial;const timeout=setTimeout(()=>{waiting.delete(id);reject(Error(method+' timed out'))},8000);
   waiting.set(id,{resolve,reject,timeout});ws.send(JSON.stringify({id,method,params}));
  });
  await send('Runtime.enable');
  await send('Page.navigate',{url:pathToFileURL(path.resolve(process.argv[3])).href});
  for(let i=0;i<100;i++){
   const value=await send('Runtime.evaluate',{expression:"document.getElementById('result')?.textContent || ''",returnByValue:true});
   if(value.result.value){JSON.parse(value.result.value);process.stdout.write(value.result.value);return;}
   if(errors.length)throw Error('Browser JavaScript error: '+JSON.stringify(errors));
   await delay(100);
  }
  throw Error('DOM probe did not produce a result: '+JSON.stringify(errors));
 } finally {
  if(ws)ws.close();
  // Terminate only the process tree started above, never another user browser.
  if(process.platform==='win32'&&child.pid)spawnSync('taskkill',['/PID',String(child.pid),'/T','/F'],{stdio:'ignore',windowsHide:true});
  else child.kill('SIGTERM');
  if(path.dirname(profile)===os.tmpdir()&&path.basename(profile).startsWith('gx-browser-test-'))
   await fs.rm(profile,{recursive:true,force:true,maxRetries:4,retryDelay:150}).catch(()=>{});
 }
}
main().catch(error=>{console.error(error.message);process.exitCode=1});
