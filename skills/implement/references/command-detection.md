# Command detection (step 3)

Resolve four commands — **unit test**, **integration test**, **lint**, **vet/typecheck** — without hard-coding any language. Run the cascade per command; the first hit wins. Print the resolved set so the user can see (and override via settings) what the engine will run.

## Cascade (first match wins)

1. **Settings override.** A non-empty `cmd_test_unit` / `cmd_test_integration` / `cmd_lint` / `cmd_vet` in `.claude/sdd.local.md` short-circuits everything. This is the escape hatch for unusual repos.
2. **Architecture-map frontmatter.** If `docs/architecture-map.md` exists and its frontmatter carries a non-empty `test_cmd` / `lint_cmd` (recorded by `survey` from what the repo actually uses), take it. `""` means unknown — fall through to the next step for that command.
3. **Makefile targets.** If a `Makefile` exists, grep its targets. Map by convention: `test` / `test-unit` → unit; `test-integration` / `integration` / `test-e2e` → integration; `lint` → lint; `vet` / `typecheck` / `check` → vet. A `Makefile` target wins over a raw tool because it encodes the repo's own wiring (flags, build tags, env).
4. **`package.json` scripts.** If present, read `scripts`: `test` / `test:unit` → unit; `test:integration` / `test:e2e` → integration; `lint` → lint; `typecheck` / `tsc` → vet. Invoke via the repo's package manager (detect `pnpm-lock.yaml` / `yarn.lock` / `package-lock.json`).
   4a. **Task-runner wrapper** (Ruby/Fastlane-style — same rationale as steps 3–4: a wrapper encodes the repo's own wiring, so it wins over a raw tool). If a `Gemfile` + `fastlane/Fastfile` (or a repo-local task-runner manifest like `Matfile`) is present, grep its lanes/tasks and map by lane-name convention: `*unit*` → unit; `*ui*` / `*integration*` / `*instrument*` → integration; a lane that runs `lint` / `detekt` / `ktlint` / `swiftlint` → lint; a build/assemble lane → vet. Invoke through the repo's runner (`bundle exec <runner> <lane>`). This is **tool-agnostic** — detect *a wrapper and its lanes*, never hard-code "Fastlane"/"MAT". (Common in mobile repos, where the real command is a lane, not a bare `xcodebuild`/`gradlew`.)
5. **Language manifests** (the broad fallback — pick the toolchain the manifest implies):
   - `go.mod` → unit `go test ./...`; integration `go test -tags=integration ./...`; vet `go vet ./...`; lint `golangci-lint run` (if installed).
   - `Cargo.toml` → `cargo test` / `cargo test -- --ignored` / `cargo clippy` / `cargo check`.
   - `pyproject.toml` / `setup.cfg` → `pytest` / `pytest -m integration` / `ruff check` (or `flake8`) / `mypy`.
   - `pom.xml` → `mvn test` / `mvn verify` / (checkstyle/spotless) / `mvn -q compile`. **(`build.gradle` alone no longer implies Maven — see the Android row: a Gradle repo with an `AndroidManifest.xml` is Android, not JVM/Maven. A `build.gradle`/`build.gradle.kts` with *no* `AndroidManifest.xml` and no `pom.xml` is a JVM-Gradle repo → `./gradlew test` / `./gradlew check`.)**
   - **iOS** — `Package.swift` / `*.xcodeproj` / `*.xcworkspace` (+ `Podfile` if present) → unit `xcodebuild test -scheme <s> -destination 'platform=iOS Simulator,name=<device>'`; lint `swiftlint` (only if on PATH); vet `xcodebuild build`. Prefer step 4a's wrapper lane if the repo has one.
   - **Android** — `build.gradle`/`build.gradle.kts` **+ `AndroidManifest.xml`** (the manifest disambiguates Android from a JVM/Maven Gradle repo) → unit `./gradlew testDebugUnitTest` (or the repo's **flavor-specific** variant, e.g. `testDevelopmentDebugUnitTest`, when product flavors exist — grep the build files for `productFlavors`); integration `./gradlew connectedDebugAndroidTest` (emulator-gated) **or the repo's device-farm lane** (e.g. Firebase Test Lab via step 4a) when defined; lint `./gradlew lint` + whichever static-analysis the repo configures (`detekt` / `ktlint` — detect, don't assume); vet `./gradlew assembleDebug`. Prefer step 4a's wrapper lane if present.
   - `composer.json` → `vendor/bin/phpunit` (or the `scripts.test` entry) / the repo's tagged integration suite / `vendor/bin/phpcs` or `php-cs-fixer` / `vendor/bin/phpstan` or `psalm` (whichever is configured).
   - `Gemfile` → `bundle exec rspec` / `bundle exec rspec --tag integration` / `rubocop` / (no conventional typecheck — skip).
   - `*.csproj` / `*.sln` → `dotnet test` / `dotnet test --filter <integration category>` / `dotnet format --verify-no-changes` / `dotnet build`.
   - any other manifest → there is no convention to trust: **ask the user for the commands** (and offer to save them to `.claude/sdd.local.md`) — never guess.
6. **Integration tier — Docker probe (server) OR simulator/emulator probe (mobile).** Whatever produced the integration command, confirm its runtime dependency is reachable before trusting it, and feed the result to `require_integration` (see [`settings.md`](./settings.md)) with the same semantics — `auto` → run if reachable else NON-red; `always` → BLOCK if unreachable; `never` → skip:
   - **Server/backend** — confirm a Docker daemon (`docker info` succeeds); most integration suites spin up an ephemeral dependency (testcontainers-style).
   - **Mobile** — the instrumented / UI / e2e tier needs a **booted simulator or emulator** the way backend integration needs Docker. Probe iOS via `xcrun simctl list | grep Booted` (boot one with `xcrun simctl boot` if needed), Android via `adb devices` / a running AVD. A device-farm lane (e.g. Firebase Test Lab from step 4a) satisfies the probe without a local device. No booted device and no farm lane → treat as unreachable (same `require_integration` handling as an absent Docker daemon).

## Reporting

After detection, print a block like:

```
detected commands:
  unit         = make test
  integration  = make test-integration   (docker: reachable)
  lint         = golangci-lint run        (binary: present)
  vet          = make vet
```

For a mobile repo the integration line notes the device probe instead of Docker, e.g.:

```
detected commands:
  unit         = bundle exec mat run_unit_tests --scheme_dev NativeMessagingSDK-Dev   (wrapper lane)
  integration  = ./gradlew connectedDebugAndroidTest                                  (emulator: booted)
  lint         = ./gradlew detekt
  vet          = ./gradlew assembleDebug
```

If a command can't be resolved: lint/vet missing → skip that gate with a one-line warning (don't fail the run); unit missing → **stop** (TDD needs a unit runner); integration missing → governed by `require_integration`.

## Notes

- Detection is read-only — never install tools. If `golangci-lint` (or any linter) isn't on PATH, note it and skip lint locally; CI can enforce it.
- Cache the resolved set for the whole run; don't re-detect per task.
- **`default_surfaces` is a hint, not a rule.** If `.claude/sdd.local.md` sets `default_surfaces` to a mobile surface, you may try the iOS/Android manifest rows first — but **a manifest found on disk always wins**. Never let the setting override actual evidence (a repo mislabelled mobile that is really a Go service still detects as Go).
