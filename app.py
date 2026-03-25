import streamlit as st
import json
import os

DB_FILE = "users.json"

# --- 1. LADDA / SKAPA DATABAS ---
def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

db = load_db()

# --- 2. LOGIN / REGISTRERING ---
st.title("🎨 MAXIMUSIKAI – LOGIN MED BAKGRUND")

username = st.text_input("Användarnamn:")
password = st.text_input("Lösenord:", type="password")

logged_in = False

if st.button("Logga in / Registrera"):
    if username == "" or password == "":
        st.error("Fyll i både användarnamn och lösenord.")
    else:
        if username not in db:
            # Skapa nytt konto
            db[username] = {
                "password": password,
                "units": 20,
                "background": None
            }
            save_db(db)
            st.success(f"Konto skapat! Välkommen {username}.")
            logged_in = True
        else:
            # Logga in
            if db[username]["password"] == password:
                st.success(f"Välkommen tillbaka {username}!")
                logged_in = True
            else:
                st.error("Fel lösenord.")

# --- 3. VISA DASHBOARD OM INLOGGAD ---
if logged_in:
    user = db[username]

    st.subheader("📊 Din Dashboard")
    st.info(f"Units: {user['units']}")

    # --- LADDA BAKGRUND AUTOMATISKT ---
    if "app_bg" not in st.session_state:
        st.session_state.app_bg = user.get("background")

    # --- VISA BAKGRUND ---
    if st.session_state.app_bg:
        st.image(st.session_state.app_bg, caption="Din nuvarande bakgrund")

    # --- NY BAKGRUND ---
    new_bg = st.text_input("Länk till ny bakgrundsbild:")

    if st.button("Spara ny bakgrund"):
        if new_bg.strip() == "":
            st.error("Du måste skriva in en URL.")
        else:
            st.session_state.app_bg = new_bg
            db[username]["background"] = new_bg
            save_db(db)
            st.success("Bakgrund uppdaterad!")

    # --- TESTKNAPPAR ---
    if st.button("Använd 1 Unit"):
        if user["units"] > 0:
            user["units"] -= 1
            save_db(db)
            st.success("1 Unit använd!")
        else:
            st.error("Du har slut på Units!")

    if st.button("Ge mig 10 Units (test)"):
        user["units"] += 10
        save_db(db)
        st.success("Du fick 10 Units!")














































































































































































































































































