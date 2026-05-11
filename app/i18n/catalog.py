"""UI strings: English base + per-locale patches (fall back to English if a key is missing)."""

from __future__ import annotations

from typing import Any

from app.i18n.patches_full import (
    AR_PATCH,
    DE_PATCH,
    FIL_PATCH,
    FR_PATCH,
    ID_PATCH,
    IT_PATCH,
    PT_PATCH,
    RU_PATCH,
)

_VALID = frozenset({"ar", "de", "en", "es", "fr", "id", "it", "fil", "pt", "ru", "hi"})

EN: dict[str, str] = {
    # —— common ——
    "kb.back": "⬅️ Back",
    "kb.main_menu": "🔙 Main Menu",
    "kb.support": "📞 Support",
    "kb.support_dm": "💬 Message @{u}",
    "kb.support_caps": "😊 SUPPORT",
    "kb.start_trading": "🚀 Start Trading",
    "kb.get_tokens": "💎 Get Tokens",
    "kb.deposit": "💰 Deposit",
    "kb.open_deposit_page": "💰 Open deposit page",
    "kb.withdraw": "🤑 Withdraw",
    "kb.settings": "🎯 Settings",
    "kb.demo_real": "🎮 Demo / Real",
    "kb.logout": "🚪 Logout",
    "kb.account_main": "⬅️ Main Menu",
    # —— demo bets ——
    "kb.demo_1": "1 $",
    "kb.demo_1_5": "1.5 $",
    "kb.demo_2": "2 $",
    "kb.demo_2_5": "2.5 $",
    "kb.demo_5": "⚠️ 5 $ ⚠️",
    "kb.demo_custom": "✏️ Custom amount",
    # —— trade pick ——
    "kb.trade_demo": "🎮 Demo Account",
    "kb.trade_real": "💰 Real Account",
    # —— reply keyboard ——
    "kb.reply_deposit": "💰 Deposit",
    "kb.reply_my_account": "📱 My Account",
    "kb.reply_status": "🏆 My Status",
    "kb.reply_support": "📞 Support",
    "kb.reply_faq": "📘 F.A.Q",
    # —— main debug menu ——
    "kb.main_settings": "settings",
    "kb.main_status": "status",
    "kb.main_help": "help",
    "kb.main_disable_trading": "disable trading",
    "kb.main_enable_trading": "enable trading",
    # —— autotrade ——
    "kb.auto_precision": "Precision strike 🎯",
    "kb.auto_high": "High-Profit ⚡",
    "kb.auto_balanced": "Balanced 📊",
    "kb.auto_conservative": "Conservative 🛡️",
    "kb.auto_manual": "🔧 Manual settings",
    # —— manual compact ——
    "kb.manual_max_steps": "📊 Max steps",
    "kb.manual_max_cycles": "✨ Max cycles",
    # —— expiry row ——
    "kb.expiry_sec": "{n} sec",
    # —— PO account ——
    "kb.po_connect": "📲 Connect PO",
    "kb.po_linked": "✅ PO ({email})",
    "kb.po_session": "🔐 PO session",
    "kb.session_sync_uid": "🆔 Refresh UID",
    "kb.session_sync_balance": "💵 Refresh balances",
    "kb.session_back_account": "⬅️ My Account",
    # —— language grid (labels localize) ——
    "lang.ar": "🇸🇦 Arabic",
    "lang.de": "🇩🇪 Deutsch",
    "lang.en": "🇬🇧 English",
    "lang.es": "🇪🇸 Español",
    "lang.fr": "🇫🇷 Français",
    "lang.id": "🇮🇩 Indonesia",
    "lang.it": "🇮🇹 Italian",
    "lang.fil": "🇵🇭 Filipino",
    "lang.pt": "🇧🇷 Português",
    "lang.ru": "🇷🇺 Русский",
    "lang.hi": "🇮🇳 Hindi",
    # —— trading mode ——
    "kb.mode_auto": "🎮 Auto Trade",
    "kb.mode_manual": "⚙️ Manual Trade",
    # —— settings hub ——
    "kb.hub_autotrade": "⚙️ Autotrade settings",
    "kb.hub_expiry": "⏳ Expiration time",
    "kb.hub_mode": "⚙️ Mode: manual/auto",
    "kb.hub_language": "🌐 Language",
    # —— legacy settings grid ——
    "kb.legacy_stake": "set stake",
    "kb.legacy_expiry": "set expiry",
    "kb.legacy_mg_on": "martingale on/off",
    "kb.legacy_mg_levels": "mg levels (1-20)",
    "kb.legacy_mg_csv": "mg multipliers csv",
    "kb.legacy_assets": "set assets",
    "kb.legacy_strategy": "strategy on/off",
    "kb.legacy_min_payout": "min payout %",
    "kb.legacy_max_stake_trade": "max stake/trade",
    "kb.legacy_max_stake_day": "max stake/day",
    "kb.legacy_max_trades": "max trades/day",
    "kb.legacy_max_loss": "max loss/day",
    "kb.legacy_cooldown": "cooldown",
    "kb.legacy_loss_streak": "loss streak",
    "kb.legacy_back": "back",
    # —— captions / messages (HTML where noted) ——
    "caption.settings_hub": (
        "⚙️ <b>Trading Settings</b>\n\n"
        "🎯 Autotrade parameters — set up settings for autobot\n"
        "⏳ Expiry time — choose time for each trade"
    ),
    "caption.settings_hub_auto_only": (
        "⚙️ <b>Trading Settings</b>\n\n"
        "🎯 Autotrade parameters — set up settings for autobot\n"
        "⏳ Expiry time — choose time for each trade\n"
        "🎮 <b>Autotrade only</b> (manual mode is disabled for this bot)"
    ),
    "caption.expiration": (
        "⌛ <b>Expiration Time</b>\n\n"
        "Current: {seconds}s\n\n"
        "💡 Best results usually at 30 sec."
    ),
    "msg.auto_trade_only": "This bot runs in autotrade mode only.",
    "msg.choose_language": "🌐 Choose language:",
    "msg.language_updated": "Language updated.",
    "caption.autotrade": (
        "🎯 <b>Autotrade Settings</b>\n\n"
        "Current strategy: {title} {emoji}\n"
        "◆ Max steps: {ms}\n"
        "◆ Max deals: {md}\n"
        "◆ Expiry: {ex}s"
    ),
    "caption.manual_compact": (
        "🔧 <b>Manual settings</b>\n\n" "◆ <b>Max steps:</b> {ms}\n" "◆ <b>Max cycles:</b> {mc}"
    ),
    "caption.max_mg_steps": "📊 <b>Max martingale steps:</b>",
    "caption.max_cycles": "✨ <b>Max cycles (trades per session):</b>",
    "strat.precision": "Precision strike",
    "strat.high_profit": "High-Profit",
    "strat.balanced": "Balanced",
    "strat.conservative": "Conservative",
    # —— start dashboard (plain text) ——
    "dash.linked_email": "{pad}📧 Linked account: {email}",
    "dash.pocket_uid": "{pad}🆔 PO UID: {uid}",
    "dash.login_successful": "✅ Login successful.",
    "dash.broker_pending": "{pad}⏳ Live balances may show N/A until the broker API syncs.",
    "dash.trading_mode": "{pad}🎮 Trading mode: {mode}",
    "dash.real_balance": "{pad}💰 Real balance: {real_bal}",
    "dash.demo_balance": "{pad}🎮 Demo balance: {demo_bal}",
    "dash.tokens": "{pad}💎 Tokens: {tokens}",
    "dash.status": "{pad}{tier_icon} Status: {tier}",
    "dash.accuracy": "{pad}📊 Signal accuracy: {accuracy}",
    # —— demo / trade screens ——
    "caption.demo_account": (
        "🎮 <b>DEMO ACCOUNT</b>\n" "Levers: {levels} (auto)\n" "Choose bet amount 👇"
    ),
    "caption.demo_lever": (
        "🎮 <b>Manual demo</b>\n\n"
        "Pick lever (martingale depth). ⭐ <b>7</b> is recommended.\n\n"
        "<i>Trade duration: <b>{expiry}s</b> (set by operator).</i>"
    ),
    "kb.demo_lever_7_rec": "⭐ 7 (recommended)",
    "kb.demo_stop_results": "🗑️ Stop and see results",
    "kb.demo_start_again": "▶️ ▶️ Start again",
    "caption.demo_session_progress_title": "🤖 <b>Trading in progress</b>",
    "caption.demo_session_result_profit": "🏆 Profit! Trade completed successfully ✅",
    "caption.demo_session_result_loss": "📉 Session closed",
    "caption.demo_session_result_body": (
        "🎯 Result: ${result}\n"
        "💰 Balance: ${balance}\n"
        "💎 Tokens spent: {tokens_spent}\n\n"
        "👇 Choose next step 👇"
    ),
    "kb.demo_support_external": "📞 Support ↗️",
    "kb.tf_1": "⏱️ 1 min",
    "kb.tf_5": "⏱️ 5 min",
    "kb.tf_15": "⏱️ 15 min",
    "caption.register": "To get started, create a Pocket Option account 👇",
    "kb.register_on_po": "🚀 Register on PO",
    "kb.ive_registered": "✅ I've registered",
    "caption.trade_where": "🎯 Choose where you want to trade:",
    # —— my account ——
    "caption.my_account": (
        "📱 <b>My Account</b>\n\n"
        "🏆 <b>Status:</b> {tier_e} {tier}\n\n"
        "💰 <b>STATISTICS REAL ACCOUNT</b>\n"
        "💵 <b>Balance:</b> {real_bal}\n"
        "📊 <b>Series:</b> {real_n} | <b>Profit:</b> {real_pnl}\n\n"
        "🎮 <b>STATISTICS DEMO ACCOUNT</b>\n"
        "💵 <b>Balance:</b> {demo_bal}\n"
        "📊 <b>Series:</b> {demo_n} | <b>Profit:</b> {demo_pnl}\n\n"
        "💎 <b>Tokens:</b> {tokens_bal}"
    ),
    "caption.po_session_head": "🔐 <b>Pocket Option session</b>\n\n",
    "caption.po_session_creds": "📧 <b>Email:</b> {email}\n✅ Credentials saved\n\n",
    "caption.po_session_no_creds": "⚠️ No saved credentials — use <b>Connect PO</b> on My Account.\n\n",
    "caption.po_session_uid": "🆔 <b>UID:</b> {uid}\n\n",
    "caption.po_session_uid_missing": "🆔 <b>UID:</b> not set\n\n",
    "caption.po_session_bal": (
        "💵 <b>Cached balances</b>\n"
        "Real: {real} | Demo: {demo}\n"
        "🕐 <b>Updated:</b> {updated}\n\n"
    ),
    "caption.po_session_bal_unknown": "💵 <b>Cached balances:</b> none yet\n\n",
    "caption.po_session_aff": "📋 <b>Affiliate:</b> {aff}\n\n",
    "caption.po_session_logs_title": "<b>Recent broker logins</b>\n",
    "caption.po_session_logs_empty": "<i>No login history yet.</i>\n",
    "caption.po_session_log_ok": "• {t} ✅\n",
    "caption.po_session_log_fail": "• {t} ❌ <code>{reason}</code>\n",
    "msg.session_login_failed": "Broker login failed. Check PO API or try again.",
    # —— real mode gate ——
    "gate.real_unavailable": (
        "⚠️ Real mode unavailable — balance is empty\n\n"
        "🔥 Unlock real trading: press 💰 DEPOSIT to fund your account\n\n"
        "🎁 First deposit gets +100% bonus — instantly doubles your balance\n\n"
        "😊 Questions? Press SUPPORT — we'll help"
    ),
}

