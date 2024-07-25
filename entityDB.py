import json
import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from tavily import TavilyClient
import logging
from enhance_vectordb import EnhancedVectorDatabase
from typing import Dict, Any, Union

load_dotenv()
tavily = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))

class EntityDB:
    def __init__(self, db_folder: str = "entity_db"):
        self.db_folder = db_folder
        if not os.path.exists(self.db_folder):
            os.makedirs(self.db_folder)
        self.vectordb = EnhancedVectorDatabase()

    @staticmethod
    def create_entity(entity_name: str, field: Optional[Dict[str, Any]] = None, value: Optional[Dict[str, Any]] = None) -> None:
        db_folder = "entity_db"  # You might want to make this configurable
        entity_data = {}
        if field:
            entity_data.update(field)
        if value:
            entity_data.update(value)

        entity_file = os.path.join(db_folder, f"{entity_name}.json")

        with open(entity_file, 'w') as f:
            json.dump(entity_data, f, indent=4)
        print(f"Entity '{entity_name}' created in the database.")

    @staticmethod
    def search_entities(query: str) -> List[str]:
        db = EntityDB()
        print(f"Searching for entities matching the query: '{query}'")
        db_folder = "entity_db"  # You might want to make this configurable
        results = [file.replace(".json", "") for file in os.listdir(db_folder) if
                   file.endswith(".json") and query in file.replace(".json", "")]
        if results:
            print(results)
            db.read_entity(query)
            return results
        else:
            print(f"No entities found matching the query: '{query}'.")
            return []

    @staticmethod
    def read_entity(entity_name: str) -> Dict[str, Any]:
        db_folder = "entity_db"  # Ensure this matches your actual db_folder path
        entity_file = os.path.join(db_folder, f"{entity_name}.json")

        try:
            if os.path.exists(entity_file):
                with open(entity_file, 'r', encoding='utf-8') as f:
                    entity_data = json.load(f)
                print(f"Successfully read entity: {entity_name}")
                print(entity_data)
                return {"status": "success", "data": entity_data}
            else:
                print(f"Entity '{entity_name}' not found in the database.")
                return {"status": "error", "message": f"Entity '{entity_name}' not found"}
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for entity '{entity_name}': {str(e)}")
            return {"status": "error", "message": f"Invalid JSON in entity file: {str(e)}"}
        except Exception as e:
            print(f"Unexpected error reading entity '{entity_name}': {str(e)}")
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}

    def update_entity(self, entity_name, **fields):
        """
        Updates an entity JSON file with new fields or updated values.

        Args:
            entity_name: The name of the entity to update.
            **fields: Keyword arguments representing the entity's fields and values to update.
        """
        entity_file = os.path.join(self.db_folder, f"{entity_name}.json")
        if os.path.exists(entity_file):
            with open(entity_file, 'r') as f:
                entity_data = json.load(f)
            entity_data.update(fields)
            with open(entity_file, 'w') as f:
                json.dump(entity_data, f, indent=4)
            print(f"Entity '{entity_name}' updated in the database.")
        else:
            print(f"Entity '{entity_name}' not found in the database. Update failed.")

    @staticmethod
    def delete_entity(entity_name: str) -> None:
        # Confirm deletion
        confirm_deletion = input(f"Are you sure you want to delete entity '{entity_name}' from the database? (yes/no): ")
        if confirm_deletion.lower() != "yes":
            print("Deletion cancelled.")
            return
        else:
            print("Deleting entity...")
        db_folder = "entity_db"  # You might want to make this configurable
        entity_file = os.path.join(db_folder, f"{entity_name}.json")
        if os.path.exists(entity_file):
            os.remove(entity_file)
            print(f"Entity '{entity_name}' deleted from the database.")
        else:
            print(f"Entity '{entity_name}' not found in the database. Deletion failed.")

    @staticmethod
    def list_entities() -> List[str]:
        db_folder = "entity_db"  # You might want to make this configurable
        print("Listing entities in the database:")
        entities = [file.replace(".json", "") for file in os.listdir(db_folder) if file.endswith(".json")]
        if entities:
            print(entities)
            return entities
        else:
            print("No entities found in the database.")
            return []


    @staticmethod
    def summon_entity(entity_name: str, field: str, field_value: str) -> None:
        print("new summoning occurring")
        db = EntityDB()
        db.search_entities(entity_name)
        if entity_name in db.search_entities(entity_name):
            print(f"Entity '{entity_name}' already exists in the database. Do you want to continue summoning? this will over write the entire JSON (yes/no)")
            confirm = input("type 'yes' to confirm overwrite or 'no': ")
            if confirm.lower() == "yes":
                print("summoning confirmed.")
                db.create_entity(entity_name, {field: field_value})
                print(f"Entity '{entity_name}' summoned into the database!")
                return
            else:
                print("Summoning canceled.")
                return
        else:
            db.create_entity(entity_name, {field: field_value})
            print(f"Entity '{entity_name}' summoned into the database!")

    @staticmethod
    def add_field(entity_name: str, field_name: str, field_value: str) -> Dict[str, Any]:
        print("add_field invoked")
        db_folder = "entity_db"  # Make sure this matches your actual db_folder path
        entity_file = os.path.join(db_folder, f"{entity_name}.json")

        if os.path.exists(entity_file):
            with open(entity_file, 'r') as f:
                entity_data = json.load(f)
        else:
            entity_data = {}

        entity_data[field_name] = field_value

        with open(entity_file, 'w') as f:
            json.dump(entity_data, f, indent=4)

        print(f"Field '{field_name}' added to entity '{entity_name}'.")
        return entity_data
    @staticmethod
    def tavily_search(query: str) -> Dict[str, Any]:
        try:
            response = tavily.qna_search(query=query, search_depth="advanced")
            print(response)
            return response
        except Exception as e:
            return {"error": f"Error performing search: {str(e)}"}

    def local_search(query: str):
        vectordb = EnhancedVectorDatabase()
        """
        Perform a local search on logs and vector database.

        Args:
        query (str): The search query.

        Returns:
        Dict[str, any]: A dictionary containing search results and context.
        """
        try:
            print(f"Performing local search for {query} ...")
            vector_results = vectordb.semantic_search(query, k=5)

            # Prepare results
            results = {
                "query": query,

                "vector_results": [
                    {"similarity": r['similarity'], "content": r['content']}
                    for r in vector_results
                ]
            }

            # Prepare context
            context = f"You searched for '{query}'. Here are the relevant results:\n"

            context += "Vector DB results:\n" + "\n".join(
                [f"{r['similarity']:.2f} - {r['content']}" for r in results["vector_results"]])
            context += "\nBased on these search results, please provide a summary or answer any questions the user might have."

            results["context"] = context
            print("search completed")
            return results

        except Exception as e:
            logging.error(f"Error performing search: {e}")
            return {"error": str(e)}


