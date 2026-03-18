package com.aigor.app

import android.os.Bundle
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.Spinner
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class SettingsActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)

        val endpointEdit: EditText = findViewById(R.id.settingsEndpointEdit)
        val tokenEdit: EditText = findViewById(R.id.settingsTokenEdit)
        val themeSpinner: Spinner = findViewById(R.id.themeSpinner)
        val saveButton: Button = findViewById(R.id.saveSettingsButton)
        val statusText: TextView = findViewById(R.id.settingsStatusText)

        val prefs = getSharedPreferences("aigor_prefs", MODE_PRIVATE)
        endpointEdit.setText(prefs.getString("openclaw_endpoint", "http://192.168.0.102:8092/chat"))
        tokenEdit.setText(prefs.getString("openclaw_hook_token", ""))

        val themes = ThemeManager.themes
        val labels = themes.map { it.label }
        val adapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, labels)
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        themeSpinner.adapter = adapter

        val currentThemeId = prefs.getString(ThemeManager.PREF_KEY, "ember_dark")
        val selectedIndex = themes.indexOfFirst { it.id == currentThemeId }.coerceAtLeast(0)
        themeSpinner.setSelection(selectedIndex)

        saveButton.setOnClickListener {
            val endpoint = endpointEdit.text.toString().trim()
            val token = tokenEdit.text.toString().trim()
            val themeId = themes[themeSpinner.selectedItemPosition].id

            if (endpoint.isBlank() || token.isBlank()) {
                statusText.text = "Omple endpoint i token"
                return@setOnClickListener
            }

            prefs.edit()
                .putString("openclaw_endpoint", endpoint)
                .putString("openclaw_hook_token", token)
                .putString(ThemeManager.PREF_KEY, themeId)
                .apply()

            statusText.text = "Configuració guardada ✅"
            setResult(RESULT_OK)
        }
    }
}