HI_PATCH: dict[str, str] = {
    "kb.back": "⬅️ वापस",
    "kb.main_menu": "🔙 मुख्य मेनू",
    "kb.support": "📞 सहायता",
    "kb.support_dm": "💬 @{u} को संदेश",
    "kb.support_caps": "😊 सहायता",
    "kb.start_trading": "🚀 ट्रेडिंग शुरू करें",
    "kb.get_tokens": "💎 टोकन प्राप्त करें",
    "kb.deposit": "💰 जमा",
    "kb.open_deposit_page": "💰 जमा पृष्ठ खोलें",
    "kb.withdraw": "🤑 निकासी",
    "kb.settings": "🎯 सेटिंग्स",
    "kb.demo_real": "🎮 डेमो / रियल",
    "kb.logout": "🚪 लॉग आउट",
    "kb.account_main": "⬅️ मुख्य मेनू",
    "kb.demo_custom": "✏️ कस्टम राशि",
    "kb.trade_demo": "🎮 डेमो खाता",
    "kb.trade_real": "💰 रियल खाता",
    "kb.reply_deposit": "💰 जमा",
    "kb.reply_my_account": "📱 मेरा खाता",
    "kb.reply_status": "🏆 मेरी स्थिति",
    "kb.reply_support": "📞 सहायता",
    "kb.reply_faq": "📘 अक्सर पूछे जाने वाले प्रश्न",
    "kb.main_settings": "सेटिंग्स",
    "kb.main_status": "स्थिति",
    "kb.main_help": "मदद",
    "kb.main_disable_trading": "ट्रेडिंग बंद करें",
    "kb.main_enable_trading": "ट्रेडिंग चालू करें",
    "kb.auto_precision": "प्रिसिजन स्ट्राइक 🎯",
    "kb.auto_high": "उच्च लाभ ⚡",
    "kb.auto_balanced": "संतुलित 📊",
    "kb.auto_conservative": "सुरक्षित 🛡️",
    "kb.auto_manual": "🔧 मैन्युअल सेटिंग्स",
    "kb.manual_max_steps": "📊 अधिकतम स्टेप",
    "kb.manual_max_cycles": "✨ अधिकतम चक्र",
    "kb.expiry_sec": "{n} सेकंड",
    "kb.po_connect": "📲 PO कनेक्ट करें",
    "kb.po_linked": "✅ PO ({email})",
    "lang.ar": "🇸🇦 अरबी",
    "lang.de": "🇩🇪 जर्मन",
    "lang.en": "🇬🇧 अंग्रेज़ी",
    "lang.es": "🇪🇸 स्पेनिश",
    "lang.fr": "🇫🇷 फ़्रेंच",
    "lang.id": "🇮🇩 इंडोनेशियाई",
    "lang.it": "🇮🇹 इटैलियन",
    "lang.fil": "🇵🇭 फिलिपीनो",
    "lang.pt": "🇧🇷 पुर्तगाली",
    "lang.ru": "🇷🇺 रूसी",
    "lang.hi": "🇮🇳 हिन्दी",
    "kb.mode_auto": "🎮 ऑटो ट्रेड",
    "kb.mode_manual": "⚙️ मैन्युअल ट्रेड",
    "kb.hub_autotrade": "⚙️ ऑटोट्रेड सेटिंग्स",
    "kb.hub_expiry": "⏳ समाप्ति समय",
    "kb.hub_mode": "⚙️ मोड: मैन्युअल/ऑटो",
    "kb.hub_language": "🌐 भाषा",
    "kb.legacy_stake": "दांव सेट करें",
    "kb.legacy_expiry": "समाप्ति सेट करें",
    "kb.legacy_mg_on": "मार्टिंगेल चालू/बंद",
    "kb.legacy_mg_levels": "एमजी स्तर (1-20)",
    "kb.legacy_mg_csv": "एमजी गुणक csv",
    "kb.legacy_assets": "संपत्ति सेट करें",
    "kb.legacy_strategy": "रणनीति चालू/बंद",
    "kb.legacy_min_payout": "न्यूनतम भुगतान %",
    "kb.legacy_max_stake_trade": "अधिकतम दांव/ट्रेड",
    "kb.legacy_max_stake_day": "अधिकतम दांव/दिन",
    "kb.legacy_max_trades": "अधिकतम ट्रेड/दिन",
    "kb.legacy_max_loss": "अधिकतम नुकसान/दिन",
    "kb.legacy_cooldown": "कूलडाउन",
    "kb.legacy_loss_streak": "हार की लकीर",
    "kb.legacy_back": "वापस",
    "caption.settings_hub": (
        "⚙️ <b>ट्रेडिंग सेटिंग्स</b>\n\n"
        "🎯 ऑटोट्रेड पैरामीटर — ऑटोबॉट के लिए सेटअप\n"
        "⏳ समाप्ति समय — प्रति ट्रेड समय चुनें\n"
        "🎮 मोड — मैन्युअल या ऑटोट्रेड"
    ),
    "caption.expiration": (
        "⌛ <b>समाप्ति समय</b>\n\n"
        "वर्तमान: {seconds}s\n\n"
        "💡 सबसे अच्छे परिणाम आमतौर पर 30 सेकंड पर।"
    ),
    "caption.trading_mode": (
        "⚙️ <b>ट्रेडिंग मोड</b>\n\n"
        "⚙️ मैन्युअल ट्रेड — क्लासिक मैन्युअल मोड।\n\n"
        "🎮 ऑटो ट्रेड [विशेष] — AI एल्गोरिथम स्वचालित ट्रेड करता है।"
    ),
    "msg.choose_language": "🌐 भाषा चुनें:",
    "msg.language_updated": "भाषा अपडेट हो गई।",
    "caption.autotrade": (
        "🎯 <b>ऑटोट्रेड सेटिंग्स</b>\n\n"
        "वर्तमान रणनीति: {title} {emoji}\n"
        "◆ अधिकतम स्टेप: {ms}\n"
        "◆ अधिकतम डील: {md}\n"
        "◆ समाप्ति: {ex}s"
    ),
    "caption.manual_compact": (
        "🔧 <b>मैन्युअल सेटिंग्स</b>\n\n"
        "◆ <b>अधिकतम स्टेप:</b> {ms}\n"
        "◆ <b>अधिकतम चक्र:</b> {mc}"
    ),
    "caption.max_mg_steps": "📊 <b>अधिकतम मार्टिंगेल स्टेप:</b>",
    "caption.max_cycles": "✨ <b>अधिकतम चक्र (सत्र में ट्रेड):</b>",
    "strat.precision": "प्रिसिजन स्ट्राइक",
    "strat.high_profit": "उच्च लाभ",
    "strat.balanced": "संतुलित",
    "strat.conservative": "सुरक्षित",
    "dash.trading_mode": "{pad}🎮 ट्रेडिंग मोड: {mode}",
    "dash.pocket_uid": "{pad}🆔 PO UID: {uid}",
    "dash.real_balance": "{pad}💰 रियल बैलेंस: {real_bal}",
    "dash.demo_balance": "{pad}🎮 डेमो बैलेंस: {demo_bal}",
    "dash.tokens": "{pad}💎 टोकन: {tokens}",
    "dash.status": "{pad}{tier_icon} स्थिति: {tier}",
    "dash.accuracy": "{pad}📊 सिग्नल सटीकता: {accuracy}",
    "caption.demo_account": (
        "🎮 <b>डेमो खाता</b>\n" "लेवर: {levels} (ऑटो)\n" "दांव राशि चुनें 👇"
    ),
    "caption.trade_where": "🎯 कहाँ ट्रेड करना चाहते हैं:",
    "caption.my_account": (
        "📱 <b>मेरा खाता</b>\n\n"
        "🏆 <b>स्थिति:</b> {tier_e} {tier}\n\n"
        "💰 <b>रियल खाता आँकड़े</b>\n"
        "💵 <b>बैलेंस:</b> {real_bal}\n"
        "📊 <b>श्रृंखला:</b> {real_n} | <b>लाभ:</b> {real_pnl}\n\n"
        "🎮 <b>डेमो खाता आँकड़े</b>\n"
        "💵 <b>बैलेंस:</b> {demo_bal}\n"
        "📊 <b>श्रृंखला:</b> {demo_n} | <b>लाभ:</b> {demo_pnl}\n\n"
        "💎 <b>टोकन:</b> {tokens_bal}"
    ),
    "gate.real_unavailable": (
        "⚠️ रियल मोड उपलब्ध नहीं — बैलेंस खाली है\n\n"
        "🔥 रियल ट्रेडिंग अनलॉक करें: 💰 जमा दबाएँ\n\n"
        "🎁 पहली जमा पर +100% बोनस\n\n"
        "😊 प्रश्न? सहायता दबाएँ"
    ),
}

