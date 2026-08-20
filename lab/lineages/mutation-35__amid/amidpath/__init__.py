"""amid: scan the same file as stdin locators for a path-condition."""

from .model import Frame, Locus, Query
from .query import index_source, query_file, query_locus

__all__ = ["Frame", "Locus", "Query", "index_source", "query_file", "query_locus"]
__version__ = "0.2.0"
