"""Full UI patches for all languages offered in the language picker (non-en/hi/es)."""

from __future__ import annotations

# Arabic
AR_PATCH: dict[str, str] = {
    "kb.back": "⬅️ رجوع",
    "kb.main_menu": "🔙 القائمة الرئيسية",
    "kb.support": "📞 الدعم",
    "kb.support_dm": "💬 مراسلة @{u}",
    "kb.support_caps": "😊 الدعم",
    "kb.start_trading": "🚀 ابدأ التداول",
    "kb.get_tokens": "💎 احصل على الرموز",
    "kb.deposit": "💰 إيداع",
    "kb.open_deposit_page": "💰 فتح صفحة الإيداع",
    "kb.withdraw": "🤑 سحب",
    "kb.settings": "🎯 الإعدادات",
    "kb.demo_real": "🎮 تجريبي / حقيقي",
    "kb.logout": "🚪 تسجيل الخروج",
    "kb.account_main": "⬅️ القائمة الرئيسية",
    "kb.demo_custom": "✏️ مبلغ مخصص",
    "kb.trade_demo": "🎮 حساب تجريبي",
    "kb.trade_real": "💰 حساب حقيقي",
    "kb.reply_deposit": "💰 إيداع",
    "kb.reply_my_account": "📱 حسابي",
    "kb.reply_status": "🏆 حالتي",
    "kb.reply_support": "📞 الدعم",
    "kb.reply_faq": "📘 الأسئلة الشائعة",
    "kb.main_settings": "إعدادات",
    "kb.main_status": "الحالة",
    "kb.main_help": "مساعدة",
    "kb.main_disable_trading": "تعطيل التداول",
    "kb.main_enable_trading": "تفعيل التداول",
    "kb.auto_precision": "ضربة دقيقة 🎯",
    "kb.auto_high": "ربح عالٍ ⚡",
    "kb.auto_balanced": "متوازن 📊",
    "kb.auto_conservative": "حذر 🛡️",
    "kb.auto_manual": "🔧 إعدادات يدوية",
    "kb.manual_max_steps": "📊 أقصى خطوات",
    "kb.manual_max_cycles": "✨ أقصى دورات",
    "kb.expiry_sec": "{n} ث",
    "kb.po_connect": "📲 ربط PO",
    "kb.po_linked": "✅ PO ({email})",
    "lang.ar": "🇸🇦 العربية",
    "lang.de": "🇩🇪 ألماني",
    "lang.en": "🇬🇧 إنجليزي",
    "lang.es": "🇪🇸 إسباني",
    "lang.fr": "🇫🇷 فرنسي",
    "lang.id": "🇮🇩 إندونيسي",
    "lang.it": "🇮🇹 إيطالي",
    "lang.fil": "🇵🇭 فلبيني",
    "lang.pt": "🇧🇷 برتغالي",
    "lang.ru": "🇷🇺 روسي",
    "lang.hi": "🇮🇳 هندي",
    "kb.mode_auto": "🎮 تداول تلقائي",
    "kb.mode_manual": "⚙️ تداول يدوي",
    "kb.hub_autotrade": "⚙️ إعدادات التداول الآلي",
    "kb.hub_expiry": "⏳ وقت الانتهاء",
    "kb.hub_mode": "⚙️ الوضع: يدوي/تلقائي",
    "kb.hub_language": "🌐 اللغة",
    "kb.legacy_stake": "تعيين الرهان",
    "kb.legacy_expiry": "تعيين الانتهاء",
    "kb.legacy_mg_on": "مارتينجيل تشغيل/إيقاف",
    "kb.legacy_mg_levels": "مستويات mg (1-20)",
    "kb.legacy_mg_csv": "مضاعفات mg csv",
    "kb.legacy_assets": "تعيين الأصول",
    "kb.legacy_strategy": "استراتيجية تشغيل/إيقاف",
    "kb.legacy_min_payout": "دفع أدنى %",
    "kb.legacy_max_stake_trade": "أقصى رهان/صفقة",
    "kb.legacy_max_stake_day": "أقصى رهان/يوم",
    "kb.legacy_max_trades": "أقصى صفقات/يوم",
    "kb.legacy_max_loss": "أقصى خسارة/يوم",
    "kb.legacy_cooldown": "تبريد",
    "kb.legacy_loss_streak": "سلسلة خسائر",
    "kb.legacy_back": "رجوع",
    "caption.settings_hub": (
        "⚙️ <b>إعدادات التداول</b>\n\n"
        "🎯 معاملات التداول الآلي\n"
        "⏳ وقت انتهاء كل صفقة\n"
        "🎮 الوضع — يدوي أو آلي"
    ),
    "caption.expiration": (
        "⌛ <b>وقت الانتهاء</b>\n\n"
        "الحالي: {seconds}s\n\n"
        "💡 أفضل النتائج غالباً عند 30 ثانية."
    ),
    "caption.trading_mode": (
        "⚙️ <b>وضع التداول</b>\n\n"
        "⚙️ تداول يدوي — الوضع الكلاسيكي.\n\n"
        "🎮 تداول آلي [حصري] — يتداول الذكاء الاصطناعي تلقائياً."
    ),
    "msg.choose_language": "🌐 اختر اللغة:",
    "msg.language_updated": "تم تحديث اللغة.",
    "caption.autotrade": (
        "🎯 <b>إعدادات التداول الآلي</b>\n\n"
        "الاستراتيجية الحالية: {title} {emoji}\n"
        "◆ أقصى خطوات: {ms}\n"
        "◆ أقصى صفقات: {md}\n"
        "◆ الانتهاء: {ex}s"
    ),
    "caption.manual_compact": (
        "🔧 <b>إعدادات يدوية</b>\n\n"
        "◆ <b>أقصى خطوات:</b> {ms}\n"
        "◆ <b>أقصى دورات:</b> {mc}"
    ),
    "caption.max_mg_steps": "📊 <b>أقصى خطوات مارتينجيل:</b>",
    "caption.max_cycles": "✨ <b>أقصى دورات (صفقات لكل جلسة):</b>",
    "strat.precision": "ضربة دقيقة",
    "strat.high_profit": "ربح عالٍ",
    "strat.balanced": "متوازن",
    "strat.conservative": "حذر",
    "dash.trading_mode": "{pad}🎮 وضع التداول: {mode}",
    "dash.real_balance": "{pad}💰 الرصيد الحقيقي: {real_bal}",
    "dash.demo_balance": "{pad}🎮 رصيد تجريبي: {demo_bal}",
    "dash.tokens": "{pad}💎 الرموز: {tokens}",
    "dash.status": "{pad}{tier_icon} الحالة: {tier}",
    "dash.accuracy": "{pad}📊 دقة الإشارة: {accuracy}",
    "caption.demo_account": (
        "🎮 <b>حساب تجريبي</b>\n" "الرافعات: {levels} (تلقائي)\n" "اختر مبلغ الرهان 👇"
    ),
    "caption.trade_where": "🎯 أين تريد التداول؟",
    "caption.my_account": (
        "📱 <b>حسابي</b>\n\n"
        "🏆 <b>الحالة:</b> {tier_e} {tier}\n\n"
        "💰 <b>إحصائيات الحساب الحقيقي</b>\n"
        "💵 <b>الرصيد:</b> {real_bal}\n"
        "📊 <b>السلسلة:</b> {real_n} | <b>الربح:</b> {real_pnl}\n\n"
        "🎮 <b>إحصائيات الحساب التجريبي</b>\n"
        "💵 <b>الرصيد:</b> {demo_bal}\n"
        "📊 <b>السلسلة:</b> {demo_n} | <b>الربح:</b> {demo_pnl}\n\n"
        "💎 <b>الرموز:</b> {tokens_bal}"
    ),
    "gate.real_unavailable": (
        "⚠️ الوضع الحقيقي غير متاح — الرصيد فارغ\n\n"
        "🔥 فعّل التداول الحقيقي: اضغط 💰 إيداع\n\n"
        "🎁 أول إيداع +100٪ مكافأة\n\n"
        "😊 أسئلة؟ اضغط الدعم"
    ),
}

