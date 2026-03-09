import asyncio
import logging
import os
import json
import time
from datetime import datetime, timezone

import aiohttp
from dotenv import load_dotenv
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram.constants import ParseMode

load_dotenv()

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
TELEGRAM_TOKEN    = os.getenv("TELEGRAM_TOKEN", "YOUR_BOT_TOKEN")
CHAT_ID           = os.getenv("CHAT_ID", "YOUR_CHAT_ID")
VALIDATOR_ADDR    = os.getenv("VALIDATOR_ADDR", "raivaloper1...")
WALLET_ADDR       = os.getenv("WALLET_ADDR", "rai1...")
MONIKER           = os.getenv("MONIKER", "MyValidator")
ADMIN_IDS         = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]

RPC_URL           = os.getenv("RPC_URL", "https://rpc.republicai.io")
REST_URL          = os.getenv("REST_URL", "https://rest.republicai.io")

GOVERNANCE_CHECK_INTERVAL  = int(os.getenv("GOVERNANCE_CHECK_INTERVAL", "60"))
VALIDATOR_CHECK_INTERVAL   = int(os.getenv("VALIDATOR_CHECK_INTERVAL", "120"))
ACTIVE_SET_CHECK_INTERVAL  = int(os.getenv("ACTIVE_SET_CHECK_INTERVAL", "300"))
UPTIME_ALERT_THRESHOLD     = float(os.getenv("UPTIME_ALERT_THRESHOLD", "95.0"))
ACTIVE_SET_MARGIN_PERCENT  = float(os.getenv("ACTIVE_SET_MARGIN_PERCENT", "5.0"))

