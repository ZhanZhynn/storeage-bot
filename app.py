import os
import logging
import atexit
import shutil
import subprocess

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from listeners import register_listeners

# Initialization
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def maybe_start_opencode_web() -> subprocess.Popen | None:
    if os.environ.get("AUTO_START_OPENCODE", "true").lower() != "true":
        return None

    opencode_path = shutil.which("opencode")
    if opencode_path is None:
        logger.warning("AUTO_START_OPENCODE enabled but 'opencode' not found in PATH")
        return None

    hostname = os.environ.get("OPENCODE_HOSTNAME", "127.0.0.1")
    port = os.environ.get("OPENCODE_PORT", "4096")

    command = [opencode_path, "web", "--hostname", hostname, "--port", port]
    logger.info("Starting OpenCode web server at http://%s:%s", hostname, port)
    process = subprocess.Popen(command)
    return process

# Register Listeners
register_listeners(app)

# Start Bolt app
if __name__ == "__main__":
    opencode_process = maybe_start_opencode_web()

    if opencode_process is not None:
        def _cleanup_opencode():
            if opencode_process.poll() is None:
                opencode_process.terminate()

        atexit.register(_cleanup_opencode)

    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
