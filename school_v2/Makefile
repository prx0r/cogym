.PHONY: check conformance rust
conformance:
	python tools/conformance.py
rust:
	cargo fmt --all -- --check
	cargo clippy --workspace --all-targets -- -D warnings
	cargo test --workspace
check: conformance rust
