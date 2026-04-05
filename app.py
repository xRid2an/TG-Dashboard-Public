import os
import json
import logging
import asyncio
import re
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, CopyTextButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from telegram.error import Conflict, NetworkError, TelegramError
load_dotenv()
logging.basicConfig(level=logging.INFO)
lll1111lllll = logging.getLogger(__name__)
lll1l1ll11l1 = os.getenv('BOT_TOKEN')
l1ll1l1111l1 = int(os.getenv('ADMIN_ID', '0'))
l11ll111llll = os.getenv('METHOD_GROUP', 'https://t.me/placeholder')
l1lll1l1l111 = os.getenv('OTP_GROUP', 'https://t.me/placeholder')
if not lll1l1ll11l1:
    raise ValueError('BOT_TOKEN not found in .env file')
if l1ll1l1111l1 == 0:
    raise ValueError('ADMIN_ID not found in .env file')
l111ll111111 = Path('service_list')
l1ll1l11ll11 = Path('data.json')
ADMIN_STATE: dict = {}
SERVICE_ICONS = {'whatsapp': '[WA]', 'facebook': '[FB]', 'telegram': '[TG]', 'google': '[GO]', 'instagram': '[IG]', 'twitter': '[TW]', 'tiktok': '[TK]', 'linkedin': '[LN]', 'snapchat': '[SC]', 'netflix': '[NF]', 'spotify': '[SP]', 'amazon': '[AM]', 'shopee': '[SH]', 'default': '[APP]'}

def l1lllll11111(l11ll1l1llll: str) -> str:
    ll1llll1111l = l11ll1l1llll.lower().strip()
    if ll1llll1111l in SERVICE_ICONS:
        return SERVICE_ICONS[ll1llll1111l]
    for ll1l11ll1l1l, l1ll1ll1ll1l in SERVICE_ICONS.items():
        if ll1l11ll1l1l in ll1llll1111l:
            return l1ll1ll1ll1l
    return SERVICE_ICONS['default']
COUNTRY_FLAGS = {'afghanistan': '🇦🇫', 'albania': '🇦🇱', 'algeria': '🇩🇿', 'andorra': '🇦🇩', 'angola': '🇦🇴', 'argentina': '🇦🇷', 'armenia': '🇦🇲', 'australia': '🇦🇺', 'austria': '🇦🇹', 'azerbaijan': '🇦🇿', 'bahrain': '🇧🇭', 'bangladesh': '🇧🇩', 'belarus': '🇧🇾', 'belgium': '🇧🇪', 'bolivia': '🇧🇴', 'bosnia': '🇧🇦', 'brazil': '🇧🇷', 'bulgaria': '🇧🇬', 'cambodia': '🇰🇭', 'cameroon': '🇨🇲', 'canada': '🇨🇦', 'chile': '🇨🇱', 'china': '🇨🇳', 'colombia': '🇨🇴', 'croatia': '🇭🇷', 'cuba': '🇨🇺', 'cyprus': '🇨🇾', 'czechia': '🇨🇿', 'denmark': '🇩🇰', 'ecuador': '🇪🇨', 'egypt': '🇪🇬', 'estonia': '🇪🇪', 'ethiopia': '🇪🇹', 'finland': '🇫🇮', 'france': '🇫🇷', 'georgia': '🇬🇪', 'germany': '🇩🇪', 'ghana': '🇬🇭', 'greece': '🇬🇷', 'guatemala': '🇬🇹', 'honduras': '🇭🇳', 'hungary': '🇭🇺', 'india': '🇮🇳', 'indonesia': '🇮🇩', 'iran': '🇮🇷', 'iraq': '🇮🇶', 'ireland': '🇮🇪', 'israel': '🇮🇱', 'italy': '🇮🇹', 'jamaica': '🇯🇲', 'japan': '🇯🇵', 'jordan': '🇯🇴', 'kazakhstan': '🇰🇿', 'kenya': '🇰🇪', 'kuwait': '🇰🇼', 'kyrgyzstan': '🇰🇬', 'laos': '🇱🇦', 'latvia': '🇱🇻', 'lebanon': '🇱🇧', 'libya': '🇱🇾', 'lithuania': '🇱🇹', 'luxembourg': '🇱🇺', 'malaysia': '🇲🇾', 'maldives': '🇲🇻', 'mali': '🇲🇱', 'malta': '🇲🇹', 'mexico': '🇲🇽', 'moldova': '🇲🇩', 'mongolia': '🇲🇳', 'morocco': '🇲🇦', 'mozambique': '🇲🇿', 'myanmar': '🇲🇲', 'nepal': '🇳🇵', 'netherlands': '🇳🇱', 'new zealand': '🇳🇿', 'nicaragua': '🇳🇮', 'nigeria': '🇳🇬', 'north korea': '🇰🇵', 'norway': '🇳🇴', 'oman': '🇴🇲', 'pakistan': '🇵🇰', 'palestine': '🇵🇸', 'panama': '🇵🇦', 'paraguay': '🇵🇾', 'peru': '🇵🇪', 'philippines': '🇵🇭', 'poland': '🇵🇱', 'portugal': '🇵🇹', 'qatar': '🇶🇦', 'romania': '🇷🇴', 'russia': '🇷🇺', 'saudi arabia': '🇸🇦', 'senegal': '🇸🇳', 'serbia': '🇷🇸', 'sierra leone': '🇸🇱', 'singapore': '🇸🇬', 'slovakia': '🇸🇰', 'somalia': '🇸🇴', 'south africa': '🇿🇦', 'south korea': '🇰🇷', 'spain': '🇪🇸', 'sri lanka': '🇱🇰', 'sudan': '🇸🇩', 'sweden': '🇸🇪', 'switzerland': '🇨🇭', 'syria': '🇸🇾', 'taiwan': '🇹🇼', 'tajikistan': '🇹🇯', 'tanzania': '🇹🇿', 'thailand': '🇹🇭', 'tunisia': '🇹🇳', 'turkey': '🇹🇷', 'turkmenistan': '🇹🇲', 'uganda': '🇺🇬', 'ukraine': '🇺🇦', 'uae': '🇦🇪', 'united arab emirates': '🇦🇪', 'uk': '🇬🇧', 'united kingdom': '🇬🇧', 'usa': '🇺🇸', 'united states': '🇺🇸', 'uruguay': '🇺🇾', 'uzbekistan': '🇺🇿', 'venezuela': '🇻🇪', 'vietnam': '🇻🇳', 'yemen': '🇾🇪', 'zambia': '🇿🇲', 'zimbabwe': '🇿🇼'}

def l1l11ll11l11(ll1ll1l1111l: str) -> str:
    l111lll1l111 = ll1ll1l1111l.strip().lower()
    for l11l1l11l11l, lll1l11ll1ll in COUNTRY_FLAGS.items():
        if l111lll1l111 == l11l1l11l11l or l111lll1l111.startswith(l11l1l11l11l) or l11l1l11l11l in l111lll1l111:
            return lll1l11ll1ll
    return '🌍'

