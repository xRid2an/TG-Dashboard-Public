# Created and developed by xRid2an

import os
import json
import logging
import asyncio
import re
import threading
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, CopyTextButton
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from telegram.constants import ParseMode
from telegram.error import Conflict, NetworkError, TelegramError

# Load environment variables
load_dotenv()

# Optional: Import web dashboard (akan jalan jika file ada)
try:
    from web_dashboard import run_dashboard
    DASHBOARD_AVAILABLE = True
except ImportError:
    DASHBOARD_AVAILABLE = False
    print("⚠️ Web dashboard tidak tersedia (file web_dashboard.py tidak ditemukan)")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── CONFIG ──────────────────────────────────────────────────────────────────
BOT_TOKEN    = os.getenv("BOT_TOKEN")
ADMIN_ID     = int(os.getenv("ADMIN_ID", "0"))
METHOD_GROUP = os.getenv("METHOD_GROUP", "https://t.me/placeholder")
OTP_GROUP    = os.getenv("OTP_GROUP", "https://t.me/placeholder")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in .env file")
if ADMIN_ID == 0:
    raise ValueError("ADMIN_ID not found in .env file")

SERVICE_LIST_DIR = Path("service_list")
DATA_FILE        = Path("data.json")
ADMIN_STATE: dict = {}

# ─── SERVICE ICONS & COLORS ───────────────────────────────────────────────────
SERVICE_ICONS = {
    "whatsapp": " ", "facebook": " ", "telegram": " ", "google": " ",
    "instagram": " ", "twitter": " ", "tiktok": " ", "linkedin": " ",
    "snapchat": " ", "netflix": " ", "spotify": " ", "amazon": " ",
    "shopee": " ", "default": " "
}

def get_service_icon(service_name: str) -> str:
    service_lower = service_name.lower().strip()
    for key, icon in SERVICE_ICONS.items():
        if key in service_lower:
            return icon
    return SERVICE_ICONS["default"]

