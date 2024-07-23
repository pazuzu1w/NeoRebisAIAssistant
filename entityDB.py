import json
import os


class EntityDB:
    def __init__(self, db_folder="entity_db"):
        self.db_folder = db_folder
        if not os.path.exists(self.db_folder):
            os.makedirs(self.db_folder)

    def create_entity(self, entity_name, fields=None, media=None):
        """
        Creates a new entity JSON file with optional media links.

        Args:
            entity_name: The name of the entity (used as the filename).
            fields: A dictionary of key-value pairs representing entity fields.
            media: A dictionary of key-value pairs for media links (local paths or URLs).
        """
        entity_data = {}
        if fields:
            entity_data.update(fields)
        if media:
            entity_data["media"] = media

        entity_file = os.path.join(self.db_folder, f"{entity_name}.json")

        with open(entity_file, 'w') as f:
            json.dump(entity_data, f, indent=4)
        print(f"Entity '{entity_name}' created in the database.")

    def read_entity(self, entity_name):
        """
        Reads an entity JSON file and returns the data.

        Args:
            entity_name: The name of the entity to read.

        Returns:
            A dictionary of entity data or None if the entity is not found.
        """
        entity_file = os.path.join(self.db_folder, f"{entity_name}.json")
        if os.path.exists(entity_file):
            with open(entity_file, 'r') as f:
                return json.load(f)
        else:
            print(f"Entity '{entity_name}' not found in the database.")
            return None

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

    def delete_entity(self, entity_name):
        """
        Deletes an entity JSON file.

        Args:
            entity_name: The name of the entity to delete.
        """
        entity_file = os.path.join(self.db_folder, f"{entity_name}.json")
        if os.path.exists(entity_file):
            os.remove(entity_file)
            print(f"Entity '{entity_name}' deleted from the database.")
        else:
            print(f"Entity '{entity_name}' not found in the database. Deletion failed.")

    def list_entities(self):
        """
        Lists all entities in the database.

        Returns:
            A list of entity names.
        """
        entities = [file.replace(".json", "") for file in os.listdir(self.db_folder) if file.endswith(".json")]
        if entities:
            return entities
        else:
            print("No entities found in the database.")
            return []

    def search_entities(self, query):
        """
        Searches for entities in the database based on a query string.

        Args:
            query: The search query string.

        Returns:++
            A list of entity names that match the query.
        """
        results = [file.replace(".json", "") for file in os.listdir(self.db_folder) if
                   file.endswith(".json") and query.lower() in file.replace(".json", "").lower()]
        if results:
            return results
        else:
            print(f"No entities found matching the query: '{query}'.")
            return []
    @staticmethod
    def create_entity_in_db(entity_name: str, fields: dict = {"exampleField": "value"},
                            media: dict = {"exampleMediaField": "mediaValue"}) -> dict:
        """

        Args:
            entity_name: The name of the entity.
            fields: A dictionary of fields for the entity. Defaults to an empty dictionary if None.
            media: Optional dictionary of media links. Defaults to an empty dictionary if None.

        Returns:
            A dictionary containing the result of the operation.
        """
        if fields is None:
            fields = {}
        if media is None:
            media = {}

        db = EntityDB()
        db.create_entity(entity_name, fields=fields, media=media)
        return {"status": "success", "entity_name": entity_name}

    def summon_entity(entity_name: str):
        """
        Creates a new entity JSON file with the given name in the entity database.

        Args:
            entity_name: The name of the entity. This will be used as the filename.
        """
        db = EntityDB()
        entity_data = {}  # We'll start with an empty entity for now.
        db.create_entity(entity_name, fields=entity_data)
        print(f"Entity '{entity_name}' summoned into the database!")

    def add_field(entity_name: str, field_name: str, field_value: str):
        """
        Adds a field to an existing entity in the database.

        Args:
            entity_name: The name of the entity to update.
            field_name: The name of the field to add.
            field_value: The value for the new field.
        """
        db = EntityDB()
        entity_data = db.read_entity(entity_name)
        if entity_data is not None:
            entity_data[field_name] = field_value
            db.update_entity(entity_name, **entity_data)
            print(f"Field '{field_name}' added to entity '{entity_name}'.")
        else:
            print(f"Entity '{entity_name}' not found. Field '{field_name}' not added.")