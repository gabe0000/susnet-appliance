SHELL := /bin/sh
PYTHON ?= python3
IMAGE ?=
REFERENCE_DIR ?= reference
QUALIFICATION_OUTPUT ?= build/qualification-report.md

.PHONY: doctor bootstrap lint unit integration packages image verify-image qualification-report sign-reference handoff test

doctor:
	$(PYTHON) tools/doctor.py

bootstrap:
	$(PYTHON) tools/bootstrap.py

lint:
	$(PYTHON) -m compileall -q tools tests
	$(PYTHON) tools/security_scan.py --repository .
	$(PYTHON) tools/validate_bootstrap.py

unit:
	$(PYTHON) -m unittest discover -s tests/unit -v

integration:
	$(PYTHON) -m unittest discover -s tests/integration -v

test: lint unit integration

packages:
	$(PYTHON) tools/release_gate.py packages

image:
	$(PYTHON) tools/release_gate.py image

verify-image:
	$(PYTHON) tools/verify_image.py "$(IMAGE)"

qualification-report:
	$(PYTHON) tools/qualification_report.py --evidence evidence/runs --output "$(QUALIFICATION_OUTPUT)"

sign-reference:
	$(PYTHON) tools/sign_reference.py --manifest "$(REFERENCE_DIR)/manifest.yaml"

handoff: test
	$(PYTHON) tools/handoff_bundle.py --output build/susnet-developer-handoff.tar.gz
