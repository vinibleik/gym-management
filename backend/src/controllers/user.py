import json
import logging
from http import HTTPStatus
from typing import Any

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src.config import APP_NAME
from src.models.user import User
from src.repositories.user import InMemoryUserRepository
from src.services.user import UserService, UserServiceValidationError

repo = InMemoryUserRepository()
service = UserService(repo)

logger = logging.getLogger(APP_NAME)


class MyJsonResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")


async def create_user(req: Request) -> JSONResponse:
    try:
        body = await req.json()
        new_user = service.create_user(body)
        return_user = User(**new_user.to_dict(exclude=["password_hash"]))
        return MyJsonResponse(
            {"user": return_user.to_dict()}, HTTPStatus.CREATED
        )
    except UserServiceValidationError as e:
        error_body = {
            "errors": [
                {"name": "body", "value": "missing keys", "reason": e.body_err}
            ]
        }
        if e.validation_error:
            error_body["errors"] = e.validation_error.to_dict()["errors"]  # type: ignore
        return MyJsonResponse(error_body, HTTPStatus.BAD_REQUEST)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Error creating user",
        ) from e


async def list_users(_: Request) -> JSONResponse:
    try:
        return MyJsonResponse(
            {
                "users": [
                    u.to_dict(exclude=["password_hash"])
                    for u in service.find_all_users()
                ]
            }
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Error listing user",
        ) from e


async def get_user(req: Request) -> JSONResponse:
    user_id = req.path_params.get("user_id", None)
    if user_id is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="path param user_id is required to get user",
        )
    try:
        user = service.find_user_by_id(int(user_id))
        if user is None:
            return MyJsonResponse(
                {"error": f"User with id {user_id} Not found"},
                HTTPStatus.NOT_FOUND,
            )
        response_user = User(**user.to_dict(exclude=["password_hash"]))
        return MyJsonResponse({"user": response_user.to_dict()})
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Error getting user with id {user_id}",
        ) from e


async def delete_user(req: Request) -> Response:
    user_id = req.path_params.get("user_id", None)
    if user_id is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="path param user_id is required to delete user",
        )
    try:
        user = service.delete_user_by_id(int(user_id))
        if user is None:
            return MyJsonResponse(
                {"error": f"User with id {user_id} Not found"},
                HTTPStatus.NOT_FOUND,
            )
        return Response(status_code=HTTPStatus.NO_CONTENT)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user with id {user_id}",
        ) from e


async def update_user(req: Request) -> JSONResponse:
    user_id = req.path_params.get("user_id", None)
    if user_id is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="path param user_id is required to update user",
        )
    try:
        body = await req.json()
        updated_user = service.update_user(user_id, body)
        if updated_user is None:
            return MyJsonResponse(
                {"error": f"User with id {user_id} Not found"},
                HTTPStatus.NOT_FOUND,
            )
        return_user = User(**updated_user.to_dict(exclude=["password_hash"]))
        return MyJsonResponse({"user": return_user.to_dict()})
    except UserServiceValidationError as e:
        error_body = {
            "errors": [
                {"name": "body", "value": "missing keys", "reason": e.body_err}
            ]
        }
        if e.validation_error:
            error_body["errors"] = e.validation_error.to_dict()["errors"]  # type: ignore
        return MyJsonResponse(error_body, HTTPStatus.BAD_REQUEST)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Error updating user with id {user_id}",
        ) from e