ES_PATCH: dict[str, str] = {
    "kb.back": "⬅️ Atrás",
    "kb.main_menu": "🔙 Menú principal",
    "kb.support": "📞 Soporte",
    "kb.support_dm": "💬 Escribir a @{u}",
    "kb.support_caps": "😊 SOPORTE",
    "kb.start_trading": "🚀 Empezar a operar",
    "kb.get_tokens": "💎 Obtener tokens",
    "kb.deposit": "💰 Depósito",
    "kb.open_deposit_page": "💰 Abrir página de depósito",
    "kb.withdraw": "🤑 Retirar",
    "kb.settings": "🎯 Ajustes",
    "kb.demo_real": "🎮 Demo / Real",
    "kb.logout": "🚪 Cerrar sesión",
    "kb.account_main": "⬅️ Menú principal",
    "kb.demo_custom": "✏️ Importe personalizado",
    "kb.trade_demo": "🎮 Cuenta demo",
    "kb.trade_real": "💰 Cuenta real",
    "kb.reply_deposit": "💰 Depósito",
    "kb.reply_my_account": "📱 Mi cuenta",
    "kb.reply_status": "🏆 Mi estado",
    "kb.reply_support": "📞 Soporte",
    "kb.reply_faq": "📘 Preguntas frecuentes",
    "kb.main_settings": "ajustes",
    "kb.main_status": "estado",
    "kb.main_help": "ayuda",
    "kb.main_disable_trading": "desactivar trading",
    "kb.main_enable_trading": "activar trading",
    "kb.auto_precision": "Precisión 🎯",
    "kb.auto_high": "Alto rendimiento ⚡",
    "kb.auto_balanced": "Equilibrado 📊",
    "kb.auto_conservative": "Conservador 🛡️",
    "kb.auto_manual": "🔧 Ajustes manuales",
    "kb.manual_max_steps": "📊 Pasos máx.",
    "kb.manual_max_cycles": "✨ Ciclos máx.",
    "kb.expiry_sec": "{n} s",
    "kb.po_connect": "📲 Conectar PO",
    "kb.po_linked": "✅ PO ({email})",
    "lang.ar": "🇸🇦 Árabe",
    "lang.de": "🇩🇪 Alemán",
    "lang.en": "🇬🇧 Inglés",
    "lang.es": "🇪🇸 Español",
    "lang.fr": "🇫🇷 Francés",
    "lang.id": "🇮🇩 Indonesio",
    "lang.it": "🇮🇹 Italiano",
    "lang.fil": "🇵🇭 Filipino",
    "lang.pt": "🇧🇷 Portugués",
    "lang.ru": "🇷🇺 Ruso",
    "lang.hi": "🇮🇳 Hindi",
    "kb.mode_auto": "🎮 Auto trading",
    "kb.mode_manual": "⚙️ Trading manual",
    "kb.hub_autotrade": "⚙️ Ajustes autotrading",
    "kb.hub_expiry": "⏳ Tiempo de expiración",
    "kb.hub_mode": "⚙️ Modo: manual/auto",
    "kb.hub_language": "🌐 Idioma",
    "kb.legacy_stake": "establecer apuesta",
    "kb.legacy_expiry": "establecer expiración",
    "kb.legacy_mg_on": "martingala on/off",
    "kb.legacy_mg_levels": "niveles mg (1-20)",
    "kb.legacy_mg_csv": "multiplicadores mg csv",
    "kb.legacy_assets": "activos",
    "kb.legacy_strategy": "estrategia on/off",
    "kb.legacy_min_payout": "pago mín. %",
    "kb.legacy_max_stake_trade": "apuesta máx./operación",
    "kb.legacy_max_stake_day": "apuesta máx./día",
    "kb.legacy_max_trades": "operaciones máx./día",
    "kb.legacy_max_loss": "pérdida máx./día",
    "kb.legacy_cooldown": "enfriamiento",
    "kb.legacy_loss_streak": "racha de pérdidas",
    "kb.legacy_back": "atrás",
    "caption.settings_hub": (
        "⚙️ <b>Ajustes de trading</b>\n\n"
        "🎯 Parámetros de autotrading\n"
        "⏳ Tiempo de expiración por operación\n"
        "🎮 Modo — Manual o Autotrading"
    ),
    "caption.expiration": (
        "⌛ <b>Tiempo de expiración</b>\n\n"
        "Actual: {seconds}s\n\n"
        "💡 Mejor rendimiento suele ser a 30 s."
    ),
    "caption.trading_mode": (
        "⚙️ <b>Modo de trading</b>\n\n"
        "⚙️ Trading manual — modo clásico.\n\n"
        "🎮 Auto trading [EXCLUSIVO] — el algoritmo opera automáticamente."
    ),
    "msg.choose_language": "🌐 Elija idioma:",
    "msg.language_updated": "Idioma actualizado.",
    "caption.autotrade": (
        "🎯 <b>Ajustes autotrading</b>\n\n"
        "Estrategia actual: {title} {emoji}\n"
        "◆ Pasos máx.: {ms}\n"
        "◆ Operaciones máx.: {md}\n"
        "◆ Expiración: {ex}s"
    ),
    "caption.manual_compact": (
        "🔧 <b>Ajustes manuales</b>\n\n"
        "◆ <b>Pasos máx.:</b> {ms}\n"
        "◆ <b>Ciclos máx.:</b> {mc}"
    ),
    "caption.max_mg_steps": "📊 <b>Pasos máx. martingala:</b>",
    "caption.max_cycles": "✨ <b>Ciclos máx. (operaciones por sesión):</b>",
    "strat.precision": "Precisión",
    "strat.high_profit": "Alto rendimiento",
    "strat.balanced": "Equilibrado",
    "strat.conservative": "Conservador",
    "dash.trading_mode": "{pad}🎮 Modo: {mode}",
    "dash.real_balance": "{pad}💰 Saldo real: {real_bal}",
    "dash.demo_balance": "{pad}🎮 Saldo demo: {demo_bal}",
    "dash.tokens": "{pad}💎 Tokens: {tokens}",
    "dash.status": "{pad}{tier_icon} Estado: {tier}",
    "dash.accuracy": "{pad}📊 Precisión señal: {accuracy}",
    "caption.demo_account": (
        "🎮 <b>CUENTA DEMO</b>\n" "Palancas: {levels} (auto)\n" "Elija apuesta 👇"
    ),
    "caption.trade_where": "🎯 ¿Dónde quiere operar?",
    "caption.my_account": (
        "📱 <b>Mi cuenta</b>\n\n"
        "🏆 <b>Estado:</b> {tier_e} {tier}\n\n"
        "💰 <b>ESTADÍSTICAS CUENTA REAL</b>\n"
        "💵 <b>Saldo:</b> {real_bal}\n"
        "📊 <b>Serie:</b> {real_n} | <b>Beneficio:</b> {real_pnl}\n\n"
        "🎮 <b>ESTADÍSTICAS CUENTA DEMO</b>\n"
        "💵 <b>Saldo:</b> {demo_bal}\n"
        "📊 <b>Serie:</b> {demo_n} | <b>Beneficio:</b> {demo_pnl}\n\n"
        "💎 <b>Tokens:</b> {tokens_bal}"
    ),
    "gate.real_unavailable": (
        "⚠️ Modo real no disponible — saldo vacío\n\n"
        "🔥 Desbloquee el trading real: pulse 💰 DEPÓSITO\n\n"
        "🎁 Primer depósito +100 % de bono\n\n"
        "😊 ¿Dudas? Pulse SOPORTE"
    ),
}

_PATCHES: dict[str, dict[str, str]] = {
    "ar": AR_PATCH,
    "de": DE_PATCH,
    "es": ES_PATCH,
    "fr": FR_PATCH,
    "hi": HI_PATCH,
    "id": ID_PATCH,
    "it": IT_PATCH,
    "fil": FIL_PATCH,
    "pt": PT_PATCH,
    "ru": RU_PATCH,
}


def normalize_lang(code: str | None) -> str:
    c = (code or "en").strip().lower()
    return c if c in _VALID else "en"


def tr(lang: str | None, key: str, **kwargs: Any) -> str:
    lang_n = normalize_lang(lang)
    raw = EN[key]
    if lang_n != "en":
        raw = _PATCHES.get(lang_n, {}).get(key, raw)
    if kwargs:
        return raw.format(**kwargs)
    return raw