# ─────────────────────────────────────────────
#  LOGGING
# ─────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
#  TRANSLATIONS
# ─────────────────────────────────────────────
TEXTS = {
    "tr": {
        "start_title": "🤖 *RAI Validator Bot*",
        "start_body": (
            "Kullanılabilir komutlar:\n\n"
            "`/status`      — Validator durumu\n"
            "`/balance`     — Cüzdan bakiyesi\n"
            "`/uptime`      — Uptime ve miss sayısı\n"
            "`/rank`        — Aktif setteki sıralama\n"
            "`/activeset`   — Aktif set analizi\n"
            "`/rewards`     — Birikmiş ödüller\n"
            "`/proposals`   — Governance oylamaları\n"
            "`/delegators`  — Delegator listesi\n"
            "`/slashing`    — Slashing parametreleri\n"
            "`/network`     — Ağ istatistikleri\n"
            "`/lang`        — Dil seçimi\n"
            "`/help`        — Bu menü\n"
        ),
        "fetching": "⏳ Sorgulanıyor...",
        "fetching_long": "⏳ Kontrol ediliyor (bu biraz sürebilir)...",
        "error_val": "❌ Validator bilgisi alınamadı.",
        "error_rpc": "❌ RPC bağlantısı kurulamadı.",
        "error_data": "❌ Veri alınamadı.",
        "no_proposals": "✅ Şu an oylamada bekleyen proposal yok.",
        "status_title": "🛡️ *Validator Durumu*",
        "moniker": "📛 Moniker",
        "address": "🔗 Adres",
        "state": "📊 Durum",
        "stake": "💰 Stake",
        "commission": "💸 Komisyon",
        "block": "📦 Blok",
        "time": "🕐 Zaman",
        "balance_title": "💳 *Cüzdan Bakiyesi*",
        "wallet": "👛 Adres",
        "balance_lbl": "💰 Bakiye",
        "rewards_lbl": "🎁 Ödüller",
        "rank_title": "🏆 *Validator Sıralaması*",
        "total_active": "📋 Toplam Aktif",
        "your_rank": "🥇 Sıralaman",
        "activeset_active_title": "✅ *Aktif Set Analizi*",
        "activeset_inactive_title": "⚠️ *Aktif Set Analizi*",
        "activeset_in": "Aktif Settesin!",
        "activeset_out": "Aktif Dışındasın",
        "active_count": "🔢 Aktif Val.",
        "my_stake": "💎 Stake'in",
        "lowest_active": "📉 En Düşük Aktif",
        "safety_margin": "🛡️ Güvenlik Marjı",
        "needed_min": "🎯 Gereken Min.",
        "missing_amount": "➕ Eksik Miktar",
        "activeset_tip": "💡 _Aktif sete girebilmek için yaklaşık *{diff:.2f} RAI* daha stake etmen gerekiyor._",
        "uptime_title": "📡 *Validator Uptime*",
        "uptime_lbl": "✅ Uptime",
        "missed_lbl": "❌ Miss",
        "window_lbl": "📊 Pencere",
        "window_val": "Son `10,000` blok",
        "proposals_title": "🗳️ *Açık Governance Oylamaları*",
        "proposal_end": "⏰ Bitiş",
        "no_title": "Başlık yok",
        "rewards_title": "🎁 *Staking Ödülleri*",
        "network_title": "🌐 *Network Durumu*",
        "chain_id": "🔗 Chain ID",
        "synced": "✅ Senkronize",
        "catching": "⚠️ Senkronize Oluyor",
        "total_power": "💎 Total Güç",
        "delegators_title": "👥 *Delegator Listesi*",
        "total_delegators": "📋 Toplam Delegator",
        "top_delegators": "🏅 İlk {n} Delegator",
        "slashing_title": "⚔️ *Slashing Parametreleri*",
        "slash_window": "📊 İmzalama Penceresi",
        "slash_min_signed": "✅ Min. İmzalama Oranı",
        "slash_downtime_jail": "🔴 Downtime Jail Süresi",
        "slash_double_sign": "💀 Double Sign Ceza",
        "slash_downtime": "⚠️ Downtime Ceza",
        "slash_tombstone": "☠️ Tombstone",
        "alert_jail_title": "🚨 *VALİDATOR JAILED!*",
        "alert_jail_body": "⚠️ Hemen unjail işlemi yapılması gerekiyor!",
        "alert_unjail": "✅ *Validator başarıyla unjailed edildi!*",
        "alert_activeset_title": "⚠️ *AKTİF SET UYARISI!*",
        "alert_activeset_body": "⚠️ _Aktif setten düşme riskin var! Delegasyon almayı dene._",
        "alert_gov_title": "🚨 *YENİ GOVERNANCE PROPOSAL!*",
        "alert_gov_summary": "📝 Özet",
        "alert_gov_vote": "👉 Oy vermek için: `/proposals`",
        "alert_uptime_title": "🚨 *UPTIME UYARISI!*",
        "alert_uptime_body": "⚠️ _Uptime eşiğin ({threshold}%) altına düştü! Nodeunu kontrol et._",
        "lang_choose": "🌐 Lütfen bir dil seçin / Please choose a language:",
        "lang_set": "✅ Dil Türkçe olarak ayarlandı.",
        "jailed_status": "🔴 Jailed",
        "active_status": "🟢 Aktif",
        "inactive_status": "🟡 İnaktif",
        "admin_only": "❌ Bu komut sadece adminler tarafından kullanılabilir.",
        "val_count_label": "👥 Aktif Val.",
    },
    "en": {
        "start_title": "🤖 *RAI Validator Bot*",
        "start_body": (
            "Available commands:\n\n"
            "`/status`      — Validator status\n"
            "`/balance`     — Wallet balance\n"
            "`/uptime`      — Uptime & missed blocks\n"
            "`/rank`        — Rank in active set\n"
            "`/activeset`   — Active set analysis\n"
            "`/rewards`     — Pending rewards\n"
            "`/proposals`   — Governance proposals\n"
            "`/delegators`  — Delegator list\n"
            "`/slashing`    — Slashing parameters\n"
            "`/network`     — Network statistics\n"
            "`/lang`        — Language selection\n"
            "`/help`        — This menu\n"
        ),
        "fetching": "⏳ Fetching...",
        "fetching_long": "⏳ Checking (this may take a moment)...",
        "error_val": "❌ Could not fetch validator info.",
        "error_rpc": "❌ Could not connect to RPC.",
        "error_data": "❌ Could not fetch data.",
        "no_proposals": "✅ No proposals currently in voting period.",
        "status_title": "🛡️ *Validator Status*",
        "moniker": "📛 Moniker",
        "address": "🔗 Address",
        "state": "📊 Status",
        "stake": "💰 Stake",
        "commission": "💸 Commission",
        "block": "📦 Block",
        "time": "🕐 Time",
        "balance_title": "💳 *Wallet Balance*",
        "wallet": "👛 Address",
        "balance_lbl": "💰 Balance",
        "rewards_lbl": "🎁 Rewards",
        "rank_title": "🏆 *Validator Rank*",
        "total_active": "📋 Total Active",
        "your_rank": "🥇 Your Rank",
        "activeset_active_title": "✅ *Active Set Analysis*",
        "activeset_inactive_title": "⚠️ *Active Set Analysis*",
        "activeset_in": "You are in the Active Set!",
        "activeset_out": "You are Outside the Active Set",
        "active_count": "🔢 Active Vals.",
        "my_stake": "💎 Your Stake",
        "lowest_active": "📉 Lowest Active",
        "safety_margin": "🛡️ Safety Margin",
        "needed_min": "🎯 Needed Min.",
        "missing_amount": "➕ Missing Amount",
        "activeset_tip": "💡 _You need approximately *{diff:.2f} RAI* more stake to enter the active set._",
        "uptime_title": "📡 *Validator Uptime*",
        "uptime_lbl": "✅ Uptime",
        "missed_lbl": "❌ Missed",
        "window_lbl": "📊 Window",
        "window_val": "Last `10,000` blocks",
        "proposals_title": "🗳️ *Open Governance Proposals*",
        "proposal_end": "⏰ End",
        "no_title": "No title",
        "rewards_title": "🎁 *Staking Rewards*",
        "network_title": "🌐 *Network Status*",
        "chain_id": "🔗 Chain ID",
        "synced": "✅ Synced",
        "catching": "⚠️ Catching Up",
        "total_power": "💎 Total Power",
        "delegators_title": "👥 *Delegator List*",
        "total_delegators": "📋 Total Delegators",
        "top_delegators": "🏅 Top {n} Delegators",
        "slashing_title": "⚔️ *Slashing Parameters*",
        "slash_window": "📊 Signed Blocks Window",
        "slash_min_signed": "✅ Min. Signed Per Window",
        "slash_downtime_jail": "🔴 Downtime Jail Duration",
        "slash_double_sign": "💀 Double Sign Slash",
        "slash_downtime": "⚠️ Downtime Slash",
        "slash_tombstone": "☠️ Tombstone",
        "alert_jail_title": "🚨 *VALIDATOR JAILED!*",
        "alert_jail_body": "⚠️ Unjail action is required immediately!",
        "alert_unjail": "✅ *Validator successfully unjailed!*",
        "alert_activeset_title": "⚠️ *ACTIVE SET WARNING!*",
        "alert_activeset_body": "⚠️ _You are at risk of dropping out of the active set! Try getting more delegations._",
        "alert_gov_title": "🚨 *NEW GOVERNANCE PROPOSAL!*",
        "alert_gov_summary": "📝 Summary",
        "alert_gov_vote": "👉 To vote: `/proposals`",
        "alert_uptime_title": "🚨 *UPTIME ALERT!*",
        "alert_uptime_body": "⚠️ _Uptime dropped below threshold ({threshold}%)! Check your node._",
        "lang_choose": "🌐 Lütfen bir dil seçin / Please choose a language:",
        "lang_set": "✅ Language set to English.",
        "jailed_status": "🔴 Jailed",
        "active_status": "🟢 Active",
        "inactive_status": "🟡 Inactive",
        "admin_only": "❌ This command is for admins only.",
        "val_count_label": "👥 Active Vals.",
    },
}

