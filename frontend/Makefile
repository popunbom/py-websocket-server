.PHONY: all
all: init run

.PHONY: init
init:
ifneq ($(shell type "npm" >/dev/null 2>&1; echo $$?), 0)
	@echo npm is not installed
	exit -1
endif
ifneq ($(shell type "pnpm" >/dev/null 2>&1; echo $$?), 0)
	# REF: https://pnpm.io/ja/installation
	curl -f https://get.pnpm.io/v6.16.js | node - add --global pnpm
endif
	pnpm i

.PHONY: run
run:
	pnpm dev
