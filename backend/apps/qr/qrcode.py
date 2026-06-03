"""QR code generation for goat ear tags.

A QR encodes the goat's public worker URL (``http://{host}/g/{uuid}``). The PNG
is written under ``MEDIA_ROOT/qr/{uuid}.png`` and a ``QRCode`` row records it.
Regenerating deactivates the previous active QR (the goat's UUID never changes),
so only one QR is active per goat — backed by the model's partial-unique
constraint.

Standard Django: plain module functions, ORM used directly. No service layer.
"""

import io
from pathlib import Path

import segno
from django.conf import settings

from apps.goats.models import QRCode

PNG_SCALE = 8
PDF_SCALE = 10


def qr_url(goat):
    """The public worker URL a scan resolves to."""
    host = getattr(settings, "FARM_LOCAL_HOSTNAME", "goatfarm.local")
    return f"http://{host}/g/{goat.id}"


def generate_qr(goat):
    """Generate (or regenerate) the active QR for ``goat``.

    Deactivates any current active QR, writes a fresh PNG, and returns the new
    active ``QRCode`` row.
    """
    QRCode.objects.filter(goat=goat, is_active=True).update(is_active=False)

    image_path = f"qr/{goat.id}.png"
    abs_path = Path(settings.MEDIA_ROOT) / image_path
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    segno.make(qr_url(goat)).save(str(abs_path), scale=PNG_SCALE)

    return QRCode.objects.create(goat=goat, image_path=image_path, is_active=True)


def build_print_pdf(goat):
    """Return PDF bytes of the goat's QR, ready to print on an ear tag."""
    buffer = io.BytesIO()
    segno.make(qr_url(goat)).save(buffer, kind="pdf", scale=PDF_SCALE)
    return buffer.getvalue()
