import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Inicjalizacja bazy danych SQLite
conn = sqlite3.connect("group_data.db")
cursor = conn.cursor()
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS group_info (
    group_id INTEGER,
    key TEXT,
    value TEXT,
    PRIMARY KEY (group_id, key)
)
"""
)
conn.commit()


# Funkcja startowa pokazująca dostępne komendy
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    commands = [
        "/start - Show all commands",
        "/set <key> <value> - Set a value for a key",
        "/get <key> - Get the value of a key"
        # Możesz dodać więcej komend tutaj
    ]
    await update.message.reply_text("\n".join(commands))


# Funkcja do ustawiania wartości
async def set_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 2:
        return await update.message.reply_text("Usage: /set <key> <value>")

    key, value = context.args
    group_id = update.effective_chat.id

    cursor.execute(
        "REPLACE INTO group_info (group_id, key, value) VALUES (?, ?, ?)",
        (group_id, key, value),
    )

    conn.commit()
    await update.message.reply_text(f"Value set for {key}")


# Funkcja do pobierania wartości
async def get_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    group_id = update.effective_chat.id
    key = context.args[0] if context.args else ""
    cursor.execute(
        "SELECT value FROM group_info WHERE group_id = ? AND key = ?", (group_id, key)
    )
    row = cursor.fetchone()
    if row:
        await update.message.reply_text(f"{key}: {row[0]}")
    else:
        await update.message.reply_text(f"No value set for {key}")


# Funkcja pomocnicza do wyświetlania dostępnych komend /get
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    group_id = update.effective_chat.id

    # Pobieranie wszystkich kluczy dla danej grupy
    cursor.execute("SELECT key FROM group_info WHERE group_id = ?", (group_id,))
    rows = cursor.fetchall()

    # Jeśli nie ma ustawionych kluczy, wyślij stosowny komunikat
    if not rows:
        await update.message.reply_text("No keys have been set.")
        return

    # Tworzenie listy dostępnych komend /get
    commands = [f"/get {row[0]}" for row in rows]
    message = "Here are all the available get commands you can use:\n" + "\n".join(
        commands
    )
    await update.message.reply_text(message)


# Dodanie handlerów
app = (
    ApplicationBuilder().token("").build()
)
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("set", set_value))
app.add_handler(CommandHandler("get", get_value))
# Dodaj inne komendy...
app.add_handler(CommandHandler("help", help))

# Uruchomienie bota
app.run_polling()
