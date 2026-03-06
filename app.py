from flask import Flask, render_template, request
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os, uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""

    if request.method == "POST":
        sender_email = request.form.get("sender_email")
        password = request.form.get("password")
        subject = request.form.get("subject")

        csv_file = request.files.get("csvfile")
        names = request.form.getlist("name[]")
        emails = request.form.getlist("email[]")

        filepath = None
        sent_count = 0

        try:
            # ✅ OPTION 1: CSV upload
            if csv_file and csv_file.filename:
                filename = secure_filename(csv_file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename}")
                csv_file.save(filepath)
                data = pd.read_csv(filepath)

            # ✅ OPTION 2: Manual Excel-style input
            else:
                rows = []
                for n, e in zip(names, emails):
                    if n.strip() and e.strip():
                        rows.append({"name": n.strip(), "email": e.strip()})

                if not rows:
                    return render_template("index.html", message="❌ Upload CSV or enter data manually")

                data = pd.DataFrame(rows)

            # Send emails
            for i in range(len(data)):
                msg = MIMEMultipart()
                msg["From"] = sender_email
                msg["To"] = data["email"][i]
                msg["Subject"] = subject

                body = f"""
Hi {data['name'][i]},

This email was sent using a bulk email web app 🚀

Regards,
Bulk Mailer
"""
                msg.attach(MIMEText(body, "plain"))

                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, password)
                server.sendmail(sender_email, data["email"][i], msg.as_string())
                server.quit()

                sent_count += 1

            message = f"✅ {sent_count} emails sent successfully!" if sent_count else "❌ No emails sent"

        except Exception as e:
            message = f"❌ Error: {e}"

        finally:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)

    return render_template("index.html", message=message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