def t(user_id: int, key: str, **kwargs) -> str:
    lang = user_languages.get(user_id, "tr")
    text = TEXTS.get(lang, TEXTS["tr"]).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text

# ─────────────────────────────────────────────
#  STATE
# ─────────────────────────────────────────────
STATE_FILE = "state.json"

def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "seen_proposals": [],
        "last_jailed": False,
        "user_languages": {},
        "uptime_alerted": False,
    }

def save_state(state: dict):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

state = load_state()
user_languages: dict[int, str] = {int(k): v for k, v in state.get("user_languages", {}).items()}

def save_user_lang(user_id: int, lang: str):
    user_languages[user_id] = lang
    state["user_languages"] = {str(k): v for k, v in user_languages.items()}
    save_state(state)

# ─────────────────────────────────────────────
#  HTTP
# ─────────────────────────────────────────────
async def get(session: aiohttp.ClientSession, url: str) -> dict | None:
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r:
            if r.status == 200:
                return await r.json(content_type=None)
    except Exception as e:
        logger.warning(f"GET {url} failed: {e}")
    return None

# ─────────────────────────────────────────────
#  CHAIN DATA FETCHERS
# ─────────────────────────────────────────────
async def fetch_validator_info(session: aiohttp.ClientSession) -> dict | None:
    data = await get(session, f"{REST_URL}/cosmos/staking/v1beta1/validators/{VALIDATOR_ADDR}")
    if data and "validator" in data:
        return data["validator"]
    return None

