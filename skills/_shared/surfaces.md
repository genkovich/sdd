# Target surfaces — what's being built (the C4-container surface taxonomy)

> **Reference-only.** Not a skill. `design` is the canonical owner of the **selection** (it picks the
> surface(s) and writes them to `sad.md`); `api` / `sequences` / `tasks` / `plan-tests` / `review`
> **read** the declaration and gate their own output by it. Each keeps a one-line pointer here and its
> own delta — the taxonomy and the gating table live **only** in this file, never duplicated per skill.

## TL;DR (короткий вступ українською)

«Таргет-сёрфейс» (target surface) — це **що саме ми будуємо** для фічі: бекенд-сервіс, веб-фронтенд,
мобільний застосунок, CLI тощо — «різні речі». Раніше плагін мовчазно припускав один зріз
(сервіс + його HTTP-контракт), а фронт жив як «зовнішній споживач». Тепер `design` **явно обирає**
поверхні на етапі архітектури, записує їх у `sad.md` → frontmatter `target_surfaces: [...]`, і всі
наступні етапи **читають** цей вибір (а не передеривовують щоразу), щоб увімкнути саме свої
поверхне-специфічні артефакти: UI-архітектурні ADR, шар задач `ui`, фронтові рівні тестів,
UI-орієнтовані flow-діаграми, правильну форму `api`-контракту.

Поверхня прив'язана до C4: **поверхня = контейнер C4, який фіча вводить або володіє ним**. Це не нове
поняття — плагін уже говорить мовою C4 у §5 SAD; тут лише робимо вибір контейнерів **явним і типізованим**.

---

## The model — a surface is a C4 container the feature owns

«Surface» is our coinage; we anchor it to vocabulary the plugin already speaks. C4 calls the unit
**container** — *a separately runnable/deployable thing: an application or a data store*
([c4model.com/abstractions/container](https://c4model.com/abstractions/container)). C4's container
diagram is exactly where surfaces **and their technology** are declared together, and C4 already
splits one feature into **one container per surface** (a server-rendered web app is one container; a
significant SPA is two — the backend API + the SPA; the worked example on c4model.com is five:
Backend API + SPA + server-side web app + mobile app + database).

So: **a target surface = a C4 container the feature introduces or owns.** Picking the surfaces *is*
deciding which §5 containers the feature draws. Data stores are **not** surfaces — they're a
`ContainerDb` that `data-model` owns; a surface is a thing that *runs behaviour*, not a thing that
*holds state*.

## The taxonomy (C4-grounded, fixed-but-extensible)

Seven surfaces, each one a C4 container type from c4model.com's enumeration (server-side web app,
client-side SPA, desktop app, mobile app, console/CLI app, serverless function/worker, + data stores):

| Surface | What it is (the C4 container) | Typical owner |
|---|---|---|
| `backend-service` | A server-side application exposing an interface (HTTP/REST, gRPC, or events). The default. | Backend Lead |
| `web-frontend` | A browser-delivered UI — **server-rendered (SSR)** *or* a **client-side SPA** (the sub-kind is a UI-architecture decision). | Frontend Lead |
| `mobile-app` | A native or cross-platform app on a phone/tablet. | Mobile Lead |
| `desktop-app` | A native or cross-platform desktop application. | Desktop Lead |
| `cli` | A console / command-line application — commands, flags, exit codes. | Backend Lead |
| `worker` | An event-consumer / scheduled job / serverless function — no request/response surface. | Backend Lead |
| `library-sdk` | A library or SDK: the public signatures/types it exposes are the contract. | Lib owner |

The list is **fixed but extensible** — a genuinely new surface (e.g. a voice/IVR or an embedded
firmware target) extends the table here, in one place, not inside a consuming skill. Most features
pick **one or two** (`[backend-service]`, or `[backend-service, web-frontend]` for a fullstack
feature); a multi-surface feature is **larger** (each surface adds its own layer + test tiers — see
[`./size-matrix.md`](./size-matrix.md)) and multi-surface is itself usually a blast-radius decision
(irreversible / multi-module → an ADR).

## The contract — declared once at design, read (never re-derived) downstream

This is the load-bearing rule, and the novel bit: no surveyed tool gates *which design artifacts get
generated* by surface (spec-kit gates file paths; Kiro gates Feature-vs-Bug). Surface-**gated artifact
selection** is ours. The mechanism is the same "declare → conditionally include" pattern, applied to
the artifact axis:

1. **`design` declares.** The Target-surface decision is the **first** §4 Solution-Strategy decision,
   derived from spec §1 «for whom» + §4 roles (the spec stays product-level — it never names a
   surface). It's gated by the blast-radius gate (multi-surface ⇒ usually an ADR) and manifested in
   the §5 C4 Container view (one container per surface).
2. **`design` writes it to the SAD frontmatter** — `target_surfaces: [backend-service, web-frontend]`
   — machine-readable, mirroring how `feature_size` is carried.
3. **Downstream reads it, never re-derives it.** `api` / `sequences` / `tasks` / `plan-tests` / `review`
   read `sad.md` frontmatter `target_surfaces` and gate their output by the table below. They do **not**
   re-infer the surface from the architecture map each run — `design` already decided, once.

This **generalizes `api`'s existing interface-kind awareness up one level**: instead of `api` silently
re-deriving the contract kind (HTTP / gRPC / CLI / events) every run, `design` declares the surface(s)
once and `api` (plus the others) read it. The derive-from-architecture-map path stays only as the
**fallback** when the SAD or the field is absent (a greenfield run where `design` was skipped).

## The gating table (what each surface turns on)

Each consuming skill reads `target_surfaces` and includes only the rows its declared surfaces select:

| Surface | `api` contract form | `sequences` flows | `tasks` layers | `plan-tests` tiers added |
|---|---|---|---|---|
| `backend-service` | OpenAPI / gRPC / events (per the sub-kind) | service + async flows | domain · infra · app · ports | (existing) unit · integration · contract |
| `web-frontend` | *consumes* the backend contract (does not author it) | UI-driven (`<user>` → `<ui>` → `<service>` → `<data-store>`) | **`ui`** | **component · visual-regression · e2e-through-UI** |
| `mobile-app` | consumes the contract | UI-driven | **`ui`** | component · e2e-through-UI |
| `desktop-app` | consumes the contract | UI-driven | **`ui`** | component · e2e-through-UI |
| `cli` | `contracts/cli.md` (commands/flags/exit-codes) | command flows | app · ports | unit · e2e (command) |
| `worker` | `contracts/events.md` (no request/response) | async flows | domain · infra | unit · integration |
| `library-sdk` | `contracts/public-api.md` (public signatures) | usage flows | domain · app | unit · contract |

Read it as: a feature with `[backend-service, web-frontend]` produces the backend contract **and** a
`ui` task layer, UI-driven sequence flows alongside the service flows, and the component /
visual-regression / e2e-through-UI test tiers on top of the backend's unit/integration/contract.

## The UI-architecture decision (per UI surface — kept light, Option B)

For each **UI surface** declared (`web-frontend` / `mobile-app` / `desktop-app`), `design` walks a
follow-on **UI-architecture decision** — this evolves today's "read-side delivery (SSR / SPA /
API-only)" §4 item up into a per-surface choice:

