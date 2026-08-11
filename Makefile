.PHONY: check check-repo check-sq0002-evidence check-sq0005-evidence check-schema-v0 check-registry list-work

check: check-repo check-sq0002-evidence check-sq0005-evidence check-schema-v0 check-registry

check-repo:
	python3 scripts/check_repository.py

check-sq0002-evidence:
	python3 scripts/bootstrap/run_toolchain_probes.py --verify

check-sq0005-evidence:
	python3 scripts/serialization/check_evidence.py

check-schema-v0:
	python3 scripts/schema/check_schema_v0.py

check-registry:
	python3 scripts/registry/check_evidence.py

list-work:
	python3 scripts/list_work.py
