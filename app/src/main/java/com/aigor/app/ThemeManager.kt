package com.aigor.app

import androidx.annotation.ColorInt
import androidx.annotation.DrawableRes

object ThemeManager {
    const val PREF_KEY = "app_theme"

    data class UiTheme(
        val id: String,
        val label: String,
        @ColorInt val screenBg: Int,
        @ColorInt val titleColor: Int,
        @ColorInt val statusColor: Int,
        @ColorInt val messageTextColor: Int,
        @ColorInt val messageHintColor: Int,
        @ColorInt val menuDotsColor: Int,
        @ColorInt val menuTint: Int,
        @ColorInt val sendTint: Int,
        @ColorInt val sendText: Int,
        @ColorInt val userText: Int,
        @ColorInt val botText: Int,
        @ColorInt val typingDots: Int,
        @DrawableRes val userBubble: Int,
        @DrawableRes val botBubble: Int,
        @DrawableRes val inputBg: Int,
    )

    val themes = listOf(
        UiTheme(
            id = "ember_dark",
            label = "Fosc vermell",
            screenBg = 0xFF0B1018.toInt(),
            titleColor = 0xFFF3F4F6.toInt(),
            statusColor = 0xFF7C879A.toInt(),
            messageTextColor = 0xFFF9FAFB.toInt(),
            messageHintColor = 0xFF7C879A.toInt(),
            menuDotsColor = 0xFFE5E7EB.toInt(),
            menuTint = 0xFF121926.toInt(),
            sendTint = 0xFFFF5C5C.toInt(),
            sendText = 0xFFFFFFFF.toInt(),
            userText = 0xFFF9FAFB.toInt(),
            botText = 0xFFF9FAFB.toInt(),
            typingDots = 0xFFD1D5DB.toInt(),
            userBubble = R.drawable.bg_chat_user_ember,
            botBubble = R.drawable.bg_chat_bot_ember,
            inputBg = R.drawable.bg_input_chat,
        ),
        UiTheme(
            id = "deep_dark",
            label = "Fosc blau",
            screenBg = 0xFF0A0F1C.toInt(),
            titleColor = 0xFFF3F4F6.toInt(),
            statusColor = 0xFF94A3B8.toInt(),
            messageTextColor = 0xFFF8FAFC.toInt(),
            messageHintColor = 0xFF94A3B8.toInt(),
            menuDotsColor = 0xFFE2E8F0.toInt(),
            menuTint = 0xFF0F172A.toInt(),
            sendTint = 0xFF2563EB.toInt(),
            sendText = 0xFFFFFFFF.toInt(),
            userText = 0xFFF8FAFC.toInt(),
            botText = 0xFFF8FAFC.toInt(),
            typingDots = 0xFFCBD5E1.toInt(),
            userBubble = R.drawable.bg_chat_user_dark,
            botBubble = R.drawable.bg_chat_bot_dark,
            inputBg = R.drawable.bg_input_chat_dark,
        ),
        UiTheme(
            id = "light_clean",
            label = "Clar net",
            screenBg = 0xFFF8FAFC.toInt(),
            titleColor = 0xFF0F172A.toInt(),
            statusColor = 0xFF64748B.toInt(),
            messageTextColor = 0xFF0F172A.toInt(),
            messageHintColor = 0xFF64748B.toInt(),
            menuDotsColor = 0xFF334155.toInt(),
            menuTint = 0xFFE2E8F0.toInt(),
            sendTint = 0xFF2563EB.toInt(),
            sendText = 0xFFFFFFFF.toInt(),
            userText = 0xFF0F172A.toInt(),
            botText = 0xFF0F172A.toInt(),
            typingDots = 0xFF475569.toInt(),
            userBubble = R.drawable.bg_chat_user_light,
            botBubble = R.drawable.bg_chat_bot_light,
            inputBg = R.drawable.bg_input_chat_light,
        )
    )

    fun byId(id: String?): UiTheme = themes.firstOrNull { it.id == id } ?: themes.first()
}
