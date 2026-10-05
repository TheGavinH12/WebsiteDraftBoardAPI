"""Run once to create the table and load a starting big board:
    python seed.py
Re-running it is safe — it clears and reloads the prospects table.
"""
from app.db import SessionLocal, Prospect, init_db

STARTING_BOARD = [
    {"rank": 1, "name": "Jeremiah Smith", "position": "WR", "school": "Ohio State", "note": "The best pure talent in the class — a receiver going this early is rare."},
    {"rank": 2, "name": "Colin Simmons", "position": "EDGE", "school": "Texas", "note": "Bends the edge like a much more experienced rusher."},
    {"rank": 3, "name": "Leonard Moore", "position": "CB", "school": "Notre Dame", "note": "Shutdown corner traits early in his career."},
    {"rank": 4, "name": "Dante Moore", "position": "QB", "school": "Oregon", "note": "Arm talent and the kind of feel for the offense that's hard to coach."},
    {"rank": 5, "name": "Arch Manning", "position": "QB", "school": "Texas", "note": "The pedigree is obvious; the tape is starting to back it up."},
    {"rank": 6, "name": "Dylan Stewart", "position": "EDGE", "school": "South Carolina", "note": "Explosive first step, still adding to his pass-rush plan."},
    {"rank": 7, "name": "Cam Coleman", "position": "WR", "school": "Auburn", "note": "Separation speed with real ball skills downfield."},
    {"rank": 8, "name": "CJ Carr", "position": "QB", "school": "Notre Dame", "note": "Strong QB class this cycle — he's a big reason why."},
    {"rank": 9, "name": "Trevor Goosby", "position": "OT", "school": "Texas", "note": "Protects the blindside for one of the top QB prospects in the class."},
    {"rank": 10, "name": "Jordan Seaton", "position": "OT", "school": "LSU", "note": "Started as a true freshman at Colorado; the floor is already a starting tackle."},
]

if __name__ == "__main__":
    init_db()
    db = SessionLocal()
    try:
        db.query(Prospect).delete()
        for row in STARTING_BOARD:
            db.add(Prospect(**row))
        db.commit()
        print(f"Seeded {len(STARTING_BOARD)} prospects.")
    finally:
        db.close()
