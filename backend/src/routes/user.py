from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.routing import Route

from src.controllers import user_controller


class HomeUser(HTTPEndpoint):
    async def get(self, req: Request):
        return await user_controller.list_users(req)

    async def post(self, req: Request):
        return await user_controller.create_user(req)


class User(HTTPEndpoint):
    async def get(self, req: Request):
        return await user_controller.get_user(req)

    async def delete(self, req: Request):
        return await user_controller.delete_user(req)

    async def put(self, req: Request):
        return await user_controller.update_user(req)


routes: tuple[Route, ...] = (
    Route("/", HomeUser),
    Route("/{user_id:int}", User),
)
