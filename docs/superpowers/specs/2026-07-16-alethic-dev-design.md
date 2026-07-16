# alethic.dev — Design

**Date:** 2026-07-16
**Status:** Approved, pending implementation plan
**Scope:** The public marketing/credibility site at alethic.dev. Not the docs, not the API, not the kernel.

---

## 1. Purpose

alethic.dev has one job: **turn a cold, skeptical evaluator into someone who runs `pip install alethic-kernel`.**

**Audience.** Someone who hears "Alethic" — from the paper, a link, a conversation — and searches for it. A researcher, a CTO, an engineer evaluating whether this is real. They arrive knowing nothing and are predisposed to bounce.

**Success.** They trust it enough to try it. The measurable proxy is clicks through to PyPI and GitHub; the real one is whether an evaluator comes away thinking "this is a serious piece of work."

**Explicit non-goals.** Not a documentation site — GitHub stays canonical for `docs/*.md`. Not lead generation. Not a company site. One page, one job.

## 2. Sequencing (hard dependencies)

The site's entire function is to route people to `pip install` and GitHub. As of today the package is not on PyPI and the repository is private, so **both CTAs are dead**. Shipping the site before those exist would repeat precisely the failure this project just corrected in its own README: publishing links that 404.

Build order, and none of it is optional:

1. **Fix blocker P0-3** (the confidence gate can be defeated by a malformed float; see the private audit report `~/homeserver/reports/alethic-prod-readiness-2026-07-16.md`). Mandatory regardless of this site — it reaches library users. **The demo makes it urgent**: the demo executes the real kernel in the visitor's browser, so an unfixed gate bypass becomes a publicly reachable exhibit of the framework failing to govern. Verified to reproduce under Pyodide, not only in CPython.
2. **Merge PR #3** (public-release hygiene) and settle the library-only v1 decision.
3. **Repository public → PyPI publish.**
4. **Then** alethic.dev, with every CTA live on day one.

The site is the last step, not the first.

## 3. Architecture

**Static site, Astro, deployed on Vercel.**

- **Vercel** — alethic.dev already delegates to `ns1/ns2.vercel-dns.com` and returns 404, meaning the domain is wired and nothing is deployed. No new infrastructure decision required.
- **Astro** — already in use for iam.med (`~/homeserver/iam-astro`), so the toolchain and deploy story are known. Zero-JS by default: the only JavaScript on the page is the demo.
- **No server, no database, no API.** This is a deliberate security property, not just simplicity. A hosted demo API is exactly the threat model of blocker P0-2 (no authentication, one shared global kernel): a public endpoint would be an unauthenticated multi-tenant kernel, i.e. the vulnerability as a service. Running the kernel client-side removes the tenancy problem by construction.

**Repository.** The site lives in its own repo (`alethicdev/alethic-dev`), not in the kernel repo. The kernel ships to PyPI and must not carry site assets; the site deploys on every push and must not be gated by the kernel's CI.

## 4. The demo

The demo is the centre of the page, not a flourish. **The refusal is the product** — a benchmark table claiming "0% unsafe actions" is a self-reported number that invites doubt; watching the kernel refuse converts. The demo is placed above the fold, before the table, so the table is read as confirmation of something already witnessed.

**Mechanism: Pyodide, running the real kernel in the visitor's browser.** Verified end-to-end in a real browser on 2026-07-16 against wheel `alethic_kernel-0.1.0-py3-none-any.whl`:

```
pyodide loaded    701ms
wheel installed   971ms
EPISODE_OK    {'task_success': 1.0, 'unsafe_action': 0.0, ...}
REFUSAL_TEST  conf=0.9 -> (True, 'COMMITTED') | conf=0.3 -> (False, 'LOW_CONFIDENCE')
```

Roughly one second from cold load to a running kernel. The library's zero runtime dependencies are what make this viable.

**Known requirement:** `alethic_kernel.alethic.__init__` eagerly imports `SqliteStore`, which imports `sqlite3`, which Pyodide unvendors. The page must call `pyodide.loadPackage(["micropip", "sqlite3"])`. (Making that import lazy in the library is worth doing on its own merits — it would let the core run anywhere without sqlite3 — but this site must not depend on that change.)

