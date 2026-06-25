from sqlalchemy.exc import IntegrityError


def integrity_error_constraint(exc: IntegrityError) -> str | None:
    """Name of the constraint that caused exc, or None if unavailable.

    asyncpg wraps the underlying asyncpg.exceptions.PostgresError (which carries
    constraint_name) as exc.orig.__cause__ rather than exposing it on exc.orig itself.
    """
    return getattr(exc.orig, "constraint_name", None) or getattr(
        getattr(exc.orig, "__cause__", None), "constraint_name", None
    )
