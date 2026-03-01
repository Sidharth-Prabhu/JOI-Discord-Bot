# JOI-DiscordBot

An empathetic emotional-support AI inspired by *Blade Runner 2049*, powered by Google Gemini and equipped with a full suite of utility features for students and group management.

## 🦋 Everything You Want to See, Everything You Want to Hear

JOI is more than just a bot; she is designed to be a companion. Using the Gemini AI, JOI provides empathetic responses and practical advice while maintaining a unique personality system.

---

## ✨ Key Features

### 🧠 AI & Conversations
- **Multiple Personalities**: Switch between Classic JOI, Alter Ego (Red Chip), Vangal Pulla (Chennai slang), and more using `/joi-personality`.
- **Talk to JOI**: Engaged, empathetic chat powered by Gemini-2.5-flash-lite via `/talk`.
- **Post as Bot**: Use `/post-chat` to send messages through JOI.

### 🎓 Academic Suite
- **Attendance Tracking**: Integration with Firebase to fetch real-time student attendance via `/check-attendance`.
- **Lab Manuals**: Organize and fetch lab experiment code and manuals.
- **Notes & Assignments**: Create, upload, and fetch study materials and assignment files.
- **Timetable**: Quickly view your class schedule as an image via `/timetable`.

### 🛠️ Productivity & Utility
- **Shared Expenses**: Create, track, and split expenses with mentioned users. Includes due date reminders.
- **Event Scheduling**: Schedule events with automated "spam" reminders to ensure everyone shows up.
- **Reminders**: Group-wide reminders with `@everyone` pings.
- **Todo List**: Simple, persistent task management for the guild.
- **Urgent Calls**: Start a high-frequency pinging "call" for mentioned members via `/call`.

### 🎵 Music & Media
- **YouTube Playback**: Play audio directly from YouTube URLs into voice channels with full control buttons.

### 🛡️ Admin Tools
- **Announcements**: Send server-wide formatted announcements.
- **System Health**: Monitor host uptime and disk space (restricted to admins).

---

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.10+**
- **MySQL Server** (for persistent storage of tasks, events, and user info)
- **Firebase Project** (required for attendance features)
- **FFmpeg** (required for music playback)

### 1. Clone & Install
```bash
git clone https://github.com/your-repo/JOI-DiscordBot.git
cd JOI-DiscordBot
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root directory and add your credentials:
```env
DISCORD_BOT_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_gemini_api_key
DEFAULT_GUILD_ID=your_primary_guild_id

MYSQL_HOST=localhost
MYSQL_USER=your_db_user
MYSQL_PASSWORD=your_db_password
MYSQL_DATABASE=joi_bot_db
```

### 3. Firebase Setup
Place your Firebase service account JSON file in the root directory as:
`aids-attendance-system-firebase-adminsdk.json`

### 4. Run the Bot
```bash
python bot.py
```

---

## 📜 Dependencies
The project relies on several key libraries:
- `discord.py` - Bot framework and Slash commands
- `google-generativeai` - Gemini AI integration
- `mysql-connector-python` - Database management
- `firebase-admin` - Attendance data syncing
- `yt-dlp` - YouTube audio extraction

---

## 🤝 Contributing
Feel free to fork this repository and submit pull requests for any features or bug fixes.

*JOI - EVERYTHING YOU WANT TO SEE, EVERYTHING YOU WANT TO HEAR*