DE_PATCH: dict[str, str] = {
    "kb.back": "⬅️ Zurück",
    "kb.main_menu": "🔙 Hauptmenü",
    "kb.support": "📞 Support",
    "kb.support_dm": "💬 Nachricht an @{u}",
    "kb.support_caps": "😊 SUPPORT",
    "kb.start_trading": "🚀 Trading starten",
    "kb.get_tokens": "💎 Tokens holen",
    "kb.deposit": "💰 Einzahlung",
    "kb.open_deposit_page": "💰 Einzahlungsseite öffnen",
    "kb.withdraw": "🤑 Auszahlung",
    "kb.settings": "🎯 Einstellungen",
    "kb.demo_real": "🎮 Demo / Real",
    "kb.logout": "🚪 Abmelden",
    "kb.account_main": "⬅️ Hauptmenü",
    "kb.demo_custom": "✏️ Eigener Betrag",
    "kb.trade_demo": "🎮 Demo-Konto",
    "kb.trade_real": "💰 Echtes Konto",
    "kb.reply_deposit": "💰 Einzahlung",
    "kb.reply_my_account": "📱 Mein Konto",
    "kb.reply_status": "🏆 Mein Status",
    "kb.reply_support": "📞 Support",
    "kb.reply_faq": "📘 F.A.Q",
    "kb.main_settings": "einstellungen",
    "kb.main_status": "status",
    "kb.main_help": "hilfe",
    "kb.main_disable_trading": "trading aus",
    "kb.main_enable_trading": "trading an",
    "kb.auto_precision": "Präzision 🎯",
    "kb.auto_high": "High-Profit ⚡",
    "kb.auto_balanced": "Ausgewogen 📊",
    "kb.auto_conservative": "Konservativ 🛡️",
    "kb.auto_manual": "🔧 Manuelle Einstellungen",
    "kb.manual_max_steps": "📊 Max. Stufen",
    "kb.manual_max_cycles": "✨ Max. Zyklen",
    "kb.expiry_sec": "{n} Sek.",
    "kb.po_connect": "📲 PO verbinden",
    "kb.po_linked": "✅ PO ({email})",
    "lang.ar": "🇸🇦 Arabisch",
    "lang.de": "🇩🇪 Deutsch",
    "lang.en": "🇬🇧 Englisch",
    "lang.es": "🇪🇸 Spanisch",
    "lang.fr": "🇫🇷 Französisch",
    "lang.id": "🇮🇩 Indonesisch",
    "lang.it": "🇮🇹 Italienisch",
    "lang.fil": "🇵🇭 Filipino",
    "lang.pt": "🇧🇷 Portugiesisch",
    "lang.ru": "🇷🇺 Russisch",
    "lang.hi": "🇮🇳 Hindi",
    "kb.mode_auto": "🎮 Auto-Trading",
    "kb.mode_manual": "⚙️ Manuelles Trading",
    "kb.hub_autotrade": "⚙️ Autotrade-Einstellungen",
    "kb.hub_expiry": "⏳ Ablaufzeit",
    "kb.hub_mode": "⚙️ Modus: manuell/auto",
    "kb.hub_language": "🌐 Sprache",
    "kb.legacy_stake": "einsatz setzen",
    "kb.legacy_expiry": "ablauf setzen",
    "kb.legacy_mg_on": "martingale an/aus",
    "kb.legacy_mg_levels": "mg-stufen (1-20)",
    "kb.legacy_mg_csv": "mg-multiplikatoren csv",
    "kb.legacy_assets": "assets setzen",
    "kb.legacy_strategy": "strategie an/aus",
    "kb.legacy_min_payout": "min. auszahlung %",
    "kb.legacy_max_stake_trade": "max. einsatz/trade",
    "kb.legacy_max_stake_day": "max. einsatz/tag",
    "kb.legacy_max_trades": "max. trades/tag",
    "kb.legacy_max_loss": "max. verlust/tag",
    "kb.legacy_cooldown": "cooldown",
    "kb.legacy_loss_streak": "verlustserie",
    "kb.legacy_back": "zurück",
    "caption.settings_hub": (
        "⚙️ <b>Trading-Einstellungen</b>\n\n"
        "🎯 Autotrade-Parameter\n"
        "⏳ Ablaufzeit pro Trade\n"
        "🎮 Modus — Manuell oder Autotrade"
    ),
    "caption.expiration": (
        "⌛ <b>Ablaufzeit</b>\n\n"
        "Aktuell: {seconds}s\n\n"
        "💡 Beste Ergebnisse oft bei 30 Sek."
    ),
    "caption.trading_mode": (
        "⚙️ <b>Trading-Modus</b>\n\n"
        "⚙️ Manuell — klassischer Modus.\n\n"
        "🎮 Auto-Trading [EXKLUSIV] — KI handelt automatisch."
    ),
    "msg.choose_language": "🌐 Sprache wählen:",
    "msg.language_updated": "Sprache aktualisiert.",
    "caption.autotrade": (
        "🎯 <b>Autotrade-Einstellungen</b>\n\n"
        "Aktuelle Strategie: {title} {emoji}\n"
        "◆ Max. Stufen: {ms}\n"
        "◆ Max. Trades: {md}\n"
        "◆ Ablauf: {ex}s"
    ),
    "caption.manual_compact": (
        "🔧 <b>Manuelle Einstellungen</b>\n\n"
        "◆ <b>Max. Stufen:</b> {ms}\n"
        "◆ <b>Max. Zyklen:</b> {mc}"
    ),
    "caption.max_mg_steps": "📊 <b>Max. Martingale-Stufen:</b>",
    "caption.max_cycles": "✨ <b>Max. Zyklen (Trades pro Sitzung):</b>",
    "strat.precision": "Präzision",
    "strat.high_profit": "High-Profit",
    "strat.balanced": "Ausgewogen",
    "strat.conservative": "Konservativ",
    "dash.trading_mode": "{pad}🎮 Modus: {mode}",
    "dash.real_balance": "{pad}💰 Echtguthaben: {real_bal}",
    "dash.demo_balance": "{pad}🎮 Demo-Guthaben: {demo_bal}",
    "dash.tokens": "{pad}💎 Tokens: {tokens}",
    "dash.status": "{pad}{tier_icon} Status: {tier}",
    "dash.accuracy": "{pad}📊 Signalgenauigkeit: {accuracy}",
    "caption.demo_account": (
        "🎮 <b>DEMO-KONTO</b>\n" "Hebel: {levels} (auto)\n" "Einsatz wählen 👇"
    ),
    "caption.trade_where": "🎯 Wo möchten Sie handeln?",
    "caption.my_account": (
        "📱 <b>Mein Konto</b>\n\n"
        "🏆 <b>Status:</b> {tier_e} {tier}\n\n"
        "💰 <b>ECHTKONTO-STATISTIK</b>\n"
        "💵 <b>Guthaben:</b> {real_bal}\n"
        "📊 <b>Serie:</b> {real_n} | <b>Gewinn:</b> {real_pnl}\n\n"
        "🎮 <b>DEMO-STATISTIK</b>\n"
        "💵 <b>Guthaben:</b> {demo_bal}\n"
        "📊 <b>Serie:</b> {demo_n} | <b>Gewinn:</b> {demo_pnl}\n\n"
        "💎 <b>Tokens:</b> {tokens_bal}"
    ),
    "gate.real_unavailable": (
        "⚠️ Echtmodus nicht verfügbar — Guthaben leer\n\n"
        "🔥 Echt-Trading freischalten: 💰 EINZAHLUNG\n\n"
        "🎁 Erste Einzahlung +100 % Bonus\n\n"
        "😊 Fragen? SUPPORT drücken"
    ),
}

