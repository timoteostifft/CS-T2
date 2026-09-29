"""Exporta o contrato OpenAPI gerado pelo app FastAPI para um arquivo JSON."""

import json
import sys
from pathlib import Path

from recomendacoes_api.app import app


def main() -> None:
    output = Path(sys.argv[1] if len(sys.argv) > 1 else "openapi.json")
    output.write_text(json.dumps(app.openapi(), indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
