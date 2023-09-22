from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog, QGraphicsView, QGraphicsScene, QVBoxLayout, QLabel, QTextEdit, QHBoxLayout, QWidget, QLayout, QPushButton
from PyQt5.QtGui import QPixmap
from PIL import Image
import imagehash
import os
import datetime

class ImageTextEditor(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("UI/form.ui", self)  # Remplacez par le chemin de votre fichier UI
        
        self.data_folder = None
        self.current_index = 0
        self.image_files = []
        self.text_files = []

        self.duplicate_window = None

        # Connect the buttons to the appropriate methods
        self.OpenFolder.clicked.connect(self.open_folder)
        self.previous.clicked.connect(self.show_previous)
        self.next.clicked.connect(self.show_next)
        self.saveText.clicked.connect(self.save_text)
        self.DoubleButton.clicked.connect(self.check_for_duplicates)
        
        self.show()

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.data_folder = folder
            self.image_files = sorted([f for f in os.listdir(self.data_folder) if f.endswith('.jpg') or f.endswith('.png')])
            self.text_files = [f.replace('.jpg', '.txt').replace('.png', '.txt') for f in self.image_files]
            
            if not self.image_files:
                QMessageBox.warning(self, "Error", "No image files found in the selected folder.")
                return
            
            self.current_index = 0  # Reset index when a new folder is loaded
            self.load_current_data()

    def load_current_data(self):
        # Load image
        image_path = os.path.join(self.data_folder, self.image_files[self.current_index])        
        pixmap = QPixmap(image_path)
        
        # Set up a QGraphicsScene and add the pixmap to it
        scene = QGraphicsScene()
        scene.addPixmap(pixmap)
        self.imageLabel.setScene(scene)

        # Image dimensions
        image_dimensions = f"{pixmap.width()}x{pixmap.height()}"
        
        # File creation/modification date
        file_timestamp = os.path.getmtime(image_path)
        file_date = datetime.datetime.fromtimestamp(file_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        # File size
        file_size_bytes = os.path.getsize(image_path)
        if file_size_bytes < 1024:
            file_size = f"{file_size_bytes} B"
        elif file_size_bytes < 1024 * 1024:
            file_size = f"{file_size_bytes / 1024:.2f} KB"
        else:
            file_size = f"{file_size_bytes / (1024 * 1024):.2f} MB"
        
        # Set image info
        image_info = f"Dimensions: {image_dimensions}\nDate: {file_date}\nSize: {file_size}"
        self.imageInfoLabel.setPlainText(image_info)
        
        # Load text
        with open(os.path.join(self.data_folder, self.text_files[self.current_index]), 'r') as file:
            text = file.read()
        self.textEdit.setPlainText(text)
        
        # Set image name
        self.imageNameLabel.setText(self.image_files[self.current_index])


    def find_duplicates_in_folder(self, folder_path):
        image_files = [f for f in os.listdir(folder_path) if f.endswith('.jpg') or f.endswith('.png')]
        hash_dict = {}

        # Compute hash for each image
        for image_file in image_files:
            image_path = os.path.join(folder_path, image_file)
            image = Image.open(image_path)
            hash_value = imagehash.average_hash(image)
            if hash_value in hash_dict:
                hash_dict[hash_value].append(image_file)
            else:
                hash_dict[hash_value] = [image_file]

        # Filter out unique images and keep only duplicates
        duplicates_lists = [v for v in hash_dict.values() if len(v) > 1]

        return duplicates_lists

    def check_for_duplicates(self):
        duplicates = self.find_duplicates_in_folder(self.data_folder)
        self.duplicate_window = DuplicateViewer(duplicates,self.data_folder )
        self.duplicate_window.show()
        
        #QMessageBox.information(self, "Duplicate Images", message)

    def show_previous(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_data()

    def show_next(self):
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.load_current_data()

    def save_text(self):
        modified_text = self.textEdit.toPlainText()
        with open(os.path.join(self.data_folder, self.text_files[self.current_index]), 'w') as file:
            file.write(modified_text)
        QMessageBox.information(self, "Success", "Text saved successfully!")

class DuplicateViewer(QtWidgets.QMainWindow):
    def __init__(self, duplicate_groups, data_folder):
        super().__init__()
        uic.loadUi("UI/double.ui", self)  # Remplacez par le chemin de votre fichier UI
        
        self.image_widgets = []  # List to hold dynamically created image widgets
        self.layout = self.horizontalLayout  # Assuming the layout name is horizontalLayout
        self.duplicate_groups = duplicate_groups
        self.folderPath = data_folder
        self.current_group_index = 0

        self.totalDouble.setText(f"01/{len(self.duplicate_groups)}")

        self.QuitButton.clicked.connect(self.close_window)
        self.NextButton.clicked.connect(self.show_next_group)
        self.PreviousButton.clicked.connect(self.show_previous_group)

        self.display_duplicates([self.duplicate_groups[self.current_group_index]])

        self.show()

    def close_window(self):
        self.close()

    def show_next_group(self):
        # Increment the current group index
        self.current_group_index += 1
        
        # If we reach the end of the groups, wrap around to the first group
        if self.current_group_index >= len(self.duplicate_groups):
            self.current_group_index = 0
        
        # Update the totalDouble label
        self.totalDouble.setText(f"{self.current_group_index + 1:02}/{len(self.duplicate_groups)}")

        # Display the next group of duplicates
        self.display_duplicates([self.duplicate_groups[self.current_group_index]])

    def show_previous_group(self):
        # Decrement the current group index
        self.current_group_index -= 1
            
        # If we reach the beginning of the groups, wrap around to the last group
        if self.current_group_index < 0:
            self.current_group_index = len(self.duplicate_groups) - 1
            
        # Update the totalDouble label
        self.totalDouble.setText(f"{self.current_group_index + 1:02}/{len(self.duplicate_groups)}")

        # Display the previous group of duplicates
        self.display_duplicates([self.duplicate_groups[self.current_group_index]])

    def delete_image(self, img_path):
        # Ask for user confirmation before deleting
        reply = QMessageBox.question(self, 'Delete Confirmation', 
                                    f'Are you sure you want to delete {img_path}?', 
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        print(img_path)
        if reply == QMessageBox.Yes:
            # Delete the image
            try:
                os.remove(img_path)
                # Optionally, also delete the associated text file if you want
                txt_path = img_path.replace('.jpg', '.txt')  # adapt if needed
                if os.path.exists(txt_path):
                    os.remove(txt_path)
                # Refresh the displayed duplicates
                self.show_next_group()
            except Exception as e:
                # If there's an error, show a message
                QMessageBox.warning(self, 'Error', f'Error deleting file: {str(e)}')

    def display_duplicates(self, duplicate_groups):
        # Clear previous widgets and layouts
        for item in self.image_widgets:
            if isinstance(item, QWidget):
                self.layout.removeWidget(item)
                item.deleteLater()
            elif isinstance(item, QLayout):
                # Clear all items from the layout
                while item.count():
                    child = item.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
                    self.layout.removeItem(item)
        self.image_widgets.clear()

        # For each group of duplicate images
        for duplicate_group in duplicate_groups:
            # Dynamically create and add widgets for each image in the group
            for image_path in duplicate_group:
                # Create the main vertical layout for this image
                v_layout = QVBoxLayout()
                image_path = os.path.join(self.folderPath, image_path)  
                # Create and set up the QGraphicsView for the image
                pixmap = QPixmap(image_path)
                graphics_view = QGraphicsView(self)
                #graphics_view.setFixedSize(400, 300)  # Set a fixed size for the view
                scene = QGraphicsScene()
                scene.addPixmap(pixmap)
                graphics_view.setScene(scene)
                v_layout.addWidget(graphics_view)

                # Create the QHBoxLayout for the text and label
                h_layout = QHBoxLayout()
                image_name_edit = QTextEdit(self)
                image_name_edit.setMaximumHeight(20)
                image_name_edit.setFixedSize(200, 20)  # Set a fixed size for the text edit

                # Extract just the image filename from the full path
                image_filename = os.path.basename(image_path)
                image_name_edit.setText(image_filename)  # Set the image name in the text edit

                label = QLabel("Image Name", self)
                label.setMaximumHeight(20)
                h_layout.addWidget(label)
                h_layout.addWidget(image_name_edit)

                # Add the horizontal layout to the vertical layout
                v_layout.addLayout(h_layout)

                
                # Add the text content from the associated .txt file
                txt_path = image_path.replace('.jpg', '.txt')  # Assuming .jpg, adapt if needed
                if os.path.exists(txt_path):
                    with open(txt_path, 'r') as f:
                        content = f.read()
                    text_edit = QTextEdit(self)
                    text_edit.setPlainText(content)
                    v_layout.addWidget(text_edit)
                
                # Add a delete button for each image
                delete_button = QPushButton("Delete", self)
                print(image_path)
                delete_button.clicked.connect(lambda img_path=image_path: self.delete_image(image_path))
                v_layout.addWidget(delete_button)

                # Add the main vertical layout to the main horizontal layout
                self.layout.addLayout(v_layout)
                self.image_widgets.append(v_layout)

app = QApplication([])
window = ImageTextEditor()
app.exec_()