FR_PATCH: dict[str, str] = {
    "kb.back": "⬅️ Retour",
    "kb.main_menu": "🔙 Menu principal",
    "kb.support": "📞 Assistance",
    "kb.support_dm": "💬 Écrire à @{u}",
    "kb.support_caps": "😊 ASSISTANCE",
    "kb.start_trading": "🚀 Commencer à trader",
    "kb.get_tokens": "💎 Obtenir des jetons",
    "kb.deposit": "💰 Dépôt",
    "kb.open_deposit_page": "💰 Ouvrir la page de dépôt",
    "kb.withdraw": "🤑 Retrait",
    "kb.settings": "🎯 Réglages",
    "kb.demo_real": "🎮 Démo / Réel",
    "kb.logout": "🚪 Déconnexion",
    "kb.account_main": "⬅️ Menu principal",
    "kb.demo_custom": "✏️ Montant personnalisé",
    "kb.trade_demo": "🎮 Compte démo",
    "kb.trade_real": "💰 Compte réel",
    "kb.reply_deposit": "💰 Dépôt",
    "kb.reply_my_account": "📱 Mon compte",
    "kb.reply_status": "🏆 Mon statut",
    "kb.reply_support": "📞 Assistance",
    "kb.reply_faq": "📘 F.A.Q",
    "kb.main_settings": "réglages",
    "kb.main_status": "statut",
    "kb.main_help": "aide",
    "kb.main_disable_trading": "désactiver le trading",
    "kb.main_enable_trading": "activer le trading",
    "kb.auto_precision": "Précision 🎯",
    "kb.auto_high": "Haut rendement ⚡",
    "kb.auto_balanced": "Équilibré 📊",
    "kb.auto_conservative": "Prudent 🛡️",
    "kb.auto_manual": "🔧 Réglages manuels",
    "kb.manual_max_steps": "📊 Pas max.",
    "kb.manual_max_cycles": "✨ Cycles max.",
    "kb.expiry_sec": "{n} s",
    "kb.po_connect": "📲 Connecter PO",
    "kb.po_linked": "✅ PO ({email})",
    "lang.ar": "🇸🇦 Arabe",
    "lang.de": "🇩🇪 Allemand",
    "lang.en": "🇬🇧 Anglais",
    "lang.es": "🇪🇸 Espagnol",
    "lang.fr": "🇫🇷 Français",
    "lang.id": "🇮🇩 Indonésien",
    "lang.it": "🇮🇹 Italien",
    "lang.fil": "🇵🇭 Filipin",
    "lang.pt": "🇧🇷 Portugais",
    "lang.ru": "🇷🇺 Russe",
    "lang.hi": "🇮🇳 Hindi",
    "kb.mode_auto": "🎮 Trading auto",
    "kb.mode_manual": "⚙️ Trading manuel",
    "kb.hub_autotrade": "⚙️ Réglages autotrading",
    "kb.hub_expiry": "⏳ Durée d’expiration",
    "kb.hub_mode": "⚙️ Mode : manuel/auto",
    "kb.hub_language": "🌐 Langue",
    "kb.legacy_stake": "définir mise",
    "kb.legacy_expiry": "définir expiration",
    "kb.legacy_mg_on": "martingale on/off",
    "kb.legacy_mg_levels": "niveaux mg (1-20)",
    "kb.legacy_mg_csv": "mult. mg csv",
    "kb.legacy_assets": "actifs",
    "kb.legacy_strategy": "stratégie on/off",
    "kb.legacy_min_payout": "gain min %",
    "kb.legacy_max_stake_trade": "mise max/trade",
    "kb.legacy_max_stake_day": "mise max/jour",
    "kb.legacy_max_trades": "trades max/jour",
    "kb.legacy_max_loss": "perte max/jour",
    "kb.legacy_cooldown": "pause",
    "kb.legacy_loss_streak": "série de pertes",
    "kb.legacy_back": "retour",
    "caption.settings_hub": (
        "⚙️ <b>Réglages de trading</b>\n\n"
        "🎯 Paramètres d’autotrading\n"
        "⏳ Expiration par trade\n"
        "🎮 Mode — Manuel ou autotrading"
    ),
    "caption.expiration": (
        "⌛ <b>Durée d’expiration</b>\n\n"
        "Actuel : {seconds}s\n\n"
        "💡 Souvent meilleurs résultats à 30 s."
    ),
    "caption.trading_mode": (
        "⚙️ <b>Mode de trading</b>\n\n"
        "⚙️ Manuel — mode classique.\n\n"
        "🎮 Auto [EXCLUSIF] — l’algorithme trade pour vous."
    ),
    "msg.choose_language": "🌐 Choisissez la langue :",
    "msg.language_updated": "Langue mise à jour.",
    "caption.autotrade": (
        "🎯 <b>Réglages autotrading</b>\n\n"
        "Stratégie : {title} {emoji}\n"
        "◆ Pas max. : {ms}\n"
        "◆ Trades max. : {md}\n"
        "◆ Expiration : {ex}s"
    ),
    "caption.manual_compact": (
        "🔧 <b>Réglages manuels</b>\n\n"
        "◆ <b>Pas max. :</b> {ms}\n"
        "◆ <b>Cycles max. :</b> {mc}"
    ),
    "caption.max_mg_steps": "📊 <b>Pas max. martingale :</b>",
    "caption.max_cycles": "✨ <b>Cycles max. (trades par session) :</b>",
    "strat.precision": "Précision",
    "strat.high_profit": "Haut rendement",
    "strat.balanced": "Équilibré",
    "strat.conservative": "Prudent",
    "dash.trading_mode": "{pad}🎮 Mode : {mode}",
    "dash.real_balance": "{pad}💰 Solde réel : {real_bal}",
    "dash.demo_balance": "{pad}🎮 Solde démo : {demo_bal}",
    "dash.tokens": "{pad}💎 Jetons : {tokens}",
    "dash.status": "{pad}{tier_icon} Statut : {tier}",
    "dash.accuracy": "{pad}📊 Précision du signal : {accuracy}",
    "caption.demo_account": (
        "🎮 <b>COMPTE DÉMO</b>\n" "Leviers : {levels} (auto)\n" "Choisissez la mise 👇"
    ),
    "caption.trade_where": "🎯 Où voulez-vous trader ?",
    "caption.my_account": (
        "📱 <b>Mon compte</b>\n\n"
        "🏆 <b>Statut :</b> {tier_e} {tier}\n\n"
        "💰 <b>STATISTIQUES RÉEL</b>\n"
        "💵 <b>Solde :</b> {real_bal}\n"
        "📊 <b>Série :</b> {real_n} | <b>Profit :</b> {real_pnl}\n\n"
        "🎮 <b>STATISTIQUES DÉMO</b>\n"
        "💵 <b>Solde :</b> {demo_bal}\n"
        "📊 <b>Série :</b> {demo_n} | <b>Profit :</b> {demo_pnl}\n\n"
        "💎 <b>Jetons :</b> {tokens_bal}"
    ),
    "gate.real_unavailable": (
        "⚠️ Mode réel indisponible — solde vide\n\n"
        "🔥 Débloquez le réel : appuyez sur 💰 DÉPÔT\n\n"
        "🎁 Premier dépôt +100 % de bonus\n\n"
        "😊 Questions ? ASSISTANCE"
    ),
}

