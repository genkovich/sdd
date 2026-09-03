---
status: current
updated_at: "2026-08-19"
reflects_commit: "baseline"
language: "Go 1.23"
build_cmd: "go build ./..."
test_cmd: "go test ./..."
lint_cmd: "golangci-lint run"
migration_tool: "golang-migrate"
frontend: ""
---

# Architecture map — shop

## Module inventory

| Module | Path | Responsibility |
|---|---|---|
| checkout | `internal/checkout/` | cart contents and the order price computation (`pricing.go`) |
| notify | `internal/notify/` | transactional email, including the order-confirmation template |

## Conventions

- One package per module under `internal/`; no cross-module imports except through an interface
  declared by the consumer (`internal/checkout/pricing.go:1`).
- Tests live beside the code as `*_test.go` (`internal/checkout/pricing_test.go`).