**Loading strategy.** Pyodide lazy-loads **on first interaction**, never on page load. The static page stays instant; only visitors who engage pay the download. Until then, the demo panel shows the scenario and a Run button.

**Presets, not a free-form editor.** The demo ships a fixed set of scenarios — clean path, low confidence, stale evidence, duplicate refund blocked by constraint — each one a rejection the kernel genuinely produces. This is a deliberate scope cut. A free-form REPL invites `NaN` and every other edge case onto the marketing page, and turns a credibility asset into an attack surface. The demo's job is to be **true**, not exhaustive. Anyone wanting to probe the kernel properly can `pip install` it — which is the conversion we want anyway.

**Assets.** The wheel is served from the site's own origin (pinned per deploy, never floating). The Pyodide CDN `<script>` tag carries `integrity="sha384-…"` and `crossorigin="anonymous"`; loading it without SRI would expose the page to CDN compromise.

## 5. Page content, in order

1. **Hero** — "Your model proposes. Alethic decides." (already the strongest line in the README). One paragraph of what it is, `pip install alethic-kernel`, DOI badge.
2. **The demo** — as specified above.
3. **Benchmark table** — the existing 1,200-episode results, with the scope stated inline: a self-run benchmark over 6 Stripe refund tasks × 50 seeds × 4 agents with controlled perturbations. Naming the scope is what makes the numbers credible; an unqualified "100% / 0%" reads as marketing.
4. **How it works** — the architecture diagram and the PROPOSE/COMMIT explanation, briefly.
5. **Paper** — "From Fragile Glue to Governed Cognition", DOI 10.5281/zenodo.18691808, and the public artifact repo `emiluzelac/governed-cognition`.
6. **Links out** — GitHub, PyPI, docs.

## 6. Claims discipline

**The site must scope every claim to the library, in-process.** That is where the governance guarantees actually hold, and the audit found six blockers that break them outside that envelope.

Specifically, the site must not: describe the framework as production-ready; suggest deploying the HTTP API; imply multi-tenancy or hosted use; or restate the "kernel is the only role that can commit" claim, which is false over HTTP (corrected in PR #3).

This is not modesty. For a governance product, a single demonstrated bypass is a credibility event that a hundred good benchmarks do not repair. The honest claims are strong on their own: a real kernel, a real refusal, a published paper, and a benchmark whose scope is stated plainly.

## 7. Error handling

- **Pyodide fails to load, WASM blocked, or CSP/corporate proxy interference** → the demo degrades to a pre-rendered static trace of the same scenario. The story still lands; the visitor never sees a blank box or a spinner that never resolves.
- **Wheel fetch fails** → same fallback.
- **Slow connection** → the Run button shows load progress rather than appearing hung. The static page is already fully readable and never blocks on the demo.
- **JavaScript disabled** → the whole page reads normally, demo panel shows the static trace. Astro's zero-JS default makes this the natural outcome rather than extra work.

## 8. Testing

- **Preset assertions in CI.** Every demo preset is asserted against the exact kernel version the wheel ships, in the site's CI. The site must never claim a refusal the code does not produce. This is the single most important test: the page's credibility rests entirely on the demo being real.
- **A browser test** (Playwright) loads the page, runs each preset through Pyodide, and asserts the expected code (`COMMITTED`, `LOW_CONFIDENCE`, `STALE_EVIDENCE`, constraint-blocked). This is the same method used to verify feasibility on 2026-07-16 and should become the regression test.
- **Link check in CI** — every outbound link resolves. This site exists because dead links are embarrassing; it must not ship any.
- **Fallback path tested** — load the page with WASM disabled and assert the static trace renders.

## 9. Out of scope

No search. No versioned docs. No blog. No waitlist, contact form, or lead capture. No heavy analytics. No hosted API or playground backend. No authentication. If any of these become worth doing, they are their own decision, made later, with reasons.

## 10. Open items (not blocking this design)

- Exact preset list and their copy — settled during implementation against the real kernel's actual return codes.
- Visual design direction (typography, palette) — deferred to implementation.
- Whether to make the `SqliteStore` import lazy in the library — a genuine improvement, tracked separately; this site works without it.