# ─── COUNTRY FLAGS LENGKAP ───────────────────────────────────────────────────
COUNTRY_FLAGS = {
    # Asia Tenggara
    "indonesia": "🇮🇩", "malaysia": "🇲🇾", "singapore": "🇸🇬", "thailand": "🇹🇭",
    "vietnam": "🇻🇳", "philippines": "🇵🇭", "myanmar": "🇲🇲", "laos": "🇱🇦",
    "cambodia": "🇰🇭", "brunei": "🇧🇳", "timor leste": "🇹🇱",
    
    # Asia Timur
    "japan": "🇯🇵", "south korea": "🇰🇷", "china": "🇨🇳", "taiwan": "🇹🇼",
    "hong kong": "🇭🇰", "macau": "🇲🇴", "mongolia": "🇲🇳", "north korea": "🇰🇵",
    
    # Asia Selatan
    "india": "🇮🇳", "pakistan": "🇵🇰", "bangladesh": "🇧🇩", "sri lanka": "🇱🇰",
    "nepal": "🇳🇵", "bhutan": "🇧🇹", "maldives": "🇲🇻", "afghanistan": "🇦🇫",
    
    # Asia Barat (Timur Tengah)
    "turkey": "🇹🇷", "saudi arabia": "🇸🇦", "uae": "🇦🇪", "united arab emirates": "🇦🇪",
    "qatar": "🇶🇦", "kuwait": "🇰🇼", "bahrain": "🇧🇭", "oman": "🇴🇲",
    "yemen": "🇾🇪", "jordan": "🇯🇴", "lebanon": "🇱🇧", "syria": "🇸🇾",
    "iraq": "🇮🇶", "iran": "🇮🇷", "israel": "🇮🇱", "palestine": "🇵🇸",
    "cyprus": "🇨🇾", "armenia": "🇦🇲", "azerbaijan": "🇦🇿", "georgia": "🇬🇪",
    
    # Asia Tengah
    "kazakhstan": "🇰🇿", "uzbekistan": "🇺🇿", "turkmenistan": "🇹🇲",
    "kyrgyzstan": "🇰🇬", "tajikistan": "🇹🇯",
    
    # Eropa Barat
    "uk": "🇬🇧", "united kingdom": "🇬🇧", "england": "🇬🇧", "great britain": "🇬🇧",
    "germany": "🇩🇪", "france": "🇫🇷", "netherlands": "🇳🇱", "belgium": "🇧🇪",
    "austria": "🇦🇹", "switzerland": "🇨🇭", "luxembourg": "🇱🇺", "ireland": "🇮🇪",
    "monaco": "🇲🇨", "liechtenstein": "🇱🇮",
    
    # Eropa Utara
    "sweden": "🇸🇪", "norway": "🇳🇴", "denmark": "🇩🇰", "finland": "🇫🇮",
    "iceland": "🇮🇸", "estonia": "🇪🇪", "latvia": "🇱🇻", "lithuania": "🇱🇹",
    
    # Eropa Selatan
    "italy": "🇮🇹", "spain": "🇪🇸", "portugal": "🇵🇹", "greece": "🇬🇷",
    "croatia": "🇭🇷", "serbia": "🇷🇸", "slovenia": "🇸🇮", "slovakia": "🇸🇰",
    "bosnia": "🇧🇦", "bosnia and herzegovina": "🇧🇦", "montenegro": "🇲🇪",
    "albania": "🇦🇱", "north macedonia": "🇲🇰", "kosovo": "🇽🇰", "malta": "🇲🇹",
    "andorra": "🇦🇩", "san marino": "🇸🇲", "vatican": "🇻🇦",
    
    # Eropa Timur
    "russia": "🇷🇺", "poland": "🇵🇱", "czechia": "🇨🇿", "czech republic": "🇨🇿",
    "hungary": "🇭🇺", "romania": "🇷🇴", "bulgaria": "🇧🇬", "ukraine": "🇺🇦",
    "belarus": "🇧🇾", "moldova": "🇲🇩",
    
    # Amerika Utara
    "usa": "🇺🇸", "united states": "🇺🇸", "america": "🇺🇸", "canada": "🇨🇦",
    "mexico": "🇲🇽", "greenland": "🇬🇱",
    
    # Amerika Tengah & Karibia
    "guatemala": "🇬🇹", "belize": "🇧🇿", "honduras": "🇭🇳", "el salvador": "🇸🇻",
    "nicaragua": "🇳🇮", "costa rica": "🇨🇷", "panama": "🇵🇦",
    "cuba": "🇨🇺", "jamaica": "🇯🇲", "haiti": "🇭🇹", "dominican republic": "🇩🇴",
    "puerto rico": "🇵🇷", "bahamas": "🇧🇸", "trinidad": "🇹🇹", "barbados": "🇧🇧",
    
    # Amerika Selatan
    "brazil": "🇧🇷", "argentina": "🇦🇷", "chile": "🇨🇱", "peru": "🇵🇪",
    "colombia": "🇨🇴", "venezuela": "🇻🇪", "ecuador": "🇪🇨", "bolivia": "🇧🇴",
    "paraguay": "🇵🇾", "uruguay": "🇺🇾", "guyana": "🇬🇾", "suriname": "🇸🇷",
    "french guiana": "🇬🇫",
    
    # Afrika Utara
    "egypt": "🇪🇬", "morocco": "🇲🇦", "algeria": "🇩🇿", "tunisia": "🇹🇳",
    "libya": "🇱🇾", "sudan": "🇸🇩", "south sudan": "🇸🇸", "mauritania": "🇲🇷",
    
    # Afrika Barat
    "nigeria": "🇳🇬", "ghana": "🇬🇭", "ivory coast": "🇨🇮", "cote d'ivoire": "🇨🇮",
    "senegal": "🇸🇳", "mali": "🇲🇱", "burkina faso": "🇧🇫", "benin": "🇧🇯",
    "guinea": "🇬🇳", "sierra leone": "🇸🇱", "liberia": "🇱🇷", "gambia": "🇬🇲",
    "togo": "🇹🇬", "niger": "🇳🇪", "cameroon": "🇨🇲", "cape verde": "🇨🇻",
    
    # Afrika Tengah
    "congo": "🇨🇬", "drc": "🇨🇩", "democratic republic of congo": "🇨🇩",
    "angola": "🇦🇴", "chad": "🇹🇩", "gabon": "🇬🇦", "equatorial guinea": "🇬🇶",
    "central african republic": "🇨🇫", "rwanda": "🇷🇼", "burundi": "🇧🇮",
    
    # Afrika Timur
    "kenya": "🇰🇪", "tanzania": "🇹🇿", "uganda": "🇺🇬", "ethiopia": "🇪🇹",
    "somalia": "🇸🇴", "djibouti": "🇩🇯", "eritrea": "🇪🇷", "mozambique": "🇲🇿",
    "madagascar": "🇲🇬", "comoros": "🇰🇲", "mauritius": "🇲🇺", "seychelles": "🇸🇨",
    
    # Afrika Selatan
    "south africa": "🇿🇦", "namibia": "🇳🇦", "botswana": "🇧🇼", "zimbabwe": "🇿🇼",
    "zambia": "🇿🇲", "malawi": "🇲🇼", "lesotho": "🇱🇸", "eswatini": "🇸🇿",
    
    # Oceania
    "australia": "🇦🇺", "new zealand": "🇳🇿", "papua new guinea": "🇵🇬",
    "fiji": "🇫🇯", "solomon islands": "🇸🇧", "vanuatu": "🇻🇺", "samoa": "🇼🇸",
    "tonga": "🇹🇴", "micronesia": "🇫🇲", "marshall islands": "🇲🇭", "palau": "🇵🇼",
    "nauru": "🇳🇷", "kiribati": "🇰🇮", "tuvalu": "🇹🇻",
}

def get_country_flag(country_name: str) -> str:
    """Mendapatkan flag dari nama negara dengan pencarian cerdas"""
    if not country_name:
        return "🌍"
    
    key = country_name.strip().lower()
    
    # Coba cari exact match
    if key in COUNTRY_FLAGS:
        return COUNTRY_FLAGS[key]
    
    # Hapus kata-kata umum
    key_clean = key.replace("the ", "").replace("republic of ", "").replace("kingdom of ", "")
    if key_clean in COUNTRY_FLAGS:
        return COUNTRY_FLAGS[key_clean]
    
    # Coba partial match
    for name, flag in COUNTRY_FLAGS.items():
        if name in key or key in name:
            return flag
    
    return "🌍"
    
def clean_country_name(raw_name: str) -> str:
    name = raw_name.replace('.txt', '')
    patterns = [r'[A-Z]{2,}-\d+-\d{4}-\d{2}-\d{2}', r'[A-Z]{2,}-\d+', r'\d{4}-\d{2}-\d{2}', r'-\d+$']
    for pattern in patterns:
        name = re.sub(pattern, '', name)
    name = re.sub(r'^[-_\s]+|[-_\s]+$', '', name)
    name = re.sub(r'[^A-Za-z\s]', '', name)
    return name.split()[0].title() if name.strip() else "Unknown"