def l1l111111ll1(l1llllll11ll: str) -> str:
    l1l1ll1llll1 = l1llllll11ll.replace('.txt', '')
    lllll11lll1l = ['[A-Z]{2,}-\\d+-\\d{4}-\\d{2}-\\d{2}', '[A-Z]{2,}-\\d+', '\\d{4}-\\d{2}-\\d{2}', '-\\d+$']
    for l11lllll1l1l in lllll11lll1l:
        l1l1ll1llll1 = re.sub(l11lllll1l1l, '', l1l1ll1llll1)
    l1l1ll1llll1 = re.sub('^[-_\\s]+|[-_\\s]+$', '', l1l1ll1llll1)
    l1l1ll1llll1 = re.sub('[^A-Za-z\\s]', '', l1l1ll1llll1)
    if l1l1ll1llll1.strip():
        return l1l1ll1llll1.split()[0].title()
    return 'Unknown'

def l1ll11ll1111(ll1lll1111l1: str) -> str:
    ll1lll1111l1 = ll1lll1111l1.strip()
    if len(ll1lll1111l1) <= 6:
        return ll1lll1111l1
    return ll1lll1111l1[:4] + '****' + ll1lll1111l1[-4:]

def ll11ll11lll1() -> dict:
    if l1ll1l11ll11.exists():
        with open(l1ll1l11ll11, 'r', encoding='utf-8') as l1l1l1111lll:
            return json.load(l1l1l1111lll)
    return {'users': {}, 'muted': {}, 'notifications': [], 'service_enabled': True, 'numbers_per_view': 6, 'button_columns': 2}

def l1111l1lll1l(l111111lll11: dict):
    with open(l1ll1l11ll11, 'w', encoding='utf-8') as l1l1lll1lll1:
        json.dump(l111111lll11, l1l1lll1lll1, ensure_ascii=False, indent=2)

def l1l111ll111l(lll1111l1lll: dict, ll11l1l111ll: int) -> dict:
    ll11l1l111ll = str(ll11l1l111ll)
    if ll11l1l111ll not in lll1111l1lll['users']:
        lll1111l1lll['users'][ll11l1l111ll] = {'first_seen': datetime.now().isoformat(), 'last_active': datetime.now().isoformat(), 'total_seen': 0, 'seen_numbers': [], 'last_3': [], 'last_24h_seen': [], 'last_file': None, 'last_service': None, 'last_country': None, 'username': '', 'full_name': ''}
    return lll1111l1lll['users'][ll11l1l111ll]

def l1ll1l1111ll(l11ll1lllll1: dict, llllll111l11: Update):
    l1l11111ll1l = llllll111l11.effective_user
    l11lll1ll1ll = l1l111ll111l(l11ll1lllll1, l1l11111ll1l.id)
    l11lll1ll1ll['last_active'] = datetime.now().isoformat()
    l11lll1ll1ll['username'] = l1l11111ll1l.username or ''
    l11lll1ll1ll['full_name'] = l1l11111ll1l.full_name or ''
    l1111l1lll1l(l11ll1lllll1)

def l1ll1111ll1l(l11ll111l11l: Path) -> int:
    if not l11ll111l11l.exists():
        return 0
    l1l1l11l111l = [llll1lll1l1l.strip() for llll1lll1l1l in l11ll111l11l.read_text(encoding='utf-8', errors='ignore').splitlines() if llll1lll1l1l.strip()]
    return len(l1l1l11l111l)

def l111lll111ll(llllll111l1l: Path) -> int:
    l1l11lll11ll = 0
    if not llllll111l1l.exists():
        return 0
    for ll1lllllll11 in llllll111l1l.glob('*.txt'):
        l1l11lll11ll += l1ll1111ll1l(ll1lllllll11)
    return l1l11lll11ll

def l111ll1l1l11():
    ll1l11l1l11l = []
    for ll1l111l11ll in l111ll111111.iterdir():
        if ll1l111l11ll.is_dir():
            ll1l11l1l11l.append(ll1l111l11ll)
    return sorted(ll1l11l1l11l, key=lambda x: x.name)

def ll111l1l1111(l1llll1111ll: Path):
    llll1l1l1l1l = []
    for l1l1l1ll111l in l1llll1111ll.glob('*.txt'):
        l1l1l11111l1 = l1l111111ll1(l1l1l1ll111l.stem)
        if l1l1l11111l1 != 'Unknown':
            llll1l1l1l1l.append(l1l1l1ll111l)
    return sorted(llll1l1l1l1l, key=lambda x: x.stem)

def l111l1111ll1(l11111l1l111: dict, l11ll1111l11: Path) -> int:
    l1lllll11l11 = 0
    for l1l1l11ll1ll in l11111l1l111['users'].values():
        for ll11ll1l1lll in l1l1l11ll1ll.get('seen_numbers', []):
            if ll11ll1l1lll.get('service') == l11ll1111l11.name:
                l1lllll11l11 += 1
    return l1lllll11l11

def ll111111l1ll(l111l1l11111: dict, l111l111lll1: str, l1l11ll1ll11: str) -> int:
    llll1l111l1l = 0
    for l1l11ll1l1l1 in l111l1l11111['users'].values():
        for l11l1l1l11ll in l1l11ll1l1l1.get('seen_numbers', []):
            if l11l1l1l11ll.get('service') == l111l111lll1 and l11l1l1l11ll.get('country') == l1l11ll1ll11:
                llll1l111l1l += 1
    return llll1l111l1l

def ll111lllll11(ll1ll1lll11l: dict, lll1l1ll111l: int, lll111ll1l1l: str, lllll111lll1: str, l11lll11lll1: Path, n: int=6):
    l1l11llll1l1 = l11lll11lll1 / f'{lllll111lll1}.txt'
    if not l1l11llll1l1.exists():
        for ll1ll1l1l111 in l11lll11lll1.glob('*.txt'):
            if l1l111111ll1(ll1ll1l1l111.stem) == lllll111lll1:
                l1l11llll1l1 = ll1ll1l1l111
                break
    if not l1l11llll1l1.exists():
        return []
    lllll11l1lll = [l11111ll1111.strip() for l11111ll1111 in l1l11llll1l1.read_text(encoding='utf-8', errors='ignore').splitlines() if l11111ll1111.strip()]
    l11ll11111ll = l1l111ll111l(ll1ll1lll11l, lll1l1ll111l)
    ll1llll1llll = set((llll11lll11l['number'] for llll11lll11l in l11ll11111ll.get('seen_numbers', []) if llll11lll11l.get('service') == lll111ll1l1l and llll11lll11l.get('country') == lllll111lll1))
    l1l11l1lll1l = [ll111ll1lll1 for ll111ll1lll1 in lllll11l1lll if ll111ll1lll1 not in ll1llll1llll]
    return l1l11l1lll1l[:n]

def l11ll11l1ll1(l1ll11111l11: dict, l1l111l11111: int, l11l1lll1l1l: str, lll1111ll1l1: str, l1111l11111l: list):
    l111llll1ll1 = l1l111ll111l(l1ll11111l11, l1l111l11111)
    l111lll111l1 = datetime.now().isoformat()
    for ll1ll11ll1ll in l1111l11111l:
        l111llll1ll1['seen_numbers'].append({'number': ll1ll11ll1ll, 'service': l11l1lll1l1l, 'country': lll1111ll1l1, 'at': l111lll111l1})
        l111llll1ll1['last_24h_seen'].append({'number': ll1ll11ll1ll, 'at': l111lll111l1})
    l111llll1ll1['last_3'] = [{'number': llll1l1lll11, 'service': l11l1lll1l1l, 'country': lll1111ll1l1} for llll1l1lll11 in l1111l11111l]
    l111llll1ll1['total_seen'] += len(l1111l11111l)
    l111llll1ll1['last_file'] = lll1111ll1l1
    l111llll1ll1['last_service'] = l11l1lll1l1l
    l111llll1ll1['last_country'] = lll1111ll1l1
    l1111l1lll1l(l1ll11111l11)