async def fetch_balance(session: aiohttp.ClientSession) -> str:
    data = await get(session, f"{REST_URL}/cosmos/bank/v1beta1/balances/{WALLET_ADDR}")
    if data and "balances" in data:
        for coin in data["balances"]:
            if coin["denom"] == "arai":
                return f"{int(coin['amount']) / 1e18:.4f} RAI"
    return "0 RAI"

async def fetch_all_validators(session: aiohttp.ClientSession) -> list:
    data = await get(session, f"{REST_URL}/cosmos/staking/v1beta1/validators?status=BOND_STATUS_BONDED&pagination.limit=200")
    if data and "validators" in data:
        return data["validators"]
    return []

async def fetch_block_height(session: aiohttp.ClientSession) -> int | None:
    data = await get(session, f"{RPC_URL}/status")
    if data:
        try:
            return int(data["result"]["sync_info"]["latest_block_height"])
        except (KeyError, TypeError):
            pass
    return None

async def fetch_proposals(session: aiohttp.ClientSession) -> list:
    data = await get(session, f"{REST_URL}/cosmos/gov/v1beta1/proposals?proposal_status=2")
    if data and "proposals" in data:
        return data["proposals"]
    return []

async def fetch_rewards(session: aiohttp.ClientSession) -> str:
    data = await get(session, f"{REST_URL}/cosmos/distribution/v1beta1/delegators/{WALLET_ADDR}/rewards")
    if data and "total" in data:
        for coin in data["total"]:
            if coin["denom"] == "arai":
                return f"{float(coin['amount']) / 1e18:.4f} RAI"
    return "0 RAI"

async def fetch_signing_info(session: aiohttp.ClientSession) -> dict | None:
    data = await get(session, f"{REST_URL}/cosmos/slashing/v1beta1/signing_infos/{VALIDATOR_ADDR}")
    if data and "val_signing_info" in data:
        return data["val_signing_info"]
    return None

async def fetch_delegators(session: aiohttp.ClientSession, limit: int = 10) -> list:
    data = await get(session, f"{REST_URL}/cosmos/staking/v1beta1/validators/{VALIDATOR_ADDR}/delegations?pagination.limit={limit}")
    if data and "delegation_responses" in data:
        return data["delegation_responses"]
    return []

async def fetch_slashing_params(session: aiohttp.ClientSession) -> dict | None:
    data = await get(session, f"{REST_URL}/cosmos/slashing/v1beta1/params")
    if data and "params" in data:
        return data["params"]
    return None

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def short_addr(addr: str, chars: int = 8) -> str:
    return f"{addr[:chars]}...{addr[-6:]}" if len(addr) > chars + 6 else addr

def status_emoji(jailed: bool, bonded: bool, uid: int) -> str:
    if jailed:
        return t(uid, "jailed_status")
    if bonded:
        return t(uid, "active_status")
    return t(uid, "inactive_status")

def tokens_to_rai(tokens: str) -> str:
    try:
        return f"{int(tokens) / 1e18:.2f} RAI"
    except (ValueError, TypeError):
        return tokens

def uptime_bar(pct: float) -> str:
    filled = int(pct / 5)
    return "█" * filled + "░" * (20 - filled)

def is_admin(user_id: int) -> bool:
    return not ADMIN_IDS or user_id in ADMIN_IDS

def sep() -> str:
    return "━━━━━━━━━━━━━━━━━━"

# ─────────────────────────────────────────────
#  COMMANDS
# ─────────────────────────────────────────────
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = f"{t(uid,'start_title')}\n\n{t(uid,'start_body')}"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def cmd_lang(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ]
    ])
    await update.message.reply_text(t(uid, "lang_choose"), reply_markup=keyboard)

