from pygdrive3 import service
import streamlit as st
import json
import os


class GDrive(object):
    SECRETS_JSON = "client_secret.json"
    BASE_FOLDER = "__AI_IMAGE_DATA"
    ROOT_FOLDER = "My Drive"  # Usually root folder in google drive is "My Drive"
    FOLDER_MIME_TYPE = 'application/vnd.google-apps.folder'

    def __init__(self):
        self.create_client_secrets()
        self.service = service.DriveService(self.SECRETS_JSON)
        self.service.auth()
        self.base_id, self.root_id = self.init_info()

    def create_client_secrets(self):
        if not os.path.exists(self.SECRETS_JSON):
            client_secrets_dict = json.loads(st.secrets['driveKey'])
            with open(self.SECRETS_JSON, 'w+') as outfile:
                json.dump(client_secrets_dict, outfile)

    @st.cache
    def init_info(self):
        """
        Get the root directory object
        Note: 
        The directory {{BASE_FOLDER}} should have been already created manually for this to work
        There should not be more than one directory with name {{BASE_FOLDER}} in any location of gdrive
        """
        folder_id = self.service.list_folders_by_name(self.BASE_FOLDER)
        base_id = folder_id[0]['id']
        root_id = self.service.get_file_info(base_id)['parents'][0]
        return base_id, root_id

    def folder_exists(self, folder_name, parent_id):
        """
        Check if the folder exists in the google drive path
        :param folder_name: (string) Name of the folder to create in GA
        :param parent_id: (string) id string of the folder
        :return file_id (string) if folder exists else return False
        """
        files = self.service.list_folders_by_name(folder_name)
        for file in files:
            file_id = file['id']
            file_obj = self.service.get_file_info(file_id)
            file_type = file_obj['mimeType']
            file_name = file_obj['name']
            if file_type == self.FOLDER_MIME_TYPE:
                parents = file_obj.get('parents')
                if parents:
                    file_parent_id = parents[0]
                    if file_parent_id == parent_id and file_name == folder_name:
                        return file_id
                    else:
                        return False

    @st.cache
    def create_folder(self, folder_name, parent_id):
        """
        Create a folder in google drive
        :param folder_name: (string) Name of the folder to create in GA
        :return (string) folder id        
        """
        folder_id = self.folder_exists(folder_name, parent_id)
        if not folder_id:
            # print("Creating folder with name - {}".format(folder_name))
            folder_id = self.service.create_folder(folder_name, parent_id)
            return folder_id
        else:
            return folder_id

    @st.cache
    def get_folder_id(self, folder_name, parent_id):
        """
        Get the folder id provided the name of the folder and parent id
        :param folder_name: (string) Name of the folder to get the id
        :param parent_id: (string) id of the parent folder to search for
        :return folder_id (string) if the folder exists else None
        """
        files = self.service.list_files_from_folder_id(parent_id)
        for file in files:
            file_type = file.get('type')
            file_name = file.get('name')
            file_id = file.get('id')
            if file_type == self.FOLDER_MIME_TYPE and file_name == folder_name:
                return file_id
            else:
                return None

    def upload_image(self, image_name, local_image_path, grocery_type, label):
        """
        Upload the provided image to the specific label (good / average / bad)
        Basic Image Upload Structure:
        [ROOT -> BASE -> GROCERY_TYPE -> LABEL -> IMAGES]
        Sample:
        ['My Drive' -> '__AI_IMAGE_DATA' -> 'apple' -> 'good' -> 'good_apple.jpg']
        :param image_name: (string) Name of the image
        :param local_image_path: (string) Path of the image from local file system
        :param grocery_type: (string) apple / banana / potato / ....
        :param label: (string) good / bad / average
        :return file_id from google drive
        """
        # Create grocery_type folder if not exists
        grocery_type_folder_id = self.get_folder_id(grocery_type, self.base_id)
        if grocery_type_folder_id is None:
            grocery_type_folder_id = self.create_folder(
                grocery_type, self.base_id)
        # Create label folder if not exists
        label_folder_id = self.get_folder_id(label, grocery_type_folder_id)
        if label_folder_id is None:
            label_folder_id = self.create_folder(label, grocery_type_folder_id)
        # Upload the file to google drive
        file_id = self.service.upload_file(
            image_name,
            local_image_path,
            label_folder_id
        )
        return file_id


if __name__ == '__main__':
    pass