def l11lll11l11l(lll11111111l: dict, ll1111lll1ll: int) -> bool:
    ll11ll11l11l = str(ll1111lll1ll)
    lll1l1111ll1 = lll11111111l.get('muted', {}).get(ll11ll11l11l)
    if not lll1l1111ll1:
        return False
    if lll1l1111ll1.get('permanent'):
        return True
    l111l111l1ll = lll1l1111ll1.get('until')
    if l111l111l1ll and datetime.fromisoformat(l111l111l1ll) > datetime.now():
        return True
    return False

def l1l1lll1l111(ll1lll1l1l1l: dict, minutes: int=20) -> int:
    l1lll1ll11l1 = datetime.now() - timedelta(minutes=minutes)
    lll11l11llll = 0
    for llll1l11111l in ll1lll1l1l1l['users'].values():
        l11l111l11ll = llll1l11111l.get('last_active', '')
        if l11l111l11ll:
            try:
                if datetime.fromisoformat(l11l111l11ll) > l1lll1ll11l1:
                    lll11l11llll += 1
            except:
                pass
    return lll11l11llll

def l1l11111l1ll(l1l11l111lll: dict) -> int:
    ll11ll1lllll = datetime.now() - timedelta(hours=24)
    ll1l11l1ll11 = 0
    for l11ll11l1lll in l1l11l111lll.get('last_24h_seen', []):
        try:
            if datetime.fromisoformat(l11ll11l1lll['at']) > ll11ll1lllll:
                ll1l11l1ll11 += 1
        except:
            pass
    return ll1l11l1ll11

def l111l1lll1l1(ll11llll1l11: bool):
    l1111l11l1ll = [[InlineKeyboardButton('📊 DASHBOARD', callback_data='user_dashboard')], [InlineKeyboardButton('📂 SERVICE LIST', callback_data='user_service_list')]]
    if ll11llll1l11:
        l1111l11l1ll.append([InlineKeyboardButton('⚙️ ADMIN PANEL', callback_data='admin_main')])
    return InlineKeyboardMarkup(l1111l11l1ll)

def ll1111111l1l():
    ll11ll111l1l = ll11ll11lll1()
    l11ll11lllll = len([l11l1llll1l1 for l11l1llll1l1 in ll11ll111l1l.get('notifications', []) if not l11l1llll1l1.get('seen')])
    l111ll1ll11l = f'📢 NOTIFICATIONS ({l11ll11lllll})' if l11ll11lllll else '📢 NOTIFICATIONS'
    l1111l1l1l11 = [[InlineKeyboardButton('📊 DASHBOARD', callback_data='admin_dashboard')], [InlineKeyboardButton('📂 SERVICE LIST', callback_data='admin_service_list')], [InlineKeyboardButton('➕ ADD NUMBERS', callback_data='admin_add_numbers'), InlineKeyboardButton('❌ REMOVE NUMBERS', callback_data='admin_remove_numbers')], [InlineKeyboardButton('📢 BROADCAST', callback_data='admin_broadcast')], [InlineKeyboardButton('👤 USER DETAILS', callback_data='admin_user_details')], [InlineKeyboardButton('🔇 MUTE USER', callback_data='admin_mute'), InlineKeyboardButton('🔊 UNMUTE USER', callback_data='admin_unmute')], [InlineKeyboardButton(l111ll1ll11l, callback_data='admin_notifications')], [InlineKeyboardButton('⚙️ SETTINGS', callback_data='admin_settings')], [InlineKeyboardButton('◀️ BACK TO USER', callback_data='user_main')]]
    return InlineKeyboardMarkup(l1111l1l1l11)

def l111ll11ll1l(llllll11lll1: str, label: str='◀️ BACK'):
    return InlineKeyboardMarkup([[InlineKeyboardButton(label, callback_data=llllll11lll1)]])

async def l1lll1ll1l11(ll1lll11ll1l: Update, ll1lll1l1ll1: ContextTypes.DEFAULT_TYPE):
    llll1l1l11ll = ll11ll11lll1()
    llll11l1l11l = ll1lll11ll1l.effective_user.id
    l1ll1l1111ll(llll1l1l11ll, ll1lll11ll1l)
    if l11lll11l11l(llll1l1l11ll, llll11l1l11l):
        await ll1lll11ll1l.message.reply_text('⛔ Anda tidak dapat menggunakan bot ini.\n\nKirim permintaan unmute ke admin:', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('📨 SEND UNMUTE REQUEST', callback_data='send_unmute_request')]]))
        return
    await ll1lll11ll1l.message.reply_text(f'👋 Selamat datang, {ll1lll11ll1l.effective_user.first_name}!', reply_markup=l111l1lll1l1(llll11l1l11l == l1ll1l1111l1))

async def lllll1l1l1l1(lll1111lll1l: Update, l111ll1l1lll: ContextTypes.DEFAULT_TYPE):
    if lll1111lll1l.effective_user.id != l1ll1l1111l1:
        await lll1111lll1l.message.reply_text('⛔ Akses ditolak.')
        return
    await lll1111lll1l.message.reply_text('⚙️ ADMIN PANEL:', reply_markup=ll1111111l1l())

async def lll111111111(ll11l11ll1ll, ll1lll1llll1):
    l1l11111l11l = ll11ll11lll1()
    l111111lll1l = ll11l11ll1ll.from_user.id
    lll111l1ll11 = []
    for ll1lllll111l in l111ll1l1l11():
        for ll1lll1ll1ll in ll111l1l1111(ll1lllll111l):
            lll1ll1l1l11 = l1l111111ll1(ll1lll1ll1ll.stem)
            ll11l11l1111 = l1ll1111ll1l(ll1lll1ll1ll)
            ll1l1lllll11 = l1l11ll11l11(lll1ll1l1l11)
            lll111l1ll11.append({'flag': ll1l1lllll11, 'country': lll1ll1l1l11, 'total': ll11l11l1111})
    lll111l1ll11.sort(key=lambda x: x['total'], reverse=True)
    lllll1ll11l1 = sum((l1ll111ll1ll['total'] for l1ll111ll1ll in lll111l1ll11))
    ll1ll1111lll = 25

    def ll1lll111l11(l1ll1111l11l, ll11l11ll111):
        l1ll1111l11l = str(l1ll1111l11l)
        return l1ll1111l11l[:ll11l11ll111] + ' ' * max(0, ll11l11ll111 - len(l1ll1111l11l))
    llllll1l111l = []
    llllll1l111l.append('╭' + '─' * ll1ll1111lll + '╮')
    llllll1l111l.append('│' + 'AVAILABLE NUMBER'.center(ll1ll1111lll))
    llllll1l111l.append('╰' + '─' * ll1ll1111lll + '╯')
    for l1l1lll11lll, l11l11111l11 in enumerate(lll111l1ll11[:10]):
        l1111lll111l = l11l11111l11['total'] / lllll1ll11l1 * 100 if lllll1ll11l1 > 0 else 0
        lllll1llllll = 30
        lllll1l1lll1 = int(l1111lll111l / 100 * lllll1llllll)
        ll1l1ll11111 = '||' * lllll1l1lll1 + ' ' * (lllll1llllll - lllll1l1lll1)
        ll11llll111l = f"{l1l1lll11lll + 1}. {l11l11111l11['flag']} {l11l11111l11['country']} ({l11l11111l11['total']})"
        l1111lll1l11 = f'╰ ‹{ll1l1ll11111}› {l1111lll111l:5.1f}%'
        llllll1l111l.append('╭' + '─' * ll1ll1111lll + '╮')
        llllll1l111l.append('│ ' + ll1lll111l11(ll11llll111l, ll1ll1111lll - 2))
        llllll1l111l.append('│ ' + l1111lll1l11.ljust(ll1ll1111lll - 2))
        llllll1l111l.append('╰' + '─' * ll1ll1111lll + '╯')
    llllll1l111l.append('╭' + '─' * ll1ll1111lll + '╮')
    llllll1l111l.append('│ ' + ll1lll111l11(f'TOTAL COUNTRIES : {len(lll111l1ll11)}', ll1ll1111lll - 2))
    llllll1l111l.append('│ ' + ll1lll111l11(f'TOTAL NUMBERS   : {lllll1ll11l1}', ll1ll1111lll - 2))
    llllll1l111l.append('╰' + '─' * ll1ll1111lll + '╯')
    await ll11l11ll1ll.edit_message_text('\n'.join(llllll1l111l), reply_markup=l111ll11ll1l('user_main'), disable_web_page_preview=True)

