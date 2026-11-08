from .models import AuditLog


def log_action(
    user,
    action,
    entity_type,
    entity_id,
    description="",
    ip_address=None,
):
    return AuditLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        description=description,
        ip_address=ip_address,
    )