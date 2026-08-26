from pydantic import BaseModel


class CurrentUser(BaseModel):
    sub: str
    username: str | None = None
    email: str | None = None
    name: str | None = None
    roles: list[str] = []
