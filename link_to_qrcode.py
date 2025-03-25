import sys
import os
from urllib.parse import urlparse
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QLineEdit, QPushButton, QLabel, QFileDialog,
    QMessageBox
)
from PyQt6.QtGui import QPixmap, QClipboard, QIcon
from PyQt6.QtCore import Qt, QSize
import qrcode
from PIL.ImageQt import ImageQt


class QRCodeGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern QR Code Generator")
        self.setWindowIcon(QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogInfoView)))
        
        # Main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # URL input section
        self.url_label = QLabel("Enter URL:")
        self.url_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout.addWidget(self.url_label)
        
        self.input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        self.url_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #4CAF50;
            }
        """)
        self.input_layout.addWidget(self.url_input)
        
        self.paste_button = QPushButton()
        self.paste_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        self.paste_button.setToolTip("Paste from clipboard")
        self.paste_button.setFixedSize(40, 40)
        self.paste_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.paste_button.clicked.connect(self.paste_from_clipboard)
        self.input_layout.addWidget(self.paste_button)
        
        self.layout.addLayout(self.input_layout)
        
        # Generate button
        self.generate_button = QPushButton("Generate QR Code")
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.generate_button.clicked.connect(self.generate_qr_code)
        self.layout.addWidget(self.generate_button)
        
        # QR Code display
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setStyleSheet("background-color: white; padding: 10px;")
        self.layout.addWidget(self.qr_label)
        
        # Save button
        self.save_button = QPushButton("Save QR Code")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_qr_code)
        self.layout.addWidget(self.save_button)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setStyleSheet("font-size: 12px; color: #666;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.status_label)
        
        # Enable/disable generate button based on input
        self.url_input.textChanged.connect(self.validate_input)
        
        # Set minimum window size
        self.setMinimumSize(400, 500)
        
        # Current QR code
        self.current_qr = None
    
    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        
        if text:
            self.url_input.setText(text)
            self.validate_input(text)
            
            # Change button to clear temporarily
            self.paste_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogResetButton))
            self.paste_button.setToolTip("Clear field")
            self.paste_button.clicked.disconnect()
            self.paste_button.clicked.connect(self.clear_field)
    
    def clear_field(self):
        self.url_input.clear()
        self.paste_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        self.paste_button.setToolTip("Paste from clipboard")
        self.paste_button.clicked.disconnect()
        self.paste_button.clicked.connect(self.paste_from_clipboard)
    
    def validate_input(self, text):
        if not text:
            self.generate_button.setEnabled(False)
            self.status_label.setText("Enter a URL to generate QR code")
            return False
        
        try:
            result = urlparse(text)
            if not all([result.scheme, result.netloc]):
                raise ValueError
            self.generate_button.setEnabled(True)
            self.status_label.setText("URL looks valid")
            return True
        except ValueError:
            self.generate_button.setEnabled(False)
            self.status_label.setText("Invalid URL format (must include http:// or https://)")
            return False
    
    def generate_qr_code(self):
        url = self.url_input.text().strip()
        
        if not self.validate_input(url):
            return
        
        try:
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            self.current_qr = img
            
            # Convert to QPixmap and display
            qim = ImageQt(img)
            pixmap = QPixmap.fromImage(qim)
            scaled_pixmap = pixmap.scaled(
                300, 300, 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.qr_label.setPixmap(scaled_pixmap)
            self.save_button.setEnabled(True)
            self.status_label.setText("QR code generated successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate QR code: {str(e)}")
            self.status_label.setText("Error generating QR code")
    
    def save_qr_code(self):
        if not self.current_qr:
            return
        
        # Get downloads folder path
        downloads_path = os.path.expanduser("~/Downloads")
        if not os.path.exists(downloads_path):
            downloads_path = os.path.expanduser("~")  # Fallback to home directory
        
        # Suggest filename based on URL
        url = self.url_input.text().strip()
        domain = urlparse(url).netloc.replace("www.", "")
        filename = f"qr_code_{domain}.png"
        default_path = os.path.join(downloads_path, filename)
        
        # Get save path from user
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save QR Code",
            default_path,
            "PNG Images (*.png);;All Files (*)"
        )
        
        if file_path:
            try:
                if not file_path.lower().endswith('.png'):
                    file_path += '.png'
                self.current_qr.save(file_path)
                self.status_label.setText(f"QR code saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save QR code: {str(e)}")
                self.status_label.setText("Error saving QR code")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Modern style
    
    # Set some modern styling
    palette = app.palette()
    palette.setColor(palette.ColorRole.Window, QColor(240, 240, 240))
    palette.setColor(palette.ColorRole.WindowText, QColor(0, 0, 0))
    palette.setColor(palette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(palette.ColorRole.AlternateBase, QColor(240, 240, 240))
    palette.setColor(palette.ColorRole.ToolTipBase, QColor(255, 255, 220))
    palette.setColor(palette.ColorRole.ToolTipText, QColor(0, 0, 0))
    palette.setColor(palette.ColorRole.Text, QColor(0, 0, 0))
    palette.setColor(palette.ColorRole.Button, QColor(240, 240, 240))
    palette.setColor(palette.ColorRole.ButtonText, QColor(0, 0, 0))
    palette.setColor(palette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(palette.ColorRole.Highlight, QColor(76, 175, 80))
    palette.setColor(palette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    window = QRCodeGenerator()
    window.show()
    sys.exit(app.exec())