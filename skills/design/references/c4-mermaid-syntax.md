# C4 Mermaid syntax — quick reference for sad.md §3 and §5

> **TL;DR (UA).** C4 — 4 рівні діаграм як zoom на мапі. **L1 Context** (система як чорний ящик + актори + зовнішні системи) = §3 SAD. **L2 Container** (внутрішня декомпозиція: модулі, сервіси, БД, черги) = §5 SAD. L3/L4 — поза межами цього skill. *Кордон довіри* (`Container_Boundary`) — лінія, за якою дані не довіряєш без перевірки.

design emits C4 Level 1 (Context) in §3 and Level 2 (Container) in §5 as Mermaid blocks inline in `sad.md`. L3 Component and L4 Code are deliberately out of scope — request a separate diagramming pass if you need them. Mermaid renders natively in GitHub and in Obsidian.

## L1 — System Context (`C4Context`)

Use in §3. The system as one black box plus people and external systems. 5–10 elements max.

```mermaid
C4Context
    title <feature> — System Context

    Person(author, "<Author role>", "creates/updates own content")
    Person(consumer, "<Consumer role>", "reads published content")
    Person_Ext(admin, "<External actor>", "out-of-band reports")

    System(app, "<Our system>", "<one-sentence description>")
    System_Ext(notifier, "<External service>", "<integration purpose>")
    SystemDb(store, "<Primary datastore>", "<what it holds>")

    Rel(author, app, "Creates and edits content", "HTTPS")
    Rel(consumer, app, "Reads content", "HTTPS")
    Rel(app, store, "Reads/writes", "<driver>")
    Rel(app, notifier, "Emits notifications", "<protocol>")
```

**Element types:**
- `Person(id, "name", "description")` — internal actor.
- `Person_Ext(id, "name", "description")` — external actor.
- `System(id, "name", "description")` — internal system.
- `System_Ext(id, "name", "description")` — external system.
- `SystemDb(id, "name", "description")` — external database (rare at L1).
- `Rel(from, to, "label", "protocol")` — connection; protocol is optional but recommended.

**Rules of thumb:**
- Show *your* system as one box — decomposition lives in L2.
- An external system = different owner / process / lifecycle. Internal modules of the same deployable do **not** appear in L1.
- 5–10 elements total. More than that = you're showing too much.

## L2 — Container (`C4Container`)

Use in §5. The inside of your system: apps, services, datastores, queues. For a single deployable, treat each *module* as a logical container.

```mermaid
C4Container
    title <feature> — Containers

    Person(author, "<Author role>")
    Person(consumer, "<Consumer role>")

    Container_Boundary(app, "<Our system>") {
        Container(web, "<Web/UI>", "<technology>", "<purpose>")
        Container(api, "<API/handler>", "<technology>", "<endpoints>")
        Container(core, "<Core module>", "<technology>", "<domain logic>")
        Container(worker, "<Background worker>", "<technology>", "polls + emits async work")
    }

    ContainerDb(store, "<Datastore>", "<technology>", "<tables/collections>")
    System_Ext(notifier, "<External service>", "<purpose>")

    Rel(author, web, "Edits content", "HTTPS")
    Rel(consumer, api, "Reads content", "HTTPS")
    Rel(web, api, "calls", "JSON/HTTPS")
    Rel(api, core, "service calls")
    Rel(core, store, "reads/writes", "<driver>")
    Rel(core, worker, "hands off async work")
    Rel(worker, notifier, "emits", "<protocol>")
```

**Element types:**
- `Container_Boundary(id, "label") { ... }` — groups containers inside one deployable unit.
- `Container(id, "name", "technology", "description")` — internal container (app, service, worker).
- `ContainerDb(id, "name", "technology", "description")` — internal datastore.
- `ContainerQueue(id, "name", "technology", "description")` — internal message queue.
- `System_Ext` and `Person` can be reused from L1.

**Rules of thumb:**
- For a single deployable: each module = one `Container`; the boundary brackets the whole process.
- Datastores live *outside* the boundary if they're separate processes (almost always).
- Show a background worker / scheduled job as its own container — its lifecycle matters even when it runs in-process.

**Multi-surface features — one `Container` per declared `target_surface`.** When §4 declares more than one surface (frontmatter `target_surfaces` → [`../../_shared/surfaces.md`](../../_shared/surfaces.md)), §5 draws one container for each. A `[backend-service, web-frontend, mobile-app]` feature shows the SPA **and** the mobile app **and** the backend API — both UI surfaces *consume* the API's contract, neither authors one:

```mermaid
C4Container
    title <feature> — Containers (multi-surface)

    Person(user, "<User role>")

    Container_Boundary(app, "<Our system>") {
        Container(spa, "<Web SPA>", "<SPA tech>", "browser UI — consumes the API")
        Container(mobile, "<Mobile app>", "<mobile tech>", "native UI — consumes the API")
        Container(api, "<Backend API>", "<backend tech>", "owns the REST/JSON contract")
    }

    ContainerDb(db, "<Datastore>", "<technology>", "<tables>")

    Rel(user, spa, "uses", "HTTPS")
    Rel(user, mobile, "uses", "HTTPS")
    Rel(spa, api, "calls", "JSON/HTTPS")
    Rel(mobile, api, "calls", "JSON/HTTPS")
    Rel(api, db, "reads/writes", "<driver>")
```

## Common mistakes

- **Mixing levels.** Don't put a component (a single class/struct) inside a Container diagram — either zoom out (it's part of the Container) or move to L3.
- **Typos in `Container_Boundary`.** Common: `Container_Bondary`, `ContainerBoundary` (no underscore). Mermaid silently renders an empty block.
- **`Rel` to an undeclared element.** Declare every `Person`/`Container`/`System*` first, then the `Rel` lines.
- **L1 with internal modules.** L1 = business scope. If a module shows up in L1, you're already at L2.
- **No label or protocol on `Rel`.** «Connected» tells the reader nothing. Always: what it does + how.

## Validating before commit

```bash
# Optional pre-commit check — extracts the Mermaid block and runs the CLI parser.
npx -y @mermaid-js/mermaid-cli@latest -i <(awk '/^```mermaid$/,/^```$/' docs/features/<slug>/sad.md) -o /tmp/out.svg
```

In practice: open `sad.md` in Obsidian or push to GitHub and inspect the render — both fail loudly on syntax errors.

## When the diagram doesn't fit

- L2 over 10–15 elements → split the feature into two SADs (one per bounded context), or drop tactical containers (the worker) into a note below the diagram.
- L1 with 15+ external systems → you're documenting the *organization*, not the *feature*. Pull back to «the systems this feature directly talks to».