- **web** → server-rendered (SSR) / SPA / hybrid;
- **mobile** → native / cross-platform;
- plus **state-management** and **routing** *only if* the feature's complexity warrants them.

Gated like any §4 strategic decision → an ADR in §9 when it crosses the blast-radius gate. Kept
**light**: this is the **only** UI artifact the plugin generates. There is deliberately **no**
component-tree, no design-token doc, no screen/wireframe artifact (that would be a separate deep
UI-design pipeline — out of scope). The `ui` task layer + the UI-architecture ADR + the frontend
test tiers + the UI sequence flows are the whole of the frontend footprint.

## The frontend test tiers (testing-trophy provenance)

The component / visual-regression / e2e-through-UI tiers `plan-tests` adds for a UI surface come from
the **"testing trophy"** — the dominant frontend testing vocabulary (web.dev's testing strategies;
Kent C. Dodds): static → unit → integration (incl. **component** and API tests) → UI (incl. **E2E**
and **visual / visual-regression**) ([web.dev/articles/ta-strategies](https://web.dev/articles/ta-strategies)).
It's the **dominant vocabulary, not a mandate** — and **stack-agnostic** here: `plan-tests` names the
*tier*, never the tool. `implement` detects the actual runner (Playwright / Storybook / a
visual-regression tool / etc.) from the repo, exactly as it already does for the backend tiers.

## Discipline

- **The taxonomy + gating table live here only.** A consuming skill that copies the table has
  duplicated the source of truth — it keeps a one-line pointer + its own delta instead.
- **`design` writes `target_surfaces`; nobody else does.** Downstream reads it. A skill that
  re-derives the surface when the SAD already declared it is the anti-pattern this file kills (the
  same shape as `api` double-deriving the interface kind).
- **The spec stays product-level.** Surfaces are derived from spec §1/§4 at design — the spec never
  names a surface, a stack, or an endpoint group.
- **Option B boundary.** Thread frontend-awareness through the existing stages; do **not** grow a
  parallel UI-design pipeline. No component-tree / token / screen artifact — if a run starts producing
  one, it's left the scope this file fixes.
- **Data stores are not surfaces.** A `ContainerDb` is `data-model`'s job; a surface runs behaviour.

## Where each skill reads this

- **`design`** — owns the **selection**: the Target-surface decision is §4's first decision, the
  UI-architecture decision follows per UI surface, both gated to ADRs; writes `target_surfaces` to
  `sad.md` frontmatter; draws one §5 C4 container per surface.
- **`api`** — reads `target_surfaces` first to pick the contract form (the table); falls back to
  derive-from-architecture-map only if the SAD/field is absent.
- **`sequences`** — for a declared UI surface, draws UI-driven flows (`<user>` → `<ui>` → `<service>`
  → `<data-store>`); adds `<ui>` to the generic participant vocabulary.
- **`tasks`** — gates the layer set by `target_surfaces`; a UI surface adds the `ui` layer (not
  auto-serialized — UI tasks can parallelize).
- **`plan-tests`** — adds the component / visual-regression / e2e-through-UI tiers when a UI surface
  is declared.
- **`review`** — the end-to-end AC trace spans UI surfaces (a UI AC traces to a component /
  e2e-through-UI test), not only backend.
