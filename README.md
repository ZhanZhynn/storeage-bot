# Slack AI Chatbot

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

Before getting started, make sure you have a development workspace where you have permissions to install apps. If you don’t have one setup, go ahead and [create one](https://slack.com/create).
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

##### OpenCode Session Setup (Local-Only)

To use your local OpenCode session instead of a provider API key, start OpenCode's local server and web interface:

```zsh
opencode web --hostname 127.0.0.1 --port 4096
```

Then export the local OpenCode URL for this Slack bot process:

```zsh
export OPENCODE_URL=http://127.0.0.1:4096
```

The app can auto-start OpenCode web server when `app.py` launches:

```zsh
export AUTO_START_OPENCODE=true
export OPENCODE_HOSTNAME=127.0.0.1
export OPENCODE_PORT=4096
```

If you prefer to manage OpenCode separately, disable auto-start:

```zsh
export AUTO_START_OPENCODE=false
```

Choose which OpenCode model(s) should appear in Slack:

```zsh
# Single model
export OPENCODE_MODEL=github-copilot/gpt-5.3-codex

# Or multiple models in the dropdown
export OPENCODE_MODELS=github-copilot/gpt-5.3-codex,github-copilot/claude-sonnet-4.5,openai/o4-mini
```

If neither `OPENCODE_MODEL` nor `OPENCODE_MODELS` is set, the app will load models from `opencode models` automatically.

### Skill Playbooks (Prompt Orchestration)

You can define task-specific skill playbooks in markdown files, and the bot will auto-select relevant ones based on the user prompt.

- Skills directory: `./skills`
- File format: one `.md` playbook per skill
- Optional override: `BOLTY_SKILLS_DIR=./skills`

Each skill should include a `keywords:` line and practical workflow steps (for example, sales analysis or spreadsheet-to-SQLite upload instructions). Matching skill content is injected into prompt context as `Skill playbooks (auto-selected)` and used by the model to choose the right tools/workflow.

Skill matching is weighted (keyword line > title/filename > body text) and the top matches are selected per prompt.
By default, only one best-matching skill is injected into prompt context (not all skills).
You can tune this behavior with `BOLTY_MAX_SKILLS_IN_PROMPT` and `BOLTY_MIN_SKILL_SCORE`.
Skills can be organized in nested folders too (for example `skills/lazada/orders.md`).

For Lazada API workflows, configure shared credentials once and the bot will inject a config hint automatically when prompts mention Lazada domains:

```zsh
export BOLTY_LAZADA_APP_KEY=<your-lazada-app-key>
export BOLTY_LAZADA_APP_SECRET=<your-lazada-app-secret>
export BOLTY_LAZADA_ACCESS_TOKEN=<your-lazada-access-token>
export BOLTY_LAZADA_REGION=MY
export BOLTY_LAZADA_API_BASE=https://api.lazada.com.my/rest
```

### Deterministic Lazada Helper (Orders MVP)

This repo includes a deterministic Lazada helper CLI to fetch order data through `/orders/get` without hand-crafting signatures in prompts.

Run example:

```zsh
python3 -m lazada_helper.cli orders get --days 7 --status all --limit 100 --max-pages 10
```

Optional explicit filters:

```zsh
python3 -m lazada_helper.cli orders get \
  --created-after 2026-04-01T00:00:00+00:00 \
  --created-before 2026-04-21T00:00:00+00:00 \
  --status shipped \
  --limit 50 \
  --offset 0
```

Output is JSON with `ok`, `status`, `total_fetched`, `orders`, paging fields, and Lazada `request_ids`.
Prefer safe wrapper for bot/tool execution:

```zsh
python3 -m lazada_helper.safe_run -- orders get --days 7 --status all --limit 100 --max-pages 10
```

Optional save without shell redirection:

```zsh
python3 -m lazada_helper.safe_run --save-json data/lazada_orders.json -- orders get --days 7 --status all --limit 100 --max-pages 10
```

Run helper commands directly (without `>` redirection) so the bot can parse stdout immediately.
If tool output is truncated, read the emitted `outputPath` file for full JSON.

Finance helper examples:

```zsh
python3 -m lazada_helper.cli finance payout-status-get \
  --created-after 2026-04-01T00:00:00+00:00 \
  --created-before 2026-04-21T00:00:00+00:00 \
  --limit 100 --offset 0 --max-pages 10

python3 -m lazada_helper.cli finance account-transactions-query \
  --created-after 2026-04-01T00:00:00+00:00 \
  --created-before 2026-04-21T00:00:00+00:00 \
  --limit 100 --offset 0 --max-pages 10

python3 -m lazada_helper.cli finance logistics-fee-detail \
  --created-after 2026-04-01T00:00:00+00:00 \
  --created-before 2026-04-21T00:00:00+00:00 \
  --limit 100 --offset 0 --max-pages 10

python3 -m lazada_helper.cli finance transaction-details-get \
  --transaction-number TXN-1001

python3 -m lazada_helper.cli products get \
  --filter all \
  --limit 100 \
  --offset 0 \
  --max-pages 10

python3 -m lazada_helper.cli products item-get \
  --item-id 123456789

python3 -m lazada_helper.cli returns-refunds return-detail-list \
  --created-after 2026-04-01T00:00:00+00:00 \
  --created-before 2026-04-21T00:00:00+00:00 \
  --limit 100 --offset 0 --max-pages 10

python3 -m lazada_helper.cli returns-refunds return-history-list \
  --created-after 2026-04-01T00:00:00+00:00 \
  --created-before 2026-04-21T00:00:00+00:00 \
  --limit 100 --offset 0 --max-pages 10

python3 -m lazada_helper.cli returns-refunds reason-list

python3 -m lazada_helper.cli returns-refunds get-reverse-orders-for-seller \
  --created-after 2026-04-01T00:00:00+00:00 \
  --created-before 2026-04-21T00:00:00+00:00 \
  --limit 100 --offset 0 --max-pages 10

python3 -m lazada_helper.cli reviews seller-history-list \
  --created-after 2026-04-01T00:00:00+00:00 \
  --created-before 2026-04-21T00:00:00+00:00 \
  --item-id 123456789 \
  --current 1 --limit 100 --max-pages 10

python3 -m lazada_helper.cli reviews seller-list-v2 \
  --item-id 123456789

python3 -m lazada_helper.cli reviews seller-reply-add \
  --id-list 12345,12346 \
  --content "Thank you for your feedback"

python3 -m lazada_helper.cli reviews get-item-reviews \
  --days 30 \
  --sort desc
```

When model responses contain markdown tables, Slack output is auto-converted into fixed-width table blocks for better readability.

Starter examples are included:

- `skills/analyze_sales_data.md`
- `skills/upload_sales_data_to_sqlite.md`

OpenCode conversations are persisted per Slack thread/DM in a local mapping file:

```zsh
export OPENCODE_SESSION_STORE=./data/opencode_sessions.json
```

This keeps each Slack thread in a single OpenCode session and sends only the latest user message each turn (instead of re-sending entire thread history).

File uploads are supported for OpenCode requests. Supported file types are images (`.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`) and spreadsheet formats (`.xlsx`, `.xls`, `.csv`).

Attach files to your Slack message/mention and the bot will download them temporarily and forward them to OpenCode with `--file`.

For images, the app validates the downloaded bytes and normalizes the temporary file extension to one of the accepted formats (`.png`, `.jpeg`, `.gif`, `.webp`) before sending to OpenCode.

The default system prompt is only prepended on the first OpenCode message in a Slack thread. Follow-up messages in the same thread use the same OpenCode session and send only the latest user message.

Make sure your Slack app has the `files:read` bot scope and is reinstalled after manifest updates, otherwise file downloads will fail and the bot will post a warning in-thread.

SQLite upload flow is also supported for spreadsheet files in messages/mentions. By default, uploads use a repo-local database file:

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

Optional (if your OpenCode server uses a password):

```zsh
export OPENCODE_SERVER_PASSWORD=<your-password>
```

Once the bot is running, open the Slack app home and choose `OpenCode Session (OpenCode)` from the provider dropdown.

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

### `/ai`

* `ai_constants.py`: Defines constants used throughout the AI module.

<a name="byo-llm"></a>
#### `ai/providers`
This module contains classes for communicating with different API providers, such as [Anthropic](https://www.anthropic.com/), [OpenAI](https://openai.com/), and [Vertex AI](cloud.google.com/vertex-ai). To add your own LLM, create a new class for it using the `base_api.py` as an example, then update `ai/providers/__init__.py` to include and utilize your new class for API communication.

* `__init__.py`: 
This file contains utility functions for handling responses from the provider APIs and retrieving available providers.

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