ID_PATCH: dict[str, str] = {
    "kb.back": "⬅️ Kembali",
    "kb.main_menu": "🔙 Menu utama",
    "kb.support": "📞 Dukungan",
    "kb.support_dm": "💬 Pesan @{u}",
    "kb.support_caps": "😊 DUKUNGAN",
    "kb.start_trading": "🚀 Mulai trading",
    "kb.get_tokens": "💎 Dapatkan token",
    "kb.deposit": "💰 Deposit",
    "kb.open_deposit_page": "💰 Buka halaman deposit",
    "kb.withdraw": "🤑 Tarik",
    "kb.settings": "🎯 Pengaturan",
    "kb.demo_real": "🎮 Demo / Riil",
    "kb.logout": "🚪 Keluar",
    "kb.account_main": "⬅️ Menu utama",
    "kb.demo_custom": "✏️ Jumlah kustom",
    "kb.trade_demo": "🎮 Akun demo",
    "kb.trade_real": "💰 Akun riil",
    "kb.reply_deposit": "💰 Deposit",
    "kb.reply_my_account": "📱 Akun saya",
    "kb.reply_status": "🏆 Status saya",
    "kb.reply_support": "📞 Dukungan",
    "kb.reply_faq": "📘 Tanya jawab",
    "kb.main_settings": "pengaturan",
    "kb.main_status": "status",
    "kb.main_help": "bantuan",
    "kb.main_disable_trading": "matikan trading",
    "kb.main_enable_trading": "aktifkan trading",
    "kb.auto_precision": "Presisi 🎯",
    "kb.auto_high": "Profit tinggi ⚡",
    "kb.auto_balanced": "Seimbang 📊",
    "kb.auto_conservative": "Konservatif 🛡️",
    "kb.auto_manual": "🔧 Setelan manual",
    "kb.manual_max_steps": "📊 Langkah maks.",
    "kb.manual_max_cycles": "✨ Siklus maks.",
    "kb.expiry_sec": "{n} dtk",
    "kb.po_connect": "📲 Hubungkan PO",
    "kb.po_linked": "✅ PO ({email})",
    "lang.ar": "🇸🇦 Arab",
    "lang.de": "🇩🇪 Jerman",
    "lang.en": "🇬🇧 Inggris",
    "lang.es": "🇪🇸 Spanyol",
    "lang.fr": "🇫🇷 Prancis",
    "lang.id": "🇮🇩 Indonesia",
    "lang.it": "🇮🇹 Italia",
    "lang.fil": "🇵🇭 Filipino",
    "lang.pt": "🇧🇷 Portugis",
    "lang.ru": "🇷🇺 Rusia",
    "lang.hi": "🇮🇳 Hindi",
    "kb.mode_auto": "🎮 Trading otomatis",
    "kb.mode_manual": "⚙️ Trading manual",
    "kb.hub_autotrade": "⚙️ Setelan autotrade",
    "kb.hub_expiry": "⏳ Waktu kedaluwarsa",
    "kb.hub_mode": "⚙️ Mode: manual/otomatis",
    "kb.hub_language": "🌐 Bahasa",
    "kb.legacy_stake": "set taruhan",
    "kb.legacy_expiry": "set kedaluwarsa",
    "kb.legacy_mg_on": "martingale on/off",
    "kb.legacy_mg_levels": "level mg (1-20)",
    "kb.legacy_mg_csv": "pengali mg csv",
    "kb.legacy_assets": "set aset",
    "kb.legacy_strategy": "strategi on/off",
    "kb.legacy_min_payout": "bayaran min %",
    "kb.legacy_max_stake_trade": "taruhan maks/trade",
    "kb.legacy_max_stake_day": "taruhan maks/hari",
    "kb.legacy_max_trades": "trade maks/hari",
    "kb.legacy_max_loss": "rugi maks/hari",
    "kb.legacy_cooldown": "jeda",
    "kb.legacy_loss_streak": "rangkaian rugi",
    "kb.legacy_back": "kembali",
    "caption.settings_hub": (
        "⚙️ <b>Pengaturan trading</b>\n\n"
        "🎯 Parameter autotrade\n"
        "⏳ Waktu kedaluwarsa tiap trade\n"
        "🎮 Mode — Manual atau autotrade"
    ),
    "caption.expiration": (
        "⌛ <b>Waktu kedaluwarsa</b>\n\n"
        "Saat ini: {seconds}s\n\n"
        "💡 Hasil terbaik biasanya di 30 dtk."
    ),
    "caption.trading_mode": (
        "⚙️ <b>Mode trading</b>\n\n"
        "⚙️ Manual — mode klasik.\n\n"
        "🎮 Otomatis [EKSKLUSIF] — AI berdagang otomatis."
    ),
    "msg.choose_language": "🌐 Pilih bahasa:",
    "msg.language_updated": "Bahasa diperbarui.",
    "caption.autotrade": (
        "🎯 <b>Setelan autotrade</b>\n\n"
        "Strategi saat ini: {title} {emoji}\n"
        "◆ Langkah maks.: {ms}\n"
        "◆ Trade maks.: {md}\n"
        "◆ Kedaluwarsa: {ex}s"
    ),
    "caption.manual_compact": (
        "🔧 <b>Setelan manual</b>\n\n"
        "◆ <b>Langkah maks.:</b> {ms}\n"
        "◆ <b>Siklus maks.:</b> {mc}"
    ),
    "caption.max_mg_steps": "📊 <b>Langkah martingale maks.:</b>",
    "caption.max_cycles": "✨ <b>Siklus maks. (trade per sesi):</b>",
    "strat.precision": "Presisi",
    "strat.high_profit": "Profit tinggi",
    "strat.balanced": "Seimbang",
    "strat.conservative": "Konservatif",
    "dash.trading_mode": "{pad}🎮 Mode trading: {mode}",
    "dash.real_balance": "{pad}💰 Saldo riil: {real_bal}",
    "dash.demo_balance": "{pad}🎮 Saldo demo: {demo_bal}",
    "dash.tokens": "{pad}💎 Token: {tokens}",
    "dash.status": "{pad}{tier_icon} Status: {tier}",
    "dash.accuracy": "{pad}📊 Akurasi sinyal: {accuracy}",
    "caption.demo_account": (
        "🎮 <b>AKUN DEMO</b>\n" "Leverage: {levels} (otomatis)\n" "Pilih taruhan 👇"
    ),
    "caption.trade_where": "🎯 Di mana Anda ingin trading?",
    "caption.my_account": (
        "📱 <b>Akun saya</b>\n\n"
        "🏆 <b>Status:</b> {tier_e} {tier}\n\n"
        "💰 <b>STATISTIK AKUN RIIL</b>\n"
        "💵 <b>Saldo:</b> {real_bal}\n"
        "📊 <b>Seri:</b> {real_n} | <b>Profit:</b> {real_pnl}\n\n"
        "🎮 <b>STATISTIK AKUN DEMO</b>\n"
        "💵 <b>Saldo:</b> {demo_bal}\n"
        "📊 <b>Seri:</b> {demo_n} | <b>Profit:</b> {demo_pnl}\n\n"
        "💎 <b>Token:</b> {tokens_bal}"
    ),
    "gate.real_unavailable": (
        "⚠️ Mode riil tidak tersedia — saldo kosong\n\n"
        "🔥 Buka trading riil: tekan 💰 DEPOSIT\n\n"
        "🎁 Deposit pertama +100% bonus\n\n"
        "😊 Ada pertanyaan? DUKUNGAN"
    ),
}

