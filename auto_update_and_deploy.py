
import os
from datetime import datetime
from app import db, Shipment, ShipmentHistory

# === CONFIG ===
TRACKING_CODE = "AWB824373517914"  # Change this to the one you want to update
NEW_HISTORY = {
    "date": datetime.now().strftime("%Y-%m-%d"),
    "time": datetime.now().strftime("%I:%M %p"),
    "location": "Berlin, Germany",
    "status": "In Transit",
    "updated_by": "Admin",
    "remarks": "Package arrived at Berlin sorting center"
}

# === STEP 1: ADD HISTORY LOCALLY ===
print("🔄 Adding new history to local database...")
shipment = Shipment.query.filter_by(tracking_code=TRACKING_CODE).first()
if not shipment:
    print(f"❌ Shipment with code {TRACKING_CODE} not found.")
    exit()
h = ShipmentHistoryid(
    shipment_id=shipment.id,
    **NEW_HISTORY
)
db.session.add(h)
db.session.commit()
print("✅ New history added successfully!")

# === STEP 2: COMMIT TO GITHUB ===
print("📦 Committing updated database to GitHub...")
os.system("git add shipments.db")
os.system('git commit -m "Update shipment history automatically"')
os.system("git push origin main")  # Change 'main' to 'master' if your branch name is master
print("✅ Changes pushed to GitHub!")

# === STEP 3: DEPLOY TO RENDER ===
print("🚀 Triggering redeploy on Render...")
print("✅ Done! Render will automatically detect changes and redeploy your app.")
print("Visit your live app in 1–2 minutes to see the update.")

