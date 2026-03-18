package com.aigor.app

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class SettingsActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)

        val endpointEdit: EditText = findViewById(R.id.settingsEndpointEdit)
        val tokenEdit: EditText = findViewById(R.id.settingsTokenEdit)
        val saveButton: Button = findViewById(R.id.saveSettingsButton)
        val statusText: TextView = findViewById(R.id.settingsStatusText)

        val prefs = getSharedPreferences("aigor_prefs", MODE_PRIVATE)
        endpointEdit.setText(prefs.getString("openclaw_endpoint", "http://192.168.0.102:18789/hooks/wake"))
        tokenEdit.setText(prefs.getString("openclaw_hook_token", ""))

        saveButton.setOnClickListener {
            val endpoint = endpointEdit.text.toString().trim()
            val token = tokenEdit.text.toString().trim()

            if (endpoint.isBlank() || token.isBlank()) {
                statusText.text = "Omple endpoint i token"
                return@setOnClickListener
            }

            prefs.edit()
                .putString("openclaw_endpoint", endpoint)
                .putString("openclaw_hook_token", token)
                .apply()

            statusText.text = "Configuració guardada ✅"
        }
    }
}
