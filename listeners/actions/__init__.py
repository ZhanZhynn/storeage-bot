from slack_bolt import App
from .set_user_selection import set_user_selection
from .sqlite_upload_quick_reply import sqlite_upload_quick_reply_callback
from ..listener_utils.sqlite_upload_flow import SQLITE_UPLOAD_QUICK_REPLY_ACTION_IDS


def register(app: App):
    app.action("pick_a_provider")(set_user_selection)
    for action_id in SQLITE_UPLOAD_QUICK_REPLY_ACTION_IDS:
        app.action(action_id)(sqlite_upload_quick_reply_callback)
