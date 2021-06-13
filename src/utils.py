import os
import numpy as np
from PIL import Image
import streamlit as st
import time

# Project Imports
from gdrive_api import GDrive


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


def upload_image(image, grocery_type, label):
    """
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
    return image_id
