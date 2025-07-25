from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox
import json, os
from core.client import SUPPORTED_MODELS, SETTINGS_PATH


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Settings")
        self.setMinimumWidth(300)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("API Key:"))
        self.api_input = QLineEdit()
        layout.addWidget(self.api_input)

        layout.addWidget(QLabel("Model:"))
        self.model_choice = QComboBox()
        for label, model in SUPPORTED_MODELS.items():
            self.model_choice.addItem(label, model)
        layout.addWidget(self.model_choice)

        layout.addWidget(QLabel("Max Tool Iterations:"))
        self.iteration_input = QSpinBox()
        self.iteration_input.setMinimum(1)
        self.iteration_input.setMaximum(20)
        layout.addWidget(self.iteration_input)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        self.load_settings()

    def load_settings(self):
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r") as f:
                config = json.load(f)
                self.api_input.setText(config.get("api_key", ""))
                model_value = config.get("model", list(SUPPORTED_MODELS.values())[0])
                index = self.model_choice.findData(model_value)
                self.model_choice.setCurrentIndex(index if index >= 0 else 0)
                self.iteration_input.setValue(config.get("max_iterations", 6))

    def save_settings(self):
        config = {
            "api_key": self.api_input.text().strip(),
            "model": self.model_choice.currentData(),
            "max_iterations": self.iteration_input.value()
        }
        os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
        with open(SETTINGS_PATH, "w") as f:
            json.dump(config, f, indent=2)
        return config
