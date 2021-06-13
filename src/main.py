# Imports
import streamlit as st
import pandas as pd
import os


# Project Imports
from utils import get_groceries, load_image, upload_image
from load_pb_model import IMG_INP_SHAPE, predict, load_models

# Set Page Title
st.set_page_config(
    page_title="Image Quality Classifier"
)


GROCERIES = get_groceries()
# Load and cache the model
models = load_models(GROCERIES)


# Set Page Heading
st.title("Image Quality Classifier")
# Drodown to select the grocery type
grocery_type = st.selectbox(
    "Select the Grocery type",
    GROCERIES,
)

selection = "Grocery type selected: {}".format(grocery_type)
st.write(selection)

uploaded_file = st.file_uploader(
    label="Choose an image", type=['jpg', 'jpeg', 'png'])
if uploaded_file is not None:
    img = load_image(uploaded_file, IMG_INP_SHAPE)
    st.image(img)
    st.write("Image Uploaded successfully")
    # Create Classify Image button on file upload
    col1, col2 = st.beta_columns([2, 3])
    classify_image = col1.button('Classify Image')
    # Classify the image on button click
    if classify_image:
        prediction = predict(models.get(grocery_type), uploaded_file)
        # Create the prediction as a data frame and display as table
        prediction = pd.DataFrame(prediction)
        col2.dataframe(prediction.style.highlight_max(
            axis=1, color='SeaGreen'))
        # Find the max probability from prediction and upload to google drive
        label = prediction.idxmax(axis=1)[0]
        image_id = upload_image(img, grocery_type, label)
