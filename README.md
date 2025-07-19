# 💬 TTYL: A TCP Chat Server with Admin & Moderator Support

Tele-type-writer-link(TTYL) is a feature-rich, terminal-based multi-client chat server built using Python’s socket programming.  
It supports private messaging, user moderation, emoji support, and real-time communication over a local network (LAN).  
Perfect for educational projects or small intranet messaging systems.

---

## 🚀 Features

### 🧑‍🤝‍🧑 User Capabilities
- `/msg <username> <message>` — Send private messages.
- `/changename <newname>` — Change your username.
- `/users` — View all connected users.
- `/vote <username>` — Vote to kick a user (majority-based).
- Emoji support (e.g., `:smile:` → 😄)

### 🛠 Admin & Moderator Commands
Roles are authenticated via passwords:
- `/kick <username>` — Kick a user *(admin & moderator)*.
- `/ban <username>` — Ban a user permanently *(admin only)*.
- `/warn <username> <message>` — Warn a user *(moderator only)*.
- `/mute <username> <minutes>` — Temporarily mute a user *(moderator only)*.

---

## 📦 Requirements

- Python 3.6+
- [`emoji`](https://pypi.org/project/emoji/) — Emoji parsing and rendering
- [`rsa`](https://pypi.org/project/rsa/) — For encrypted messaging
- [`python-dotenv`](  https://pypi.org/project/python-dotenv/) — Read key‑value pairs from a `.env` file into environment variables  
- [`cryptography`](  https://pypi.org/project/cryptography/) — Provides cryptographic recipes and primitives (e.g. RSA, AES)  

### ✅ Install dependencies:

```bash
pip install emoji rsa python-dotenv cryptography
```

🖥️ Run the Server

```bash
python server.py
```
## 🛡️ User Roles

| Role      | Username     | Password               | Permissions                         |
|-----------|--------------|------------------------|-------------------------------------|
| **Admin** | `admin`      | `notanadminpassword`   | Full control (kick, ban)            |
| **Mod**   | `moderator`  | `modpassword`          | Moderate users (kick, mute, warn)   |
| **User**  | Any          | –                      | Chat, vote, private msg             |


## 😊 Emoji Support

Type aliases in your messages (e.g., `:fire:`) and they’ll automatically be converted to emojis.

| Alias         | Emoji | Alias          | Emoji |
|---------------|-------|----------------|-------|
| `:smile:`     | 😄    | `:wave:`       | 👋    |
| `:laugh:`     | 😂    | `:eyes:`       | 👀    |
| `:sad:`       | 😢    | `:sleep:`      | 😴    |
| `:angry:`     | 😠    | `:sunglasses:` | 😎    |
| `:heart:`     | ❤️    | `:ok:`         | 👌    |
| `:thumbsup:`  | 👍    | `:star:`       | ⭐    |
| `:clap:`      | 👏    | `:fire:`       | 🔥    |


## 🔐 Planned Enhancements

- ✅ Unique username enforcement  
- ✅ LAN-based real-time chat  
- ✅ Emoji support  
- ✅ RSA-based encryption support  
- 🔒 End-to-end encryption *(WIP)*  
- 🧾 Reporting and audit logs *(WIP)*  
- 📨 Cross-subnet connectivity *(WIP)*

## 👥 Made By

- Anirudh Nayak
- Sucheth K Katte