def mask_number(number: str) -> str:
    number = number.strip()
    return number[:4] + "****" + number[-4:] if len(number) > 6 else number

# ─── DATA HELPERS ─────────────────────────────────────────────────────────────
def load_data() -> dict:
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}, "muted": {}, "notifications": [], "service_enabled": True, "numbers_per_view": 6, "button_columns": 2}

def save_data(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(data: dict, uid: int) -> dict:
    uid = str(uid)
    if uid not in data["users"]:
        data["users"][uid] = {
            "first_seen": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "total_seen": 0, "seen_numbers": [], "last_3": [],
            "last_24h_seen": [], "last_file": None, "last_service": None,
            "last_country": None, "username": "", "full_name": ""
        }
    return data["users"][uid]

def touch_user(data: dict, update: Update):
    u = update.effective_user
    user = get_user(data, u.id)
    user["last_active"] = datetime.now().isoformat()
    user["username"] = u.username or ""
    user["full_name"] = u.full_name or ""
    save_data(data)

def count_numbers_in_file(fpath: Path) -> int:
    if not fpath.exists(): return 0
    lines = [l.strip() for l in fpath.read_text(encoding="utf-8", errors="ignore").splitlines() if l.strip()]
    return len(lines)

def count_numbers_in_folder(folder: Path) -> int:
    return sum(count_numbers_in_file(f) for f in folder.glob("*.txt")) if folder.exists() else 0

def get_service_folders():
    return sorted([f for f in SERVICE_LIST_DIR.iterdir() if f.is_dir()], key=lambda x: x.name) if SERVICE_LIST_DIR.exists() else []

def get_country_files(service_folder: Path):
    files = [f for f in service_folder.glob("*.txt") if clean_country_name(f.stem) != "Unknown"]
    return sorted(files, key=lambda x: x.stem)

def get_available_services():
    """Hanya kembalikan layanan yang memiliki stok > 0"""
    available = []
    for folder in get_service_folders():
        total = count_numbers_in_folder(folder)
        if total > 0:
            available.append((folder, total))
    return available

def get_next_numbers(data: dict, uid: int, service: str, country: str, service_folder: Path, n: int = 6):
    fpath = service_folder / f"{country}.txt"
    if not fpath.exists():
        for f in service_folder.glob("*.txt"):
            if clean_country_name(f.stem) == country:
                fpath = f
                break
    if not fpath.exists(): return []
    
    lines = [l.strip() for l in fpath.read_text(encoding="utf-8", errors="ignore").splitlines() if l.strip()]
    user = get_user(data, uid)
    seen = set(num["number"] for num in user.get("seen_numbers", []) if num.get("service") == service and num.get("country") == country)
    available = [l for l in lines if l not in seen]
    return available[:n]

def mark_numbers_seen(data: dict, uid: int, service: str, country: str, numbers: list):
    user = get_user(data, uid)
    now = datetime.now().isoformat()
    for num in numbers:
        user["seen_numbers"].append({"number": num, "service": service, "country": country, "at": now})
        user["last_24h_seen"].append({"number": num, "at": now})
    user["last_3"] = [{"number": n, "service": service, "country": country} for n in numbers]
    user["total_seen"] += len(numbers)
    user["last_file"] = country
    user["last_service"] = service
    user["last_country"] = country
    save_data(data)

def is_muted(data: dict, uid: int) -> bool:
    uid_str = str(uid)
    mute_info = data.get("muted", {}).get(uid_str)
    if not mute_info: return False
    if mute_info.get("permanent"): return True
    until = mute_info.get("until")
    return until and datetime.fromisoformat(until) > datetime.now()

def get_remaining_stock(data: dict, uid: int, service: str, country: str) -> tuple:
    folder = SERVICE_LIST_DIR / service
    fpath = folder / f"{country}.txt"
    if not fpath.exists():
        for f in folder.glob("*.txt"):
            if clean_country_name(f.stem) == country:
                fpath = f
                break
    total = count_numbers_in_file(fpath)
    user = get_user(data, uid)
    seen = len([num for num in user.get("seen_numbers", []) if num.get("service") == service and num.get("country") == country])
    return total, seen, total - seen

# ─── KEYBOARDS ───────────────────────────────────────────────────────────────
def main_menu_kb(is_admin: bool):
    rows = [[InlineKeyboardButton("📊 DASHBOARD", callback_data="user_dashboard")]]
    rows.append([InlineKeyboardButton("📂 SERVICE LIST", callback_data="user_service_list")])
    if is_admin:
        rows.append([InlineKeyboardButton("⚙️ ADMIN PANEL", callback_data="admin_main")])
    return InlineKeyboardMarkup(rows)

def admin_panel_kb():
    data = load_data()
    notif_count = len([n for n in data.get("notifications", []) if not n.get("seen")])
    notif_label = f"📢 NOTIFICATIONS ({notif_count})" if notif_count else "📢 NOTIFICATIONS"
    rows = [
        [InlineKeyboardButton("📊 DASHBOARD", callback_data="admin_dashboard")],
        [InlineKeyboardButton("📂 SERVICE LIST", callback_data="admin_service_list")],
        [InlineKeyboardButton("➕ ADD NUMBERS", callback_data="admin_add_numbers"), InlineKeyboardButton("❌ REMOVE NUMBERS", callback_data="admin_remove_numbers")],
        [InlineKeyboardButton("📢 BROADCAST", callback_data="admin_broadcast")],
        [InlineKeyboardButton("👤 USER DETAILS", callback_data="admin_user_details")],
        [InlineKeyboardButton("🔇 MUTE USER", callback_data="admin_mute"), InlineKeyboardButton("🔊 UNMUTE USER", callback_data="admin_unmute")],
        [InlineKeyboardButton(notif_label, callback_data="admin_notifications")],
        [InlineKeyboardButton("⚙️ SETTINGS", callback_data="admin_settings")],
        [InlineKeyboardButton("◀️ BACK TO USER", callback_data="user_main")],
    ]
    return InlineKeyboardMarkup(rows)

def back_kb(target: str, label: str = "◀️ BACK"):
    return InlineKeyboardMarkup([[InlineKeyboardButton(label, callback_data=target)]])

# ─── COMMAND HANDLERS ────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    uid = update.effective_user.id
    touch_user(data, update)
    if is_muted(data, uid):
        await update.message.reply_text(
            "⛔ Anda tidak dapat menggunakan bot ini.\n\nKirim permintaan unmute ke admin:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📨 SEND UNMUTE REQUEST", callback_data="send_unmute_request")]]))
        return
    await update.message.reply_text(
        f"👋 Selamat datang, {update.effective_user.first_name}!",
        reply_markup=main_menu_kb(uid == ADMIN_ID))

