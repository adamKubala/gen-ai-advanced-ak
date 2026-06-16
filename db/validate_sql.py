import sqlglot
from sqlglot import exp

from config.settings import get_config
from db.allowlist import ALLOWED_TABLES
from utils.logger import get_logger

logger = get_logger(__name__) #__name__ is the name of the current module

FORBIDDEN_KEYWORDS = frozenset(
    {"insert", "update", "delete", "drop", "alter", "truncate", "create", "grant", "revoke"}
)

class SqlValidationError(ValueError):
    """Raised when SQL validation failed."""

def normalize_sql(sql: str) -> str:
    """Normalize SQL by parsing and re-generating it."""
    return sql.strip().rstrip(";")

def validate_sql(sql: str, max_limit: int | None = None) -> str:
    if max_limit is None:
        max_limit = get_config().sql_max_limit

    cleaned = normalize_sql(sql)
    lowered = cleaned.lower()

    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in lowered:
            raise SqlValidationError(f"Forbidden keyword '{keyword}' found in SQL.")


    try:
        expression = sqlglot.parse_one(cleaned, dialect="postgres")
    except sqlglot.errors.ParseError as ex:
        raise SqlValidationError(f"SQL parsing error: {ex}")
    

    if not isinstance(expression, exp.Select):
        raise SqlValidationError("Only SELECT statements are allowed.")
    
    tables = {t.name.lower() for t in expression.find_all(exp.Table)}
    unknown = tables - ALLOWED_TABLES
    if unknown:
        raise SqlValidationError(f"Unknown tables referenced: {', '.join(unknown)}. Allowed tables: {', '.join(sorted(ALLOWED_TABLES))}")
    
    limit_node = expression.args.get("limit")
    if limit_node is not None:
        try:
            limit_value = int(limit_node.expression.this)
        except:
            raise SqlValidationError("Not able to get LIMIT value.")
        
        if limit_value < 0:
            raise SqlValidationError("LIMIT value must be non-negative.")
        
        if limit_value > max_limit:
            raise SqlValidationError(f"LIMIT value {limit_value} exceeds maximum allowed {max_limit}.")
        
        logger.info("SQL Query validated successfully with LIMIT: %d", limit_value)
        return cleaned