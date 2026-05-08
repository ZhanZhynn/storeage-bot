# StoreAge Bot

An AI-powered Slack chatbot with multi-marketplace platform helpers (Lazada, Shopee). The bot routes AI interactions through OpenCode CLI and provides deterministic CLI helpers for marketplace operations.

This Slack chatbot app template offers a customizable solution for integrating AI-powered conversations into your Slack workspace. Here's what the app can do out of the box:

* Interact with the bot by mentioning it in conversations and threads
* Send direct messages to the bot for private interactions
* Use the `/ask-bolty` command to communicate with the bot in channels where it hasn't been added
* Use the `/upload-sqlite` command to run guided spreadsheet-to-SQLite uploads
* Utilize a custom function for integration with Workflow Builder to summarize messages in conversations
* Select your preferred API/model from the app home to customize the bot's responses
* Bring Your Own Language Model [BYO LLM](#byo-llm) for customization
* Custom FileStateStore creates a file in /data per user to store API/model preferences

Inspired by [ChatGPT-in-Slack](https://github.com/seratch/ChatGPT-in-Slack/tree/main)

## Quick Start (Docker, Remote Linux)

```bash
ssh <user>@<server>
sudo mkdir -p /opt/storeage-bot && sudo chown -R "$USER":"$USER" /opt/storeage-bot
cd /opt/storeage-bot
git clone <your-repo-url> .
cp .env.example .env
nano .env
docker compose build
docker compose up -d
docker compose ps
docker compose logs -f --tail=200
```

This runs the bot 24/7 with `restart: always` and persists SQLite/session data in `./data`.

Before getting started, make sure you have a development workspace where you have permissions to install apps. If you don't have one setup, go ahead and [create one](https://slack.com/create).
## Installation

#### Prerequisites
* To use the OpenAI and Anthropic models, you must have an account with sufficient credits.
* To use the Vertex models, you must have [a Google Cloud Provider project](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#expandable-1) with sufficient credits.

#### Create a Slack App
1. Open [https://api.slack.com/apps/new](https://api.slack.com/apps/new) and choose "From an app manifest"
2. Choose the workspace you want to install the application to
3. Copy the contents of [manifest.json](./manifest.json) into the text box that says `*Paste your manifest code here*` (within the JSON tab) and click *Next*
4. Review the configuration and click *Create*
5. Click *Install to Workspace* and *Allow* on the screen that follows. You'll then be redirected to the App Configuration dashboard.

#### Environment Variables
Before you can run the app, you'll need to store some environment variables.

1. Open your apps configuration page from this list, click **OAuth & Permissions** in the left hand menu, then copy the Bot User OAuth Token. You will store this in your environment as `SLACK_BOT_TOKEN`.
2. Click **Basic Information** from the left hand menu and follow the steps in the App-Level Tokens section to create an app-level token with the `connections:write` scope. Copy this token. You will store this in your environment as `SLACK_APP_TOKEN`.

Next, set the gathered tokens as environment variables using the following commands:

```zsh
# MacOS/Linux
export SLACK_BOT_TOKEN=<your-bot-token>
export SLACK_APP_TOKEN=<your-app-token>
export OPENCODE_URL=http://127.0.0.1:4096
export OPENCODE_MODEL=opencode/ling-2.6-flash-free
export OPENCODE_MODELS=opencode/ling-2.6-flash-free,opencode/nemotron-3-super-free,opencode/minimax-m2.5-free,opencode/gpt-5-nano
export BOLTY_LAZADA_APP_KEY=
export BOLTY_LAZADA_APP_SECRET=
export BOLTY_LAZADA_ACCESS_TOKEN=
```

```pwsh
# Windows
set SLACK_BOT_TOKEN=<your-bot-token>
set SLACK_APP_TOKEN=<your-app-token>
```

Different models from different AI providers are available if the corresponding environment variable is added, as shown in the sections below.

##### Anthropic Setup

To interact with Anthropic models, navigate to your Anthropic account dashboard to [create an API key](https://console.anthropic.com/settings/keys), then export the key as follows:

```zsh
export ANTHROPIC_API_KEY=<your-api-key>
```

##### Google Cloud Vertex AI Setup

To use Google Cloud Vertex AI, [follow this quick start](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#expandable-1) to create a project for sending requests to the Gemini API, then gather [Application Default Credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc) with the strategy to match your development environment.

Once your project and credentials are configured, export environment variables to select from Gemini models:

```zsh
export VERTEX_AI_PROJECT_ID=<your-project-id>
export VERTEX_AI_LOCATION=<location-to-deploy-model>
```

The project location can be located under the **Region** on the [Vertex AI](https://console.cloud.google.com/vertex-ai) dashboard, as well as more details about available Gemini models.

##### OpenAI Setup

Unlock the OpenAI models from your OpenAI account dashboard by clicking [create a new secret key](https://platform.openai.com/api-keys), then export the key like so:

```zsh
export OPENAI_API_KEY=<your-api-key>
```

##### OpenCode CLI Setup

The bot routes all AI interactions through the **OpenCode CLI** (`opencode run`). The OpenCode web UI is **not** required.

1. Install OpenCode and ensure `opencode` is in your `PATH`.

2. **(Optional) Start an OpenCode session server** for persistent conversation sessions across Slack threads:

```zsh
opencode web --hostname 127.0.0.1 --port 4096
```

Then set `OPENCODE_URL` so the bot attaches to it:

```zsh
export OPENCODE_URL=http://127.0.0.1:4096
```

If `OPENCODE_URL` is not set, each `opencode run` invocation is standalone (no session persistence across thread replies).

3. Choose which OpenCode model(s) should appear in Slack:

```zsh
# Single model
export OPENCODE_MODEL=github-copilot/gpt-5.3-codex

# Or multiple models in the dropdown
export OPENCODE_MODELS=github-copilot/gpt-5.3-codex,github-copilot/claude-sonnet-4.5,openai/o4-mini
```

If neither `OPENCODE_MODEL` nor `OPENCODE_MODELS` is set, the app will load models from `opencode models` automatically.

Optional (if your OpenCode server uses a password):

```zsh
export OPENCODE_SERVER_PASSWORD=<your-password>
```

OpenCode conversations are persisted per Slack thread/DM in a local mapping file:

```zsh
export OPENCODE_SESSION_STORE=./data/opencode_sessions.json
```

This keeps each Slack thread in a single OpenCode session and sends only the latest user message each turn (instead of re-sending entire thread history).

### Skill Playbooks (Prompt Orchestration)

You can define task-specific skill playbooks in markdown files, and the bot will auto-select relevant ones based on the user prompt.

- Skills directory: `./skills`
- File format: one `.md` playbook per skill
- Optional override: `BOLTY_SKILLS_DIR=./skills`

Each skill should include a `keywords:` line and practical workflow steps (for example, sales analysis or spreadsheet-to-SQLite upload instructions). Matching skill content is injected into prompt context as `Skill playbooks (auto-selected)` and used by the model to choose the right tools/workflow.

Skill matching is weighted (keyword line > title/filename > body text) and the top matches are selected per prompt.
By default, only one best-matching skill is injected into prompt context (not all skills).
You can tune this behavior with `BOLTY_MAX_SKILLS_IN_PROMPT` and `BOLTY_MIN_SKILL_SCORE`.
Skills can be organized in nested folders too (for example `skills/lazada/orders.md` or `skills/shopee/orders.md`).

### Platform Helpers (Multi-Marketplace Architecture)

The bot supports deterministic CLI helpers for marketplace platforms. Each platform follows the same pattern:

```
platform_helpers/
├── __init__.py          # Package init with registry exports
├── registry.py          # Platform auto-discovery and registration
├── lazada/              # Lazada API helper (fully implemented)
│   ├── cli.py           # Argparse CLI with domain/action subcommands
│   ├── client.py        # Signed API client
│   ├── safe_run.py      # Bot-safe wrapper with JSON output
│   ├── orders.py        # Order domain functions
│   ├── finance.py       # Finance domain functions
│   ├── products.py      # Product domain functions
│   ├── reviews.py       # Review domain functions
│   └── returns_refunds.py  # Returns/refunds domain functions
└── shopee/              # Shopee API helper (client + CLI)
    ├── cli.py
    ├── client.py
    ├── models.py
    ├── orders.py
    ├── products.py
    ├── returns_refunds.py
    ├── safe_run.py
    └── __init__.py
```

#### Adding a New Platform

1. Create `platform_helpers/<name>/` with the same module pattern as `lazada/`
2. Register it in `platform_helpers/registry.py` (add a `PlatformHelper` entry)
3. Add skill playbooks in `skills/<name>/`
4. Set the platform's env vars (e.g., `BOLTY_SHOPEE_PARTNER_ID`, etc.)

The AI context layer auto-discovers registered platforms — no changes needed in the AI/listener code.

#### Lazada Platform Helper

Configure shared credentials for Lazada API workflows:

```zsh
export BOLTY_LAZADA_APP_KEY=<your-lazada-app-key>
export BOLTY_LAZADA_APP_SECRET=<your-lazada-app-secret>
export BOLTY_LAZADA_ACCESS_TOKEN=<your-lazada-access-token>
export BOLTY_LAZADA_REGION=MY
export BOLTY_LAZADA_API_BASE=https://api.lazada.com.my/rest
```

Run examples:

```zsh
python3 -m platform_helpers.lazada.cli orders get --days 7 --status all --limit 100 --max-pages 10

python3 -m platform_helpers.lazada.cli finance payout-status-get \
  --created-after 2026-04-01T00:00:00+00:00 \
  --created-before 2026-04-21T00:00:00+00:00 \
  --limit 100 --offset 0 --max-pages 10

python3 -m platform_helpers.lazada.cli products get \
  --filter all --limit 100 --offset 0 --max-pages 10

python3 -m platform_helpers.lazada.cli returns-refunds return-detail-list \
  --created-after 2026-04-01T00:00:00+00:00 \
  --created-before 2026-04-21T00:00:00+00:00 \
  --limit 100 --offset 0 --max-pages 10

python3 -m platform_helpers.lazada.cli reviews get-item-reviews \
  --days 30 --sort desc
```

Safe wrapper for bot/tool execution:

```zsh
python3 -m platform_helpers.lazada.safe_run -- orders get --days 7 --status all --limit 100 --max-pages 10
```

Backward-compatible aliases still work:

```zsh
python3 -m lazada_helper.cli orders get --days 7
python3 -m lazada_helper.safe_run -- orders get --days 7
```

Output is JSON with `ok`, `status`, `total_fetched`, records, paging fields, and API `request_ids`.

#### Shopee Platform Helper

Configure shared credentials for Shopee API workflows:

```zsh
export BOLTY_SHOPEE_PARTNER_ID=<your-partner-id>
export BOLTY_SHOPEE_PARTNER_KEY=<your-partner-key>
export BOLTY_SHOPEE_SHOP_ID=<authorized-shop-id>
export BOLTY_SHOPEE_ACCESS_TOKEN=<access-token>
export BOLTY_SHOPEE_REFRESH_TOKEN=<refresh-token>
export BOLTY_SHOPEE_ENVIRONMENT=production  # or sandbox
export BOLTY_SHOPEE_REGION=global           # global|china|us
```

Authorization flow:

```zsh
python3 -m platform_helpers.shopee.cli auth url --redirect https://your.callback.io/callback

# Then exchange code for tokens:
python3 -m platform_helpers.shopee.cli auth token-get \
  --code <code-from-callback> \
  --shop-id <shop-id-from-callback>
```

Example API calls:

```zsh
python3 -m platform_helpers.shopee.cli orders get --days 7
python3 -m platform_helpers.shopee.cli orders get --days 7 --time-range-field create_time
python3 -m platform_helpers.shopee.cli orders items --order-sn-list 230101ABCD1234,230101ABCD5678
python3 -m platform_helpers.shopee.cli products get --page-size 50
python3 -m platform_helpers.shopee.cli returns-refunds list --page-size 50
```

Safe wrapper for bot/tool execution:

```zsh
python3 -m platform_helpers.shopee.safe_run -- orders get --days 7
```

Token refresh is automatic whenever a request is made and the current token is near expiry (requires
`BOLTY_SHOPEE_REFRESH_TOKEN` plus a `shop_id` or `merchant_id`).

Shopee Order API reference (used for `orders get`):
- https://open.shopee.com/documents/v2/v2.order.get_order_list?module=94&type=1

When model responses contain markdown tables, Slack output is auto-converted into fixed-width table blocks for better readability.

### File Uploads

File uploads are supported for OpenCode requests. Supported file types are images (`.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`) and spreadsheet formats (`.xlsx`, `.xls`, `.csv`).

Attach files to your Slack message/mention and the bot will download them temporarily and forward them to OpenCode with `--file`.

For images, the app validates the downloaded bytes and normalizes the temporary file extension to one of the accepted formats (`.png`, `.jpeg`, `.gif`, `.webp`) before sending to OpenCode.

The default system prompt is only prepended on the first OpenCode message in a Slack thread. Follow-up messages in the same thread use the same OpenCode session and send only the latest user message.

Make sure your Slack app has the `files:read` bot scope and is reinstalled after manifest updates, otherwise file downloads will fail and the bot will post a warning in-thread.

### SQLite Upload Flow

SQLite upload flow is supported for spreadsheet files in messages/mentions. By default, uploads use a repo-local database file:

```zsh
./data/bolty.db
```

You can override this path with:

```zsh
export BOLTY_SQLITE_DB_PATH=./data/bolty.db
```

The bot also injects this SQLite path and current table list into AI prompt context, so when users ask about table data without a path, it will prefer this configured DB first.

Example prompts in Slack:

- `upload this csv to sqlite table sales`
- `upload to table sales sheet Summary`
- `mode shared`
- `create table sales_2026`
- `confirm upload`
- `cancel`

You can also start a guided flow via slash command:

```zsh
/upload-sqlite table sales
```

After running the command, reply in the started thread with your spreadsheet attachment and any follow-up instructions.

## Docker Deployment (24/7 Linux)

This project includes a Docker runtime that bundles Python + OpenCode CLI in one container. It is designed for Slack Socket Mode, so you do not need to expose inbound HTTP ports.

### Files Used

- `Dockerfile`
- `docker-compose.yml`
- `.env.example`

### 1) Prepare the Linux Host

Install Docker Engine and Docker Compose plugin on the remote Linux machine.

```bash
docker --version
docker compose version
```

### 2) Deploy (First Time)

```bash
# on your remote host
sudo mkdir -p /opt/storeage-bot
sudo chown -R "$USER":"$USER" /opt/storeage-bot
cd /opt/storeage-bot

# clone
git clone <your-repo-url> .

# create runtime env file
cp .env.example .env
```

Edit `.env` and set at minimum:

- `SLACK_BOT_TOKEN`
- `SLACK_APP_TOKEN`
- `OPENCODE_MODEL` (or `OPENCODE_MODELS`)
- `BOLTY_LAZADA_APP_KEY`
- `BOLTY_LAZADA_APP_SECRET`
- `BOLTY_LAZADA_ACCESS_TOKEN`

Then build and run:

```bash
cd /opt/storeage-bot
docker compose config
docker compose build
docker compose up -d
docker compose ps
docker compose logs -f --tail=200
```

### 3) Update (New Release)

```bash
cd /opt/storeage-bot

# optional safety tag before update
git tag "pre-update-$(date +%Y%m%d-%H%M%S)"

git fetch --all --tags
git pull --ff-only

docker compose build
docker compose up -d --remove-orphans
docker image prune -f

docker compose ps
docker compose logs -f --tail=200
```

### 4) Rollback (Git Tag/Commit)

Use this if a new deployment is unhealthy.

```bash
cd /opt/storeage-bot

# pick one target: a tag, branch, or commit SHA
git log --oneline -n 20
git checkout <known-good-tag-or-commit>

docker compose build
docker compose up -d --remove-orphans

docker compose ps
docker compose logs -f --tail=200
```

When ready to return to your main line after rollback testing:

```bash
cd /opt/storeage-bot
git checkout main
git pull --ff-only
docker compose build
docker compose up -d --remove-orphans
```

### 5) Runtime Operations

```bash
# restart bot
docker compose restart

# stop/start
docker compose stop
docker compose start

# view logs
docker compose logs -f --tail=200

# check env keys resolved by compose
docker compose config
```

### 6) Data Persistence and Backup

Persistent app data is stored in `./data` on the host (mounted to `/app/data` in container), including:

- SQLite DB (`bolty.db`)
- OpenCode session stores
- Upload/session files

Backup example:

```bash
cd /opt/storeage-bot
tar -czf "backup-data-$(date +%Y%m%d-%H%M%S).tar.gz" data
```

Restore example:

```bash
cd /opt/storeage-bot
tar -xzf backup-data-YYYYmmdd-HHMMSS.tar.gz
docker compose restart
```

### Setup Your Local Project
```zsh
# Clone this project onto your machine
git clone https://github.com/slack-samples/bolt-python-ai-chatbot.git

# Change into this project directory
cd bolt-python-ai-chatbot

# Setup your python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the dependencies
pip install -r requirements.txt

# Start your local server
python3 app.py
```

#### Linting
```zsh
# Run ruff check from root directory for linting
ruff check .

# Run ruff format from root directory for code formatting
ruff format .
```

## Project Structure

### `manifest.json`

`manifest.json` is a configuration for Slack apps. With a manifest, you can create an app with a pre-defined configuration, or adjust the configuration of an existing app.


### `app.py`

`app.py` is the entry point for the application and is the file you'll run to start the server. This project aims to keep this file as thin as possible, primarily using it as a way to route inbound requests.


### `/listeners`

Every incoming request is routed to a "listener". Inside this directory, we group each listener based on the Slack Platform feature used, so `/listeners/commands` handles incoming [Slash Commands](https://api.slack.com/interactivity/slash-commands) requests, `/listeners/events` handles [Events](https://api.slack.com/apis/events-api) and so on.

The shared AI response lifecycle (file downloads, provider calls, image/spreadsheet uploads, error handling) is in `listeners/listener_utils/ai_handler.py`. The event handlers (`app_mentioned.py`, `app_messaged.py`) are thin adapters.

### `/ai`

* `ai_constants.py`: Defines constants used throughout the AI module.


<a name="byo-llm"></a>
#### `ai/providers`
This module contains classes for communicating with different API providers, such as [Anthropic](https://www.anthropic.com/), [OpenAI](https://openai.com/), and [Vertex AI](cloud.google.com/vertex-ai). To add your own LLM, create a new class for it using the `base_api.py` as an example, then update `ai/providers/__init__.py` to include and utilize your new class for API communication.

* `__init__.py`: 
This file contains utility functions for handling responses from the provider APIs and retrieving available providers. It dynamically injects platform context (Lazada, Shopee, etc.) based on prompt keywords.

### `/platform_helpers`

Marketplace-specific API helpers organized by platform. Each platform sub-package follows the same pattern: `client.py` → domain modules → `cli.py` → `safe_run.py`. The `registry.py` enables auto-discovery so the AI layer injects context for any configured platform.

### `/state_store`

* `user_identity.py`: This file defines the UserIdentity class for creating user objects. Each object represents a user with the user_id, provider, and model attributes.

* `user_state_store.py`: This file defines the base class for FileStateStore.

* `file_state_store.py`: This file defines the FileStateStore class which handles the logic for creating and managing files for each user.

* `set_user_state.py`: This file creates a user object and uses a FileStateStore to save the user's selected provider to a JSON file.

* `get_user_state.py`: This file retrieves a users selected provider from the JSON file created with `set_user_state.py`.

## App Distribution / OAuth

Only implement OAuth if you plan to distribute your application across multiple workspaces. A separate `app_oauth.py` file can be found with relevant OAuth settings.

When using OAuth, Slack requires a public URL where it can send requests. In this template app, we've used [`ngrok`](https://ngrok.com/download). Checkout [this guide](https://ngrok.com/docs#getting-started-expose) for setting it up.

Start `ngrok` to access the app on an external network and create a redirect URL for OAuth. 

```
ngrok http 3000
```

This output should include a forwarding address for `http` and `https` (we'll use `https`). It should look something like the following:

```
Forwarding   https://3cb89939.ngrok.io -> http://localhost:3000
```

Navigate to **OAuth & Permissions** in your app configuration and click **Add a Redirect URL**. The redirect URL should be set to your `ngrok` forwarding address with the `slack/oauth_redirect` path appended. For example:

```
https://3cb89939.ngrok.io/slack/oauth_redirect
```
