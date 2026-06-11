"""Admin panel — ConversationHandler assembler."""
from telegram.ext import (
    CallbackQueryHandler, CommandHandler, ConversationHandler, MessageHandler, filters,
)

from bot.constants import *
from bot.handlers.admin.menu import admin_cmd, main_menu_cb, admin_cancel
from bot.handlers.admin.channels import (
    channels_list_cb, channels_cb, channel_detail_cb, channel_edit_cb,
    channel_edit_input, channel_add_id, channel_add_title, channel_add_link,
)
from bot.handlers.admin.users import (
    users_menu_cb, users_search, user_detail_cb, user_xp_input, user_points_input,
)
from bot.handlers.admin.broadcast import (
    broadcast_menu_cb, broadcast_text_receive, broadcast_photo_receive,
    broadcast_btn_text, broadcast_btn_url, broadcast_target_cb, broadcast_confirm_cb,
)
from bot.handlers.admin.settings import settings_cb, webapp_url_receive


def get_admin_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("admin", admin_cmd)],
        states={
            ADM_MENU: [
                CallbackQueryHandler(main_menu_cb, pattern="^am_"),
                CallbackQueryHandler(settings_cb, pattern="^set_"),
            ],
            ADM_CHANNELS_LIST: [CallbackQueryHandler(channels_cb)],
            ADM_CHANNEL_ADD_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, channel_add_id)],
            ADM_CHANNEL_ADD_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, channel_add_title)],
            ADM_CHANNEL_ADD_LINK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, channel_add_link),
                CommandHandler("skip", channel_add_link),
            ],
            ADM_CHANNEL_DETAIL: [CallbackQueryHandler(channel_detail_cb)],
            ADM_CHANNEL_EDIT: [CallbackQueryHandler(channel_edit_cb)],
            ADM_CHANNEL_EDIT_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, channel_edit_input),
                CommandHandler("skip", channel_edit_input),
            ],
            ADM_USERS_MENU: [CallbackQueryHandler(users_menu_cb)],
            ADM_USERS_SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, users_search)],
            ADM_USER_DETAIL: [CallbackQueryHandler(user_detail_cb)],
            ADM_USER_XP_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_xp_input)],
            ADM_USER_POINTS_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_points_input)],
            ADM_BROADCAST_MENU: [CallbackQueryHandler(broadcast_menu_cb)],
            ADM_BROADCAST_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_text_receive)],
            ADM_BROADCAST_PHOTO: [MessageHandler(filters.PHOTO, broadcast_photo_receive)],
            ADM_BROADCAST_BTN_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_btn_text)],
            ADM_BROADCAST_BTN_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_btn_url)],
            ADM_BROADCAST_TARGET: [CallbackQueryHandler(broadcast_target_cb)],
            ADM_BROADCAST_CONFIRM: [CallbackQueryHandler(broadcast_confirm_cb)],
            ADM_SETTINGS_WEBAPP: [MessageHandler(filters.TEXT & ~filters.COMMAND, webapp_url_receive)],
        },
        fallbacks=[CommandHandler("cancel", admin_cancel), CommandHandler("admin", admin_cmd)],
        per_message=False,
    )
