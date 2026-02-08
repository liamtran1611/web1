from flask import Flask, render_template_string, request

app = Flask(__name__)

# --- Simple SQLite setup ---
import sqlite3, datetime, smtplib, os
from email.message import EmailMessage

def init_db():
    EMAIL_TO = "liamtran16112000@gmail.com"
    EMAIL_FROM = "liamtran16112000@gmail.com"
    GMAIL_APP_PASSWORD = os.getenv("bzla ugjz gcqs kjab")


def send_email_notification(choice, ts, ip, ua):
    # Read the app password inside the function
    gmail_app_password = os.getenv("GMAIL_APP_PASSWORD", "")

    if not gmail_app_password or choice != "YES":
        print("Email not sent: App password not set or choice not YES")
        return

    try:
        msg = EmailMessage()
        msg["Subject"] = "💘 Valentine Response: YES"
        msg["From"] = "liamtran16112000@gmail.com"
        msg["To"] = "liamtran16112000@gmail.com"
        msg.set_content(
            f"She clicked YES! 💕\n\nTime (UTC): {ts}\nIP: {ip}\nDevice: {ua}\n"
        )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login("liamtran16112000@gmail.com", gmail_app_password)
            smtp.send_message(msg)

        print("Email sent successfully ✅")
    except Exception as e:
        print(f"Failed to send email: {e}")


init_db()

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Will You Be My Valentine? 💌</title>
    <style>
        body {
            height: 100vh;
            margin: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #ff9a9e, #fad0c4);
            font-family: Arial, sans-serif;
        }
        .card {
            background: white;
            padding: 40px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            position: relative;
        }
        h1 {
            margin-bottom: 30px;
        }
        button {
            font-size: 18px;
            padding: 12px 24px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            position: relative;
        }
        #yes {
            background-color: #ff4d6d;
            color: white;
            margin-right: 20px;
        }
        #no {
            background-color: #ccc;
            position: relative;
        }
    .buttons {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 24px;
            margin-top: 20px;
            position: relative;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>Hey Saho, will you be my Valentine? 💖</h1>
        <div class="buttons">
            <button id="yes" onclick="yesClicked()">Yes</button>
            <button id="no">No</button>
        </div>
    </div>

    <script>
        const noBtn = document.getElementById('no');
        const yesBtn = document.getElementById('yes');

        function sendLog(choice) {
            fetch('/log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ choice })
            }).catch(() => {});
        }

        // YES button logs and opens date page
        yesBtn.addEventListener('click', () => {
            sendLog('YES');
            document.body.innerHTML = `
                <div style=\"display:flex;align-items:center;justify-content:center;height:100vh;font-family:Arial;background:linear-gradient(135deg,#ff9a9e,#fad0c4);\">
                    <div style=\"background:white;padding:40px;border-radius:20px;text-align:center;box-shadow:0 10px 30px rgba(0,0,0,0.2);\">
                        <h1>It’s a date then! 💕</h1>
                        <p style=\"font-size:20px;\">🍽️ <strong>Restaurant:</strong> IDK</p>
                        <p style=\"font-size:20px;\">⏰ <strong>Time:</strong> Didnt thinks this far</p>
                        <p style=\"margin-top:20px;font-size:18px;\">Can’t wait to see you 😄</p>
                    </div>
                </div>
            `;
        });

        // If NO is ever clicked, log it
        noBtn.addEventListener('click', () => sendLog('NO'));

        // Make NO button move smoothly and randomly
        document.addEventListener('mousemove', (e) => {
            const rect = noBtn.getBoundingClientRect();
            const distance = Math.hypot(
                e.clientX - (rect.left + rect.width / 2),
                e.clientY - (rect.top + rect.height / 2)
            );

            if (distance < 120) {
                const padding = 30;
                const maxX = window.innerWidth - noBtn.offsetWidth - padding;
                const maxY = window.innerHeight - noBtn.offsetHeight - padding;

                const x = Math.random() * maxX + padding;
                const y = Math.random() * maxY + padding;

                noBtn.style.position = 'fixed';
                noBtn.style.transition = 'left 0.35s ease, top 0.35s ease';
                noBtn.style.left = x + 'px';
                noBtn.style.top = y + 'px';
            }
        });
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/log", methods=["POST"])
def log_choice():
    data = request.get_json(silent=True) or {}
    choice = data.get("choice", "unknown")

    ts = datetime.datetime.utcnow().isoformat()
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    ua = request.headers.get('User-Agent', 'unknown')

    with sqlite3.connect('valentine.db') as conn:
        conn.execute(
            "INSERT INTO responses (choice, timestamp, ip, user_agent) VALUES (?, ?, ?, ?)",
            (choice, ts, ip, ua)
        )

        send_email_notification(choice, ts, ip, ua)

    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

