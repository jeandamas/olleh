from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.payments.models import LayawayPayment
from apps.orders.models import Layaway


@transaction.atomic
def confirm_layaway_payment(payment: LayawayPayment, confirmed_by) -> Layaway:
    """
    Staff confirms a layaway payment: add amount to layaway.amount_paid_rwf,
    set confirmed_at/confirmed_by. If layaway is now paid in full, mark it completed.
    """
    if payment.confirmed_at is not None:
        raise ValidationError("This payment is already confirmed.")
    layaway = payment.layaway
    if layaway.status not in (Layaway.STATUS_ACTIVE, Layaway.STATUS_COOLING_OFF):
        raise ValidationError(
            "Payments can only be confirmed for active or cooling-off layaways."
        )
    new_total_paid = layaway.amount_paid_rwf + payment.amount_rwf
    if new_total_paid > layaway.total_rwf:
        raise ValidationError(
            f"Confirming {payment.amount_rwf:,} RWF would exceed layaway total "
            f"({layaway.total_rwf:,} RWF). Current amount paid: {layaway.amount_paid_rwf:,} RWF."
        )
    now = timezone.now()
    payment.confirmed_at = now
    payment.confirmed_by = confirmed_by
    payment.save(update_fields=["confirmed_at", "confirmed_by"])
    layaway.amount_paid_rwf = new_total_paid
    layaway.save(update_fields=["amount_paid_rwf"])
    if (
        layaway.status == Layaway.STATUS_ACTIVE
        and layaway.amount_paid_rwf >= layaway.total_rwf
    ):
        layaway.mark_completed()
    return layaway
