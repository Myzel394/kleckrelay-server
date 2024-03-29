from jinja2 import Environment, FileSystemLoader

from app import life_constants
from app.models import LanguageType
from ._get_root_dir import ROOT_DIR

__all__ = [
    "LanguageType",
    "render",
]

TEMPLATE_DIR = ROOT_DIR / "templates" / "emails"

env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR.absolute())),
    autoescape=True,
)


def render(name: str, /, **kwargs) -> str:
    template = env.get_template(name)

    return template.render(
        APP_DOMAIN=life_constants.API_DOMAIN,
        **kwargs,
    )