async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Akses ditolak.")
        return
    await update.message.reply_text("⚙️ ADMIN PANEL:", reply_markup=admin_panel_kb())

# ─── USER PANEL CALLBACKS ────────────────────────────────────────────────────
async def user_dashboard(query, context):
    data = load_data()
    uid = query.from_user.id
    
    user_data = get_user(data, uid)
    total_seen = user_data.get("total_seen", 0)
    last_24h = len([s for s in user_data.get("last_24h_seen", []) if datetime.fromisoformat(s["at"]) > datetime.now() - timedelta(hours=24)])
    
    total_stok = sum(count_numbers_in_folder(f) for f in get_service_folders())
    
    service_progress = []
    for folder in get_service_folders():
        service_name = folder.name
        total_service = count_numbers_in_folder(folder)
        seen_service = len([s for s in user_data.get("seen_numbers", []) if s.get("service") == service_name])
        if total_service > 0:
            percent = (seen_service / total_service) * 100
            service_progress.append(f"{get_service_icon(service_name)} {service_name}: {seen_service}/{total_service} ({percent:.0f}%)")
    
    progress_text = "\n".join(service_progress[:5]) if service_progress else "Belum ada aktivitas"
    
    message = f"""📊 *USER DASHBOARD*

👤 *Profil Anda:*

• Total nomor dilihat: *{total_seen}*
• Aktivitas 24 jam: *{last_24h}*
• Total stok sistem: *{total_stok}*

📈 *Progres per Layanan:*
{progress_text}

💡 *Tips:* Setiap nomor hanya bisa dilihat sekali!
"""
    await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=back_kb("user_main"))

async def user_service_list(query, context):
    data = load_data()
    uid = query.from_user.id

    if is_muted(data, uid):
        await query.edit_message_text("⛔ Anda tidak dapat menggunakan bot ini.", reply_markup=back_kb("user_main"))
        return

    if not data.get("service_enabled", True):
        await query.edit_message_text("⚠️ Service List sedang dinonaktifkan.", reply_markup=back_kb("user_main"))
        return
    
    available_services = get_available_services()
    
    if not available_services:
        await query.edit_message_text(
            "📭 *TIDAK ADA LAYANAN*\n\nMaaf, saat ini tidak ada layanan yang tersedia.\nSilakan cek kembali nanti.",
            parse_mode=ParseMode.MARKDOWN, reply_markup=back_kb("user_main")
        )
        return
    
    rows = []
    for folder, total in available_services:
        icon = get_service_icon(folder.name)
        rows.append([InlineKeyboardButton(f"{icon} {folder.name.upper()} ({total})", callback_data=f"user_country_list:{folder.name}")])
    
    rows.append([InlineKeyboardButton("◀️ BACK", callback_data="user_main")])
    
    await query.edit_message_text(
        f"🎨 *LAYANAN TERSEDIA*\n\nTersedia {len(available_services)} layanan dengan total {sum(t for _, t in available_services)} nomor.\nKlik tombol di bawah 👇",
        parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(rows)
    )

