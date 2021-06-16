from pymongo import MongoClient
from gridfs import GridFS
import streamlit as st


class MongoDB(object):
    mongo_user = st.secrets['mongo_user']
    mongo_password = st.secrets['mongo_password']
    connection_string = "mongodb+srv://{}:{}@groceryqualityclassifie.hjj29.mongodb.net/grocery_images".format(
        mongo_user, mongo_password)
    db_name = 'grocery_images'
    collection_name = 'images'

    def __init__(self) -> None:
        super().__init__()
        self.client = MongoClient(self.connection_string)
        self.db = self.client[self.db_name]
        self.fs = GridFS(self.db)
        # A collection is analogous to a table of an RDBMS
        self.collection = self.db[self.collection_name]

    def create_document(self, document):
        """
        :param document: (dict). Sample below:
        {
            'image_path': "path of the image_file",
            'item_type': 'apple'
            'label': "good / bad / average"
        }
        :return ('bson.objectid.ObjectId') id of the document
        """
        image_path = document.get('image_path')
        image_name = str(image_path.split("/")[-1])
        with open(image_path, 'rb') as img_file:
            img = self.fs.put(
                img_file.read(), content_type='image/jpeg', filename=image_name)
        document_to_insert = {
            'image_name': image_name,
            'image_store_id': img,
            'uploaded_time': img.generation_time,
            'item_type': document.get('item_type'),
            'label': document.get('label')
        }
        document_id = self.collection.insert_one(
            document_to_insert).inserted_id
        return document_id

    def update_document(self, document_id, update_fields):
        """
        :param document_id: ('bson.objectid.ObjectId') id of the document
        :param update_fields: (dict) key-value pair of fields to update
        update_fields = {
            'image_name': 'new_name.jpg',
            'label': 'good'
        }
        :return (bool) update_result
        """
        query = {'_id': document_id}
        update = {"$set": update_fields}
        update_result = self.collection.update_one(query, update)
        return update_result.acknowledged

    def read_image(self, query):
        """
        WARNING:
        Work in Progress. Implementation is incomplete!
        """
        img = self.fs.find_one(query)
        with open('5.jpg', 'wb') as outfile:
            outfile.write(img.read())
        return True


if __name__ == '__main__':
    pass