async def ll1lll11l1ll(l1ll11l1l1ll, llllll1111l1):
    ll1l11ll1ll1 = []
    for l1111ll11111 in l111ll1l1l11():
        ll11ll1ll111 = l111lll111ll(l1111ll11111)
        l1ll1l11lll1 = l1lllll11111(l1111ll11111.name)
        ll1l11ll1ll1.append([InlineKeyboardButton(f'{l1ll1l11lll1} {l1111ll11111.name} ({ll11ll1ll111})', callback_data=f'user_country_list:{l1111ll11111.name}')])
    ll1l11ll1ll1.append([InlineKeyboardButton('◀️ BACK', callback_data='user_main')])
    await l1ll11l1l1ll.edit_message_text('📁 *SERVICE LIST*\n\nSilakan pilih layanan:', parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(ll1l11ll1ll1))

async def l1l1l11llll1(lll111llll1l, ll11111l1111, l1lll1l1111l: str):
    llll1lllll1l = ll11ll11lll1()
    l111111l111l = lll111llll1l.from_user.id
    if l11lll11l11l(llll1lllll1l, l111111l111l):
        await lll111llll1l.edit_message_text('⛔ Anda tidak dapat menggunakan bot ini.', reply_markup=l111ll11ll1l('user_main'))
        return
    if not llll1lllll1l.get('service_enabled', True):
        await lll111llll1l.edit_message_text('⚠️ Service List sedang dinonaktifkan.', reply_markup=l111ll11ll1l('user_service_list'))
        return
    ll11l11ll11l = l111ll111111 / l1lll1l1111l
    lll111l111l1 = ll111l1l1111(ll11l11ll11l)
    if not lll111l111l1:
        await lll111llll1l.edit_message_text('📂 Tidak ada file di folder ini.', reply_markup=l111ll11ll1l('user_service_list'))
        return
    l1lll1l1l1l1 = f'📱 Select country for *{l1lll1l1111l.upper()}*:\n\n'
    l1l1ll11l1ll = []
    for lll1lll1l11l in lll111l111l1:
        l111l11111l1 = l1l111111ll1(lll1lll1l11l.stem)
        ll1l111111l1 = l1ll1111ll1l(lll1lll1l11l)
        l11lll1lll1l = l1l11ll11l11(l111l11111l1)
        l1lll1l1l1l1 += f'{l11lll1lll1l} {l111l11111l1} ({ll1l111111l1})\n'
        l1l1ll11l1ll.append([InlineKeyboardButton(f'{l11lll1lll1l} {l111l11111l1}', callback_data=f'user_numbers:{l1lll1l1111l}:{l111l11111l1}')])
    l1l1ll11l1ll.append([InlineKeyboardButton('◀️ BACK TO SERVICES', callback_data='user_service_list')])
    await lll111llll1l.edit_message_text(l1lll1l1l1l1, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(l1l1ll11l1ll))

