from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import ErrorEvent

from app.bot.handlers import router
from app.config import get_settings
from app.db.mongo import mongo
from app.observability.log import configure_logging, log_exception
from app.services.market_data import market_data
from app.services.assets import reload_po_otc_cache_from_db
from app.services.balance_worker import balance_worker
from app.services.otc_assets_worker import otc_assets_worker
from app.services.pocketoption_auth import pocketoption_auth


async def run_bot() -> None:
    configure_logging(level=get_settings().log_level)
    await mongo.connect()
    await reload_po_otc_cache_from_db()
    await pocketoption_auth.start()
    await market_data.start()
    await balance_worker.start()
    await otc_assets_worker.start()
    settings = get_settings()
    bot = Bot(token=settings.require_bot_token(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)

    @dp.errors()
    async def _telegram_errors(event: ErrorEvent) -> bool:
        log_exception("telegram_update_handler_failed", event.exception, update_id=event.update.update_id)
        hint = (
            "Something went wrong. Try /start again.\n\n"
            "If /start never replies: run the Telegram worker with\n"
            "  python -m app\n"
            "and ensure MongoDB is running (not only the API: python -m app.web)."
        )
        try:
            if event.update.message:
                await event.update.message.answer(hint, parse_mode=None)
            elif event.update.callback_query and event.update.callback_query.message:
                await event.update.callback_query.answer("Error — see new message.", show_alert=False)
                await event.update.callback_query.message.answer(hint, parse_mode=None)
        except Exception:
            pass
        return True

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        await otc_assets_worker.stop()
        await balance_worker.stop()
        await market_data.stop()
        await pocketoption_auth.close()
        await mongo.close()


async def run_bot_forever() -> None:
    while True:
        try:
            await run_bot()
        except asyncio.CancelledError:
            raise
        except Exception:
            await asyncio.sleep(3)

