from apscheduler.schedulers.background import BackgroundScheduler
from auto_reply import auto_reply
import time


def check_emails():
    print("\n🔄 Checking Gmail automatically...")
    
    try:
        auto_reply()
        print("✅ Email check completed.")
    except Exception as e:
        print("❌ Error:", e)


scheduler = BackgroundScheduler()

scheduler.add_job(
    check_emails,
    "interval",
    minutes=1
)

scheduler.start()

print("🤖 Automatic Email Auto Reply System Started!")
print("📧 Gmail will be checked every 1 minute.")
print("🛑 Press Ctrl+C to stop.")

try:
    while True:
        time.sleep(10)

except KeyboardInterrupt:
    scheduler.shutdown()
    print("\n🛑 Automatic system stopped.")