async def ll1llll11l11(l1ll11111lll, l1ll1l111l11, ll11lll11ll1: str, l1l1l1111l1l: str):
    l1ll11111l1l = ll11ll11lll1()
    ll111lllllll = l1ll11111lll.from_user.id
    if l11lll11l11l(l1ll11111l1l, ll111lllllll):
        await l1ll11111lll.edit_message_text('⛔ Anda tidak dapat menggunakan bot ini.\nSilakan kirim permintaan unmute ke admin:', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('📨 SEND UNMUTE REQUEST', callback_data='send_unmute_request')]]))
        return
    ll111l1llll1 = l1ll11111l1l.get('numbers_per_view', 6)
    ll11ll11ll11 = l111ll111111 / ll11lll11ll1
    ll111111llll = ll111lllll11(l1ll11111l1l, ll111lllllll, ll11lll11ll1, l1l1l1111l1l, ll11ll11ll11, ll111l1llll1)
    if not ll111111llll:
        await l1ll11111lll.edit_message_text(f'✅ *{ll11lll11ll1} › {l1l1l1111l1l}*\n\nTidak ada nomor baru.', parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◀️ BACK', callback_data=f'user_country_list:{ll11lll11ll1}')], [InlineKeyboardButton('💬 METHOD GROUP', url=l11ll111llll), InlineKeyboardButton('🔐 OTP GROUP', url=l1lll1l1l111)]]))
        return
    l11ll11l1ll1(l1ll11111l1l, ll111lllllll, ll11lll11ll1, l1l1l1111l1l, ll111111llll)

    def l1111lll11l1(l111lllllll1):
        l111lllllll1 = l111lllllll1.strip()
        return f'+{l111lllllll1}' if not l111lllllll1.startswith('+') else l111lllllll1
    l1ll111l1l11 = [l1111lll11l1(l1llll11lll1) for l1llll11lll1 in ll111111llll]
    l11l1l1l111l = l1l11ll11l11(l1l1l1111l1l)
    llllll1l1ll1 = l1ll11111l1l.get('button_columns', 2)

    def llll1llll111(l11l11l1l11l, ll1l11l11ll1, cols_per_row=2):
        ll1ll1ll11l1 = []
        l1lll1lll111 = []
        for ll11lll1ll11 in l11l11l1l11l:
            l1llll11l1ll = l1ll11ll1111(ll11lll1ll11)
            llll111111ll = InlineKeyboardButton(text=f'{ll1l11l11ll1} {l1llll11l1ll}', copy_text=CopyTextButton(text=ll11lll1ll11))
            l1lll1lll111.append(llll111111ll)
            if len(l1lll1lll111) == cols_per_row:
                ll1ll1ll11l1.append(l1lll1lll111)
                l1lll1lll111 = []
        if l1lll1lll111:
            ll1ll1ll11l1.append(l1lll1lll111)
        return ll1ll1ll11l1
    ll1lll1l1l11 = llll1llll111(l1ll111l1l11, l11l1l1l111l, llllll1l1ll1)
    l1ll1l1ll1ll = [InlineKeyboardButton('◀️ BACK', callback_data=f'user_country_list:{ll11lll11ll1}'), InlineKeyboardButton('🔄 REFRESH', callback_data=f'user_refresh:{ll11lll11ll1}:{l1l1l1111l1l}')]
    lll11l11ll11 = [InlineKeyboardButton('💬 METHOD GROUP', url=l11ll111llll), InlineKeyboardButton('🔐 OTP GROUP', url=l1lll1l1l111)]
    await l1ll11111lll.edit_message_text(f'📂 *{ll11lll11ll1} › {l1l1l1111l1l}*\n\nKlik nomor untuk menyalin 👇', parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(ll1lll1l1l11 + [l1ll1l1ll1ll, lll11l11ll11]))

async def ll11ll1ll1l1(l1lll111llll, ll11lll11111, lll111llll11: str, llll1llllll1: str):
    await ll1llll11l11(l1lll111llll, ll11lll11111, lll111llll11, llll1llllll1)

async def l1111l1ll1l1(l111lllll11l, ll11l111ll1l):
    llll11ll11ll = ll11ll11lll1()
    l1l1l1llllll = l111lllll11l.from_user.id
    ll111ll1l1l1 = l111lllll11l.from_user
    llll11ll11ll.setdefault('notifications', []).append({'type': 'unmute_request', 'uid': l1l1l1llllll, 'username': ll111ll1l1l1.username or '', 'full_name': ll111ll1l1l1.full_name or '', 'at': datetime.now().isoformat(), 'seen': False})
    l1111l1lll1l(llll11ll11ll)
    await l111lllll11l.edit_message_text('📨 Permintaan unmute telah dikirim ke admin.')

async def llll1111111l(lllll11l1l1l, l1111l1111ll):
    ll1lll11l11l = ll11ll11lll1()
    l1l111lll1l1 = ['📊 ADMIN DASHBOARD', '=' * 30, '']
    for lllllll11l11 in l111ll1l1l11():
        l11lll1l1lll = l111lll111ll(lllllll11l11)
        ll11llllll1l = l111l1111ll1(ll1lll11l11l, lllllll11l11)
        lll111l11l11 = l11lll1l1lll - ll11llllll1l
        l1l111lll1l1.append(f'{lllllll11l11.name}: {ll11llllll1l}/{l11lll1l1lll} seen, {lll111l11l11} left')
    ll1lll1lllll = len(ll1lll11l11l['users'])
    ll1l1l1ll111 = l1l1lll1l111(ll1lll11l11l, 20)
    l1l111lll1l1.extend(['', f'👥 Total Users: {ll1lll1lllll}', f'🕐 Active (20m): {ll1l1l1ll111}'])
    await lllll11l1l1l.edit_message_text('\n'.join(l1l111lll1l1), reply_markup=l111ll11ll1l('admin_main'))

async def l11l11l1llll(lll1l1ll1111, llll11ll1l1l):
    l1lllllll11l = []
    for l1l1l111l111 in l111ll1l1l11():
        llll11111l11 = l111lll111ll(l1l1l111l111)
        l1lllllll11l.append([InlineKeyboardButton(f'📂 {l1l1l111l111.name} ({llll11111l11})', callback_data=f'admin_country_view:{l1l1l111l111.name}')])
    l1lllllll11l.append([InlineKeyboardButton('◀️ BACK', callback_data='admin_main')])
    await lll1l1ll1111.edit_message_text('📂 SERVICE LIST', reply_markup=InlineKeyboardMarkup(l1lllllll11l))

async def l1llllllll11(ll1l11ll1lll, l1l1l11lll1l, l1l11l11ll1l: str):
    ll1111ll1l1l = ll11ll11lll1()
    ll1l111llll1 = l111ll111111 / l1l11l11ll1l
    l1llll1ll111 = []
    for l11111l1111l in ll111l1l1111(ll1l111llll1):
        ll1ll1l11lll = l1l111111ll1(l11111l1111l.stem)
        ll11l11llll1 = l1ll1111ll1l(l11111l1111l)
        llllllll1l1l = ll111111l1ll(ll1111ll1l1l, l1l11l11ll1l, ll1ll1l11lll)
        llll111ll1l1 = l1l11ll11l11(ll1ll1l11lll)
        l1llll1ll111.append([InlineKeyboardButton(f'{llll111ll1l1} {ll1ll1l11lll}: {llllllll1l1l}/{ll11l11llll1}', callback_data='noop')])
    l1llll1ll111.append([InlineKeyboardButton('◀️ BACK', callback_data='admin_service_list')])
    await ll1l11ll1lll.edit_message_text(f'🌍 {l1l11l11ll1l} - COUNTRIES', reply_markup=InlineKeyboardMarkup(l1llll1ll111))

async def ll11111llll1(lll1llll1l1l, lll1111l11l1):
    l1l1111l11l1 = []
    for l1l11ll111ll in l111ll1l1l11():
        l1l1111l11l1.append([InlineKeyboardButton(f'📂 {l1l11ll111ll.name}', callback_data=f'admin_add_pick_country:{l1l11ll111ll.name}')])
    l1l1111l11l1.append([InlineKeyboardButton('◀️ BACK', callback_data='admin_main')])
    await lll1llll1l1l.edit_message_text('➕ ADD NUMBERS - Pilih service:', reply_markup=InlineKeyboardMarkup(l1l1111l11l1))

async def lll1l111ll11(l1ll1lll1l11, l111l1l111ll, ll1lllll1111: str):
    ADMIN_STATE.clear()
    ADMIN_STATE['add_service'] = ll1lllll1111
    ADMIN_STATE['state'] = 'awaiting_add_file'
    await l1ll1lll1l11.edit_message_text(f'📁 Kirim file .txt untuk {ll1lllll1111}:', reply_markup=l111ll11ll1l('admin_add_numbers'))

async def l11ll1ll1lll(l11l1l1ll111, l1l1l11l11l1):
    l1l1l11l1l11 = []
    for ll11lll1l11l in l111ll1l1l11():
        l1l1l11l1l11.append([InlineKeyboardButton(f'📂 {ll11lll1l11l.name}', callback_data=f'admin_remove_pick_country:{ll11lll1l11l.name}')])
    l1l1l11l1l11.append([InlineKeyboardButton('◀️ BACK', callback_data='admin_main')])
    await l11l1l1ll111.edit_message_text('❌ REMOVE NUMBERS - Pilih service:', reply_markup=InlineKeyboardMarkup(l1l1l11l1l11))

async def l1l1l1lll111(llll1l11llll, llllll1lll1l, ll11l1ll11ll: str):
    l1ll111111ll = l111ll111111 / ll11l1ll11ll
    l11l1ll11l11 = []
    for l1ll11l1ll11 in ll111l1l1111(l1ll111111ll):
        ll1ll1l111l1 = l1l111111ll1(l1ll11l1ll11.stem)
        lllllll11ll1 = l1ll1111ll1l(l1ll11l1ll11)
        lllll111l11l = l1l11ll11l11(ll1ll1l111l1)
        l11l1ll11l11.append([InlineKeyboardButton(f'🗑 {lllll111l11l} {ll1ll1l111l1} ({lllllll11ll1})', callback_data=f'admin_remove_confirm:{ll11l1ll11ll}:{ll1ll1l111l1}')])
    l11l1ll11l11.append([InlineKeyboardButton('◀️ BACK', callback_data='admin_remove_numbers')])
    await llll1l11llll.edit_message_text(f'🗑 {ll11l1ll11ll} - Pilih file:', reply_markup=InlineKeyboardMarkup(l11l1ll11l11))

async def l11l11111l1l(llllll11llll, ll1ll11111l1, ll1ll11l1l11: str, lllll1l111l1: str):
    l1lll11l1l11 = l111ll111111 / ll1ll11l1l11
    for ll11l1111111 in l1lll11l1l11.glob('*.txt'):
        if l1l111111ll1(ll11l1111111.stem) == lllll1l111l1:
            ll11l1111111.unlink()
            break
    await llllll11llll.edit_message_text(f'✅ {lllll1l111l1} telah dihapus.', reply_markup=l111ll11ll1l('admin_main'))

async def l111lll1llll(ll1l1llll111, l1111l111l1l):
    ADMIN_STATE.clear()
    ADMIN_STATE['state'] = 'awaiting_broadcast'
    await ll1l1llll111.edit_message_text('📢 Kirim pesan broadcast:', reply_markup=l111ll11ll1l('admin_main'))

async def l1l1111l1l1l(lll11ll111ll, l1llll11ll11):
    ADMIN_STATE.clear()
    ADMIN_STATE['state'] = 'awaiting_user_details_input'
    await lll11ll111ll.edit_message_text('🔍 Masukkan User ID:', reply_markup=l111ll11ll1l('admin_main'))

async def ll1lll11llll(l1l111ll1l1l, l11llll11ll1):
    ADMIN_STATE.clear()
    ADMIN_STATE['state'] = 'awaiting_mute_id'
    await l1l111ll1l1l.edit_message_text('🔇 Masukkan User ID untuk mute:', reply_markup=l111ll11ll1l('admin_main'))

async def l1l11l1ll1ll(l11lll1l1ll1, lll1l1l11l11):
    ADMIN_STATE.clear()
    ADMIN_STATE['state'] = 'awaiting_unmute_id'
    await l11lll1l1ll1.edit_message_text('🔊 Masukkan User ID untuk unmute:', reply_markup=l111ll11ll1l('admin_main'))

async def l1ll1l11l11l(ll1llllll1ll, ll1lllllllll):
    l1lllll1l11l = ll11ll11lll1()
    ll1l11lll11l = [l111lll1lll1 for l111lll1lll1 in l1lllll1l11l.get('notifications', []) if l111lll1lll1.get('type') == 'unmute_request']
    for l1111111ll1l in ll1l11lll11l:
        l1111111ll1l['seen'] = True
    l1111l1lll1l(l1lllll1l11l)
    if not ll1l11lll11l:
        await ll1llllll1ll.edit_message_text('📭 Tidak ada notifikasi.', reply_markup=l111ll11ll1l('admin_main'))
        return
    l1ll111ll1l1 = []
    for l1111111ll1l in ll1l11lll11l[-20:]:
        l1ll111ll1l1.append([InlineKeyboardButton(f"👤 {l1111111ll1l['full_name']} (ID: {l1111111ll1l['uid']})", callback_data='noop')])
        l1ll111ll1l1.append([InlineKeyboardButton('🔊 UNMUTE', callback_data=f"admin_do_unmute_notif:{l1111111ll1l['uid']}")])
    l1ll111ll1l1.append([InlineKeyboardButton('◀️ BACK', callback_data='admin_main')])
    await ll1llllll1ll.edit_message_text('📢 UNMUTE REQUESTS:', reply_markup=InlineKeyboardMarkup(l1ll111ll1l1))

async def ll111l1l11l1(l1111l11ll1l, ll1ll1l1l1ll, l1ll1l1l11l1: int):
    ll1111lllll1 = ll11ll11lll1()
    ll1111lllll1['muted'].pop(str(l1ll1l1l11l1), None)
    l1111l1lll1l(ll1111lllll1)
    try:
        await ll1ll1l1l1ll.bot.send_message(l1ll1l1l11l1, '✅ Anda telah di-unmute.')
    except:
        pass
    await l1111l11ll1l.edit_message_text(f'✅ User {l1ll1l1l11l1} telah di-unmute.', reply_markup=l111ll11ll1l('admin_main'))

async def lll1l111lll1(ll1l11lll111, l11lll1lllll):
    l1l11lllll1l = ll11ll11lll1()
    lll111l1lll1 = l1l11lllll1l.get('service_enabled', True)
    ll1111111lll = l1l11lllll1l.get('numbers_per_view', 6)
    l111111ll1ll = l1l11lllll1l.get('button_columns', 2)
    ll11111lll11 = '✅ ON' if lll111l1lll1 else '❌ OFF'
    l1ll1111lll1 = [[InlineKeyboardButton(f'⚙️ SERVICE LIST: {ll11111lll11}', callback_data='admin_toggle_service')], [InlineKeyboardButton(f'🔢 NUMBERS PER VIEW: {ll1111111lll}', callback_data='admin_set_number_count')], [InlineKeyboardButton(f'🔘 BUTTON COLUMNS: {l111111ll1ll}', callback_data='admin_set_button_columns')], [InlineKeyboardButton('◀️ BACK', callback_data='admin_main')]]
    await ll1l11lll111.edit_message_text('⚙️ SETTINGS:', reply_markup=InlineKeyboardMarkup(l1ll1111lll1))

async def l11l11l11ll1(l111ll11l111, ll111l111l1l):
    l1lll1l1l11l = ll11ll11lll1()
    l1lll1l1l11l['service_enabled'] = not l1lll1l1l11l.get('service_enabled', True)
    l1111l1lll1l(l1lll1l1l11l)
    await lll1l111lll1(l111ll11l111, ll111l111l1l)

async def l11l1l1lllll(l1ll11lll11l, lll1111ll1ll):
    ADMIN_STATE.clear()
    ADMIN_STATE['state'] = 'awaiting_number_count'
    await l1ll11lll11l.edit_message_text('🔢 Masukkan jumlah nomor per tampilan (1-20):', reply_markup=l111ll11ll1l('admin_settings'))

async def llll1l1ll1ll(ll1l11l1111l, ll11l11lll1l):
    ADMIN_STATE.clear()
    ADMIN_STATE['state'] = 'awaiting_button_columns'
    await ll1l11l1111l.edit_message_text('🔘 Masukkan jumlah kolom tombol (1-4):', reply_markup=l111ll11ll1l('admin_settings'))

async def l11ll111lll1(ll1ll1ll11ll: Update, l1lllll1l111: ContextTypes.DEFAULT_TYPE):
    l1l111l11l1l = ADMIN_STATE.get('state')
    l1l111ll1l11 = ll1ll1ll11ll.effective_user.id
    l1111l11l111 = ll11ll11lll1()
    if l1l111ll1l11 == l1ll1l1111l1:
        if l1l111l11l1l == 'awaiting_broadcast':
            ADMIN_STATE.clear()
            l111l11llll1 = list(l1111l11l111['users'].keys())
            ll111l11llll, lll11l1111ll = (0, 0)
            for ll11l1l1l11l in l111l11llll1:
                try:
                    await ll1ll1ll11ll.message.copy_to(chat_id=int(ll11l1l1l11l))
                    ll111l11llll += 1
                    await asyncio.sleep(0.05)
                except Exception as e:
                    lll1111lllll.warning(f'Broadcast failed for {ll11l1l1l11l}: {e}')
                    lll11l1111ll += 1
            await ll1ll1ll11ll.message.reply_text(f'✅ Broadcast selesai!\n\n📤 Terkirim: {ll111l11llll}\n❌ Gagal: {lll11l1111ll}', reply_markup=l111ll11ll1l('admin_main'))
            return
        if l1l111l11l1l == 'awaiting_add_file' and ll1ll1ll11ll.message.document:
            l1l11lllllll = ADMIN_STATE.get('add_service')
            l11l11l1l1l1 = ll1ll1ll11ll.message.document
            ll1l1l1l1l11 = l11l11l1l1l1.file_name or 'upload.txt'
            if not ll1l1l1l1l11.endswith('.txt'):
                await ll1ll1ll11ll.message.reply_text('❌ Hanya file .txt yang diterima.')
                return
            ll1ll1l1ll11 = l111ll111111 / l1l11lllllll
            ll1ll1l1ll11.mkdir(parents=True, exist_ok=True)
            ll1ll111ll11 = ll1ll1l1ll11 / ll1l1l1l1l11
            l1l111ll1lll = await l11l11l1l1l1.get_file()
            await l1l111ll1lll.download_to_drive(str(ll1ll111ll11))
            l1l1ll1l1111 = l1ll1111ll1l(ll1ll111ll11)
            ADMIN_STATE.clear()
            await ll1ll1ll11ll.message.reply_text(f'✅ File ditambahkan!\n📂 {l1l11lllllll}\n📄 {ll1l1l1l1l11}\n🔢 Total: {l1l1ll1l1111} nomor', reply_markup=l111ll11ll1l('admin_main'))
            return
        if l1l111l11l1l == 'awaiting_mute_id':
            ADMIN_STATE.clear()
            try:
                l1l1111111ll = int(ll1ll1ll11ll.message.text.strip())
                l1111l11l111.setdefault('muted', {})[str(l1l1111111ll)] = {'permanent': True, 'at': datetime.now().isoformat()}
                l1111l1lll1l(l1111l11l111)
                await ll1ll1ll11ll.message.reply_text(f'✅ User {l1l1111111ll} telah di-mute.', reply_markup=l111ll11ll1l('admin_main'))
            except ValueError:
                await ll1ll1ll11ll.message.reply_text('❌ ID tidak valid.', reply_markup=l111ll11ll1l('admin_main'))
            return
        if l1l111l11l1l == 'awaiting_unmute_id':
            ADMIN_STATE.clear()
            try:
                l1l1111111ll = int(ll1ll1ll11ll.message.text.strip())
                l1111l11l111.setdefault('muted', {}).pop(str(l1l1111111ll), None)
                l1111l1lll1l(l1111l11l111)
                try:
                    await l1lllll1l111.bot.send_message(l1l1111111ll, '✅ Anda telah di-unmute.')
                except:
                    pass
                await ll1ll1ll11ll.message.reply_text(f'✅ User {l1l1111111ll} telah di-unmute.', reply_markup=l111ll11ll1l('admin_main'))
            except ValueError:
                await ll1ll1ll11ll.message.reply_text('❌ ID tidak valid.', reply_markup=l111ll11ll1l('admin_main'))
            return
        if l1l111l11l1l == 'awaiting_user_details_input':
            ADMIN_STATE.clear()
            try:
                l1l1111111ll = str(int(ll1ll1ll11ll.message.text.strip()))
                if l1l1111111ll in l1111l11l111['users']:
                    l1l11l1l1ll1 = l1111l11l111['users'][l1l1111111ll]
                    l1l1llllll1l = (datetime.now() - datetime.fromisoformat(l1l11l1l1ll1['first_seen'])).days
                    l111l1l1lll1 = f"👤 *USER DETAILS*\n\n📛 Name: {l1l11l1l1ll1.get('full_name', 'N/A')}\n🆔 ID: {l1l1111111ll}\n📅 Member since: {l1l1llllll1l} hari\n👁️ Total seen: {l1l11l1l1ll1.get('total_seen', 0)}\n⏰ Last 24h: {l1l11111l1ll(l1l11l1l1ll1)}\n🔢 Last 3: {', '.join([ll11l1llll1l['number'] for ll11l1llll1l in l1l11l1l1ll1.get('last_3', [])]) or 'None'}"
                    await ll1ll1ll11ll.message.reply_text(l111l1l1lll1, parse_mode=ParseMode.MARKDOWN, reply_markup=l111ll11ll1l('admin_main'))
                else:
                    await ll1ll1ll11ll.message.reply_text('❌ User tidak ditemukan.', reply_markup=l111ll11ll1l('admin_main'))
            except ValueError:
                await ll1ll1ll11ll.message.reply_text('❌ ID tidak valid.', reply_markup=l111ll11ll1l('admin_main'))
            return
        if l1l111l11l1l == 'awaiting_number_count':
            ADMIN_STATE.clear()
            try:
                l1l1l1ll1l1l = int(ll1ll1ll11ll.message.text.strip())
                if l1l1l1ll1l1l < 1 or l1l1l1ll1l1l > 20:
                    raise ValueError
                l1111l11l111['numbers_per_view'] = l1l1l1ll1l1l
                l1111l1lll1l(l1111l11l111)
                await ll1ll1ll11ll.message.reply_text(f'✅ Setiap tampilan akan menampilkan {l1l1l1ll1l1l} nomor.', reply_markup=l111ll11ll1l('admin_settings'))
            except ValueError:
                await ll1ll1ll11ll.message.reply_text('❌ Masukkan angka yang valid (1-20).', reply_markup=l111ll11ll1l('admin_settings'))
            return
        if l1l111l11l1l == 'awaiting_button_columns':
            ADMIN_STATE.clear()
            try:
                lllll1l1111l = int(ll1ll1ll11ll.message.text.strip())
                if lllll1l1111l < 1 or lllll1l1111l > 4:
                    raise ValueError
                l1111l11l111['button_columns'] = lllll1l1111l
                l1111l1lll1l(l1111l11l111)
                await ll1ll1ll11ll.message.reply_text(f'✅ Tombol akan ditampilkan dalam {lllll1l1111l} kolom.', reply_markup=l111ll11ll1l('admin_settings'))
            except ValueError:
                await ll1ll1ll11ll.message.reply_text('❌ Masukkan angka yang valid (1-4).', reply_markup=l111ll11ll1l('admin_settings'))
            return
    if l11lll11l11l(l1111l11l111, l1l111ll1l11):
        await ll1ll1ll11ll.message.reply_text('⛔ Anda tidak dapat menggunakan bot ini.', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('📨 SEND UNMUTE REQUEST', callback_data='send_unmute_request')]]))
        return
    l1ll1l1111ll(l1111l11l111, ll1ll1ll11ll)

