import json
import functools
from pathlib import Path
from django import template
from django.conf import settings
from django.utils.html import format_html

register = template.Library()


@functools.cache
def _load_manifest():
    manifest_path = Path(settings.BASE_DIR) / "static" / "dist" / ".vite" / "manifest.json"
    if manifest_path.exists():
        return json.loads(manifest_path.read_text())
    return {}


@register.simple_tag
def vite_asset(entry: str) -> str:
    if settings.DEBUG:
        _load_manifest.cache_clear()
    manifest = _load_manifest()
    chunk = manifest.get(entry)
    if chunk is None:
        return format_html("<!-- vite_asset: {} not in manifest -->", entry)
    file = chunk["file"]
    tag = format_html('<script type="module" src="{}/{}"></script>', settings.STATIC_URL + "dist/", file)
    css_tags = "".join(
        format_html('<link rel="stylesheet" href="{}/{}">',  settings.STATIC_URL + "dist/", css)
        for css in chunk.get("css", [])
    )
    return css_tags + tag
