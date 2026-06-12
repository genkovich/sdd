# Command detection (step 3)

Resolve four commands — **unit test**, **integration test**, **lint**, **vet/typecheck** — without hard-coding any language. Run the cascade per command; the first hit wins. Print the resolved set so the user can see (and override via settings) what the engine will run.

## Cascade (first match wins)

1. **Settings override.** A non-empty `cmd_test_unit` / `cmd_test_integration` / `cmd_lint` / `cmd_vet` in `.claude/sdd.local.md` short-circuits everything. This is the escape hatch for unusual repos.
2. **Makefile targets.** If a `Makefile` exists, grep its targets. Map by convention: `test` / `test-unit` → unit; `test-integration` / `integration` / `test-e2e` → integration; `lint` → lint; `vet` / `typecheck` / `check` → vet. A `Makefile` target wins over a raw tool because it encodes the repo's own wiring (flags, build tags, env).
3. **`package.json` scripts.** If present, read `scripts`: `test` / `test:unit` → unit; `test:integration` / `test:e2e` → integration; `lint` → lint; `typecheck` / `tsc` → vet. Invoke via the repo's package manager (detect `pnpm-lock.yaml` / `yarn.lock` / `package-lock.json`).
4. **Language manifests** (the broad fallback — pick the toolchain the manifest implies):
   - `go.mod` → unit `go test ./...`; integration `go test -tags=integration ./...`; vet `go vet ./...`; lint `golangci-lint run` (if installed).
   - `Cargo.toml` → `cargo test` / `cargo test -- --ignored` / `cargo clippy` / `cargo check`.
   - `pyproject.toml` / `setup.cfg` → `pytest` / `pytest -m integration` / `ruff check` (or `flake8`) / `mypy`.
   - `pom.xml` / `build.gradle` → `mvn test` / `mvn verify` / (checkstyle/spotless) / `mvn -q compile`.
   - `composer.json` → `vendor/bin/phpunit` (or the `scripts.test` entry) / the repo's tagged integration suite / `vendor/bin/phpcs` or `php-cs-fixer` / `vendor/bin/phpstan` or `psalm` (whichever is configured).
   - `Gemfile` → `bundle exec rspec` / `bundle exec rspec --tag integration` / `rubocop` / (no conventional typecheck — skip).
   - `*.csproj` / `*.sln` → `dotnet test` / `dotnet test --filter <integration category>` / `dotnet format --verify-no-changes` / `dotnet build`.
   - any other manifest → there is no convention to trust: **ask the user for the commands** (and offer to save them to `.claude/sdd.local.md`) — never guess.
5. **Integration tier — Docker probe.** Whatever produced the integration command, confirm a Docker daemon is reachable (`docker info` succeeds) before trusting it — most integration suites spin up an ephemeral dependency (testcontainers-style). Feed the probe result to `require_integration` (see [`settings.md`](./settings.md)): `auto` → run if reachable else NON-red; `always` → BLOCK if unreachable; `never` → skip.

## Reporting

After detection, print a block like:

```
detected commands:
  unit         = make test
  integration  = make test-integration   (docker: reachable)
  lint         = golangci-lint run        (binary: present)
  vet          = make vet
```

If a command can't be resolved: lint/vet missing → skip that gate with a one-line warning (don't fail the run); unit missing → **stop** (TDD needs a unit runner); integration missing → governed by `require_integration`.

## Notes

- Detection is read-only — never install tools. If `golangci-lint` (or any linter) isn't on PATH, note it and skip lint locally; CI can enforce it.
- Cache the resolved set for the whole run; don't re-detect per task.