async def user_country_list(query, context, service_name: str):
    data = load_data()
    uid = query.from_user.id

    if is_muted(data, uid):
        await query.edit_message_text("⛔ Anda tidak dapat menggunakan bot ini.", reply_markup=back_kb("user_main"))
        return

    folder = SERVICE_LIST_DIR / service_name
    files = get_country_files(folder)

    if not files:
        await query.edit_message_text(f"📂 *{service_name.upper()}*\n\nTidak ada file tersedia.", parse_mode=ParseMode.MARKDOWN, reply_markup=back_kb("user_service_list"))
        return

    keyboard = []
    for f in files:
        country = clean_country_name(f.stem)
        total, seen, remaining = get_remaining_stock(data, uid, service_name, country)
        flag = get_country_flag(country)
        
        if remaining > 0:
            button_text = f"{flag} {country} ✅ ({remaining}/{total})"
        else:
            button_text = f"{flag} {country} ⚠️ (Habis)"
        
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"user_numbers:{service_name}:{country}")])
    
    keyboard.append([InlineKeyboardButton("◀️ BACK TO SERVICES", callback_data="user_service_list")])
    
    await query.edit_message_text(
        f"🌍 *{service_name.upper()} - DAFTAR NEGARA*\n\nKlik negara untuk melihat nomor 👇",
        parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def user_numbers(query, context, service_name: str, country: str):
    data = load_data()
    uid = query.from_user.id

    if is_muted(data, uid):
        await query.edit_message_text("⛔ Anda tidak dapat menggunakan bot ini.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📨 SEND UNMUTE REQUEST", callback_data="send_unmute_request")]]))
        return

    n = data.get("numbers_per_view", 6)
    folder = SERVICE_LIST_DIR / service_name
    numbers = get_next_numbers(data, uid, service_name, country, folder, n)

    total, seen, remaining = get_remaining_stock(data, uid, service_name, country)

    if not numbers:
        await query.edit_message_text(
            f"✅ *{service_name} › {country}*\n\n✨ *SELAMAT!* ✨\n\nAnda telah melihat semua nomor!\n\nTotal dilihat: *{seen}/{total}*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ BACK", callback_data=f"user_country_list:{service_name}")],
                [InlineKeyboardButton("💬 METHOD GROUP", url=METHOD_GROUP), InlineKeyboardButton("🔐 OTP GROUP", url=OTP_GROUP)],
            ])
        )
        return

    mark_numbers_seen(data, uid, service_name, country, numbers)
    
    flag = get_country_flag(country)
    icon = get_service_icon(service_name)
    
    def fmt_num(n): return f"+{n.strip()}" if not n.strip().startswith("+") else n.strip()
    formatted = [fmt_num(num) for num in numbers]
    cols_per_row = data.get("button_columns", 2)

    # Buat tombol nomor
    num_rows = []
    temp_row = []
    for num in formatted:
        masked = mask_number(num)
        btn = InlineKeyboardButton(text=f"{icon} {flag} {masked}", copy_text=CopyTextButton(text=num))
        temp_row.append(btn)
        if len(temp_row) == cols_per_row:
            num_rows.append(temp_row)
            temp_row = []
    if temp_row:
        num_rows.append(temp_row)
    
    # Tombol kontrol
    control_buttons = [
        [InlineKeyboardButton("🔄 Change Number", callback_data=f"user_refresh:{service_name}:{country}"),
         InlineKeyboardButton("➕ Add Prefix", callback_data=f"add_prefix:{service_name}:{country}")],
        [InlineKeyboardButton("🌍 Other Countries", callback_data=f"user_country_list:{service_name}"),
         InlineKeyboardButton("❌ Close", callback_data="user_main")],
    ]
    
    group_row = [InlineKeyboardButton("💬 METHOD GROUP", url=METHOD_GROUP), InlineKeyboardButton("🔐 OTP GROUP", url=OTP_GROUP)]
    
    status_emoji = "✅" if remaining > 0 else "⚠️"
    await query.edit_message_text(
        f"{icon} *{service_name.upper()} › {country}*\n\n"
        f"Klik tombol untuk menyalin nomor 👇\n\n"
        f"{status_emoji} *Stok tersisa: {remaining}/{total}*\n\n"
        f"✨ *Setiap nomor hanya bisa dilihat sekali!*",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(num_rows + control_buttons + [group_row])
    )

async def user_refresh(query, context, service_name: str, country: str):
    await user_numbers(query, context, service_name, country)

async def add_prefix_handler(query, context, service_name: str, country: str):
    await query.edit_message_text(
        f"✏️ *ADD PREFIX - {service_name.upper()} › {country}*\n\n"
        f"Fitur ini akan segera hadir!\n\n"
        f"Saat ini Anda bisa langsung klik nomor untuk menyalin.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=back_kb(f"user_country_list:{service_name}")
    )

async def send_unmute_request(query, context):
    data = load_data()
    uid = query.from_user.id
    user = query.from_user
    data.setdefault("notifications", []).append({
        "type": "unmute_request", "uid": uid, "username": user.username or "",
        "full_name": user.full_name or "", "at": datetime.now().isoformat(), "seen": False
    })
    save_data(data)
    await query.edit_message_text("📨 Permintaan unmute telah dikirim ke admin.", reply_markup=back_kb("user_main"))

# ─── ADMIN PANEL CALLBACKS ───────────────────────────────────────────────────
async def admin_dashboard(query, context):
    data = load_data()
    lines = ["📊 *ADMIN DASHBOARD*\n" + "=" * 20 + "\n"]
    for folder in get_service_folders():
        total = count_numbers_in_folder(folder)
        seen = sum(1 for u in data["users"].values() for n in u.get("seen_numbers", []) if n.get("service") == folder.name)
        lines.append(f"{get_service_icon(folder.name)} {folder.name}: {seen}/{total} seen, {total-seen} left")
    lines.extend([f"\n👥 Total Users: {len(data['users'])}", f"🔇 Muted Users: {len(data.get('muted', {}))}"])
    await query.edit_message_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN, reply_markup=back_kb("admin_main"))

async def admin_service_list_view(query, context):
    rows = []
    for folder in get_service_folders():
        total = count_numbers_in_folder(folder)
        rows.append([InlineKeyboardButton(f"📂 {folder.name} ({total})", callback_data=f"admin_country_view:{folder.name}")])
    rows.append([InlineKeyboardButton("◀️ BACK", callback_data="admin_main")])
    await query.edit_message_text("📂 SERVICE LIST", reply_markup=InlineKeyboardMarkup(rows))

async def admin_country_view(query, context, service_name: str):
    data = load_data()
    folder = SERVICE_LIST_DIR / service_name
    rows = []
    for f in get_country_files(folder):
        country = clean_country_name(f.stem)
        total = count_numbers_in_file(f)
        seen = sum(1 for u in data["users"].values() for n in u.get("seen_numbers", []) if n.get("service") == service_name and n.get("country") == country)
        flag = get_country_flag(country)
        rows.append([InlineKeyboardButton(f"{flag} {country}: {seen}/{total}", callback_data="noop")])
    rows.append([InlineKeyboardButton("◀️ BACK", callback_data="admin_service_list")])
    await query.edit_message_text(f"🌍 {service_name} - COUNTRIES", reply_markup=InlineKeyboardMarkup(rows))

