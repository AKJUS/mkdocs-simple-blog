"""Regression tests for issue #92 -- page-dates divider duplicating
blog_list's own first-item border on pages with no body content.
"""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from jinja2 import Environment, FileSystemLoader

from mkdocs_simple_blog.plugin.dates import format_date

from .fixtures import THEME_DIR


def _url_filter(path: str) -> str:
    return path


def _template_env(*, register_fmt_date: bool = True) -> Environment:
    env = Environment(loader=FileSystemLoader(str(THEME_DIR)), autoescape=True)
    env.filters["url"] = _url_filter
    if register_fmt_date:
        env.filters["fmt_date"] = format_date
        env.globals["fmt_date"] = format_date
    return env


class PageDatesDividerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.env = _template_env()
        self.template = self.env.get_template("modules/content.html")

    def _render(self, content: str) -> str:
        config = SimpleNamespace(theme=SimpleNamespace(components=None))
        page = SimpleNamespace(
            title="Blog",
            content=content,
            meta={"date": "2024-01-05"},
            file=None,
        )
        return self.template.render(config=config, page=page)

    def test_no_divider_when_page_has_no_body_content(self) -> None:
        html = self._render("")
        self.assertIn("page-dates", html)
        self.assertNotIn("page-dates-divider", html)

    def test_divider_present_when_page_has_body_content(self) -> None:
        html = self._render("<p>Some real body text.</p>")
        self.assertIn("page-dates-divider", html)


class MissingFmtDateFilterTests(unittest.TestCase):
    """Regression tests for issue #96 -- content.html crashed on any page
    with a `date` in front matter when the `simple-blog-posts` plugin
    wasn't installed/enabled, since `fmt_date` is only ever registered by
    that plugin's `on_env` hook, yet page_dates is on by default and
    content.html is the theme's own base template, used by every page."""

    def setUp(self) -> None:
        self.env = _template_env(register_fmt_date=False)
        self.template = self.env.get_template("modules/content.html")

    def test_renders_without_crashing_when_plugin_is_not_installed(
        self,
    ) -> None:
        config = SimpleNamespace(theme=SimpleNamespace(components=None))
        page = SimpleNamespace(
            title="Test",
            content="<p>A test file</p>",
            meta={"date": "2025-09-15"},
            file=None,
        )
        html = self.template.render(config=config, page=page)
        self.assertIn("2025-09-15", html)
