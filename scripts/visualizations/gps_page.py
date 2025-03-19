import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import random
import folium
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
    QFrame, QSizePolicy, QStackedWidget, QGroupBox, QLineEdit,QSpacerItem, QComboBox
)
from PyQt5.QtCore import QSize, Qt, QUrl, QTimer, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView  # 用于显示地图

from utils.log import LoggerManager

logger_manager = LoggerManager()
logger = logger_manager.get_logger()

def generate_map_with_mock_location(map_type):
    ''' Generates a folium map with a mock GPS position marked with a red dot and different map types '''
    latitude, longitude = get_mock_gps_location()
    map_path = "gps_map.html"
    
    m = folium.Map(location=[latitude, longitude], zoom_start=12, tiles=map_type)
    folium.Marker([latitude, longitude], popup="Current Location", icon=folium.Icon(color='red')).add_to(m)
    
    m.save(map_path)
    return map_path

def get_mock_gps_location():
    ''' Simulate receiving GPS location '''
    latitude = 26.460554 # Simulated latitude
    longitude = -81.435710

    return latitude, longitude

def update_gps_info(self):
    ''' Simulate GPS signal updates '''
    signal_strength = random.choice(["Weak", "Moderate", "Strong"])
    satellite_count = random.randint(4, 12)

    self.signal_strength_label.setText(f"Signal Strength: {signal_strength}")
    self.satellite_count_label.setText(f"Satellites Detected: {satellite_count}")

def update_map_type(self):
    ''' Update map type based on user selection '''
    self.current_map_type = self.map_type_selector.currentText()
    map_path = generate_map_with_mock_location(self.current_map_type)
    self.map_view.setUrl(QUrl.fromLocalFile(os.path.abspath(map_path)))


class GpsPage(QWidget):

    backClicked = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.create_gps_setting_page()
        
    def create_gps_setting_page(self):
        '''GPS settings page
         with embedded folium map and sidebar, allowing map type selection'''
        page = QWidget()
        gps_setting_layout = QHBoxLayout(self)

        # Generate map with simulated GPS position
        self.current_map_type = "OpenStreetMap"  # Default map type
        map_path = generate_map_with_mock_location(self.current_map_type)
        
        # Map View (occupying left half)
        self.map_view = QWebEngineView()
        self.map_view.setUrl(QUrl.fromLocalFile(os.path.abspath(map_path)))
        self.map_view.setMinimumSize(600, 600)
        gps_setting_layout.addWidget(self.map_view, 1)  # Left side

        # Sidebar for GPS signal status (Right side)
        sidebarLayout = QVBoxLayout()
        sidebarLayout.setAlignment(Qt.AlignTop)

        gps_status_label = QLabel("GPS Signal Status")
        gps_status_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")
        sidebarLayout.addWidget(gps_status_label)

        self.signal_strength_label = QLabel("Signal Strength: ")
        self.satellite_count_label = QLabel("Satellites Detected: ")
        sidebarLayout.addWidget(self.signal_strength_label)
        sidebarLayout.addWidget(self.satellite_count_label)
        sidebarLayout.addStretch()

        # Map type selection dropdown
        map_type_label = QLabel("Select Map Type:")
        self.map_type_selector = QComboBox()
        self.map_type_selector.addItems(["OpenStreetMap", "Esri.WorldImagery"])  # Two map options
        self.map_type_selector.currentTextChanged.connect(lambda: update_map_type(self))
        sidebarLayout.addWidget(map_type_label)
        sidebarLayout.addWidget(self.map_type_selector)

        # Back button
        backButton = QPushButton("Back")
        backButton.setStyleSheet("background-color: red; color: white; font-size: 16px; padding: 5px;")
        backButton.clicked.connect(self.backClicked.emit)
        sidebarLayout.addWidget(backButton)
        
        gps_setting_layout.addLayout(sidebarLayout, 1)  # Right side
        
        # page.setLayout(gps_setting_layout)
        
        # Start updating GPS info
        update_gps_info(self)
