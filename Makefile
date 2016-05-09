.PHONY: tests devinstall docs
APP=siglock
COV=siglock
OPTS=

tests:
	py.test $(APP)

devinstall:
	pip install -e .
	pip install -e .[tests]

docs:
	sphinx-apidoc --force -o docs/source/modules/ siglock
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