IT_PATCH: dict[str, str] = {
    "kb.back": "⬅️ Indietro",
    "kb.main_menu": "🔙 Menu principale",
    "kb.support": "📞 Supporto",
    "kb.support_dm": "💬 Scrivi a @{u}",
    "kb.support_caps": "😊 SUPPORTO",
    "kb.start_trading": "🚀 Inizia a fare trading",
    "kb.get_tokens": "💎 Ottieni token",
    "kb.deposit": "💰 Deposito",
    "kb.open_deposit_page": "💰 Apri pagina deposito",
    "kb.withdraw": "🤑 Prelievo",
    "kb.settings": "🎯 Impostazioni",
    "kb.demo_real": "🎮 Demo / Reale",
    "kb.logout": "🚪 Esci",
    "kb.account_main": "⬅️ Menu principale",
    "kb.demo_custom": "✏️ Importo personalizzato",
    "kb.trade_demo": "🎮 Conto demo",
    "kb.trade_real": "💰 Conto reale",
    "kb.reply_deposit": "💰 Deposito",
    "kb.reply_my_account": "📱 Il mio account",
    "kb.reply_status": "🏆 Il mio stato",
    "kb.reply_support": "📞 Supporto",
    "kb.reply_faq": "📘 F.A.Q",
    "kb.main_settings": "impostazioni",
    "kb.main_status": "stato",
    "kb.main_help": "aiuto",
    "kb.main_disable_trading": "disattiva trading",
    "kb.main_enable_trading": "attiva trading",
    "kb.auto_precision": "Precisione 🎯",
    "kb.auto_high": "Alto profitto ⚡",
    "kb.auto_balanced": "Bilanciato 📊",
    "kb.auto_conservative": "Conservativo 🛡️",
    "kb.auto_manual": "🔧 Impostazioni manuali",
    "kb.manual_max_steps": "📊 Passi max",
    "kb.manual_max_cycles": "✨ Cicli max",
    "kb.expiry_sec": "{n} sec",
    "kb.po_connect": "📲 Collega PO",
    "kb.po_linked": "✅ PO ({email})",
    "lang.ar": "🇸🇦 Arabo",
    "lang.de": "🇩🇪 Tedesco",
    "lang.en": "🇬🇧 Inglese",
    "lang.es": "🇪🇸 Spagnolo",
    "lang.fr": "🇫🇷 Francese",
    "lang.id": "🇮🇩 Indonesiano",
    "lang.it": "🇮🇹 Italiano",
    "lang.fil": "🇵🇭 Filippino",
    "lang.pt": "🇧🇷 Portoghese",
    "lang.ru": "🇷🇺 Russo",
    "lang.hi": "🇮🇳 Hindi",
    "kb.mode_auto": "🎮 Trading automatico",
    "kb.mode_manual": "⚙️ Trading manuale",
    "kb.hub_autotrade": "⚙️ Impostazioni autotrading",
    "kb.hub_expiry": "⏳ Scadenza",
    "kb.hub_mode": "⚙️ Modalità: manuale/auto",
    "kb.hub_language": "🌐 Lingua",
    "kb.legacy_stake": "imposta puntata",
    "kb.legacy_expiry": "imposta scadenza",
    "kb.legacy_mg_on": "martingale on/off",
    "kb.legacy_mg_levels": "livelli mg (1-20)",
    "kb.legacy_mg_csv": "moltiplicatori mg csv",
    "kb.legacy_assets": "imposta asset",
    "kb.legacy_strategy": "strategia on/off",
    "kb.legacy_min_payout": "payout min %",
    "kb.legacy_max_stake_trade": "puntata max/trade",
    "kb.legacy_max_stake_day": "puntata max/giorno",
    "kb.legacy_max_trades": "trade max/giorno",
    "kb.legacy_max_loss": "perdita max/giorno",
    "kb.legacy_cooldown": "cooldown",
    "kb.legacy_loss_streak": "serie perdite",
    "kb.legacy_back": "indietro",
    "caption.settings_hub": (
        "⚙️ <b>Impostazioni trading</b>\n\n"
        "🎯 Parametri autotrading\n"
        "⏳ Scadenza per operazione\n"
        "🎮 Modalità — Manuale o autotrading"
    ),
    "caption.expiration": (
        "⌛ <b>Tempo di scadenza</b>\n\n"
        "Attuale: {seconds}s\n\n"
        "💡 Spesso migliori risultati a 30 sec."
    ),
    "caption.trading_mode": (
        "⚙️ <b>Modalità di trading</b>\n\n"
        "⚙️ Manuale — modalità classica.\n\n"
        "🎮 Automatico [ESCLUSIVO] — l’algoritmo opera per te."
    ),
    "msg.choose_language": "🌐 Scegli la lingua:",
    "msg.language_updated": "Lingua aggiornata.",
    "caption.autotrade": (
        "🎯 <b>Autotrading</b>\n\n"
        "Strategia attuale: {title} {emoji}\n"
        "◆ Passi max: {ms}\n"
        "◆ Operazioni max: {md}\n"
        "◆ Scadenza: {ex}s"
    ),
    "caption.manual_compact": (
        "🔧 <b>Impostazioni manuali</b>\n\n"
        "◆ <b>Passi max:</b> {ms}\n"
        "◆ <b>Cicli max:</b> {mc}"
    ),
    "caption.max_mg_steps": "📊 <b>Passi martingale max:</b>",
    "caption.max_cycles": "✨ <b>Cicli max (operazioni per sessione):</b>",
    "strat.precision": "Precisione",
    "strat.high_profit": "Alto profitto",
    "strat.balanced": "Bilanciato",
    "strat.conservative": "Conservativo",
    "dash.trading_mode": "{pad}🎮 Modalità: {mode}",
    "dash.real_balance": "{pad}💰 Saldo reale: {real_bal}",
    "dash.demo_balance": "{pad}🎮 Saldo demo: {demo_bal}",
    "dash.tokens": "{pad}💎 Token: {tokens}",
    "dash.status": "{pad}{tier_icon} Stato: {tier}",
    "dash.accuracy": "{pad}📊 Precisione segnale: {accuracy}",
    "caption.demo_account": (
        "🎮 <b>CONTO DEMO</b>\n" "Leva: {levels} (auto)\n" "Scegli puntata 👇"
    ),
    "caption.trade_where": "🎯 Dove vuoi tradare?",
    "caption.my_account": (
        "📱 <b>Il mio account</b>\n\n"
        "🏆 <b>Stato:</b> {tier_e} {tier}\n\n"
        "💰 <b>STATISTICHE REALE</b>\n"
        "💵 <b>Saldo:</b> {real_bal}\n"
        "📊 <b>Serie:</b> {real_n} | <b>Profitto:</b> {real_pnl}\n\n"
        "🎮 <b>STATISTICHE DEMO</b>\n"
        "💵 <b>Saldo:</b> {demo_bal}\n"
        "📊 <b>Serie:</b> {demo_n} | <b>Profitto:</b> {demo_pnl}\n\n"
        "💎 <b>Token:</b> {tokens_bal}"
    ),
    "gate.real_unavailable": (
        "⚠️ Modalità reale non disponibile — saldo vuoto\n\n"
        "🔥 Sblocca il reale: premi 💰 DEPOSITO\n\n"
        "🎁 Primo deposito +100% bonus\n\n"
        "😊 Domande? SUPPORTO"
    ),
}

