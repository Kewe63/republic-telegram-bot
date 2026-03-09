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

### 1. Install Requirements

Python 3.10 or higher is required.

```bash
pip install -r requirements.txt
```

### 2. Create Configuration File

```bash
cp .env.example .env
```

Then open `.env` in a text editor and fill in your values:

```env
TELEGRAM_TOKEN=123456789:ABCdef...
CHAT_ID=-100123456789
VALIDATOR_ADDR=raivaloper1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WALLET_ADDR=rai1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MONIKER=MyValidator
```

### 3. Start the Bot

```bash
python rai_bot.py
```

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

---

## ⚠️ Security

- Never commit your `.env` file to Git
- Back up `state.json` (it stores proposal and jail history)
- Never share your bot token with anyone
