// Opt-in local Chrome transport. Requiring this file does not start a browser.
const fs = require('node:fs/promises');
const os = require('node:os');
const path = require('node:path');
const {spawn, spawnSync} = require('node:child_process');
const {pathToFileURL} = require('node:url');
const {setTimeout: delay} = require('node:timers/promises');

async function connectDevTools(endpoint, {timeoutMs = 3000, signal} = {}) {
  const deadline = AbortSignal.timeout(timeoutMs);
  let targets;
  try {
    const response = await fetch(endpoint + '/json/list', {
      signal: signal ? AbortSignal.any([signal, deadline]) : deadline,
    });
    if (!response.ok) throw Error('DevTools HTTP status ' + response.status);
    targets = await response.json();
  } catch (error) {
    if (signal?.aborted) throw signal.reason;
    if (deadline.aborted) throw Error('DevTools HTTP request timed out');
    throw error;
  }
  const target = targets.find(item => item.type === 'page' && item.webSocketDebuggerUrl);
  if (!target) throw Error('DevTools page target is missing');
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  try {
    await new Promise((resolve, reject) => {
      const finish = error => {
        clearTimeout(timer);
        ws.removeEventListener('open', opened);
        ws.removeEventListener('error', failed);
        ws.removeEventListener('close', closed);
        signal?.removeEventListener('abort', aborted);
        error ? reject(error) : resolve();
      };
      const opened = () => finish();
      const failed = () => finish(Error('DevTools WebSocket connection failed'));
      const closed = () => finish(Error('DevTools WebSocket closed before connecting'));
      const aborted = () => finish(signal.reason);
      const timer = setTimeout(() => finish(Error('DevTools WebSocket connection timed out')), timeoutMs);
      ws.addEventListener('open', opened);
      ws.addEventListener('error', failed);
      ws.addEventListener('close', closed);
      signal?.addEventListener('abort', aborted, {once: true});
      if (signal?.aborted) aborted();
    });
    return ws;
  } catch (error) {
    // Cancelling a pending Node WebSocket can emit an error during close.
    ws.addEventListener('error', () => {}, {once: true});
    ws.close();
    throw error;
  }
}

async function stopBrowser(child) {
  if (!child?.pid) return;
  if (process.platform === 'win32') {
    spawnSync('taskkill', ['/PID', String(child.pid), '/T', '/F'],
      {stdio: 'ignore', windowsHide: true, timeout: 5000});
  } else {
    // Chrome has its own process group, including its renderer children.
    try { process.kill(-child.pid, 'SIGTERM'); } catch (error) { if (error.code !== 'ESRCH') throw error; }
    if (child.exitCode === null && child.signalCode === null)
      await Promise.race([new Promise(resolve => child.once('exit', resolve)), delay(1500)]);
    try { process.kill(-child.pid, 'SIGKILL'); } catch (error) { if (error.code !== 'ESRCH') throw error; }
  }
}