FIL_PATCH: dict[str, str] = {
    "kb.back": "⬅️ Bumalik",
    "kb.main_menu": "🔙 Main menu",
    "kb.support": "📞 Suporta",
    "kb.support_dm": "💬 Mag-message kay @{u}",
    "kb.support_caps": "😊 SUPORTA",
    "kb.start_trading": "🚀 Simulan ang trading",
    "kb.get_tokens": "💎 Kumuha ng tokens",
    "kb.deposit": "💰 Deposito",
    "kb.open_deposit_page": "💰 Buksan ang deposit page",
    "kb.withdraw": "🤑 Mag-withdraw",
    "kb.settings": "🎯 Settings",
    "kb.demo_real": "🎮 Demo / Real",
    "kb.logout": "🚪 Logout",
    "kb.account_main": "⬅️ Main menu",
    "kb.demo_custom": "✏️ Custom amount",
    "kb.trade_demo": "🎮 Demo account",
    "kb.trade_real": "💰 Real account",
    "kb.reply_deposit": "💰 Deposito",
    "kb.reply_my_account": "📱 Aking account",
    "kb.reply_status": "🏆 Aking status",
    "kb.reply_support": "📞 Suporta",
    "kb.reply_faq": "📘 F.A.Q",
    "kb.main_settings": "settings",
    "kb.main_status": "status",
    "kb.main_help": "tulong",
    "kb.main_disable_trading": "patayin ang trading",
    "kb.main_enable_trading": "buksan ang trading",
    "kb.auto_precision": "Precision strike 🎯",
    "kb.auto_high": "Mataas na kita ⚡",
    "kb.auto_balanced": "Balanse 📊",
    "kb.auto_conservative": "Konserbatibo 🛡️",
    "kb.auto_manual": "🔧 Manual settings",
    "kb.manual_max_steps": "📊 Max na hakbang",
    "kb.manual_max_cycles": "✨ Max na cycle",
    "kb.expiry_sec": "{n} seg",
    "kb.po_connect": "📲 Ikonekta ang PO",
    "kb.po_linked": "✅ PO ({email})",
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
    "kb.mode_auto": "🎮 Auto trade",
    "kb.mode_manual": "⚙️ Manual trade",
    "kb.hub_autotrade": "⚙️ Autotrade settings",
    "kb.hub_expiry": "⏳ Oras ng expiry",
    "kb.hub_mode": "⚙️ Mode: manual/auto",
    "kb.hub_language": "🌐 Wika",
    "kb.legacy_stake": "set stake",
    "kb.legacy_expiry": "set expiry",
    "kb.legacy_mg_on": "martingale on/off",
    "kb.legacy_mg_levels": "mg levels (1-20)",
    "kb.legacy_mg_csv": "mg multipliers csv",
    "kb.legacy_assets": "set assets",
    "kb.legacy_strategy": "strategy on/off",
    "kb.legacy_min_payout": "min payout %",
    "kb.legacy_max_stake_trade": "max stake/trade",
    "kb.legacy_max_stake_day": "max stake/araw",
    "kb.legacy_max_trades": "max trades/araw",
    "kb.legacy_max_loss": "max loss/araw",
    "kb.legacy_cooldown": "cooldown",
    "kb.legacy_loss_streak": "sunod-sunod na talo",
    "kb.legacy_back": "bumalik",
    "caption.settings_hub": (
        "⚙️ <b>Trading settings</b>\n\n"
        "🎯 Autotrade parameters\n"
        "⏳ Expiry time bawat trade\n"
        "🎮 Mode — Manual o autotrade"
    ),
    "caption.expiration": (
        "⌛ <b>Oras ng expiry</b>\n\n"
        "Kasalukuyan: {seconds}s\n\n"
        "💡 Kadalasang pinakamabuti sa 30 seg."
    ),
    "caption.trading_mode": (
        "⚙️ <b>Trading mode</b>\n\n"
        "⚙️ Manual trade — klasikong mode.\n\n"
        "🎮 Auto trade [EXCLUSIVE] — awtomatikong nagte-trade ang AI."
    ),
    "msg.choose_language": "🌐 Pumili ng wika:",
    "msg.language_updated": "Na-update ang wika.",
    "caption.autotrade": (
        "🎯 <b>Autotrade settings</b>\n\n"
        "Kasalukuyang strategy: {title} {emoji}\n"
        "◆ Max na hakbang: {ms}\n"
        "◆ Max na deals: {md}\n"
        "◆ Expiry: {ex}s"
    ),
    "caption.manual_compact": (
        "🔧 <b>Manual settings</b>\n\n"
        "◆ <b>Max na hakbang:</b> {ms}\n"
        "◆ <b>Max na cycle:</b> {mc}"
    ),
    "caption.max_mg_steps": "📊 <b>Max na martingale steps:</b>",
    "caption.max_cycles": "✨ <b>Max na cycle (trades bawat session):</b>",
    "strat.precision": "Precision strike",
    "strat.high_profit": "Mataas na kita",
    "strat.balanced": "Balanse",
    "strat.conservative": "Konserbatibo",
    "dash.trading_mode": "{pad}🎮 Trading mode: {mode}",
    "dash.real_balance": "{pad}💰 Real balance: {real_bal}",
    "dash.demo_balance": "{pad}🎮 Demo balance: {demo_bal}",
    "dash.tokens": "{pad}💎 Tokens: {tokens}",
    "dash.status": "{pad}{tier_icon} Status: {tier}",
    "dash.accuracy": "{pad}📊 Katumpakan ng signal: {accuracy}",
    "caption.demo_account": (
        "🎮 <b>DEMO ACCOUNT</b>\n" "Leverage: {levels} (auto)\n" "Pumili ng taya 👇"
    ),
    "caption.trade_where": "🎯 Saan mo gustong mag-trade?",
    "caption.my_account": (
        "📱 <b>Aking account</b>\n\n"
        "🏆 <b>Status:</b> {tier_e} {tier}\n\n"
        "💰 <b>REAL ACCOUNT STATS</b>\n"
        "💵 <b>Balance:</b> {real_bal}\n"
        "📊 <b>Series:</b> {real_n} | <b>Kita:</b> {real_pnl}\n\n"
        "🎮 <b>DEMO ACCOUNT STATS</b>\n"
        "💵 <b>Balance:</b> {demo_bal}\n"
        "📊 <b>Series:</b> {demo_n} | <b>Kita:</b> {demo_pnl}\n\n"
        "💎 <b>Tokens:</b> {tokens_bal}"
    ),
    "gate.real_unavailable": (
        "⚠️ Hindi available ang real mode — walang balanse\n\n"
        "🔥 I-unlock ang real: pindutin ang 💰 DEPOSIT\n\n"
        "🎁 Unang deposit +100% bonus\n\n"
        "😊 May tanong? SUPORTA"
    ),
}