async def admin_add_numbers_start(query, context):
    rows = [[InlineKeyboardButton(f"📂 {folder.name}", callback_data=f"admin_add_pick_country:{folder.name}")] for folder in get_service_folders()]
    rows.append([InlineKeyboardButton("◀️ BACK", callback_data="admin_main")])
    await query.edit_message_text("➕ ADD NUMBERS - Pilih service:", reply_markup=InlineKeyboardMarkup(rows))

async def admin_add_pick_country(query, context, service_name: str):
    ADMIN_STATE.clear()
    ADMIN_STATE["add_service"] = service_name
    ADMIN_STATE["state"] = "awaiting_add_file"
    await query.edit_message_text(f"📁 Kirim file .txt untuk {service_name}:", reply_markup=back_kb("admin_add_numbers"))

async def admin_remove_numbers_start(query, context):
    rows = [[InlineKeyboardButton(f"📂 {folder.name}", callback_data=f"admin_remove_pick_country:{folder.name}")] for folder in get_service_folders()]
    rows.append([InlineKeyboardButton("◀️ BACK", callback_data="admin_main")])
    await query.edit_message_text("❌ REMOVE NUMBERS - Pilih service:", reply_markup=InlineKeyboardMarkup(rows))

async def admin_remove_pick_country(query, context, service_name: str):
    folder = SERVICE_LIST_DIR / service_name
    rows = []
    for f in get_country_files(folder):
        country = clean_country_name(f.stem)
        total = count_numbers_in_file(f)
        flag = get_country_flag(country)
        rows.append([InlineKeyboardButton(f"🗑 {flag} {country} ({total})", callback_data=f"admin_remove_confirm:{service_name}:{country}")])
    rows.append([InlineKeyboardButton("◀️ BACK", callback_data="admin_remove_numbers")])
    await query.edit_message_text(f"🗑 {service_name} - Pilih file:", reply_markup=InlineKeyboardMarkup(rows))

async def admin_remove_confirm(query, context, service_name: str, country: str):
    folder = SERVICE_LIST_DIR / service_name
    for f in folder.glob("*.txt"):
        if clean_country_name(f.stem) == country:
            f.unlink()
            break
    await query.edit_message_text(f"✅ {country} telah dihapus.", reply_markup=back_kb("admin_main"))

async def admin_broadcast_start(query, context):
    ADMIN_STATE.clear()
    ADMIN_STATE["state"] = "awaiting_broadcast"
    await query.edit_message_text("📢 Kirim pesan broadcast:", reply_markup=back_kb("admin_main"))

async def admin_user_details_start(query, context):
    ADMIN_STATE.clear()
    ADMIN_STATE["state"] = "awaiting_user_details_input"
    await query.edit_message_text("🔍 Masukkan User ID:", reply_markup=back_kb("admin_main"))

async def admin_mute_start(query, context):
    ADMIN_STATE.clear()
    ADMIN_STATE["state"] = "awaiting_mute_id"
    await query.edit_message_text("🔇 Masukkan User ID untuk mute:", reply_markup=back_kb("admin_main"))

async def admin_unmute_start(query, context):
    ADMIN_STATE.clear()
    ADMIN_STATE["state"] = "awaiting_unmute_id"
    await query.edit_message_text("🔊 Masukkan User ID untuk unmute:", reply_markup=back_kb("admin_main"))

async def admin_notifications_view(query, context):
    data = load_data()
    notifs = [n for n in data.get("notifications", []) if n.get("type") == "unmute_request"]
    for n in notifs:
        n["seen"] = True
    save_data(data)
    if not notifs:
        await query.edit_message_text("📭 Tidak ada notifikasi.", reply_markup=back_kb("admin_main"))
        return
    rows = []
    for n in notifs[-20:]:
        rows.append([InlineKeyboardButton(f"👤 {n['full_name']} (ID: {n['uid']})", callback_data="noop")])
        rows.append([InlineKeyboardButton("🔊 UNMUTE", callback_data=f"admin_do_unmute_notif:{n['uid']}")])
    rows.append([InlineKeyboardButton("◀️ BACK", callback_data="admin_main")])
    await query.edit_message_text("📢 UNMUTE REQUESTS:", reply_markup=InlineKeyboardMarkup(rows))

async def admin_do_unmute_notif(query, context, uid: int):
    data = load_data()
    data["muted"].pop(str(uid), None)
    save_data(data)
    try:
        await context.bot.send_message(uid, "✅ Anda telah di-unmute.")
    except:
        pass
    await query.edit_message_text(f"✅ User {uid} telah di-unmute.", reply_markup=back_kb("admin_main"))

async def admin_settings(query, context):
    data = load_data()
    enabled = data.get("service_enabled", True)
    n_count = data.get("numbers_per_view", 6)
    cols = data.get("button_columns", 2)
    status = "✅ ON" if enabled else "❌ OFF"
    rows = [
        [InlineKeyboardButton(f"⚙️ SERVICE LIST: {status}", callback_data="admin_toggle_service")],
        [InlineKeyboardButton(f"🔢 NUMBERS PER VIEW: {n_count}", callback_data="admin_set_number_count")],
        [InlineKeyboardButton(f"🔘 BUTTON COLUMNS: {cols}", callback_data="admin_set_button_columns")],
        [InlineKeyboardButton("◀️ BACK", callback_data="admin_main")],
    ]
    await query.edit_message_text("⚙️ SETTINGS:", reply_markup=InlineKeyboardMarkup(rows))

