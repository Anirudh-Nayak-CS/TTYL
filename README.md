#💬 TTYL: A TCP Chat Server with Admin & Moderator Support
TTYL is a feature-rich, terminal-based multi-client chat server built using Python’s socket programming. It supports private messaging, user moderation, emoji support, and real-time communication over a local network (LAN). Perfect for educational projects or small intranet messaging systems.

🚀 Features
🧑‍🤝‍🧑 User Capabilities
/msg <username> <message> — Send private messages.

/changename <newname> — Change your username.

/users — View all connected users.

/vote <username> — Vote to kick a user (majority based).

Emoji support (e.g., :smile: → 😄).

🛠 Admin & Moderator Commands
Admin and moderator roles are authenticated using passwords.

/kick <username> — Kick a user (admin & moderator).

/ban <username> — Ban a user permanently (admin only).

/warn <username> <msg> — Warn a user (moderator only).

/mute <username> <minutes> — Temporarily mute a user (moderator only).

📦 Requirements
Python 3.6+

emoji — Emoji parsing and rendering

rsa — (Optional) For encrypted messaging (used internally)

Install dependencies with:

bash
Copy
Edit
pip install emoji rsa
🖥️ Run the Server
bash
Copy
Edit
python server.py
Server will listen on your local IP (auto-detected via socket.gethostname()).

🧪 Sample Output (Client Join)
csharp
Copy
Edit
[STARTING] Server is starting.....
[LISTENING] Server is listening 192.168.1.xxx
[NEW-CONNECTION] alice connected
[ACTIVE CONNECTIONS] 1
🛡️ User Roles
Role	Username	Password	Permissions
Admin	admin	notanadminpassword	Full control (kick, ban)
Moderator	moderator	modpassword	Moderate users (kick, mute)
Regular	any	-	Chat, vote, private msg

😊 Emoji Support
Type aliases in your messages like :fire: or :laugh: and they’ll automatically be converted to emojis.

Alias	Emoji
:smile:	😄
:laugh:	😂
:sad:	😢
:angry:	😠
:heart:	❤️
:thumbsup:	👍
:clap:	👏
:fire:	🔥
:star:	⭐
:ok:	👌
:wave:	👋
:eyes:	👀
:sleep:	😴
:sunglasses:	😎

🔐 Planned Enhancements
✅ Unique username enforcement

✅ LAN-based real-time chat

✅ Emoji support

✅ RSA-based encryption support

🔒 End-to-end encryption (WIP)

🧾 Reporting and audit logs (WIP)

📨 Cross-subnet connectivity (WIP)
