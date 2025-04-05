import json
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, TypedDict

_INIT_NAME = "__init__"


class FieldErrorDict(TypedDict):
    name: str
    value: Any
    reason: str | None


@dataclass
class FieldError(Exception):
    name: str
    value: Any
    reason: str | None = None

    def to_dict(self) -> FieldErrorDict:
        return {"name": self.name, "value": self.value, "reason": self.reason}

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def __str__(self) -> str:
        _repr = f"{self.__class__.__name__}: Invalid value <{self.value}> for field <{self.name}>"
        if self.reason:
            _repr += "\n  " + f"Reason: {self.reason}"
        return _repr

    def __repr__(self) -> str:
        if self.reason:
            return f'{self.__class__.__name__}({self.name}, {self.value}, "{self.reason}")'
        return f"{self.__class__.__name__}({self.name}, {self.value})"


class ValidationErrorDict(TypedDict):
    cls_name: str
    errors: list[FieldErrorDict]


@dataclass
class ValidationError(Exception):
    cls_name: str
    errors: list[FieldError]

    def to_dict(self) -> ValidationErrorDict:
        return {
            "cls_name": self.cls_name,
            "errors": [e.to_dict() for e in self.errors],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def __str__(self) -> str:
        errors_str = "\n".join(map(str, self.errors))
        return f"""\
{self.__class__.__name__}: Error while validating {self.cls_name}. The following errors were found:
{errors_str}"""

    def __repr__(self) -> str:
        errors_str = ",\n    ".join(repr(e) for e in self.errors)
        _repr = f"""\
{self.__class__.__name__}(
  "{self.cls_name}",
  [
    {errors_str}
  ]
)"""
        return _repr


def is_dataclass_class(cls) -> bool:
    return is_dataclass(cls) and isinstance(cls, type)


def _validator_name(field_name: str) -> str:
    return f"__validate_{field_name}__"


def validate_fields(self):
    errors: list[FieldError] = []
    for field in fields(self):
        name = field.name
        value = getattr(self, name)
        validator = getattr(self, _validator_name(name), None)

        try:
            if validator and not validator(name=name, value=value):
                raise FieldError(name=name, value=value)
        except FieldError as f:
            errors.append(f)
    if errors:
        raise ValidationError(cls_name=self.__class__.__name__, errors=errors)


def validate_dataclass(cls):
    if not is_dataclass_class(cls):
        raise ValueError(f"class {cls.__name__} must be a dataclass")

    cls__init__ = getattr(cls, _INIT_NAME, None)

    def validate__init__(self, *args, **kwargs):
        if cls__init__:
            cls__init__(self, *args, **kwargs)
        validate_fields(self)

    setattr(cls, _INIT_NAME, validate__init__)

    return cls
