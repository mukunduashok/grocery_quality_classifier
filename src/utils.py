import os
from PIL import Image
import streamlit as st
import time

# Project Imports
# from gdrive_api import GDrive
from mongodb_api import MongoDB


@st.cache(allow_output_mutation=True)
def get_db_obj():
    db = MongoDB()
    return db


@st.cache
def get_groceries():
    """
    Utility function to get the list of grocery items the suite can classify
    Detects from the available models in the 'models' directory
    """
    groceries = [item for item in os.listdir(
        'models') if os.path.isdir(os.path.join('models', item))]
    return groceries


def load_image(img, inp_shape):
    """
    Load the image from file uploader and resize the image
    :param img: st.file_uploader() object
    :param inp_shape: (tuple) - img_height, img_width. Sample: (224, 224)
    """
    with Image.open(img) as _img:
        image = _img.resize(inp_shape)
    return image


@st.cache
def save_to_local(img_obj, grocery_type):
    """
    Function to save the image to local
    :param image: Pillow.Image.open() object
    :param grocery_type: apple / mango / ...
    :return name of the image saved in local
    """
    image_name = "{}_{}.jpg".format(grocery_type, time.time())
    img_obj.save(image_name)
    return image_name


@st.cache
def save_to_db(image, grocery_type, label):
    """
    Saves the image object to local. Uploads the image to mongo db. 
    Creates a mapping record in collection - images. Deletes the image from local.
    :param image: Pillow.Image.open() object
    :param grocery_type: apple / mango / ...
    :param label: good / bad / average
    :return id of the uploaded image from google drive
    """
    saved_file = save_to_local(image, grocery_type)
    db = get_db_obj()
    # now = time.time()
    # image_name = "{}_{}".format(grocery_type, now)
    document = {'image_path': saved_file,
                'item_type': grocery_type, 'label': label}
    doc_id = db.create_document(document)
    os.remove(saved_file)
    return doc_id


@st.cache(max_entries=2)
def update_label(doc_id, new_label):
    """
    Provided the document ID and new label name,
    the function will update the label name in the document
    :param doc_id: ('bson.objectid.ObjectId') id of the document
    ;param label: (str) "good / bad / average"
    :return (bool) True if success. False if failed
    """
    db = get_db_obj()
    return db.update_document(doc_id, {'label': new_label})


def upload_image(image, grocery_type, label):
    """
    Warning: The Google Drive upload functionality is not used any more. 
    Instead please use save_to_db function to store images in mongodb

    Saves the image object to local. Uploads the image to google drive. Deletes the image from local

    :param image: Pillow.Image.open() object
    :param grocery_type: apple / mango / ...
    :param label: good / bad / average
    :return id of the uploaded image from google drive
     """
    saved_file = save_to_local(image, grocery_type)
    drive = GDrive()
    now = time.time()
    image_name = "{}_{}_{}".format(grocery_type, label, now)
    image_id = drive.upload_image(image_name, saved_file, grocery_type, label)
    os.remove(saved_file)
    return image_id, image_name
