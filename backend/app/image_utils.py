import base64
import binascii
import tempfile
from pathlib import Path


SUPPORTED_IMAGE_TYPES: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def _split_data_url(image_base64: str) -> tuple[str | None, str]:
    if image_base64.startswith("data:") and "," in image_base64:
        header, payload = image_base64.split(",", 1)
        media_type = header.removeprefix("data:").split(";", 1)[0]
        return media_type, payload
    return None, image_base64


def validate_base64_image(image_base64: str) -> bytes:
    """Validate a base64 image string and return decoded bytes."""
    media_type, payload = _split_data_url(image_base64.strip())
    if media_type is not None and media_type not in SUPPORTED_IMAGE_TYPES:
        raise ValueError("Unsupported image type. Use JPEG, PNG, or WebP.")

    try:
        decoded = base64.b64decode(payload, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Image must be a valid base64 string.") from exc

    if not decoded:
        raise ValueError("Image data is empty.")

    return decoded


def save_temp_image(image_base64: str) -> str:
    """Save an uploaded/webcam image to a temporary file and return its path."""
    media_type, _ = _split_data_url(image_base64.strip())
    decoded = validate_base64_image(image_base64)
    suffix = SUPPORTED_IMAGE_TYPES.get(media_type or "image/jpeg", ".jpg")

    # Hackathon demo only: images are written to the OS temp directory and are
    # not treated as permanent records. Production systems should use secure
    # storage, explicit consent, access controls, and retention/deletion policies.
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_image:
        temp_image.write(decoded)
        return str(Path(temp_image.name))


def image_to_data_url(image_base64: str) -> str:
    """Return a browser-ready data URL for an uploaded/webcam base64 image."""
    media_type, payload = _split_data_url(image_base64.strip())
    validate_base64_image(image_base64)
    return f"data:{media_type or 'image/jpeg'};base64,{payload}"