async def l1l1ll1ll111(l1l11lll1ll1: Update, l111lll1l1ll: ContextTypes.DEFAULT_TYPE):
    lllll111ll1l = l1l11lll1ll1.callback_query
    await lllll111ll1l.answer()
    lll11ll1lll1 = lllll111ll1l.data
    l1llll1ll1ll = lllll111ll1l.from_user.id
    llll11ll1lll = ll11ll11lll1()
    if lll11ll1lll1 == 'noop':
        return
    if lll11ll1lll1 == 'user_main':
        await lllll111ll1l.edit_message_text('🏠 *MENU UTAMA*', parse_mode=ParseMode.MARKDOWN, reply_markup=l111l1lll1l1(l1llll1ll1ll == l1ll1l1111l1))
        return
    if lll11ll1lll1 == 'user_dashboard':
        await lll111111111(lllll111ll1l, l111lll1l1ll)
        return
    if lll11ll1lll1 == 'user_service_list':
        await ll1lll11l1ll(lllll111ll1l, l111lll1l1ll)
        return
    if lll11ll1lll1.startswith('user_country_list:'):
        lll1l11l1l11 = lll11ll1lll1.split(':', 1)[1]
        await l1l1l11llll1(lllll111ll1l, l111lll1l1ll, lll1l11l1l11)
        return
    if lll11ll1lll1.startswith('user_numbers:'):
        l1llll111111, lll1l11l1l11, lllll11l111l = lll11ll1lll1.split(':', 2)
        await ll1llll11l11(lllll111ll1l, l111lll1l1ll, lll1l11l1l11, lllll11l111l)
        return
    if lll11ll1lll1.startswith('user_refresh:'):
        l1llll111111, lll1l11l1l11, lllll11l111l = lll11ll1lll1.split(':', 2)
        await ll11ll1ll1l1(lllll111ll1l, l111lll1l1ll, lll1l11l1l11, lllll11l111l)
        return
    if lll11ll1lll1 == 'send_unmute_request':
        await l1111l1ll1l1(lllll111ll1l, l111lll1l1ll)
        return
    if l1llll1ll1ll != l1ll1l1111l1:
        await lllll111ll1l.answer('⛔ Akses ditolak.', show_alert=True)
        return
    if lll11ll1lll1 == 'admin_main':
        await lllll111ll1l.edit_message_text('⚙️ *ADMIN PANEL*', parse_mode=ParseMode.MARKDOWN, reply_markup=ll1111111l1l())
        return
    if lll11ll1lll1 == 'admin_dashboard':
        await llll1111111l(lllll111ll1l, l111lll1l1ll)
        return
    if lll11ll1lll1 == 'admin_service_list':
        await l11l11l1llll(lllll111ll1l, l111lll1l1ll)
        return
    if lll11ll1lll1.startswith('admin_country_view:'):
        lll1l11l1l11 = lll11ll1lll1.split(':', 1)[1]
        await l1llllllll11(lllll111ll1l, l111lll1l1ll, lll1l11l1l11)
        return
    if lll11ll1lll1 == 'admin_add_numbers':
        await ll11111llll1(lllll111ll1l, l111lll1l1ll)
        return
    if lll11ll1lll1.startswith('admin_add_pick_country:'):
        lll1l11l1l11 = lll11ll1lll1.split(':', 1)[1]
        await lll1l111ll11(lllll111ll1l, l111lll1l1ll, lll1l11l1l11)
        return
    if lll11ll1lll1 == 'admin_remove_numbers':
        await l11ll1ll1lll(lllll111ll1l, l111lll1l1ll)
        return
    if lll11ll1lll1.startswith('admin_remove_pick_country:'):
        lll1l11l1l11 = lll11ll1lll1.split(':', 1)[1]
        await l1l1l1lll111(lllll111ll1l, l111lll1l1ll, lll1l11l1l11)
        return
    if lll11ll1lll1.startswith('admin_remove_confirm:'):
        l1llll111111, lll1l11l1l11, lllll11l111l = lll11ll1lll1.split(':', 2)
        await l11l11111l1l(lllll111ll1l, l111lll1l1ll, lll1l11l1l11, lllll11l111l)
        return
    if lll11ll1lll1 == 'admin_broadcast':
        await l111lll1llll(lllll111ll1l, l111lll1l1ll)
        return
    if lll11ll1lll1 == 'admin_user_details':
        await l1l1111l1l1l(lllll111ll1l, l111lll1l1ll)
        return
    if lll11ll1lll1 == 'admin_mute':
        await ll1lll11llll(lllll111ll1l, l111lll1l1ll)
        return
    if lll11ll1lll1 == 'admin_unmute':
        await l1l11l1ll1ll(lllll111ll1l, l111lll1l1ll)
        return
    if lll11ll1lll1 == 'admin_notifications':
        await l1ll1l11l11l(lllll111ll1l, l111lll1l1ll)
        return
    if lll11ll1lll1.startswith('admin_do_unmute_notif:'):
        llll11l1l1l1 = int(lll11ll1lll1.split(':', 1)[1])
        await ll111l1l11l1(lllll111ll1l, l111lll1l1ll, llll11l1l1l1)
        return
    if lll11ll1lll1 == 'admin_settings':
        await lll1l111lll1(lllll111ll1l, l111lll1l1ll)
        return
    if lll11ll1lll1 == 'admin_toggle_service':
        await l11l11l11ll1(lllll111ll1l, l111lll1l1ll)
        return
    if lll11ll1lll1 == 'admin_set_number_count':
        await l11l1l1lllll(lllll111ll1l, l111lll1l1ll)
        return
    if lll11ll1lll1 == 'admin_set_button_columns':
        await llll1l1ll1ll(lllll111ll1l, l111lll1l1ll)
        return