async def admin_toggle_service(query, context):
    data = load_data()
    data["service_enabled"] = not data.get("service_enabled", True)
    save_data(data)
    await admin_settings(query, context)

async def admin_set_number_count(query, context):
    ADMIN_STATE.clear()
    ADMIN_STATE["state"] = "awaiting_number_count"
    await query.edit_message_text("🔢 Masukkan jumlah nomor per tampilan (1-20):", reply_markup=back_kb("admin_settings"))

async def admin_set_button_columns(query, context):
    ADMIN_STATE.clear()
    ADMIN_STATE["state"] = "awaiting_button_columns"
    await query.edit_message_text("🔘 Masukkan jumlah kolom tombol (1-4):", reply_markup=back_kb("admin_settings"))

# ─── MESSAGE HANDLER ─────────────────────────────────────────────────────────
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = ADMIN_STATE.get("state")
    uid = update.effective_user.id
    data = load_data()

    if uid == ADMIN_ID:
        if state == "awaiting_broadcast":
            ADMIN_STATE.clear()
            users = list(data["users"].keys())
            success, failed = 0, 0
            for u_id in users:
                try:
                    await update.message.copy_to(chat_id=int(u_id))
                    success += 1
                    await asyncio.sleep(0.05)
                except:
                    failed += 1
            await update.message.reply_text(f"✅ Broadcast selesai!\n\n📤 Terkirim: {success}\n❌ Gagal: {failed}", reply_markup=back_kb("admin_main"))
            return

        if state == "awaiting_add_file" and update.message.document:
            service = ADMIN_STATE.get("add_service")
            doc = update.message.document
            fname = doc.file_name or "upload.txt"
            if not fname.endswith(".txt"):
                await update.message.reply_text("❌ Hanya file .txt yang diterima.")
                return
            folder = SERVICE_LIST_DIR / service
            folder.mkdir(parents=True, exist_ok=True)
            fpath = folder / fname
            tg_file = await doc.get_file()
            await tg_file.download_to_drive(str(fpath))
            total = count_numbers_in_file(fpath)
            ADMIN_STATE.clear()
            await update.message.reply_text(f"✅ File ditambahkan!\n📂 {service}\n📄 {fname}\n🔢 Total: {total} nomor", reply_markup=back_kb("admin_main"))
            return

        if state == "awaiting_mute_id":
            ADMIN_STATE.clear()
            try:
                target_id = int(update.message.text.strip())
                data.setdefault("muted", {})[str(target_id)] = {"permanent": True, "at": datetime.now().isoformat()}
                save_data(data)
                await update.message.reply_text(f"✅ User {target_id} telah di-mute.", reply_markup=back_kb("admin_main"))
            except ValueError:
                await update.message.reply_text("❌ ID tidak valid.", reply_markup=back_kb("admin_main"))
            return

        if state == "awaiting_unmute_id":
            ADMIN_STATE.clear()
            try:
                target_id = int(update.message.text.strip())
                data.setdefault("muted", {}).pop(str(target_id), None)
                save_data(data)
                try:
                    await context.bot.send_message(target_id, "✅ Anda telah di-unmute.")
                except:
                    pass
                await update.message.reply_text(f"✅ User {target_id} telah di-unmute.", reply_markup=back_kb("admin_main"))
            except ValueError:
                await update.message.reply_text("❌ ID tidak valid.", reply_markup=back_kb("admin_main"))
            return

        if state == "awaiting_user_details_input":
            ADMIN_STATE.clear()
            try:
                target_id = str(int(update.message.text.strip()))
                if target_id in data["users"]:
                    u = data["users"][target_id]
                    days_used = (datetime.now() - datetime.fromisoformat(u["first_seen"])).days
                    text = f"👤 *USER DETAILS*\n\n📛 Name: {u.get('full_name', 'N/A')}\n🆔 ID: {target_id}\n📅 Member since: {days_used} hari\n👁️ Total seen: {u.get('total_seen', 0)}\n🔢 Last 3: {', '.join([n['number'] for n in u.get('last_3', [])]) or 'None'}"
                    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=back_kb("admin_main"))
                else:
                    await update.message.reply_text("❌ User tidak ditemukan.", reply_markup=back_kb("admin_main"))
            except ValueError:
                await update.message.reply_text("❌ ID tidak valid.", reply_markup=back_kb("admin_main"))
            return

        if state == "awaiting_number_count":
            ADMIN_STATE.clear()
            try:
                n = int(update.message.text.strip())
                if n < 1 or n > 20:
                    raise ValueError
                data["numbers_per_view"] = n
                save_data(data)
                await update.message.reply_text(f"✅ Setiap tampilan akan menampilkan {n} nomor.", reply_markup=back_kb("admin_settings"))
            except ValueError:
                await update.message.reply_text("❌ Masukkan angka yang valid (1-20).", reply_markup=back_kb("admin_settings"))
            return

        if state == "awaiting_button_columns":
            ADMIN_STATE.clear()
            try:
                cols = int(update.message.text.strip())
                if cols < 1 or cols > 4:
                    raise ValueError
                data["button_columns"] = cols
                save_data(data)
                await update.message.reply_text(f"✅ Tombol akan ditampilkan dalam {cols} kolom.", reply_markup=back_kb("admin_settings"))
            except ValueError:
                await update.message.reply_text("❌ Masukkan angka yang valid (1-4).", reply_markup=back_kb("admin_settings"))
            return

    if is_muted(data, uid):
        await update.message.reply_text("⛔ Anda tidak dapat menggunakan bot ini.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📨 SEND UNMUTE REQUEST", callback_data="send_unmute_request")]]))
        return
    touch_user(data, update)