async def callback_lang(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    lang = "tr" if query.data == "lang_tr" else "en"
    save_user_lang(uid, lang)
    await query.edit_message_text(t(uid, "lang_set"))

async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(t(uid, "fetching"))
    async with aiohttp.ClientSession() as session:
        val = await fetch_validator_info(session)
        height = await fetch_block_height(session)

    if not val:
        await update.message.reply_text(t(uid, "error_val"))
        return

    jailed = val.get("jailed", False)
    bonded = val.get("status") == "BOND_STATUS_BONDED"
    tokens = tokens_to_rai(val.get("tokens", "0"))
    commission = float(val.get("commission", {}).get("commission_rates", {}).get("rate", "0")) * 100
    moniker = val.get("description", {}).get("moniker", MONIKER)

    text = (
        f"{t(uid,'status_title')}\n{sep()}\n"
        f"{t(uid,'moniker')}  : `{moniker}`\n"
        f"{t(uid,'address')}   : `{short_addr(VALIDATOR_ADDR)}`\n"
        f"{t(uid,'state')}    : {status_emoji(jailed, bonded, uid)}\n"
        f"{t(uid,'stake')}    : `{tokens}`\n"
        f"{t(uid,'commission')} : `{commission:.1f}%`\n"
        f"{t(uid,'block')}    : `{height:,}`\n"
        f"{t(uid,'time')}    : `{datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}`"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def cmd_balance(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(t(uid, "fetching"))
    async with aiohttp.ClientSession() as session:
        balance = await fetch_balance(session)
        rewards = await fetch_rewards(session)

    text = (
        f"{t(uid,'balance_title')}\n{sep()}\n"
        f"{t(uid,'wallet')}   : `{short_addr(WALLET_ADDR)}`\n"
        f"{t(uid,'balance_lbl')}  : `{balance}`\n"
        f"{t(uid,'rewards_lbl')} : `{rewards}`\n"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def cmd_rank(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(t(uid, "fetching"))
    async with aiohttp.ClientSession() as session:
        validators = await fetch_all_validators(session)

    if not validators:
        await update.message.reply_text(t(uid, "error_data"))
        return

    sorted_vals = sorted(validators, key=lambda v: int(v.get("tokens", 0)), reverse=True)
    rank = next((i + 1 for i, v in enumerate(sorted_vals) if v.get("operator_address") == VALIDATOR_ADDR), None)
    total = len(sorted_vals)

    text = (
        f"{t(uid,'rank_title')}\n{sep()}\n"
        f"{t(uid,'total_active')} : `{total}`\n"
        f"{t(uid,'your_rank')}    : `#{rank}`\n"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def cmd_activeset(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(t(uid, "fetching"))
    async with aiohttp.ClientSession() as session:
        all_vals_data = await get(session, f"{REST_URL}/cosmos/staking/v1beta1/validators?pagination.limit=500")
        my_val = await fetch_validator_info(session)

    if not all_vals_data or not my_val:
        await update.message.reply_text(t(uid, "error_data"))
        return

    all_vals = all_vals_data.get("validators", [])
    bonded = [v for v in all_vals if v.get("status") == "BOND_STATUS_BONDED"]
    bonded_sorted = sorted(bonded, key=lambda v: int(v.get("tokens", 0)))
    lowest_active_tokens = int(bonded_sorted[0]["tokens"]) if bonded_sorted else 0
    my_tokens = int(my_val.get("tokens", 0))
    in_active = my_val.get("status") == "BOND_STATUS_BONDED"

    if in_active:
        margin_rai = (my_tokens - lowest_active_tokens) / 1e18
        text = (
            f"{t(uid,'activeset_active_title')}\n{sep()}\n"
            f"📊 : {t(uid,'activeset_in')}\n"
            f"{t(uid,'active_count')} : `{len(bonded)}`\n"
            f"{t(uid,'my_stake')}     : `{my_tokens / 1e18:.2f} RAI`\n"
            f"{t(uid,'lowest_active')}: `{lowest_active_tokens / 1e18:.2f} RAI`\n"
            f"{t(uid,'safety_margin')}: `+{margin_rai:.2f} RAI`\n"
        )
    else:
        diff_rai = (lowest_active_tokens - my_tokens) / 1e18
        text = (
            f"{t(uid,'activeset_inactive_title')}\n{sep()}\n"
            f"📊 : {t(uid,'activeset_out')}\n"
            f"{t(uid,'active_count')}  : `{len(bonded)}`\n"
            f"{t(uid,'my_stake')}      : `{my_tokens / 1e18:.2f} RAI`\n"
            f"{t(uid,'needed_min')}    : `{lowest_active_tokens / 1e18:.2f} RAI`\n"
            f"{t(uid,'missing_amount')}: `{diff_rai:.2f} RAI`\n\n"
            f"{t(uid,'activeset_tip', diff=diff_rai)}"
        )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def cmd_uptime(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(t(uid, "fetching_long"))
    async with aiohttp.ClientSession() as session:
        signing_info = await fetch_signing_info(session)

    missed = 0
    if signing_info:
        missed = int(signing_info.get("missed_blocks_counter", 0))
    window = 10000
    signed = window - missed
    uptime = (signed / window) * 100
    bar = uptime_bar(uptime)

    text = (
        f"{t(uid,'uptime_title')}\n{sep()}\n"
        f"⬛ `[{bar}]`\n"
        f"{t(uid,'uptime_lbl')} : `{uptime:.2f}%`\n"
        f"{t(uid,'missed_lbl')} : `{missed}` blok\n"
        f"{t(uid,'window_lbl')} : {t(uid,'window_val')}\n"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def cmd_proposals(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(t(uid, "fetching"))
    async with aiohttp.ClientSession() as session:
        proposals = await fetch_proposals(session)

    if not proposals:
        await update.message.reply_text(t(uid, "no_proposals"))
        return

    text = f"{t(uid,'proposals_title')} ({len(proposals)})\n{sep()}\n\n"
    for p in proposals[:5]:
        pid   = p.get("proposal_id", "?")
        title = p.get("content", {}).get("title", t(uid, "no_title"))
        end   = p.get("voting_end_time", "")[:10]
        text += f"🔹 *#{pid}* — {title}\n   {t(uid,'proposal_end')}: `{end}`\n\n"

    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def cmd_rewards(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(t(uid, "fetching"))
    async with aiohttp.ClientSession() as session:
        rewards = await fetch_rewards(session)
        balance = await fetch_balance(session)

    text = (
        f"{t(uid,'rewards_title')}\n{sep()}\n"
        f"{t(uid,'balance_lbl')} : `{balance}`\n"
        f"{t(uid,'rewards_lbl')} : `{rewards}`\n"
        f"{t(uid,'time')} : `{datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}`"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def cmd_network(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(t(uid, "fetching"))
    async with aiohttp.ClientSession() as session:
        status = await get(session, f"{RPC_URL}/status")
        validators = await fetch_all_validators(session)

    if not status:
        await update.message.reply_text(t(uid, "error_rpc"))
        return

    sync = status.get("result", {}).get("sync_info", {})
    height      = sync.get("latest_block_height", "?")
    catching    = sync.get("catching_up", False)
    chain_id    = status.get("result", {}).get("node_info", {}).get("network", "?")
    total_power = sum(int(v.get("tokens", 0)) for v in validators)

    text = (
        f"{t(uid,'network_title')}\n{sep()}\n"
        f"{t(uid,'chain_id')}    : `{chain_id}`\n"
        f"{t(uid,'block')}        : `{int(height):,}`\n"
        f"🔄 Sync        : {t(uid,'catching') if catching else t(uid,'synced')}\n"
        f"{t(uid,'val_count_label')} : `{len(validators)}`\n"
        f"{t(uid,'total_power')} : `{total_power / 1e18:.0f} RAI`\n"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def cmd_delegators(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(t(uid, "fetching"))
    async with aiohttp.ClientSession() as session:
        delegators = await fetch_delegators(session, limit=10)

    if not delegators:
        await update.message.reply_text(t(uid, "error_data"))
        return

    sorted_d = sorted(
        delegators,
        key=lambda d: int(d.get("balance", {}).get("amount", 0)),
        reverse=True,
    )

    text = (
        f"{t(uid,'delegators_title')}\n{sep()}\n"
        f"{t(uid,'total_delegators')} : `{len(sorted_d)}`\n"
        f"{t(uid,'top_delegators', n=min(10, len(sorted_d)))}\n\n"
    )
    for i, d in enumerate(sorted_d[:10], 1):
        addr  = d.get("delegation", {}).get("delegator_address", "?")
        amount = int(d.get("balance", {}).get("amount", 0)) / 1e18
        text += f"`{i:>2}.` `{short_addr(addr)}` — `{amount:.2f} RAI`\n"

    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def cmd_slashing(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(t(uid, "fetching"))
    async with aiohttp.ClientSession() as session:
        params = await fetch_slashing_params(session)

    if not params:
        await update.message.reply_text(t(uid, "error_data"))
        return

    window       = params.get("signed_blocks_window", "?")
    min_signed   = float(params.get("min_signed_per_window", "0")) * 100
    downtime_dur = params.get("downtime_jail_duration", "?")
    slash_double = float(params.get("slash_fraction_double_sign", "0")) * 100
    slash_down   = float(params.get("slash_fraction_downtime", "0")) * 100
    tombstone    = params.get("tombstone", False)

    text = (
        f"{t(uid,'slashing_title')}\n{sep()}\n"
        f"{t(uid,'slash_window')}      : `{window}` blok\n"
        f"{t(uid,'slash_min_signed')}  : `{min_signed:.1f}%`\n"
        f"{t(uid,'slash_downtime_jail')}: `{downtime_dur}`\n"
        f"{t(uid,'slash_double_sign')} : `{slash_double:.2f}%`\n"
        f"{t(uid,'slash_downtime')}    : `{slash_down:.4f}%`\n"
        f"{t(uid,'slash_tombstone')}   : `{tombstone}`\n"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ─────────────────────────────────────────────
#  ALERT TASKS
# ─────────────────────────────────────────────
async def alert_governance(bot: Bot):
    global state
    logger.info("Governance alert started.")
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                proposals = await fetch_proposals(session)
            for p in proposals:
                pid = p.get("proposal_id")
                if pid and pid not in state["seen_proposals"]:
                    state["seen_proposals"].append(pid)
                    save_state(state)
                    title = p.get("content", {}).get("title", "N/A")
                    desc  = p.get("content", {}).get("description", "")[:200]
                    end   = p.get("voting_end_time", "")[:10]
                    text = (
                        f"🚨 *YENİ GOVERNANCE PROPOSAL!*\n"
                        f"🚨 *NEW GOVERNANCE PROPOSAL!*\n"
                        f"{sep()}\n"
                        f"🔹 ID     : `#{pid}`\n"
                        f"📋 Başlık / Title : *{title}*\n"
                        f"📝 Özet / Summary : _{desc}..._\n"
                        f"⏰ Bitiş / End    : `{end}`\n\n"
                        f"👉 `/proposals`"
                    )
                    await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Governance check error: {e}")
        await asyncio.sleep(GOVERNANCE_CHECK_INTERVAL)

async def alert_jail(bot: Bot):
    global state
    logger.info("Jail alert started.")
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                val = await fetch_validator_info(session)
            if val:
                jailed = val.get("jailed", False)
                if jailed and not state.get("last_jailed"):
                    state["last_jailed"] = True
                    save_state(state)
                    await bot.send_message(
                        chat_id=CHAT_ID,
                        text=(
                            f"🚨 *VALİDATOR JAILED! / VALIDATOR JAILED!*\n{sep()}\n"
                            f"📛 Moniker : `{MONIKER}`\n"
                            f"🔗 Adres   : `{short_addr(VALIDATOR_ADDR)}`\n\n"
                            "⚠️ Hemen unjail yapılması gerekiyor!\n"
                            "⚠️ Unjail is required immediately!"
                        ),
                        parse_mode=ParseMode.MARKDOWN,
                    )
                elif not jailed and state.get("last_jailed"):
                    state["last_jailed"] = False
                    save_state(state)
                    await bot.send_message(
                        chat_id=CHAT_ID,
                        text="✅ *Validator unjailed! / Validator unjailed başarılı!*",
                        parse_mode=ParseMode.MARKDOWN,
                    )
        except Exception as e:
            logger.error(f"Jail check error: {e}")
        await asyncio.sleep(VALIDATOR_CHECK_INTERVAL)

async def alert_active_set(bot: Bot):
    logger.info("Active set alert started.")
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                all_data = await get(session, f"{REST_URL}/cosmos/staking/v1beta1/validators?pagination.limit=500")
                my_val   = await fetch_validator_info(session)

            if all_data and my_val:
                bonded = [v for v in all_data.get("validators", []) if v.get("status") == "BOND_STATUS_BONDED"]
                bonded_sorted = sorted(bonded, key=lambda v: int(v.get("tokens", 0)))
                lowest = int(bonded_sorted[0]["tokens"]) if bonded_sorted else 0
                my_tokens = int(my_val.get("tokens", 0))
                margin = my_tokens - lowest

                if my_val.get("status") == "BOND_STATUS_BONDED" and margin < lowest * (ACTIVE_SET_MARGIN_PERCENT / 100):
                    await bot.send_message(
                        chat_id=CHAT_ID,
                        text=(
                            f"⚠️ *AKTİF SET UYARISI / ACTIVE SET WARNING!*\n{sep()}\n"
                            f"💎 Stake'in       : `{my_tokens / 1e18:.2f} RAI`\n"
                            f"📉 En Düşük Aktif : `{lowest / 1e18:.2f} RAI`\n"
                            f"🛡️ Marjın         : `{margin / 1e18:.2f} RAI`\n\n"
                            "⚠️ _Aktif setten düşme riskin var! / You risk falling out of the active set!_"
                        ),
                        parse_mode=ParseMode.MARKDOWN,
                    )
        except Exception as e:
            logger.error(f"Active set check error: {e}")
        await asyncio.sleep(ACTIVE_SET_CHECK_INTERVAL)

async def alert_uptime(bot: Bot):
    global state
    logger.info("Uptime alert started.")
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                signing_info = await fetch_signing_info(session)
            if signing_info:
                missed = int(signing_info.get("missed_blocks_counter", 0))
                uptime = ((10000 - missed) / 10000) * 100
                if uptime < UPTIME_ALERT_THRESHOLD and not state.get("uptime_alerted"):
                    state["uptime_alerted"] = True
                    save_state(state)
                    await bot.send_message(
                        chat_id=CHAT_ID,
                        text=(
                            f"🚨 *UPTIME UYARISI / UPTIME ALERT!*\n{sep()}\n"
                            f"📡 Uptime   : `{uptime:.2f}%`\n"
                            f"❌ Miss     : `{missed}` blok\n"
                            f"⚠️ Eşik / Threshold: `{UPTIME_ALERT_THRESHOLD}%`\n\n"
                            "⚠️ _Nodeunu kontrol et! / Check your node!_"
                        ),
                        parse_mode=ParseMode.MARKDOWN,
                    )
                elif uptime >= UPTIME_ALERT_THRESHOLD and state.get("uptime_alerted"):
                    state["uptime_alerted"] = False
                    save_state(state)
        except Exception as e:
            logger.error(f"Uptime check error: {e}")
        await asyncio.sleep(VALIDATOR_CHECK_INTERVAL)

# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
async def post_init(application: Application):
    bot = application.bot
    application.create_task(alert_governance(bot))
    application.create_task(alert_jail(bot))
    application.create_task(alert_active_set(bot))
    application.create_task(alert_uptime(bot))

def main():
    app = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start",      cmd_start))
    app.add_handler(CommandHandler("help",       cmd_start))
    app.add_handler(CommandHandler("lang",       cmd_lang))
    app.add_handler(CommandHandler("status",     cmd_status))
    app.add_handler(CommandHandler("balance",    cmd_balance))
    app.add_handler(CommandHandler("rank",       cmd_rank))
    app.add_handler(CommandHandler("activeset",  cmd_activeset))
    app.add_handler(CommandHandler("uptime",     cmd_uptime))
    app.add_handler(CommandHandler("proposals",  cmd_proposals))
    app.add_handler(CommandHandler("rewards",    cmd_rewards))
    app.add_handler(CommandHandler("network",    cmd_network))
    app.add_handler(CommandHandler("delegators", cmd_delegators))
    app.add_handler(CommandHandler("slashing",   cmd_slashing))
    app.add_handler(CallbackQueryHandler(callback_lang, pattern="^lang_"))

    logger.info("🤖 RAI Validator Bot started.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
