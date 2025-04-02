import json
from collections.abc import Iterable
from dataclasses import fields
from typing import Any, TypedDict

_POST_INIT_NAME = "__post_init__"


class FieldError(TypedDict):
    field: str
    value: Any
    msg: str


class ValidationError(Exception): ...


class FieldsValidationError(ValidationError):
    errors: tuple[FieldError, ...]

    def __init__(self, errors: Iterable[FieldError], *args: object) -> None:
        self.errors = tuple(errors)
        super().__init__(self._repr_msg(), *args)

    def _repr_msg(self) -> str:
        return json.dumps(self.errors)


def validate_dataclass(cls):
    _post_init_func = getattr(cls, _POST_INIT_NAME, None)

    def dataclass_validation(self, *args, **kwargs):
        # Call the __post_init__ for the class before validation
        if _post_init_func:
            try:
                _post_init_func(self, *args, **kwargs)
            except Exception as e:
                raise ValidationError(
                    f"Error with post initializing class {cls.__name__}"
                ) from e

        errors: list[FieldError] = []
        for field in fields(self):
            name = field.name
            value = getattr(self, name)
            try:
                validator = getattr(self, f"__validate_{name}__", None)

                if validator is not None and not validator(value):
                    errors.append(
                        {
                            "field": name,
                            "value": value,
                            "msg": f"Invalid value {value} for field {name}",
                        }
                    )
            except Exception as e:
                errors.append(
                    {
                        "field": name,
                        "value": value,
                        "msg": str(e),
                    }
                )
        if errors:
            raise FieldsValidationError(errors)

    setattr(cls, _POST_INIT_NAME, dataclass_validation)

    return cls
