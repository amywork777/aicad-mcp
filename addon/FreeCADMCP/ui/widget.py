from PySide2 import QtWidgets, QtCore, QtGui
import os, json, base64
import tempfile
from typing import List, Any

from ui.settings_dialog import SettingsDialog, SETTINGS_PATH
from core.client import FreeCADAI, load_settings
import json

import re
import os
import tempfile
import base64
from uuid import uuid4

class AsyncWorker(QtCore.QThread):
    stepReady = QtCore.Signal(dict)

    def __init__(self, coroutine, parent=None):
        super().__init__(parent)
        self.coro = coroutine

    def run(self):
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def wrapper():
            async for step in self.coro:
                self.stepReady.emit(step)

        loop.run_until_complete(wrapper())
        loop.close()

class ChatWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ai = FreeCADAI()

        self.file_paths: List[str] = []
        self.workers = []
        self._init_ui()

    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        self.chat = QtWidgets.QTextBrowser()
        self.chat.setOpenExternalLinks(True)
        self.chat.setStyleSheet("""
            QTextBrowser {
                font-family: 'Segoe UI', sans-serif;
                font-size: 10pt;
            }
            .tool-call {
                color: #bbb;
                background-color: #222;
                padding: 6px 10px;
                margin: 6px 0;
                border-left: 4px solid #4e9;
                font-size: 9.5pt;
                font-family: 'Segoe UI', sans-serif;
            }
            .code {
                font-family: Consolas, monospace;
                background-color: #111;
                color: #8f8;
                padding: 8px;
                border-radius: 5px;
                font-size: 9pt;
            }
        """)

        self.file_preview = QtWidgets.QLabel("")
        self.file_preview.setAlignment(QtCore.Qt.AlignCenter)
        self.file_preview.setFixedHeight(100)
        self.file_preview.setStyleSheet("background-color: #222; color: white; border: 1px solid #444;")
        self.file_preview.setVisible(False)

        file_buttons = QtWidgets.QHBoxLayout()
        self.add_file_btn = QtWidgets.QPushButton("📎 Add File")
        self.clear_files_btn = QtWidgets.QPushButton("❌ Clear Files")
        file_buttons.addWidget(self.add_file_btn)
        file_buttons.addWidget(self.clear_files_btn)

        input_layout = QtWidgets.QHBoxLayout()
        self.input_field = QtWidgets.QLineEdit()
        self.send_btn = QtWidgets.QPushButton("💬 Send")
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)

        layout.addWidget(self.chat)
        layout.addWidget(self.file_preview)
        layout.addLayout(file_buttons)
        layout.addLayout(input_layout)

        self.add_file_btn.clicked.connect(self.add_file)
        self.clear_files_btn.clicked.connect(self.clear_files)
        self.send_btn.clicked.connect(self.handle_send)
        self.input_field.returnPressed.connect(self.handle_send)

        self.settings_btn = QtWidgets.QPushButton("⚙️ Settings")
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.settings_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.settings_btn.clicked.connect(self.open_settings)

    def open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec_():
            dlg.save_settings()

            # start new
            self.chat.clear()
            self._append_message("Claude", "Starting a new session with updated model...")

            # refresh
            self.ai = FreeCADAI()

    def add_file(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        dlg.setNameFilter("All Files (*);;Images (*.png *.jpg *.jpeg *.gif);;CAD Files (*.FCStd);;Videos (*.mp4 *.avi)")
        if dlg.exec_():
            self.file_paths += dlg.selectedFiles()
            self.update_file_preview()

    def clear_files(self):
        self.file_paths.clear()
        self.update_file_preview()

    def update_file_preview(self):
        if not self.file_paths:
            self.file_preview.setVisible(False)
            return
        self.file_preview.setVisible(True)
        if len(self.file_paths) == 1:
            name = os.path.basename(self.file_paths[0])
            self.file_preview.setText(f"📎 {name}")
        else:
            self.file_preview.setText(f"{len(self.file_paths)} files attached")

    def handle_send(self):
        query = self.input_field.text().strip()
        if not query and not self.file_paths:
            return

        self._append_message("You", query)
        self._render_attached_files()
        self.input_field.clear()

        # Create and run the worker
        coro = self.ai.run(query, self.file_paths.copy())
        worker = AsyncWorker(coro)
        worker.stepReady.connect(self._stream_steps)  
        worker.finished.connect(lambda: self.workers.remove(worker))
        self.workers.append(worker)
        worker.start()

        self.clear_files()


    def _stream_steps(self, step: dict) -> None:
        raw = step["content"]

        formatted = self._format_markdown(raw)
        self._append_message("Chat", formatted)

    # def _render_inline_images(self, raw: str) -> tuple[str, List[str]]:
    #     pattern = re.compile(r'!\[[^\]]*\]\((data:image/(png|jpe?g|gif);base64,([A-Za-z0-9+/=]+))\)')
    #     thumbs: List[str] = []

    #     def replace_with_nothing(match):
    #         fmt = match.group(2)
    #         b64 = match.group(3)

    #         # Pad base64 if necessary
    #         missing_padding = len(b64) % 4
    #         if missing_padding:
    #             b64 += '=' * (4 - missing_padding)

    #         try:
    #             img_data = base64.b64decode(b64)
    #             pix = QtGui.QPixmap()
    #             if not pix.loadFromData(img_data):
    #                 return ''  # skip invalid image

    #             thumb_pix = pix.scaled(200, 150, QtCore.Qt.KeepAspectRatio)
    #             fname = f'thumb_{uuid4().hex}.{fmt}'
    #             path = os.path.join(tempfile.gettempdir(), fname)
    #             thumb_pix.save(path)

    #             thumbs.append(f'<img src="{path}" width="200" />')
    #         except Exception as e:
    #             print(f"Image decoding failed: {e}")
    #             return ''

    #         return ''

    #     cleaned_raw = pattern.sub(replace_with_nothing, raw)
    #     return cleaned_raw, thumbs

    def _format_markdown(self, text: str) -> str:
        text = text.strip()

        # Headings: simple <h1>, <h2>, <h3>
        text = re.sub(r"(?m)^### (.+)$", r"<h3>\1</h3>", text)
        text = re.sub(r"(?m)^## (.+)$", r"<h2>\1</h2>", text)
        text = re.sub(r"(?m)^# (.+)$", r"<h1>\1</h1>", text)

        # Bold text: **bold**
        text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)

        # Inline code formatting: `code`
        text = re.sub(
            r"`([^`\n]+)`",
            r"<code style='padding:2px 4px; border-radius:3px;'>\1</code>",
            text
        )

        # Match numbered issues like 1. **Wall Thickness Issues:**
        text = re.sub(r"(?m)^(\d+)\. \*\*(.+?)\*\*:\s*$", r"<h3>\1. \2</h3>", text)

        # List of object/face/location/thickness inside issues
        # def format_issue_block(match):
        #     lines = match.group(1).strip().split("\n")
        #     html = "<ul style='margin-left:20px;'>"
        #     for line in lines:
        #         if line.strip():
        #             html += f"<li>{line.strip()}</li>"
        #     html += "</ul>"
        #     return html

        # text = re.sub(r"(?ms)^- (.+?)(?=\n\n|$)", format_issue_block, text)

        # General cleaning
        text = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', text)  # remove images
        text = re.sub(r"\n{2,}", "<br><br>", text)  # normalize line breaks

        return text


    def _render_attached_files(self):
        for path in self.file_paths:
            fname = os.path.basename(path)
            ext = os.path.splitext(fname)[1].lower()
            if ext in [".png", ".jpg", ".jpeg", ".gif"]:
                pix = QtGui.QPixmap(path).scaled(200, 150, QtCore.Qt.KeepAspectRatio)
                thumb_path = os.path.join(tempfile.gettempdir(), f"chat_img_{fname}")
                pix.save(thumb_path)
                self.chat.append(f'<img src="{thumb_path}" width="200" />')
            else:
                self.chat.append(f'<div style="color:#ccc;">📎 {fname}</div>')


    def _append_message(self, sender: str, message: str):
        self.chat.append(f"<div style='margin-top:10px;'><b>{sender}:</b><br>{message}</div>")

