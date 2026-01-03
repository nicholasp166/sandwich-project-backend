from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path # Import Path for better path handling
from src.services.dbservice import DBService
import json

router = APIRouter(
    prefix="/pubsub",
    tags=["pubsub"],
)


@router.get("/subs")
async def showSubs():
    db_service = DBService()
    try:
        subs = db_service.get_all_premade_sandwiches()
        processed_subs = []
        for sub in subs:
            i = 0
            sub_items = {}
            sub_items["id"] = str(i)
            sub_items["name"] = sub.get("name", "")
            sub_items["description"] = sub.get("description", "")  
            sub_items["ingredients"] = sub.get("ingredients", [])
            sub_items["tags"] = sub.get("tags", [])
            processed_subs.append(sub_items)
            i += 1
        return JSONResponse(content=processed_subs)
          
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sandwiches: {e}")
    finally:
        db_service.close_connection()

@router.post("/addsub")
async def addSub(sandwich: dict):
    db_service = DBService()
    try:
        sandwich_id = db_service.add_premade_sandwich(sandwich)
        return JSONResponse(content={"message": "Sandwich added successfully", "sandwich_id": sandwich_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add sandwich: {e}")
    finally:
        db_service.close_connection()

@router.get("/ingredients")
async def get_ingredients():
    db_service = DBService()
    try:
        ingredients = db_service.get_all_ingredients()
        processed_ingredients = []
        for i,ing in enumerate(ingredients):
            item = {
                "id": str(i),
                "name": ing.get("name", ""),
                "type": ing.get("type", ""),
                "description": ing.get("description", ""),
                "tags": ing.get("tags", []),
            }
            processed_ingredients.append(item)
        return JSONResponse(content=processed_ingredients)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve ingredients: {e}")
    finally:
        db_service.close_connection()

@router.post("/addingredient")
async def addingredient(ingredient: dict):
    db_service = DBService()
    try:
        ingredient_id = db_service.add_ingredient(ingredient)
        return JSONResponse(content={"message": "Ingredient added successfully", "ingredient_id": ingredient_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add ingredient: {e}")
    finally:
        db_service.close_connection()