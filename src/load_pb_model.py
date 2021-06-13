import streamlit as st
import numpy as np
import os
import tensorflow as tf
from PIL import Image, ImageOps
import time

IMG_INP_SHAPE = (224, 224)  # Use this for .pb model
CHANNELS = 3
LABELS = ('average', 'bad', 'good')


@st.cache(allow_output_mutation=True)
def load_models(groceries):
    models = {}
    for grocery_type in groceries:
        model_path = os.path.join('models', grocery_type)
        model = tf.keras.models.load_model(model_path)
        models.update({grocery_type: model})
    return models


class ImageClassifier(object):
    """
    Classifier to read the .pb model and predict the classes
    """

    def __init__(self, model, image_size):
        """
        :param model: Model loaded using tf.keras
        :param image_size: input size of the image (tuple); Sample - (224, 224)
        """
        self.model = model
        self.image_size = image_size
        # Create the array of the right shape to feed into the keras model
        # The 'length' or number of images you can put into the array is
        # determined by the first position in the shape tuple, in this case 1.
        self.data = np.ndarray(
            shape=(1, self.image_size[0], self.image_size[1], 3), dtype=np.float32)

    def preprocess_input(self, img):
        image = Image.open(img)
        # resize the image to a 224x224 with the same strategy as in TM2
        # resizing the image to be at least 224x224 and then cropping from the center
        image = ImageOps.fit(image, self.image_size, Image.ANTIALIAS)
        # turn the image into a numpy array
        image_array = np.array(image)
        # Normalize the image
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
        # Load the image into the array
        self.data[0] = normalized_image_array

    def run(self, img):
        """
        :param image: a (1, image_size, image_size, 3) np.array
        Returns list of [Label, Probability], of type List<str, float>
        """
        self.preprocess_input(img)
        prediction = self.model.predict(self.data)
        return prediction


def predict(model, image):
    """
    :param model: Model loaded using tf.keras
    :param image_size: the uploaded file as such
    """
    classifier = ImageClassifier(model, image_size=IMG_INP_SHAPE)
    start_time = time.time()
    prediction = classifier.run(image)[0]
    end_time = time.time()
    print("Time taken to predict using pb model is {} seconds".format(
        end_time - start_time))
    # Convert to percentage from probability (p * 100)
    prediction = prediction * 100
    # Reshape the numpy array from array([3.00000e-04, 3.57900e-03, 9.96421e-01])
    # to array([[3.00000e-04], [3.57900e-03], [9.96421e-01]])
    prediction = prediction.reshape((-1, 1)).tolist()
    # Create a dictionary of labels and predictions
    prediction = dict(zip(LABELS, prediction))
    return prediction
