from __future__ import annotations

from importlib import import_module
from pkgutil import iter_modules

from dishka import Container, Module, make_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from .providers import db_module, settings_module


def _discover_modules() -> list[Module]:
    modules: list[Module] = []
    try:
        pkg = import_module("modules")
    except ModuleNotFoundError:
        return modules
    for info in iter_modules(pkg.__path__):
        if not info.ispkg:
            continue
        try:
            di = import_module(f"{pkg.__name__}.{info.name}.di")
        except ModuleNotFoundError:
            continue
        mod = getattr(di, "di", None) or getattr(di, "module", None)
        if isinstance(mod, Module):
            modules.append(mod)
    return modules


def build_container() -> Container:
    modules = [
        settings_module(),
        db_module(),
        *_discover_modules(),
    ]
    return make_container(*modules)


def setup_di(app: FastAPI) -> Container:
    container = build_container()
    setup_dishka(container, app)  # type: ignore[arg-type]
    return container
