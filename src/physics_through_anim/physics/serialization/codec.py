"""Generic, dependency-free codec: dataclass <-> dict / JSON / XML (Milestone M17).

The framework's specs (``ProblemScenePlan`` and the M18 presentation specs) are
plain dataclasses. This module round-trips any such spec through a JSON- or
XML-friendly form using only the field *type hints* -- no Pydantic, no schema
duplication. Enums serialise by value, tuples/lists/dicts recurse, and
``X | None`` fields are honoured.

    text = to_json(plan)                       # dataclass -> JSON text
    plan = from_json(ProblemScenePlan, text)   # JSON text -> dataclass
    xml  = to_xml(plan, root="plan")           # dataclass -> XML text
    plan = from_xml(ProblemScenePlan, xml)     # XML text  -> dataclass
"""

from __future__ import annotations

import json
import types
from dataclasses import fields, is_dataclass
from enum import Enum
from typing import Union, get_args, get_origin, get_type_hints
from xml.etree.ElementTree import Element, fromstring, tostring

__all__ = [
    "to_jsonable",
    "from_jsonable",
    "to_json",
    "from_json",
    "to_xml",
    "from_xml",
]

_PRIMITIVES = (str, int, float, bool)


# --- dataclass <-> plain (JSON-safe) python -----------------------------------

def to_jsonable(obj: object) -> object:
    """Convert a dataclass/enum/tuple/list/dict tree into JSON-safe primitives."""
    if obj is None or isinstance(obj, _PRIMITIVES):
        return obj
    if isinstance(obj, Enum):
        return obj.value
    if is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: to_jsonable(getattr(obj, f.name)) for f in fields(obj)}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(x) for x in obj]
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    raise TypeError(f"Cannot serialise value of type {type(obj).__name__!r}.")


def from_jsonable(tp: object, data: object, *, strict: bool = True) -> object:
    """Rebuild a value of type ``tp`` from the JSON-safe ``data`` (inverse of above).

    With ``strict=False`` an unknown ``Enum`` value is left as its raw form instead
    of raising -- so a validator can report it rather than the loader crashing.
    """
    origin = get_origin(tp)
    if origin in (Union, types.UnionType):
        if data is None:
            return None
        non_none = [a for a in get_args(tp) if a is not type(None)]
        # Try each arm (e.g. ``Bearing | float``): use the first that accepts ``data``.
        for arm in non_none:
            try:
                return from_jsonable(arm, data, strict=True)
            except (ValueError, TypeError, KeyError):
                continue
        if strict:
            return from_jsonable(non_none[0], data, strict=True)
        return data
    if is_dataclass(tp) and isinstance(tp, type):
        hints = get_type_hints(tp)
        kwargs = {f.name: from_jsonable(hints[f.name], data[f.name], strict=strict)
                  for f in fields(tp) if f.init and isinstance(data, dict) and f.name in data}
        return tp(**kwargs)
    if origin in (list,):
        (elem,) = get_args(tp) or (object,)
        return [from_jsonable(elem, x, strict=strict) for x in data]
    if origin in (tuple,):
        args = get_args(tp)
        if not args or (len(args) == 2 and args[1] is Ellipsis):
            elem = args[0] if args else object
            return tuple(from_jsonable(elem, x, strict=strict) for x in data)
        return tuple(from_jsonable(a, x, strict=strict) for a, x in zip(args, data, strict=False))
    if origin in (dict,):
        args = get_args(tp)
        val_t = args[1] if len(args) == 2 else object
        return {k: from_jsonable(val_t, v, strict=strict) for k, v in data.items()}
    if isinstance(tp, type) and issubclass(tp, Enum):
        try:
            return tp(data)
        except ValueError:
            if strict:
                raise
            return data
    if isinstance(tp, type) and tp in _PRIMITIVES and data is not None:
        return data if isinstance(data, bool) else tp(data)
    return data


def to_json(obj: object, *, indent: int | None = 2) -> str:
    """Serialise a dataclass spec to JSON text."""
    return json.dumps(to_jsonable(obj), indent=indent)


def from_json(tp: type, text: str, *, strict: bool = True) -> object:
    """Reconstruct a ``tp`` instance from JSON text."""
    return from_jsonable(tp, json.loads(text), strict=strict)


# --- plain python <-> XML (type-tagged, so ints/floats round-trip faithfully) --

def _to_element(tag: str, obj: object) -> Element:
    el = Element(tag)
    if obj is None:
        el.set("type", "null")
    elif isinstance(obj, bool):
        el.set("type", "bool")
        el.text = "true" if obj else "false"
    elif isinstance(obj, int):
        el.set("type", "int")
        el.text = str(obj)
    elif isinstance(obj, float):
        el.set("type", "float")
        el.text = repr(obj)
    elif isinstance(obj, str):
        el.set("type", "str")
        el.text = obj
    elif isinstance(obj, list):
        el.set("type", "list")
        for item in obj:
            el.append(_to_element("item", item))
    elif isinstance(obj, dict):
        el.set("type", "dict")
        for key, value in obj.items():
            child = _to_element("entry", value)
            child.set("key", str(key))
            el.append(child)
    else:
        raise TypeError(f"Cannot serialise value of type {type(obj).__name__!r} to XML.")
    return el


def _from_element(el: Element) -> object:
    kind = el.get("type")
    if kind == "null":
        return None
    if kind == "bool":
        return (el.text or "").strip() == "true"
    if kind == "int":
        return int(el.text or "0")
    if kind == "float":
        return float(el.text or "0")
    if kind == "str":
        return el.text or ""
    if kind == "list":
        return [_from_element(child) for child in el]
    if kind == "dict":
        return {child.get("key", ""): _from_element(child) for child in el}
    raise ValueError(f"Unknown XML type tag {kind!r}.")


def to_xml(obj: object, *, root: str = "spec") -> str:
    """Serialise a dataclass spec to type-tagged XML text."""
    return tostring(_to_element(root, to_jsonable(obj)), encoding="unicode")


def from_xml(tp: type, text: str, *, strict: bool = True) -> object:
    """Reconstruct a ``tp`` instance from XML text produced by :func:`to_xml`."""
    return from_jsonable(tp, _from_element(fromstring(text)), strict=strict)
