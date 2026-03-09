# 🤖 RAI Validator Telegram Bot

A Telegram bot for real-time monitoring of your Republic AI Network validator node.

---

## 📋 Features

### Commands
| Command | Description |
|---|---|
| `/start` / `/help` | Show command menu |
| `/lang` | Language selection (🇹🇷 Türkçe / 🇬🇧 English) |
| `/status` | Validator status (jailed, bonded, stake, commission) |
| `/balance` | Wallet balance |
| `/uptime` | Uptime percentage and missed block count |
| `/rank` | Rank within the active set |
| `/activeset` | Active set analysis (margin, missing amount) |
| `/rewards` | Accumulated staking rewards |
| `/proposals` | Open governance proposals |
| `/delegators` | Top 10 delegator list |
| `/slashing` | Slashing parameters |
| `/network` | Network statistics (chain ID, block height, total power) |

### Automatic Alerts
| Alert | Trigger |
|---|---|
| 🚨 Validator Jailed | Instant notification when validator is jailed |
| ✅ Validator Unjailed | Notification when unjail is completed |
| ⚠️ Active Set Warning | When validator is at risk of leaving the active set |
| 🚨 Uptime Alert | When uptime drops below threshold (default: 95%) |
| 🚨 New Governance Proposal | When a new proposal enters voting period |

---

## 🗂️ File Structure

```
republic telegram bot/
├── rai_bot.py          # Main bot file
├── requirements.txt    # Python dependencies
├── .env.example        # Configuration template
├── .env                # Your config (do not commit to git!)
├── state.json          # Auto-generated (state file)
└── README.md           # This file
```

---

## ⚙️ Setup

### Prerequisites
- Python 3.10 or higher
- A Telegram account
- Republic AI Network validator node (optional for monitoring)

### 1. Install Python Dependencies

First, ensure you have Python 3.10+ installed. You can check your version with:

```bash
python --version
```

If you don't have Python, download it from [python.org](https://www.python.org/downloads/).

Install the required packages:

```bash
pip install -r requirements.txt
```

This will install:
- `python-telegram-bot`: For Telegram bot functionality
- `aiohttp`: For HTTP requests to blockchain APIs
- `python-dotenv`: For loading environment variables from .env file

### 2. Create Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the prompts to create your bot and get the **BOT TOKEN**
4. Copy the token (it looks like `123456789:ABCdef...`)

### 3. Get Chat ID

You need the chat ID where the bot will send alerts. For a group:

1. Add your bot to the desired Telegram group
2. Send a message in the group
3. Visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` in your browser
4. Look for `"chat":{"id":<CHAT_ID>}` in the response
5. Copy the negative number (e.g., `-100123456789`)

For personal use, you can message the bot and use your user ID.

### 4. Configure Validator Information

If you have a Republic AI validator:

- **VALIDATOR_ADDR**: Your validator address (starts with `raivaloper1...`)
- **WALLET_ADDR**: Your wallet address (starts with `rai1...`)
- **MONIKER**: Your validator name

You can find these in your validator setup or blockchain explorer.

### 5. Create Configuration File

Copy the example configuration:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
# Required
TELEGRAM_TOKEN=your_bot_token_here
CHAT_ID=your_chat_id_here

# Optional (for validator monitoring)
VALIDATOR_ADDR=raivaloper1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WALLET_ADDR=rai1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MONIKER=YourValidatorName

# Optional customizations
ADMIN_IDS=123456789,987654321  # Comma-separated Telegram user IDs for admin access
UPTIME_ALERT_THRESHOLD=95.0     # Alert when uptime drops below this %
```

### 6. Start the Bot

Run the bot:

```bash
python rai_bot.py
```

The bot will start and begin monitoring. You should see output like:
```
Bot started successfully!
Monitoring validator: YourValidatorName
```

### 7. Test the Bot

Send `/start` to your bot or in the group to see available commands.

---

## 🔧 Troubleshooting

### Bot doesn't respond
- Check your `TELEGRAM_TOKEN` is correct
- Ensure the bot is added to the group (if using group chat)
- Verify `CHAT_ID` matches the group/user ID

### Validator data not showing
- Confirm `VALIDATOR_ADDR` and `WALLET_ADDR` are correct
- Check network connectivity to Republic AI APIs
- Ensure your validator is active on the network

### Permission errors
- Make sure `.env` file exists and is readable
- Check file permissions if running on Linux/Mac

### Python errors
- Verify Python 3.10+ is installed
- Try `pip install --upgrade pip` then reinstall requirements
- Check for conflicting Python installations

---

## 🔑 Configuration Variables

| Variable | Description | Default |
|---|---|---|
| `TELEGRAM_TOKEN` | Bot token from BotFather | — |
| `CHAT_ID` | Chat/group ID where alerts are sent | — |
| `VALIDATOR_ADDR` | Validator address (`raivaloper1...`) | — |
| `WALLET_ADDR` | Wallet address (`rai1...`) | — |
| `MONIKER` | Validator name | `MyValidator` |
| `ADMIN_IDS` | Admin Telegram IDs (comma separated) | Empty = everyone |
| `RPC_URL` | Tendermint RPC endpoint | `https://rpc.republicai.io` |
| `REST_URL` | Cosmos REST API endpoint | `https://rest.republicai.io` |
| `GOVERNANCE_CHECK_INTERVAL` | Governance check frequency (seconds) | `60` |
| `VALIDATOR_CHECK_INTERVAL` | Validator check frequency (seconds) | `120` |
| `ACTIVE_SET_CHECK_INTERVAL` | Active set check frequency (seconds) | `300` |
| `UPTIME_ALERT_THRESHOLD` | Uptime alert threshold (%) | `95.0` |
| `ACTIVE_SET_MARGIN_PERCENT` | Active set margin warning threshold (%) | `5.0` |

---

## 🤖 How to Get a Bot Token

1. Open Telegram and talk to [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Choose a name and username for your bot
4. Copy the token into your `.env` file

## 💬 How to Find Your Chat ID

- **Personal chat:** Send `/start` to [@userinfobot](https://t.me/userinfobot)
- **Group:** Add the bot to a group, then visit `https://api.telegram.org/bot<TOKEN>/getUpdates`

---

## 🌐 Language Selection

The bot supports both Turkish and English. Each user can choose their own language:

```
/lang
```

After the command, select a language from the inline keyboard. The preference is stored per user in `state.json`.

---

## 🔒 Admin Authorization

You can restrict bot access by adding Telegram user IDs to `ADMIN_IDS` in your `.env` file:

```env
ADMIN_IDS=123456789,987654321
```

If left empty, all users can access all commands.

---

## 📦 Dependencies

```
python-telegram-bot==21.5
aiohttp==3.9.5
python-dotenv==1.0.1
```

---

## 🛠️ Developer Notes

- Bot state is stored in `state.json` (seen proposals, jail history, language preferences, uptime alert state)
- Data source: Tendermint RPC + Cosmos REST API
- `state.json` is created automatically on first run and resets if deleted
- 
---

## ⚠️ Security

- Never commit your `.env` file to Git  
- Back up `state.json` (it stores proposal and jail history)
- Never share your bot token with anyone

---

<img width="412" height="437" alt="image" src="https://github.com/user-attachments/assets/9b34f00d-f0b8-4268-86b0-a35e1df92cb5" />

---

- Built with ❤️ for the Republic AI Network validator community. 
 
