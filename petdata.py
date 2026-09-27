"""
petdata.py
Data model + persistence for PetPal Assistant.

Everything the app knows about a pet, and the species-adaptive
defaults called for in the PRD (section 3 "Design implication" and
section 6.1 "Species-aware fields" / 6.4 "Daily Pet-Care Checklist"),
lives here. Kept free of any Kivy imports so it can be unit-tested
or reused headlessly.
"""

import json
import os
import uuid
from datetime import date, datetime

# ---------------------------------------------------------------------------
# Species-specific configuration
#
# Each species gets: an icon (emoji, avoids bundling image assets for the
# prototype), its own default daily checklist wording, and its own default
# grooming task list -- this is the "species-aware fields" requirement from
# the PRD (dogs get nail-clipping-only view, birds get wing/beak/nail trims,
# cats get litter habits, etc.)
# ---------------------------------------------------------------------------

SPECIES = ["Dog", "Cat", "Bird"]

SPECIES_ICON = {
    "Dog": "\U0001F436",   # dog face
    "Cat": "\U0001F431",   # cat face
    "Bird": "\U0001F426",  # bird
}

# Daily checklist templates -- (task_key, display_label)
SPECIES_DAILY_TASKS = {
    "Dog": [
        ("fed", "Fed"),
        ("walked", "Walked"),
        ("played", "Played / Attention"),
        ("water", "Water refreshed"),
        ("medication", "Medication given"),
    ],
    "Cat": [
        ("fed", "Fed"),
        ("litter", "Litter box checked"),
        ("played", "Played / Attention"),
        ("water", "Water refreshed"),
        ("medication", "Medication given"),
    ],
    "Bird": [
        ("fed", "Fed"),
        ("cage_time", "Cage cleaned / out-of-cage time"),
        ("played", "Played / Attention"),
        ("water", "Water refreshed"),
        ("medication", "Medication given"),
    ],
}

# Grooming task defaults per species (task_key, label, default_frequency_days)
SPECIES_GROOMING_DEFAULTS = {
    "Dog": [
        ("bath", "Bath", 28),
        ("nails", "Nail trimming", 21),
        ("coat", "Coat brushing/trimming", 14),
        ("ears", "Ear cleaning", 30),
        ("teeth", "Teeth cleaning", 7),
    ],
    "Cat": [
        ("nails", "Nail trimming", 21),
        ("coat", "Coat brushing", 7),
        ("ears", "Ear cleaning", 30),
        ("teeth", "Teeth cleaning", 14),
        ("litter_deep", "Litter box deep clean", 7),
    ],
    "Bird": [
        ("nails", "Nail trimming", 30),
        ("wings", "Wing trimming", 60),
        ("beak", "Beak check", 30),
        ("feathers", "Feather / preening check", 7),
        ("cage_deep", "Cage deep clean", 7),
    ],
}

# Breed lists are intentionally short for the prototype; PRD calls for a
# full searchable breed list plus "mixed/other" post-MVP.
SPECIES_BREEDS = {
    "Dog": ["Labrador Retriever", "Golden Retriever", "German Shepherd",
            "Beagle", "Indie / Mixed", "Other"],
    "Cat": ["Domestic Shorthair", "Persian", "Siamese", "Maine Coon",
            "Indie / Mixed", "Other"],
    "Bird": ["Budgerigar", "Cockatiel", "Lovebird", "African Grey",
             "Indian Ringneck", "Other"],
}


def today_str():
    return date.today().isoformat()


class Pet:
    """One pet profile (PRD 6.1 Pet Profile Management)."""

    def __init__(self, name, species, breed, dob="", sex="", weight="",
                 notes="", pet_id=None, checklist_log=None):
        self.id = pet_id or str(uuid.uuid4())
        self.name = name
        self.species = species if species in SPECIES else "Dog"
        self.breed = breed
        self.dob = dob            # ISO date string, optional
        self.sex = sex            # "Male" / "Female" / "Unknown"
        self.weight = weight      # free-text (e.g. "12 kg") for the prototype
        self.notes = notes
        # checklist_log: { "2026-09-27": {"fed": true, "walked": false, ...} }
        self.checklist_log = checklist_log or {}

    # -- daily checklist ---------------------------------------------------
    def tasks_for_today(self):
        """Return the species-adaptive task list: [(key, label, done)]."""
        template = SPECIES_DAILY_TASKS.get(self.species, SPECIES_DAILY_TASKS["Dog"])
        day_state = self.checklist_log.setdefault(today_str(), {})
        return [(key, label, day_state.get(key, False)) for key, label in template]

    def toggle_task(self, key):
        day_state = self.checklist_log.setdefault(today_str(), {})
        day_state[key] = not day_state.get(key, False)
        return day_state[key]

    def today_progress(self):
        tasks = self.tasks_for_today()
        done = sum(1 for _, _, v in tasks if v)
        return done, len(tasks)

    # -- grooming defaults ---------------------------------------------------
    def grooming_defaults(self):
        return SPECIES_GROOMING_DEFAULTS.get(self.species, SPECIES_GROOMING_DEFAULTS["Dog"])

    # -- serialization -------------------------------------------------------
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "species": self.species,
            "breed": self.breed,
            "dob": self.dob,
            "sex": self.sex,
            "weight": self.weight,
            "notes": self.notes,
            "checklist_log": self.checklist_log,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            name=d.get("name", ""),
            species=d.get("species", "Dog"),
            breed=d.get("breed", ""),
            dob=d.get("dob", ""),
            sex=d.get("sex", ""),
            weight=d.get("weight", ""),
            notes=d.get("notes", ""),
            pet_id=d.get("id"),
            checklist_log=d.get("checklist_log", {}),
        )


class PetStore:
    """Loads/saves all pets for the (single, prototype) account to JSON."""

    def __init__(self, data_dir):
        os.makedirs(data_dir, exist_ok=True)
        self.path = os.path.join(data_dir, "petpal_data.json")
        self.pets = []
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                self.pets = [Pet.from_dict(p) for p in raw.get("pets", [])]
            except (json.JSONDecodeError, OSError):
                self.pets = []
        else:
            self.pets = []

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(
                {"pets": [p.to_dict() for p in self.pets],
                 "saved_at": datetime.now().isoformat()},
                f, indent=2,
            )

    def add_pet(self, pet: Pet):
        self.pets.append(pet)
        self.save()

    def remove_pet(self, pet_id):
        self.pets = [p for p in self.pets if p.id != pet_id]
        self.save()

    def get_pet(self, pet_id):
        for p in self.pets:
            if p.id == pet_id:
                return p
        return None
