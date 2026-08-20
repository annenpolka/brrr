"""ambit: the ambit of a predicate.

Name a snippet; emit every locus whose path-condition contains it.
Files come from stdin locators (`rg | ambit`) or explicit FILE operands.
No implicit tree walk.
"""

from .model import Frame, Locus, Query
from .query import index_source, query_file, query_locus

__all__ = ["Frame", "Locus", "Query", "index_source", "query_file", "query_locus"]
__version__ = "0.2.0"
