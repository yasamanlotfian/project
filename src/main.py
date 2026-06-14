from typing import Union, Optional
from fastapi import FastAPI, HTTPException

app = FastAPI()


items = []


def get_all_items():
    return items


def create_item_service(name: str):
    item = {
        "id": len(items) + 1,
        "name": name
    }
    items.append(item)
    return item


def find_item(item_id: int):
    for item in items:
        if item["id"] == item_id:
            return item
    return None


def update_item_service(item_id: int, name: Optional[str]):
    item = find_item(item_id)

    if item is None:
        return None

    if name is not None:
        item["name"] = name

    return item


def delete_item_service(item_id: int):
    for i, item in enumerate(items):
        if item["id"] == item_id:
            return items.pop(i)

    return None


@app.get("/")
def read_root():
    return {
        "hello": "world",
        "items": get_all_items()
    }


@app.get("/items")
def get_items():
    return get_all_items()


@app.post("/items")
def create_item(name: str):
    return create_item_service(name)


@app.patch("/items/{item_id}")
def update_item(item_id: int, name: Optional[str] = None):
    result = update_item_service(item_id, name)

    if result is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return result


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    result = delete_item_service(item_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return result
