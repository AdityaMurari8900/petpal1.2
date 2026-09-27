"""
PetPal Assistant - Phase 1 MVP functional prototype
=====================================================

Covers, per the PRD:
  * 6.1 Pet Profile Management -> multi-pet support, dog/cat/bird
  * Section 3 design implication -> species-adaptive UI (forms +
    checklist change shape based on species)
  * 6.4 Daily Pet-Care Checklist -> species-aware daily checklist
    with one-tap check-off and a progress/streak-style summary

This is a single-account local prototype: no backend, no auth, no
Vet Connect / vet finder / notifications engine (those are later
phases per PRD section 10). Data is stored in a local JSON file via
petdata.PetStore so the app is fully usable offline.
"""

import os

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.metrics import dp

from petdata import PetStore, Pet, SPECIES, SPECIES_ICON, SPECIES_BREEDS

KV_PATH = os.path.join(os.path.dirname(__file__), "main.kv")


# ---------------------------------------------------------------------------
# Reusable row widgets (registered so main.kv can instantiate them)
# ---------------------------------------------------------------------------

class PetCard(BoxLayout):
    """One row in the pet list / pet switcher."""
    pet_id = StringProperty("")
    pet_name = StringProperty("")
    pet_icon = StringProperty("")
    pet_subtitle = StringProperty("")
    progress_text = StringProperty("")


class ChecklistRow(BoxLayout):
    """One species-adaptive daily-checklist item with a checkbox."""
    task_key = StringProperty("")
    task_label = StringProperty("")
    is_done = ObjectProperty(False)


class GroomingRow(BoxLayout):
    """One grooming-default row shown on the pet profile screen."""
    task_label = StringProperty("")
    frequency_text = StringProperty("")


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------

class PetListScreen(Screen):
    """Home screen: multi-pet switcher (PRD 6.1 'Switch between pets')."""

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        store = App.get_running_app().store
        container = self.ids.pet_list_box
        container.clear_widgets()

        if not store.pets:
            self.ids.empty_state.opacity = 1
            self.ids.empty_state.height = dp(80)
        else:
            self.ids.empty_state.opacity = 0
            self.ids.empty_state.height = 0

        for pet in store.pets:
            done, total = pet.today_progress()
            card = PetCard(
                pet_id=pet.id,
                pet_name=pet.name,
                pet_icon=SPECIES_ICON.get(pet.species, "\U0001F43E"),
                pet_subtitle=f"{pet.species} · {pet.breed or 'Breed not set'}",
                progress_text=f"Today: {done}/{total} done",
            )
            container.add_widget(card)

    def open_pet(self, pet_id):
        app = App.get_running_app()
        app.current_pet_id = pet_id
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "checklist"

    def confirm_delete(self, pet_id, pet_name):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        content.add_widget(Label(text=f"Remove {pet_name}'s profile?"))
        btn_row = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(44))
        popup = Popup(title="Confirm removal", content=content,
                       size_hint=(0.8, 0.35))

        def do_delete(*_):
            App.get_running_app().store.remove_pet(pet_id)
            popup.dismiss()
            self.refresh()

        yes_btn = Button(text="Remove")
        yes_btn.bind(on_release=do_delete)
        no_btn = Button(text="Cancel")
        no_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(no_btn)
        btn_row.add_widget(yes_btn)
        content.add_widget(btn_row)
        popup.open()


class AddPetScreen(Screen):
    """Species-adaptive pet creation form (PRD 6.1 Pet Profile Management)."""

    selected_species = StringProperty("Dog")
    breed_options = ListProperty(SPECIES_BREEDS["Dog"])

    def on_pre_enter(self, *args):
        # reset form each time the screen is opened
        self.selected_species = "Dog"
        self.ids.name_input.text = ""
        self.ids.dob_input.text = ""
        self.ids.weight_input.text = ""
        self.ids.notes_input.text = ""
        self._update_species_buttons()
        self.ids.breed_spinner.values = SPECIES_BREEDS["Dog"]
        self.ids.breed_spinner.text = "Select breed"
        self.ids.sex_spinner.text = "Unknown"

    def select_species(self, species):
        self.selected_species = species
        self.ids.breed_spinner.values = SPECIES_BREEDS.get(species, [])
        self.ids.breed_spinner.text = "Select breed"
        self._update_species_buttons()

    def _update_species_buttons(self):
        # visually mark the selected species button; kv reads these ids
        for sp in SPECIES:
            btn = self.ids.get(f"species_btn_{sp.lower()}")
            if btn:
                btn.selected = (sp == self.selected_species)

    def save_pet(self):
        name = self.ids.name_input.text.strip()
        if not name:
            self._show_error("Please enter a pet name.")
            return

        breed = self.ids.breed_spinner.text
        if breed in ("Select breed", ""):
            breed = "Not specified"

        pet = Pet(
            name=name,
            species=self.selected_species,
            breed=breed,
            dob=self.ids.dob_input.text.strip(),
            sex=self.ids.sex_spinner.text,
            weight=self.ids.weight_input.text.strip(),
            notes=self.ids.notes_input.text.strip(),
        )
        App.get_running_app().store.add_pet(pet)
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "pet_list"

    def _show_error(self, message):
        from kivy.uix.label import Label
        popup = Popup(title="Missing info",
                       content=Label(text=message),
                       size_hint=(0.75, 0.3))
        popup.open()

    def cancel(self):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "pet_list"


class ChecklistScreen(Screen):
    """Species-adaptive daily checklist for the currently selected pet."""

    pet_name = StringProperty("")
    pet_icon = StringProperty("")
    pet_meta = StringProperty("")
    progress_text = StringProperty("")

    def on_pre_enter(self, *args):
        self.refresh()

    def _current_pet(self):
        app = App.get_running_app()
        return app.store.get_pet(app.current_pet_id)

    def refresh(self):
        pet = self._current_pet()
        if pet is None:
            self.manager.current = "pet_list"
            return

        self.pet_name = pet.name
        self.pet_icon = SPECIES_ICON.get(pet.species, "\U0001F43E")
        self.pet_meta = f"{pet.species} · {pet.breed or 'Breed not set'}"

        container = self.ids.checklist_box
        container.clear_widgets()
        for key, label, done in pet.tasks_for_today():
            row = ChecklistRow(task_key=key, task_label=label, is_done=done)
            container.add_widget(row)

        done, total = pet.today_progress()
        self.progress_text = f"{done} / {total} tasks done today"

        # grooming defaults reference panel (species-aware, PRD 6.5)
        groom_box = self.ids.grooming_box
        groom_box.clear_widgets()
        for _, label, freq_days in pet.grooming_defaults():
            groom_box.add_widget(
                GroomingRow(task_label=label,
                            frequency_text=f"every {freq_days} days")
            )

    def toggle(self, task_key):
        pet = self._current_pet()
        if pet is None:
            return
        pet.toggle_task(task_key)
        App.get_running_app().store.save()
        self.refresh()

    def go_back(self):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "pet_list"


class RootManager(ScreenManager):
    pass


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

class PetPalApp(App):
    current_pet_id = StringProperty("")

    def build(self):
        self.title = "PetPal Assistant"
        self.store = PetStore(self.user_data_dir)
        Builder.load_file(KV_PATH)
        return RootManager()

    def on_stop(self):
        # belt-and-braces save on exit
        if hasattr(self, "store"):
            self.store.save()


if __name__ == "__main__":
    PetPalApp().run()
