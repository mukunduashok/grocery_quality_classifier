# Imports
import streamlit as st
import pandas as pd


# Project Imports
from utils import get_groceries, load_image, save_to_db, update_label
from load_pb_model import predict, load_models, LABELS
from session_state import get_state

# Set Page Title
st.set_page_config(
    page_title="Image Quality Classifier"
)

state = get_state(
    image_uploaded=False,
    classify_requested=False,
    saved_to_db=False,
    update_classify_requested=False,
    updated_to_db=False
)

GROCERIES = get_groceries()
# Load and cache the model
models = load_models(GROCERIES)


# Set Page Heading
left_header, right_header = st.beta_columns([3, 1])
left_header.title("Image Quality Classifier")
right_header.image("./assets/logo.jpeg")
# Drodown to select the grocery type
grocery_type = st.selectbox(
    "Select the Grocery type",
    GROCERIES,
)
model = models.get(grocery_type)
inp_shape = model.input_shape[1:3]
selection = "Grocery type selected: {}".format(grocery_type)
st.write(selection)

uploaded_file = st.file_uploader(
    label="Choose an image", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    state.image_uploaded = True    
    img = load_image(uploaded_file, inp_shape)
    st.image(img)
    st.write("Image Uploaded successfully")
    state.classify_requested = True

# Classify the image on button click / once uploaded
if state.classify_requested:
    prediction = predict(model, uploaded_file, inp_shape)
    # Create the prediction as a data frame and display as table
    prediction = pd.DataFrame(prediction)
    st.dataframe(prediction.style.highlight_max(axis=1, color='SeaGreen'))
    # Find the max probability from prediction and upload to google drive
    label = prediction.idxmax(axis=1)[0]
    doc_id = save_to_db(img, grocery_type, label)
    if doc_id:
        state.saved_to_db = True

if state.saved_to_db:
    st.markdown('#')
    labels = ['Select'] + list(LABELS)
    classification_preference = st.selectbox(
        'Not Happy ? Update product quality', labels)
    if classification_preference != 'Select':
        col3, col4 = st.beta_columns([2, 1])
        submit_user_preference = col3.button('Submit')
        if submit_user_preference:
            update_label(doc_id, classification_preference)
            state.updated_to_db = True
            col4.write('Updated!')