PT_PATCH: dict[str, str] = {
    "kb.back": "⬅️ Voltar",
    "kb.main_menu": "🔙 Menu principal",
    "kb.support": "📞 Suporte",
    "kb.support_dm": "💬 Mensagem para @{u}",
    "kb.support_caps": "😊 SUPORTE",
    "kb.start_trading": "🚀 Iniciar trading",
    "kb.get_tokens": "💎 Obter tokens",
    "kb.deposit": "💰 Depósito",
    "kb.open_deposit_page": "💰 Abrir página de depósito",
    "kb.withdraw": "🤑 Saque",
    "kb.settings": "🎯 Configurações",
    "kb.demo_real": "🎮 Demo / Real",
    "kb.logout": "🚪 Sair",
    "kb.account_main": "⬅️ Menu principal",
    "kb.demo_custom": "✏️ Valor personalizado",
    "kb.trade_demo": "🎮 Conta demo",
    "kb.trade_real": "💰 Conta real",
    "kb.reply_deposit": "💰 Depósito",
    "kb.reply_my_account": "📱 Minha conta",
    "kb.reply_status": "🏆 Meu status",
    "kb.reply_support": "📞 Suporte",
    "kb.reply_faq": "📘 Perguntas frequentes",
    "kb.main_settings": "configurações",
    "kb.main_status": "status",
    "kb.main_help": "ajuda",
    "kb.main_disable_trading": "desativar trading",
    "kb.main_enable_trading": "ativar trading",
    "kb.auto_precision": "Precisão 🎯",
    "kb.auto_high": "Alto lucro ⚡",
    "kb.auto_balanced": "Equilibrado 📊",
    "kb.auto_conservative": "Conservador 🛡️",
    "kb.auto_manual": "🔧 Ajustes manuais",
    "kb.manual_max_steps": "📊 Passos máx.",
    "kb.manual_max_cycles": "✨ Ciclos máx.",
    "kb.expiry_sec": "{n} s",
    "kb.po_connect": "📲 Conectar PO",
    "kb.po_linked": "✅ PO ({email})",
    "lang.ar": "🇸🇦 Árabe",
    "lang.de": "🇩🇪 Alemão",
    "lang.en": "🇬🇧 Inglês",
    "lang.es": "🇪🇸 Espanhol",
    "lang.fr": "🇫🇷 Francês",
    "lang.id": "🇮🇩 Indonésio",
    "lang.it": "🇮🇹 Italiano",
    "lang.fil": "🇵🇭 Filipino",
    "lang.pt": "🇧🇷 Português",
    "lang.ru": "🇷🇺 Russo",
    "lang.hi": "🇮🇳 Hindi",
    "kb.mode_auto": "🎮 Auto trading",
    "kb.mode_manual": "⚙️ Trading manual",
    "kb.hub_autotrade": "⚙️ Autotrade",
    "kb.hub_expiry": "⏳ Tempo de expiração",
    "kb.hub_mode": "⚙️ Modo: manual/auto",
    "kb.hub_language": "🌐 Idioma",
    "kb.legacy_stake": "definir aposta",
    "kb.legacy_expiry": "definir expiração",
    "kb.legacy_mg_on": "martingale on/off",
    "kb.legacy_mg_levels": "níveis mg (1-20)",
    "kb.legacy_mg_csv": "multiplicadores mg csv",
    "kb.legacy_assets": "ativos",
    "kb.legacy_strategy": "estratégia on/off",
    "kb.legacy_min_payout": "pagamento mín. %",
    "kb.legacy_max_stake_trade": "aposta máx./operação",
    "kb.legacy_max_stake_day": "aposta máx./dia",
    "kb.legacy_max_trades": "operações máx./dia",
    "kb.legacy_max_loss": "perda máx./dia",
    "kb.legacy_cooldown": "espera",
    "kb.legacy_loss_streak": "sequência de perdas",
    "kb.legacy_back": "voltar",
    "caption.settings_hub": (
        "⚙️ <b>Configurações de trading</b>\n\n"
        "🎯 Parâmetros de autotrade\n"
        "⏳ Expiração por operação\n"
        "🎮 Modo — Manual ou autotrade"
    ),
    "caption.expiration": (
        "⌛ <b>Tempo de expiração</b>\n\n"
        "Atual: {seconds}s\n\n"
        "💡 Melhores resultados costumam ser em 30 s."
    ),
    "caption.trading_mode": (
        "⚙️ <b>Modo de trading</b>\n\n"
        "⚙️ Manual — modo clássico.\n\n"
        "🎮 Automático [EXCLUSIVO] — o algoritmo opera por você."
    ),
    "msg.choose_language": "🌐 Escolha o idioma:",
    "msg.language_updated": "Idioma atualizado.",
    "caption.autotrade": (
        "🎯 <b>Autotrade</b>\n\n"
        "Estratégia atual: {title} {emoji}\n"
        "◆ Passos máx.: {ms}\n"
        "◆ Operações máx.: {md}\n"
        "◆ Expiração: {ex}s"
    ),
    "caption.manual_compact": (
        "🔧 <b>Ajustes manuais</b>\n\n"
        "◆ <b>Passos máx.:</b> {ms}\n"
        "◆ <b>Ciclos máx.:</b> {mc}"
    ),
    "caption.max_mg_steps": "📊 <b>Passos máx. martingale:</b>",
    "caption.max_cycles": "✨ <b>Ciclos máx. (operações por sessão):</b>",
    "strat.precision": "Precisão",
    "strat.high_profit": "Alto lucro",
    "strat.balanced": "Equilibrado",
    "strat.conservative": "Conservador",
    "dash.trading_mode": "{pad}🎮 Modo: {mode}",
    "dash.real_balance": "{pad}💰 Saldo real: {real_bal}",
    "dash.demo_balance": "{pad}🎮 Saldo demo: {demo_bal}",
    "dash.tokens": "{pad}💎 Tokens: {tokens}",
    "dash.status": "{pad}{tier_icon} Status: {tier}",
    "dash.accuracy": "{pad}📊 Precisão do sinal: {accuracy}",
    "caption.demo_account": (
        "🎮 <b>CONTA DEMO</b>\n" "Alavancagem: {levels} (auto)\n" "Escolha a aposta 👇"
    ),
    "caption.trade_where": "🎯 Onde quer operar?",
    "caption.my_account": (
        "📱 <b>Minha conta</b>\n\n"
        "🏆 <b>Status:</b> {tier_e} {tier}\n\n"
        "💰 <b>ESTATÍSTICAS CONTA REAL</b>\n"
        "💵 <b>Saldo:</b> {real_bal}\n"
        "📊 <b>Série:</b> {real_n} | <b>Lucro:</b> {real_pnl}\n\n"
        "🎮 <b>ESTATÍSTICAS CONTA DEMO</b>\n"
        "💵 <b>Saldo:</b> {demo_bal}\n"
        "📊 <b>Série:</b> {demo_n} | <b>Lucro:</b> {demo_pnl}\n\n"
        "💎 <b>Tokens:</b> {tokens_bal}"
    ),
    "gate.real_unavailable": (
        "⚠️ Modo real indisponível — saldo vazio\n\n"
        "🔥 Desbloqueie o real: toque 💰 DEPÓSITO\n\n"
        "🎁 Primeiro depósito +100% bônus\n\n"
        "😊 Dúvidas? SUPORTE"
    ),
}

