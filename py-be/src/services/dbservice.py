from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import urllib.parse
import os
from bson.objectid import ObjectId # Important for querying by ID

load_dotenv()

class DBService:
    def __init__(self, db_name="psdb"):
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_cluster_host = os.getenv("DB_CLUSTER_HOST")
        db_app_name = os.getenv("DB_APP_NAME") # Get the app name from .env

        if not all([db_user, db_password, db_cluster_host, db_app_name]):
            raise ValueError("One or more DB environment variables (DB_USER, DB_PASSWORD, DB_CLUSTER_HOST, DB_APP_NAME) not set.")

        encoded_password = urllib.parse.quote_plus(db_password)
        # Construct URI without appName parameter in the string
        self.uri = f"mongodb+srv://{db_user}:{encoded_password}@{db_cluster_host}/psdb?retryWrites=true&w=majority"
        
        self.client = None
        self.db_name = db_name
        self._connect(app_name=db_app_name) # Pass app_name to the connect method

    def _connect(self, app_name: str = None):
        """Establishes the MongoDB connection."""
        try:
            # Pass server_api and appName as keyword arguments to MongoClient
            client_options = {"server_api": ServerApi('1')}
            if app_name:
                client_options["appName"] = app_name

            self.client = MongoClient(self.uri, **client_options)
            self.client.admin.command('ping')
            print("Ping")
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            self.client = None # Ensure client is None on failure
            raise # Re-raise to indicate connection failure

    def get_db(self):
        """Returns the current database instance."""
        if not self.client:
            self._connect() # Attempt to reconnect if client is somehow lost
        return self.client[self.db_name]

    def close_connection(self):
        """Closes the MongoDB connection."""
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")
            self.client = None

    # --- Ingredient-specific DB Operations ---
    def get_ingredients_collection(self):
        return self.get_db()["psb_ingredients"]

    def get_all_ingredients(self):
        return list(self.get_ingredients_collection().find({}))

    def get_ingredient_by_id(self, ingredient_id: str):
        try:
            return self.get_ingredients_collection().find_one({"_id": ObjectId(ingredient_id)})
        except Exception: # Handle invalid ObjectId string
            return None

    def add_ingredient(self, ingredient_data: dict):
        # Apply default values if not provided
        if "is_available" not in ingredient_data:
            ingredient_data["is_available"] = True
        result = self.get_ingredients_collection().insert_one(ingredient_data)
        return str(result.inserted_id)

    def update_ingredient(self, ingredient_id: str, update_data: dict):
        result = self.get_ingredients_collection().update_one(
            {"_id": ObjectId(ingredient_id)},
            {"$set": update_data}
        )
        return result.modified_count

    def delete_ingredient(self, ingredient_id: str):
        result = self.get_ingredients_collection().delete_one({"_id": ObjectId(ingredient_id)})
        return result.deleted_count

    # --- Premade Sandwich-specific DB Operations ---
    def get_premade_sandwiches_collection(self):
        return self.get_db()["psb_premade"]

    def get_all_premade_sandwiches(self):
        return list(self.get_premade_sandwiches_collection().find({}))

    def get_premade_sandwich_by_id(self, sandwich_id: str):
        try:
            return self.get_premade_sandwiches_collection().find_one({"_id": ObjectId(sandwich_id)})
        except Exception: # Handle invalid ObjectId string
            return None

    def add_premade_sandwich(self, sandwich_data: dict):
        if "is_available" not in sandwich_data:
            sandwich_data["is_available"] = True
        # Convert ingredient_id strings to ObjectIds if present in nested list
        if 'ingredients' in sandwich_data and isinstance(sandwich_data['ingredients'], list):
            for item in sandwich_data['ingredients']:
                if 'ingredient_id' in item and isinstance(item['ingredient_id'], str):
                    try:
                        item['ingredient_id'] = ObjectId(item['ingredient_id'])
                    except Exception:
                        # Handle error for invalid ingredient_id in the input data
                        pass
        result = self.get_premade_sandwiches_collection().insert_one(sandwich_data)
        return str(result.inserted_id)

    def update_premade_sandwich(self, sandwich_id: str, update_data: dict):
        # Similarly, convert ingredient_id strings to ObjectIds in update_data if needed
        if 'ingredients' in update_data and isinstance(update_data['ingredients'], list):
            for item in update_data['ingredients']:
                if 'ingredient_id' in item and isinstance(item['ingredient_id'], str):
                    try:
                        item['ingredient_id'] = ObjectId(item['ingredient_id'])
                    except Exception:
                        pass
        result = self.get_premade_sandwiches_collection().update_one(
            {"_id": ObjectId(sandwich_id)},
            {"$set": update_data}
        )
        return result.modified_count

    def delete_premade_sandwich(self, sandwich_id: str):
        result = self.get_premade_sandwiches_collection().delete_one({"_id": ObjectId(sandwich_id)})
        return result.deleted_count

if __name__ == "__main__":
    db_service = DBService()
    
    try:
        # Add an ingredient with the updated structure
        new_ingredient = {
            "name": "Sourdough Bread",
            "type": "bread",
            "description": "Crusty, tangy sourdough bread, a perfect base for any sandwich.", # Corrected typo and added description
            "tags": ["artisan", "specialty"], # Added tags

        }

       # ingredient_id = db_service.add_ingredient(new_ingredient)
       # print(f"Added ingredient: {new_ingredient['name']} with ID {ingredient_id}")

        # Get all ingredients
        all_ingredients = db_service.get_all_ingredients()
        print(f"\nAll ingredients: {len(all_ingredients)} found")
        all_sw = db_service.get_all_premade_sandwiches()
        print(f"\nAll ingredients: {len(all_sw)} found")
        # for ing in all_ingredients:
        #     print(ing)
        
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        db_service.close_connection()