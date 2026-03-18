package com.aigor.app

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject
import java.io.BufferedReader
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import java.util.regex.Pattern
import kotlin.concurrent.thread

class MainActivity : AppCompatActivity() {

    private lateinit var messageEdit: EditText
    private lateinit var statusText: TextView
    private lateinit var responseText: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        messageEdit = findViewById(R.id.messageEdit)
        statusText = findViewById(R.id.statusText)
        responseText = findViewById(R.id.responseText)

        val sendButton: Button = findViewById(R.id.sendButton)
        val openSettingsButton: Button = findViewById(R.id.openSettingsButton)

        consumeSharedText(intent)

        openSettingsButton.setOnClickListener {
            startActivity(Intent(this, SettingsActivity::class.java))
        }

        sendButton.setOnClickListener {
            val prefs = getSharedPreferences("aigor_prefs", MODE_PRIVATE)
            val endpoint = prefs.getString("openclaw_endpoint", "").orEmpty().trim()
            val token = prefs.getString("openclaw_hook_token", "").orEmpty().trim()
            val message = messageEdit.text.toString().trim()

            if (endpoint.isBlank()) {
                statusText.text = "Estat: falta endpoint (Settings)"
                return@setOnClickListener
            }
            if (token.isBlank()) {
                statusText.text = "Estat: falta token (Settings)"
                return@setOnClickListener
            }
            if (message.isBlank()) {
                statusText.text = "Estat: escriu algun missatge"
                return@setOnClickListener
            }

            sendToOpenClaw(endpoint, token, message)
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        consumeSharedText(intent)
    }

    private fun consumeSharedText(intent: Intent?) {
        if (intent?.action == Intent.ACTION_SEND && intent.type == "text/plain") {
            val shared = intent.getStringExtra(Intent.EXTRA_TEXT)?.trim().orEmpty()
            if (shared.isNotBlank()) {
                val current = messageEdit.text.toString().trim()
                val combined = if (current.isBlank()) shared else "$current\n\n$shared"
                messageEdit.setText(combined)
                statusText.text = "Estat: text compartit carregat"
            }
        }
    }

    private fun extractUrls(text: String): List<String> {
        val pattern = Pattern.compile("(https?://[^\\s]+)")
        val matcher = pattern.matcher(text)
        val urls = mutableListOf<String>()
        while (matcher.find()) {
            matcher.group(1)?.let { urls.add(it) }
        }
        return urls.distinct()
    }

    private fun sendToOpenClaw(endpoint: String, token: String, message: String) {
        statusText.text = "Estat: enviant..."
        responseText.text = "(esperant resposta...)"

        thread {
            try {
                val urls = extractUrls(message)
                val payloadText = if (urls.isEmpty()) {
                    message
                } else {
                    "$message\n\nURLs detectades: ${urls.joinToString(", ")}" 
                }
                val payload = JSONObject().apply {
                    put("text", payloadText)
                    put("mode", "now")
                }

                val conn = (URL(endpoint).openConnection() as HttpURLConnection).apply {
                    requestMethod = "POST"
                    setRequestProperty("Content-Type", "application/json")
                    setRequestProperty("Authorization", "Bearer $token")
                    connectTimeout = 15000
                    readTimeout = 20000
                    doOutput = true
                }

                OutputStreamWriter(conn.outputStream).use { it.write(payload.toString()) }

                val code = conn.responseCode
                val body = try {
                    if (code in 200..299) {
                        conn.inputStream.bufferedReader().use(BufferedReader::readText)
                    } else {
                        conn.errorStream?.bufferedReader()?.use(BufferedReader::readText).orEmpty()
                    }
                } catch (_: Exception) {
                    ""
                }

                runOnUiThread {
                    if (code in 200..299) {
                        statusText.text = "Estat: enviat OK ($code)"
                    } else {
                        statusText.text = "Estat: error HTTP $code"
                    }
                    responseText.text = if (body.isBlank()) "(resposta buida)" else body
                }

                conn.disconnect()
            } catch (e: Exception) {
                runOnUiThread {
                    statusText.text = "Estat: error ${e.message}"
                    responseText.text = "(sense resposta per error de connexió)"
                }
            }
        }
    }
}
