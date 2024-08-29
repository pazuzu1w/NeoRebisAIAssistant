import json
import json
import os
from dotenv import load_dotenv
from tavily import TavilyClient
import logging
from typing import Dict, Any, List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()
tavily = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))


class EntityDB:
    def __init__(self, db_folder: str = "entity_db"):
        self.db_folder = db_folder
        if not os.path.exists(self.db_folder):
            os.makedirs(self.db_folder)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_file = os.path.join(self.db_folder, "entity_vectors.json")
        self.load_vectors()

    def load_vectors(self):
        if os.path.exists(self.vector_file):
            with open(self.vector_file, 'r') as f:
                self.entity_vectors = json.load(f)
        else:
            self.entity_vectors = {}

    def save_vectors(self):
        with open(self.vector_file, 'w') as f:
            json.dump(self.entity_vectors, f)

    def vectorize_entity(self, entity_name: str, entity_data: Dict[str, Any]):
        entity_text = json.dumps(entity_data)
        vector = self.model.encode([entity_text])[0].tolist()
        self.entity_vectors[entity_name] = vector
        self.save_vectors()

    @staticmethod
    def create_entity(entity_name: str, field: Optional[Dict[str, Any]] = None,
                      value: Optional[Dict[str, Any]] = None) -> None:
        db_folder = "entity_db"
        entity_data = {}
        if field:
            entity_data.update(field)
        if value:
            entity_data.update(value)

        entity_file = os.path.join(db_folder, f"{entity_name}.json")

        with open(entity_file, 'w') as f:
            json.dump(entity_data, f, indent=4)

        print(f"Entity '{entity_name}' created in the database.")

        # Vectorize the entity
        db = EntityDB()
        db.vectorize_entity(entity_name, entity_data)
        print(f"Entity '{entity_name}' vectorized.")

    @staticmethod
    def search_entities(query: str) -> List[str]:
        db_folder = "entity_db"
        print(f"Searching for entities matching the query: '{query}'")
        results = [file.replace(".json", "") for file in os.listdir(db_folder) if
                   file.endswith(".json") and query in file.replace(".json", "")]
        if results:
            print(results)
            EntityDB.read_entity(query)
            return results
        else:
            print(f"No entities found matching the query: '{query}'.")
            return []

    @staticmethod
    def read_entity(entity_name: str) -> Dict[str, Any]:
        db_folder = "entity_db"
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

    @staticmethod
    def update_entity(entity_name: str, **fields):
        db_folder = "entity_db"
        entity_file = os.path.join(db_folder, f"{entity_name}.json")
        if os.path.exists(entity_file):
            with open(entity_file, 'r') as f:
                entity_data = json.load(f)
            entity_data.update(fields)
            with open(entity_file, 'w') as f:
                json.dump(entity_data, f, indent=4)

            print(f"Entity '{entity_name}' updated in the database.")

            # Re-vectorize the entity
            db = EntityDB()
            db.vectorize_entity(entity_name, entity_data)
            print(f"Entity '{entity_name}' re-vectorized.")
        else:
            print(f"Entity '{entity_name}' not found in the database. Update failed.")

    @staticmethod
    def delete_entity(entity_name: str) -> None:
        db_folder = "entity_db"
        confirm_deletion = input(
            f"Are you sure you want to delete entity '{entity_name}' from the database? (yes/no): ")
        if confirm_deletion.lower() != "yes":
            print("Deletion cancelled.")
            return

        entity_file = os.path.join(db_folder, f"{entity_name}.json")
        if os.path.exists(entity_file):
            os.remove(entity_file)
            print(f"Entity '{entity_name}' deleted from the database.")

            # Remove from vector store
            db = EntityDB()
            if entity_name in db.entity_vectors:
                del db.entity_vectors[entity_name]
                db.save_vectors()
                print(f"Entity '{entity_name}' removed from vector store.")
        else:
            print(f"Entity '{entity_name}' not found in the database. Deletion failed.")

    @staticmethod
    def list_entities() -> List[str]:
        db_folder = "entity_db"
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
        print("New summoning occurring")
        if entity_name in EntityDB.search_entities(entity_name):
            print(
                f"Entity '{entity_name}' already exists in the database. Do you want to continue summoning? This will overwrite the entire JSON (yes/no)")
            confirm = input("Type 'yes' to confirm overwrite or 'no': ")
            if confirm.lower() == "yes":
                print("Summoning confirmed.")
                EntityDB.create_entity(entity_name, {field: field_value})
                print(f"Entity '{entity_name}' summoned into the database!")
                return
            else:
                print("Summoning canceled.")
                return
        else:
            EntityDB.create_entity(entity_name, {field: field_value})
            print(f"Entity '{entity_name}' summoned into the database!")

    @staticmethod
    def add_field(entity_name: str, field_name: str, field_value: str) -> Dict[str, Any]:
        print("add_field invoked")
        db_folder = "entity_db"
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

        # Re-vectorize the entity
        db = EntityDB()
        db.vectorize_entity(entity_name, entity_data)
        print(f"Entity '{entity_name}' re-vectorized.")

        return entity_data

    @staticmethod
    def tavily_search(query: str) -> Dict[str, Any]:
        try:
            response = tavily.qna_search(query=query, search_depth="advanced")
            print(response)
            return response
        except Exception as e:
            return {"error": f"Error performing search: {str(e)}"}

    def semantic_search(self, query: str = "tony", top_k: int = 5) -> List[Dict[str, Any]]:
        query_vector = self.model.encode([query])[0]

        similarities = []
        for entity_name, entity_vector in self.entity_vectors.items():
            similarity = cosine_similarity([query_vector], [entity_vector])[0][0]
            similarities.append((entity_name, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)
        top_results = similarities[:top_k]

        results = []
        for entity_name, similarity in top_results:
            entity_file = os.path.join(self.db_folder, f"{entity_name}.json")
            with open(entity_file, 'r') as f:
                entity_data = json.load(f)
            results.append({
                "entity_name": entity_name,
                "similarity": similarity,
                "data": entity_data
            })

        formatted_results = "\n\n".join(
            [f"entity_name: {r['entity_name']}\nsimilarity: {r['similarity']:.2f}\ndata: {r['data']}" for r in results]
        )
        print(formatted_results)
        return formatted_results

    @staticmethod
    def local_search(query: str):
        """
        Perform a local search on logs and vector database.

        Args:
        query (str): The search query.

        Returns:
        Dict[str, any]: A dictionary containing search results and context.
        """
        try:
            print(f"Performing local search for {query} ...")
            db = EntityDB()
            vector_results = db.semantic_search(query, top_k=5)

            # Prepare results
            results = {
                "query": query,
                "vector_results": [
                    {"similarity": r['similarity'], "entity_name": r['entity_name'], "data": r['data']}
                    for r in vector_results
                ]
            }

            # Prepare context
            context = f"You searched for '{query}'. Here are the relevant results:\n"

            context += "Vector DB results:\n" + "\n".join(
                [f"{r['similarity']:.2f} - {r['entity_name']}: {r['data']}" for r in results["vector_results"]])
            context += "\nBased on these search results, please provide a summary or answer any questions the user might have."

            results["context"] = context
            print("Search completed")
            return results

        except Exception as e:
            logging.error(f"Error performing search: {e}")
            return {"error": str(e)}