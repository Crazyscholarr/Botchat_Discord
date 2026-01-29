# Discord Automation Bot 🤖

A comprehensive and powerful Discord automation tool designed for managing multiple accounts, AI chat interactions, and server management tasks.

## 🌟 Key Features

*   **Advanced AI Chat System**:
    *   Supports **Grok AI (xAI)**, **Gemini (Google)**, and **ChatGPT (OpenAI)**.
    *   **Smart Fallback System**: Automatically switches to backup AI providers if one fails.
    *   **Context Awareness**: Can reply to users or send standalone messages based on probability settings.
    *   **Multi-Channel Support**: Chat in multiple channels across different servers simultaneously.
    *   **Rest Mode**: Intelligent pause system when channels are inactive to mimic human behavior.
    *   **DM Automation**: Auto-reply to Direct Messages.

*   **Account Management**:
    *   Bulk profile updates: Change Display Name, Username, Password, and Avatar.
    *   Excel-based account management (`accounts.xlsx`).
    *   Token validation and status checking.

*   **Server Interaction**:
    *   Auto Joiner (with Invite Codes).
    *   Auto Leaver.
    *   Button Clicker & Reaction Adder (for verifications or giveaways).
    *   Guild Presence Checker.

*   **System & Security**:
    *   **Multi-threaded**: Run multiple accounts in parallel.
    *   **Proxy Support**: HTTP/HTTPS proxy support for both Discord and AI APIs.
    *   **Captcha Solving**: Integrated support for **2Captcha** and **CapSolver**.
    *   **Github Version Check**: Automatically checks for updates.
    *   **Concurrency Locking**: Prevents multiple accounts from spamming the same guild simultaneously.

## Once it reaches 100 stars, I will upload the full version to you, or you can use it earlier for 10 USDT by messaging me directly.

## 📋 Requirements

*   Python 3.11.6 or higher.
*   `accounts.xlsx` file with valid Discord tokens.
*   (Optional) Proxies for accounts and AI services.
*   (Optional) API Keys for AI services (Grok, Gemini, OpenAI).
*   (Optional) API Key for Captcha services (2Captcha/CapSolver) if dealing with captchas.

## 🚀 Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Crazyscholarr/Autochat_discord.git
    cd Autochat_discord
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure**:
    *   Rename or create `config.yaml` based on the provided structure.
    *   Fill `data/accounts.xlsx` with your account details.

## ⚙️ Configuration

### 1. `data/accounts.xlsx`
The Excel file should have the following columns:
*   `DISCORD_TOKEN`: The authentication token for the account.
*   `PROXY`: HTTP/HTTPS proxy in `user:pass@ip:port` format.
*   `USERNAME`: (Optional) Logic reference.
*   `PASSWORD`: (Optional) For changing password/email.
*   `NEW_PASSWORD`: (Optional) New password to set.
*   `NEW_NAME`: (Optional) New display name to set.
*   `NEW_USERNAME`: (Optional) New username to set.
*   `MESSAGES_FILE`: (Optional) specific message file for this account.

### 2. `config.yaml`
Key sections to configure:

*   **SETTINGS**: Global threads, retry attempts, account ranges, and delays.
*   **AI_CHATTER**:
    *   `CHANNELS`: List of `GUILD_ID` and `CHANNEL_ID` to chat in.
    *   `AI_SELECTION_MODE`: `grok`, `gemini`, `chatgpt`, `random`, or `alternate`.
    *   `ANSWER_PERCENTAGE` & `REPLY_PERCENTAGE`: Control chat behavior.
    *   `FORBIDDEN_WORDS`: Words that stop the bot from replying.
*   **AI Providers** (`GROK`, `GEMINI`, `CHAT_GPT`): API keys and model selection.
*   **CAPTCHA_SERVICES**: Configure 2Captcha or CapSolver keys.
*   **REST_MODE**: Settings to pause the bot during inactivity.

## 🎮 Usage

Run the main script:
```bash
python main.py
```

### Main Menu Options

1.  **AI Chat tự động (Automated AI Chat)**:
    *   Starts the multi-threaded scheduler to chat in configured channels.
    *   Uses settings from `AI_CHATTER` in `config.yaml`.
2.  **AI Chat DM tự động (Automated DM AI Chat)**:
    *   Responds to incoming DMs using AI.
3.  **Tham gia server [Token]**: Make accounts join a server via invite code.
4.  **Nhấn nút [Token]**: Interact with buttons on a specific message.
5.  **Nhấn reaction [Token]**: Add reactions to a specific message.
6.  **Đổi tên hiển thị [Token]**: Bulk change display names.
7.  **Đổi tên đăng nhập [Token + Mật khẩu]**: Bulk change usernames (requires password).
8.  **Đổi mật khẩu [Token + Mật khẩu]**: Bulk change passwords.
9.  **Đổi ảnh đại diện [Token]**: Bulk upload avatars from `data/pictures`.
10. **Gửi tin nhắn vào kênh [Token]**: Send a static message to a channel.
11. **Kiểm tra token [Token]**: Check which tokens are alive.
12. **Rời khỏi server [Token]**: Mass leave servers.
13. **Hiển thị tất cả server [Token]**: List servers accounts are in.
14. **Kiểm tra token trong server [Token]**: Check if accounts are present in a specific guild.

## � Project Structure

```
├── config.yaml          # Main configuration
├── main.py              # Entry point
├── process.py           # Logic handler
├── requirements.txt     # Dependencies
├── data/
│   ├── accounts.xlsx    # Data source
│   ├── messages/        # Text files for static messages
│   └── pictures/        # Images for avatars
└── src/                 # Source code modules
```

## ⚠️ Disclaimer
This tool is for educational purposes only. Automating user accounts is against Discord's Terms of Service. Use at your own risk. The developer is not responsible for any bans or penalties.