async def llll1ll1111l(lll1l111l111: object, lll1111l11ll: ContextTypes.DEFAULT_TYPE):
    ll1l1ll1111l = lll1111l11ll.error
    if isinstance(ll1l1ll1111l, Conflict):
        lll1111lllll.warning('Conflict error - menunggu...')
        await asyncio.sleep(5)
    elif isinstance(ll1l1ll1111l, NetworkError):
        lll1111lllll.warning(f'Network error: {ll1l1ll1111l}')
    else:
        lll1111lllll.error(f'Error: {ll1l1ll1111l}', exc_info=ll1l1ll1111l)

def l111l11ll11l():
    l111ll111111.mkdir(exist_ok=True)
    for ll1llll11l1l in ['Google', 'Facebook', 'Telegram', 'WhatsApp', 'Instagram', 'Twitter', 'TikTok']:
        (l111ll111111 / ll1llll11l1l).mkdir(exist_ok=True)
    l11ll111ll1l = Application.builder().token(lll1l1ll11l1).connect_timeout(30).read_timeout(30).write_timeout(30).build()
    l11ll111ll1l.add_handler(CommandHandler('start', l1lll1ll1l11))
    l11ll111ll1l.add_handler(CommandHandler('admin', lllll1l1l1l1))
    l11ll111ll1l.add_handler(CallbackQueryHandler(l1l1ll1ll111))
    l11ll111ll1l.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, l11ll111lll1))
    l11ll111ll1l.add_error_handler(llll1ll1111l)
    lll1111lllll.info('Bot is running...')
    l11ll111ll1l.run_polling(drop_pending_updates=True, allowed_updates=['message', 'callback_query'])
if __name__ == '__main__':
    l111l11ll11l()
