from slack_bolt import App

from .ask_command import ask_callback
from .sqlite_upload_command import sqlite_upload_callback


def register(app: App):
    app.command("/ask-bolty")(ask_callback)
    app.command("/upload-sqlite")(sqlite_upload_callback)