# ─── CALLBACK ROUTER ─────────────────────────────────────────────────────────
async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data_str = query.data
    uid = query.from_user.id
    data = load_data()

    if data_str == "noop":
        return

    # User panel
    if data_str == "user_main":
        await query.edit_message_text("🏠 *MAIN MENU*", parse_mode=ParseMode.MARKDOWN, reply_markup=main_menu_kb(uid == ADMIN_ID))
        return
    if data_str == "user_dashboard":
        await user_dashboard(query, context)
        return
    if data_str == "user_service_list":
        await user_service_list(query, context)
        return
    if data_str.startswith("user_country_list:"):
        await user_country_list(query, context, data_str.split(":", 1)[1])
        return
    if data_str.startswith("user_numbers:"):
        _, svc, country = data_str.split(":", 2)
        await user_numbers(query, context, svc, country)
        return
    if data_str.startswith("user_refresh:"):
        _, svc, country = data_str.split(":", 2)
        await user_refresh(query, context, svc, country)
        return
    if data_str.startswith("add_prefix:"):
        _, svc, country = data_str.split(":", 2)
        await add_prefix_handler(query, context, svc, country)
        return
    if data_str == "send_unmute_request":
        await send_unmute_request(query, context)
        return

    # Admin panel
    if uid != ADMIN_ID:
        await query.answer("⛔ Akses ditolak.", show_alert=True)
        return

    if data_str == "admin_main":
        await query.edit_message_text("⚙️ *ADMIN PANEL*", parse_mode=ParseMode.MARKDOWN, reply_markup=admin_panel_kb())
        return
    if data_str == "admin_dashboard":
        await admin_dashboard(query, context)
        return
    if data_str == "admin_service_list":
        await admin_service_list_view(query, context)
        return
    if data_str.startswith("admin_country_view:"):
        await admin_country_view(query, context, data_str.split(":", 1)[1])
        return
    if data_str == "admin_add_numbers":
        await admin_add_numbers_start(query, context)
        return
    if data_str.startswith("admin_add_pick_country:"):
        await admin_add_pick_country(query, context, data_str.split(":", 1)[1])
        return
    if data_str == "admin_remove_numbers":
        await admin_remove_numbers_start(query, context)
        return
    if data_str.startswith("admin_remove_pick_country:"):
        await admin_remove_pick_country(query, context, data_str.split(":", 1)[1])
        return
    if data_str.startswith("admin_remove_confirm:"):
        _, svc, country = data_str.split(":", 2)
        await admin_remove_confirm(query, context, svc, country)
        return
    if data_str == "admin_broadcast":
        await admin_broadcast_start(query, context)
        return
    if data_str == "admin_user_details":
        await admin_user_details_start(query, context)
        return
    if data_str == "admin_mute":
        await admin_mute_start(query, context)
        return
    if data_str == "admin_unmute":
        await admin_unmute_start(query, context)
        return
    if data_str == "admin_notifications":
        await admin_notifications_view(query, context)
        return
    if data_str.startswith("admin_do_unmute_notif:"):
        await admin_do_unmute_notif(query, context, int(data_str.split(":", 1)[1]))
        return
    if data_str == "admin_settings":
        await admin_settings(query, context)
        return
    if data_str == "admin_toggle_service":
        await admin_toggle_service(query, context)
        return
    if data_str == "admin_set_number_count":
        await admin_set_number_count(query, context)
        return
    if data_str == "admin_set_button_columns":
        await admin_set_button_columns(query, context)
        return

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    err = context.error
    if isinstance(err, Conflict):
        logger.warning("Conflict error - menunggu...")
        await asyncio.sleep(5)
    elif isinstance(err, NetworkError):
        logger.warning(f"Network error: {err}")
    else:
        logger.error(f"Error: {err}", exc_info=err)

# ─── MAIN ────────────────────────────────────────────────────────────────────
def main():
    SERVICE_LIST_DIR.mkdir(exist_ok=True)
    default_folders = ["WhatsApp", "Facebook", "Telegram", "Google", "Instagram", "Twitter", "TikTok", "LinkedIn"]
    for folder_name in default_folders:
        (SERVICE_LIST_DIR / folder_name).mkdir(exist_ok=True)

    # Optional: Start web dashboard jika tersedia
    if DASHBOARD_AVAILABLE:
        try:
            dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
            dashboard_thread.start()
            logger.info(f"✅ Web Dashboard started on port {os.environ.get('PORT', 5000)}")
            repl_url = f"https://{os.environ.get('REPL_SLUG', 'localhost')}.{os.environ.get('REPL_OWNER', 'replit')}.repl.co"
            logger.info(f"🔗 Akses dashboard di: {repl_url}")
        except Exception as e:
            logger.warning(f"⚠️ Gagal start web dashboard: {e}")
    else:
        print("ℹ️ Bot berjalan tanpa web dashboard (file web_dashboard.py tidak ditemukan)")

    app = (Application.builder().token(BOT_TOKEN).connect_timeout(30).read_timeout(30).write_timeout(30).build())
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CallbackQueryHandler(callback_router))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, message_handler))
    app.add_error_handler(error_handler)

    logger.info("🤖 Bot Telegram is running...")
    app.run_polling(drop_pending_updates=True, allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()
