/* Read-only browser observation. Call gxObserveUI({root: '#target'}) in an existing browser. */
(function (host) {
  "use strict";
  function gxObserveUI(options = {}) {
    const bounded = (value, fallback, max) => {
      const n = value === undefined ? fallback : value;
      if (!Number.isInteger(n) || n < 1 || n > max) throw new Error("Invalid observation limit");
      return n;
    };
    const maxElements = bounded(options.maxElements, 250, 1000);
    const maxScan = bounded(options.maxScan, 2500, 10000);
    const includeTransparent = options.includeTransparent === undefined ? false : options.includeTransparent;
    if (typeof includeTransparent !== "boolean") throw new Error("includeTransparent must be a boolean");
    const scope = options.root === undefined ? "body" : options.root;
    if (typeof scope !== "string" || !scope.trim()) throw new Error("A scope selector is required");
    const root = document.querySelector(scope);
    if (!root) throw new Error("Observation scope not found");
    const round = (n) => Math.round(n * 100) / 100;
    const styles = new WeakMap();
    const styleFor = (element) => {
      if (!styles.has(element)) styles.set(element, getComputedStyle(element));
      return styles.get(element);
    };
    const opacities = new WeakMap();
    const opacityFor = (element) => {
      const pending = [];
      let ancestor = element;
      while (ancestor && !opacities.has(ancestor)) {
        pending.push(ancestor);
        ancestor = ancestor.parentElement;
      }
      let opacity = ancestor ? opacities.get(ancestor) : 1;
      for (let i = pending.length - 1; i >= 0; i -= 1) {
        opacity *= Number(styleFor(pending[i]).opacity);
        opacities.set(pending[i], opacity);
      }
      return opacities.get(element);
    };
    const selectors = new WeakMap();
    const selectorFor = (element) => {
      if (selectors.has(element)) return selectors.get(element);
      const parts = [];
      for (let el = element; el && el.nodeType === 1; el = el.parentElement) {
        if (el.id && document.querySelectorAll("#" + CSS.escape(el.id)).length === 1) {
          parts.unshift("#" + CSS.escape(el.id));
          break;
        }
        const siblings = el.parentElement ? Array.from(el.parentElement.children).filter((s) => s.tagName === el.tagName) : [el];
        parts.unshift(el.tagName.toLowerCase() + (siblings.length > 1 ? ":nth-of-type(" + (siblings.indexOf(el) + 1) + ")" : ""));
      }
      const selector = parts.join(" > ");
      selectors.set(element, selector);
      return selector;
    };
    const elements = [];
    const groups = new Map();
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT);
    let el = root;
    let scanned = 0;
    let transparentSkipped = 0;
    while (el && scanned < maxScan && elements.length < maxElements) {
      scanned += 1;
      const tag = el.tagName.toLowerCase();
      const style = styleFor(el);
      const rect = el.getBoundingClientRect();
      if (!["script", "style", "template", "noscript"].includes(tag) &&
          rect.width > 0 && rect.height > 0 && style.visibility === "visible" && style.display !== "none") {
        const effectiveOpacity = opacityFor(el);
        if (effectiveOpacity === 0 && !includeTransparent) {
          transparentSkipped += 1;
          el = walker.nextNode();
          continue;
        }
        const selector = selectorFor(el);
        elements.push({
          selector, tag, role: el.getAttribute("role"),
          visibility: { effectiveOpacity, transparent: effectiveOpacity === 0 },
          rect: { x: round(rect.x), y: round(rect.y), width: round(rect.width), height: round(rect.height) },
          styles: { color: style.color, backgroundColor: style.backgroundColor,
            fontFamily: style.fontFamily, fontSize: style.fontSize, fontWeight: style.fontWeight,
            lineHeight: style.lineHeight, display: style.display, opacity: style.opacity, gap: style.gap,
            padding: style.padding, borderRadius: style.borderRadius },
          clippedContentCandidate: el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1,
        });
        if (el.parentElement) {
          const key = selectorFor(el.parentElement) + "|" + tag + "|" + Array.from(el.classList).sort().join(".") + "|" + (el.getAttribute("role") || "");
          if (!groups.has(key)) groups.set(key, []);
          groups.get(key).push(selector);
        }
      }
      el = walker.nextNode();
    }
    return {
      schemaVersion: 1, claims: "observation-only", scope,
      viewport: { width: innerWidth, height: innerHeight, dpr: devicePixelRatio },
      scroll: { x: scrollX, y: scrollY }, fontsStatus: document.fonts ? document.fonts.status : "unknown",
      coverage: { scanned, captured: elements.length, maxElements, maxScan, truncated: el !== null,
        includeTransparent, transparentSkipped,
        inclusion: "positive-area-visibility-visible" + (includeTransparent ? "" : "-positive-effective-opacity"),
        excludes: ["text-and-input-values", "shadow-roots", "iframe-documents", "pseudo-elements", "interaction-states"] },
      elements,
      repeatCandidates: Array.from(groups.values()).filter((members) => members.length > 1)
        .map((members) => ({ count: members.length, members })),
    };
  }
  if (typeof module !== "undefined" && module.exports) module.exports = gxObserveUI;
  else host.gxObserveUI = gxObserveUI;
})(globalThis);