RU_PATCH: dict[str, str] = {
    "kb.back": "⬅️ Назад",
    "kb.main_menu": "🔙 Главное меню",
    "kb.support": "📞 Поддержка",
    "kb.support_dm": "💬 Написать @{u}",
    "kb.support_caps": "😊 ПОДДЕРЖКА",
    "kb.start_trading": "🚀 Начать торговлю",
    "kb.get_tokens": "💎 Получить токены",
    "kb.deposit": "💰 Депозит",
    "kb.open_deposit_page": "💰 Открыть страницу депозита",
    "kb.withdraw": "🤑 Вывод",
    "kb.settings": "🎯 Настройки",
    "kb.demo_real": "🎮 Демо / Реал",
    "kb.logout": "🚪 Выйти",
    "kb.account_main": "⬅️ Главное меню",
    "kb.demo_custom": "✏️ Своя сумма",
    "kb.trade_demo": "🎮 Демо-счёт",
    "kb.trade_real": "💰 Реальный счёт",
    "kb.reply_deposit": "💰 Депозит",
    "kb.reply_my_account": "📱 Мой аккаунт",
    "kb.reply_status": "🏆 Мой статус",
    "kb.reply_support": "📞 Поддержка",
    "kb.reply_faq": "📘 ЧаВо",
    "kb.main_settings": "настройки",
    "kb.main_status": "статус",
    "kb.main_help": "помощь",
    "kb.main_disable_trading": "выключить торговлю",
    "kb.main_enable_trading": "включить торговлю",
    "kb.auto_precision": "Точный удар 🎯",
    "kb.auto_high": "Высокая прибыль ⚡",
    "kb.auto_balanced": "Сбалансировано 📊",
    "kb.auto_conservative": "Осторожно 🛡️",
    "kb.auto_manual": "🔧 Ручные настройки",
    "kb.manual_max_steps": "📊 Макс. шаги",
    "kb.manual_max_cycles": "✨ Макс. циклы",
    "kb.expiry_sec": "{n} сек",
    "kb.po_connect": "📲 Подключить PO",
    "kb.po_linked": "✅ PO ({email})",
    "lang.ar": "🇸🇦 Арабский",
    "lang.de": "🇩🇪 Немецкий",
    "lang.en": "🇬🇧 Английский",
    "lang.es": "🇪🇸 Испанский",
    "lang.fr": "🇫🇷 Французский",
    "lang.id": "🇮🇩 Индонезийский",
    "lang.it": "🇮🇹 Итальянский",
    "lang.fil": "🇵🇭 Филиппинский",
    "lang.pt": "🇧🇷 Португальский",
    "lang.ru": "🇷🇺 Русский",
    "lang.hi": "🇮🇳 Хинди",
    "kb.mode_auto": "🎮 Автоторговля",
    "kb.mode_manual": "⚙️ Ручная торговля",
    "kb.hub_autotrade": "⚙️ Автоторговля",
    "kb.hub_expiry": "⏳ Время экспирации",
    "kb.hub_mode": "⚙️ Режим: ручной/авто",
    "kb.hub_language": "🌐 Язык",
    "kb.legacy_stake": "ставка",
    "kb.legacy_expiry": "экспирация",
    "kb.legacy_mg_on": "мартингейл вкл/выкл",
    "kb.legacy_mg_levels": "уровни mg (1-20)",
    "kb.legacy_mg_csv": "множители mg csv",
    "kb.legacy_assets": "активы",
    "kb.legacy_strategy": "стратегия вкл/выкл",
    "kb.legacy_min_payout": "мин. выплата %",
    "kb.legacy_max_stake_trade": "макс. ставка/сделка",
    "kb.legacy_max_stake_day": "макс. ставка/день",
    "kb.legacy_max_trades": "макс. сделок/день",
    "kb.legacy_max_loss": "макс. убыток/день",
    "kb.legacy_cooldown": "пауза",
    "kb.legacy_loss_streak": "серия убытков",
    "kb.legacy_back": "назад",
    "caption.settings_hub": (
        "⚙️ <b>Настройки торговли</b>\n\n"
        "🎯 Параметры автоторговли\n"
        "⏳ Экспирация сделки\n"
        "🎮 Режим — вручную или авто"
    ),
    "caption.expiration": (
        "⌛ <b>Время экспирации</b>\n\n"
        "Сейчас: {seconds}s\n\n"
        "💡 Часто лучший результат при 30 сек."
    ),
    "caption.trading_mode": (
        "⚙️ <b>Режим торговли</b>\n\n"
        "⚙️ Вручную — классический режим.\n\n"
        "🎮 Авто [ЭКСКЛЮЗИВ] — алгоритм торгует сам."
    ),
    "msg.choose_language": "🌐 Выберите язык:",
    "msg.language_updated": "Язык обновлён.",
    "caption.autotrade": (
        "🎯 <b>Автоторговля</b>\n\n"
        "Стратегия: {title} {emoji}\n"
        "◆ Макс. шаги: {ms}\n"
        "◆ Макс. сделки: {md}\n"
        "◆ Экспирация: {ex}s"
    ),
    "caption.manual_compact": (
        "🔧 <b>Ручные настройки</b>\n\n"
        "◆ <b>Макс. шаги:</b> {ms}\n"
        "◆ <b>Макс. циклы:</b> {mc}"
    ),
    "caption.max_mg_steps": "📊 <b>Макс. шаги мартингейла:</b>",
    "caption.max_cycles": "✨ <b>Макс. циклы (сделок за сессию):</b>",
    "strat.precision": "Точный удар",
    "strat.high_profit": "Высокая прибыль",
    "strat.balanced": "Сбалансировано",
    "strat.conservative": "Осторожно",
    "dash.trading_mode": "{pad}🎮 Режим: {mode}",
    "dash.real_balance": "{pad}💰 Реальный баланс: {real_bal}",
    "dash.demo_balance": "{pad}🎮 Демо баланс: {demo_bal}",
    "dash.tokens": "{pad}💎 Токены: {tokens}",
    "dash.status": "{pad}{tier_icon} Статус: {tier}",
    "dash.accuracy": "{pad}📊 Точность сигнала: {accuracy}",
    "caption.demo_account": (
        "🎮 <b>ДЕМО-СЧЁТ</b>\n" "Плечо: {levels} (авто)\n" "Выберите ставку 👇"
    ),
    "caption.trade_where": "🎯 Где хотите торговать?",
    "caption.my_account": (
        "📱 <b>Мой аккаунт</b>\n\n"
        "🏆 <b>Статус:</b> {tier_e} {tier}\n\n"
        "💰 <b>СТАТИСТИКА РЕАЛ</b>\n"
        "💵 <b>Баланс:</b> {real_bal}\n"
        "📊 <b>Серия:</b> {real_n} | <b>Прибыль:</b> {real_pnl}\n\n"
        "🎮 <b>СТАТИСТИКА ДЕМО</b>\n"
        "💵 <b>Баланс:</b> {demo_bal}\n"
        "📊 <b>Серия:</b> {demo_n} | <b>Прибыль:</b> {demo_pnl}\n\n"
        "💎 <b>Токены:</b> {tokens_bal}"
    ),
    "gate.real_unavailable": (
        "⚠️ Реальный режим недоступен — пустой баланс\n\n"
        "🔥 Откройте реал: нажмите 💰 ДЕПОЗИТ\n\n"
        "🎁 Первый депозит +100% бонус\n\n"
        "😊 Вопросы? ПОДДЕРЖКА"
    ),
}
