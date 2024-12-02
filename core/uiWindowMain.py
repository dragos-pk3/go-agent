from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QDateEdit, QComboBox, QTextEdit, QPushButton, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy
from PyQt5.QtCore import QDate
import sqlite3
import sys
import os

# # Add the project root directory to Python path
# project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(project_root)
import jsonSRW
from processDataClass import ProcessData
from htmlReplace import HTMLReplacer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.html_replacer = HTMLReplacer()

        self.setWindowTitle("GoCamper Oferte")

        # Create main layout
        layout = QVBoxLayout()
        horizontal_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        # Create a widget to hold the start date layout
        start_date_widget = QWidget()
        startDateLayout = QHBoxLayout(start_date_widget)
        self.start_date_label = QLabel(self)
        self.start_date_label.setText("Start Date: ")
        # Start date picker
        self.start_date_picker = QDateEdit(self)
        self.start_date_picker.setCalendarPopup(True)
        self.start_date_picker.setDate(QDate.currentDate())
        self.start_date_picker.setDisplayFormat("dd.MM")
        startDateLayout.addWidget(self.start_date_label)
        startDateLayout.addWidget(self.start_date_picker)
        startDateLayout.addItem(horizontal_spacer)
        layout.addWidget(start_date_widget)

        end_date_widget = QWidget() 
        endDateLayout = QHBoxLayout(end_date_widget)
        self.end_date_label = QLabel(self)
        self.end_date_label.setText("End Date: ")
        # End date picker
        self.end_date_picker = QDateEdit(self)
        self.end_date_picker.setCalendarPopup(True)
        self.end_date_picker.setDate(QDate.currentDate().addDays(3))
        self.end_date_picker.setDisplayFormat("dd.MM")
        endDateLayout.addWidget(self.end_date_label)
        endDateLayout.addWidget(self.end_date_picker)
        endDateLayout.addItem(horizontal_spacer)
        layout.addWidget(end_date_widget)

        # ComboBox for Autorulota picker
        self.autovan_combo_box = QComboBox(self)
        layout.addWidget(self.autovan_combo_box)
        self.populate_autovan_combo_box()

        # Rich TextEdit for the generated output
        self.output_text_edit = QTextEdit(self)
        self.output_text_edit.setAcceptRichText(True)
        layout.addWidget(self.output_text_edit)

        # Button for generating output
        self.generate_button = QPushButton("Generate Output", self)
        self.generate_button.clicked.connect(self.generate_output)
        layout.addWidget(self.generate_button)

        # Set main layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def populate_autovan_combo_box(self):
        data = jsonSRW.read_json("__userfiles__\\user_config.json")
        conn = sqlite3.connect(data["DB_PATH"])
        cursor = conn.cursor()
        
        # Modified query to get distinct combinations of type and city
        cursor.execute("""
            SELECT MIN(vehicle_id) as vehicle_id, autovan_type, location_city 
            FROM VehiclesSummary 
            GROUP BY autovan_type, location_city
        """)
        
        rows = cursor.fetchall()
        for row in rows:
            self.autovan_combo_box.addItem(f"{row[1]} - {row[2]}", row[0])
        conn.close()

    def generate_output(self):
        start_date = self.start_date_picker.date().toString("dd.MM")
        end_date = self.end_date_picker.date().toString("dd.MM")
        selected_autovan = self.autovan_combo_box.currentText().split(" - ")[0]
        vehicle_id = self.autovan_combo_box.currentData()
        # Process the data with the GUI values instead of using input()
        processed_data = ProcessData()
        processed_data.process(vehicle_id, start_date, end_date)

        if not processed_data:
            self.output_text_edit.setText("No data processed. Please check your inputs.")
            return

        # Use HTMLReplacer to process the template
        html_output = self.html_replacer.process_template(processed_data.output)
        self.output_text_edit.setHtml(html_output)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
