from typing import Union
from fastapi import FastAPI

app = FastAPI()
items = []

@app.get("/")
def read_root():
    print("current items :", items)
    return {"hello": "world", "items": items}

# GET
@app.get("/items")
def get_items():
    print("GET/items ->", items)
    return items

# POST
@app.post("/items")
def create_item(name: str):
    item = {"id": len(items) + 1, "name": name}
    items.append(item)
    print("item  created:", item)
    print("All items :", items)
    return item


# PATCH
@app.patch("/items/{item_id}")
def update_item(item_id: int, name: Union[str, None] = None):
    for item in items:
        if item["id"] == item_id:
            if name:
                item["name"] = name

            print("item updated:", item)
            return item
        print("updated failled:Item not found")

# DELETE
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    for i, item in enumerate(items):
        if item["id"] == item_id:
            removed = items.pop(i)
            print("Item removed:", removed)
            print("Removing items: ", items)

            return removed
print("Delete failled :Item not found")