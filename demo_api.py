from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Demo API for TestForge")

USERS: list[dict[str, Any]] = []
ORDERS: list[dict[str, Any]] = []


class UserPayload(BaseModel):
    name: str
    email: str
    age: int


class OrderPayload(BaseModel):
    user_id: int
    total: float
    currency: str = "USD"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/login")
def login() -> dict[str, str]:
    return {"token": "demo-token", "expires_in": 3600}


@app.get("/users")
def list_users(authorization: str | None = Header(default=None, alias="Authorization")) -> list[dict[str, Any]]:
    if authorization != "Bearer demo-token":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return USERS


@app.post("/users")
def create_user(payload: UserPayload, authorization: str | None = Header(default=None, alias="Authorization")) -> dict[str, Any]:
    if authorization != "Bearer demo-token":
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not payload.name or len(payload.name) < 2:
        raise HTTPException(status_code=400, detail="Invalid name")
    if "@" not in payload.email:
        raise HTTPException(status_code=400, detail="Invalid email")
    user = {"id": len(USERS) + 1, "name": payload.name, "email": payload.email, "age": payload.age}
    USERS.append(user)
    return {"id": user["id"], "name": payload.name, "email": payload.email, "age": payload.age}


@app.get("/users/{user_id}")
def get_user(user_id: int, authorization: str | None = Header(default=None, alias="Authorization")) -> dict[str, Any]:
    if authorization != "Bearer demo-token":
        raise HTTPException(status_code=401, detail="Unauthorized")
    for user in USERS:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")


@app.put("/users/{user_id}")
def update_user(user_id: int, payload: UserPayload, authorization: str | None = Header(default=None, alias="Authorization")) -> dict[str, Any]:
    if authorization != "Bearer demo-token":
        raise HTTPException(status_code=401, detail="Unauthorized")
    for idx, user in enumerate(USERS):
        if user["id"] == user_id:
            user.update({"name": payload.name, "email": payload.email, "age": payload.age})
            USERS[idx] = user
            return user
    raise HTTPException(status_code=404, detail="User not found")


@app.delete("/users/{user_id}")
def delete_user(user_id: int, authorization: str | None = Header(default=None, alias="Authorization")) -> dict[str, str]:
    if authorization != "Bearer demo-token":
        raise HTTPException(status_code=401, detail="Unauthorized")
    for idx, user in enumerate(USERS):
        if user["id"] == user_id:
            del USERS[idx]
            return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="User not found")


@app.post("/orders")
def create_order(payload: OrderPayload, authorization: str | None = Header(default=None, alias="Authorization")) -> dict[str, Any]:
    if authorization != "Bearer demo-token":
        raise HTTPException(status_code=401, detail="Unauthorized")
    order = {"id": len(ORDERS) + 1, "user_id": payload.user_id, "total": payload.total, "currency": payload.currency}
    ORDERS.append(order)
    return order


@app.get("/orders/{order_id}")
def get_order(order_id: int, authorization: str | None = Header(default=None, alias="Authorization")) -> dict[str, Any]:
    if authorization != "Bearer demo-token":
        raise HTTPException(status_code=401, detail="Unauthorized")
    for order in ORDERS:
        if order["id"] == order_id:
            return order
    raise HTTPException(status_code=404, detail="Order not found")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("demo_api:app", host="0.0.0.0", port=8002, reload=False)
