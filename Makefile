.PHONY: install install-uv install-pre-commit lint

## Installe uv (si absent) puis les hooks pre-commit
install: install-uv install-pre-commit

## Installe uv (gestionnaire de paquets/venv Python)
install-uv:
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "Installation de uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	else \
		echo "uv est déjà installé ($$(uv --version))"; \
	fi

## Installe pre-commit via uv et active les hooks git
install-pre-commit: install-uv
	uv tool install pre-commit
	uv tool run pre-commit install

## Lint backend (appelé par pnpm run lint:backend)
lint:
	uv tool run pre-commit run --all-files
