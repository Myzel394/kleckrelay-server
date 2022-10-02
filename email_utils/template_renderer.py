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
)


def render(name: str, language: LanguageType, /, **kwargs) -> str:
    template_name = f"{name}.{str(language).split('.')[1]}.jinja2"

    template = env.get_template(template_name)

    return template.render(
        EMAIL_LANDING_PAGE_URL_TEXT=life_constants.EMAIL_LANDING_PAGE_URL_TEXT,
        EMAIL_LANDING_PAGE_URL=life_constants.EMAIL_LANDING_PAGE_URL,
        APP_DOMAIN=life_constants.DOMAIN,
        **kwargs,
    )
