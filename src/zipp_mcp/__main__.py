"""Module entry — lets ``python -m zipp_mcp`` work identically to the
``zipp-mcp`` script registered in pyproject.toml."""
from zipp_mcp.cli import main

if __name__ == "__main__":
    main()