async function runProbe({browser, fixture, profileParent = os.tmpdir(), signal,
  startupTimeoutMs = 25000, connectTimeoutMs = 3000}) {
  const profile = await fs.mkdtemp(path.join(profileParent, 'gx-browser-test-'));
  const waiting = new Map(), errors = [];
  let child, ws, spawnError, failure, serial = 0;
  const failPending = error => {
    for (const pending of waiting.values()) { clearTimeout(pending.timeout); pending.reject(error); }
    waiting.clear();
  };
  const aborted = () => failPending(signal.reason);
  signal?.addEventListener('abort', aborted, {once: true});
  try {
    signal?.throwIfAborted();
    child = spawn(browser, ['--headless=new', '--disable-gpu', '--no-first-run',
      '--disable-breakpad', '--disable-crash-reporter', '--noerrdialogs',
      '--disable-extensions', '--disable-background-networking', '--remote-debugging-port=0',
      '--user-data-dir=' + profile, 'about:blank'],
    {stdio: 'ignore', windowsHide: true, detached: process.platform !== 'win32'});
    child.on('error', error => { spawnError = Error('Browser launch failed: ' + error.message); });
    if (child.pid) await fs.writeFile(path.join(profile, 'gx-browser-pid'), String(child.pid));
    let port;
    const startupDeadline = Date.now() + startupTimeoutMs;
    while (Date.now() < startupDeadline) {
      signal?.throwIfAborted();
      if (spawnError) throw spawnError;
      if (child.exitCode !== null || child.signalCode !== null) throw Error('Browser exited before DevTools started');
      try {
        const value = (await fs.readFile(path.join(profile, 'DevToolsActivePort'), 'utf8')).split('\n')[0];
        if (/^\d+$/.test(value) && Number(value) > 0 && Number(value) <= 65535) { port = value; break; }
      } catch (error) { if (!['ENOENT', 'EBUSY', 'EACCES', 'EPERM'].includes(error.code)) throw error; }
      await delay(100, undefined, {signal});
    }
    if (!port) throw Error('Browser startup timed out');
    ws = await connectDevTools('http://127.0.0.1:' + port, {timeoutMs: connectTimeoutMs, signal});
    ws.onmessage = event => {
      let msg;
      try { msg = JSON.parse(event.data); } catch { failPending(Error('Invalid DevTools response')); return; }
      if (msg.method === 'Runtime.exceptionThrown') errors.push(msg.params.exceptionDetails);
      const pending = waiting.get(msg.id);
      if (!pending) return;
      waiting.delete(msg.id);
      clearTimeout(pending.timeout);
      msg.error ? pending.reject(Error(JSON.stringify(msg.error))) : pending.resolve(msg.result);
    };
    ws.onclose = () => failPending(Error('DevTools connection closed'));
    ws.onerror = () => failPending(Error('DevTools connection failed'));
    const send = (method, params = {}) => new Promise((resolve, reject) => {
      if (signal?.aborted) { reject(signal.reason); return; }
      const id = ++serial;
      const timeout = setTimeout(() => { waiting.delete(id); reject(Error(method + ' timed out')); }, 8000);
      waiting.set(id, {resolve, reject, timeout});
      try { ws.send(JSON.stringify({id, method, params})); }
      catch (error) { waiting.delete(id); clearTimeout(timeout); reject(error); }
    });
    const evaluate = async expression => {
      const result = await send('Runtime.evaluate', {expression, returnByValue: true});
      if (result.exceptionDetails) throw Error('Browser evaluation failed: ' + JSON.stringify(result.exceptionDetails));
      return result.result.value;
    };
    await send('Runtime.enable');
    await send('Page.navigate', {url: pathToFileURL(path.resolve(fixture)).href});
    for (let i = 0; i < 100; i++) {
      const value = await evaluate("document.getElementById('result')?.textContent || ''");
      if (errors.length) throw Error('Browser JavaScript error: ' + JSON.stringify(errors));
      if (value) {
        const payload = JSON.parse(value);
        // Trusted local fixtures can request sequential real Chrome AX snapshots.
        if (payload.axScenarios) {
          payload.accessibility = {};
          await send('Accessibility.enable');
          for (const scenario of payload.axScenarios) {
            await evaluate(scenario.expression);
            payload.accessibility[scenario.name] = (await send('Accessibility.getFullAXTree')).nodes;
          }
          delete payload.axScenarios;
        }
        return payload;
      }
      await delay(100, undefined, {signal});
    }
    throw Error('DOM probe did not produce a result');
  } catch (error) {
    failure = error;
    throw error;
  } finally {
    signal?.removeEventListener('abort', aborted);
    failPending(Error('Probe stopped'));
    ws?.close();
    try { await stopBrowser(child); }
    finally {
      // Only remove the profile created here, never the caller's parent directory.
      try {
        await fs.rm(profile, {recursive: true, force: true, maxRetries: 10, retryDelay: 200});
      } catch (error) {
        if (failure) throw Error(failure.message + '; profile cleanup failed: ' + error.message);
        throw error;
      }
    }
  }
}

module.exports = {connectDevTools, runProbe};
if (require.main === module) {
  const controller = new AbortController();
  const onSigterm = () => controller.abort(Error('Probe stopped by SIGTERM'));
  const onSigint = () => controller.abort(Error('Probe stopped by SIGINT'));
  process.on('SIGTERM', onSigterm);
  process.on('SIGINT', onSigint);
  runProbe({browser: process.argv[2], fixture: process.argv[3],
    profileParent: process.env.GX_BROWSER_PROFILE_PARENT || os.tmpdir(), signal: controller.signal})
    .then(payload => process.stdout.write(JSON.stringify(payload)))
    .catch(error => { console.error(error.message); process.exitCode = 1; })
    .finally(() => {
      process.removeListener('SIGTERM', onSigterm);
      process.removeListener('SIGINT', onSigint);
    });
}
