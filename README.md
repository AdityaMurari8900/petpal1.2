# PetPal Assistant — Phase 1 MVP Prototype

A functional, species-adaptive mobile prototype covering the PRD's Phase 1
MVP slice:

- **Multi-pet support** for dogs, cats, and birds (add, switch, remove pets)
- **Species-adaptive UI** — the pet form and the daily checklist change
  shape depending on species (e.g. cats get "Litter box checked", birds get
  "Cage cleaned / out-of-cage time", dogs get "Walked")
- **Daily pet-care checklist** with one-tap check-off and a per-pet
  progress summary, plus a read-only species-aware grooming defaults panel

Built with **Python + Kivy**. Everything runs locally on-device (JSON file
storage) — no backend, accounts, or network calls in this prototype.

Out of scope for this prototype (later phases per the PRD): vaccination
tracker, food/nutrition tracking, Vet Connect, vet finder, notifications
engine.

---

## Files in this repo

| File | Purpose |
|---|---|
| `main.py` | App entry point, screens (pet list, add pet, checklist) |
| `main.kv` | Kivy layout/styling |
| `petdata.py` | Pet model, species-specific data, JSON persistence |
| `buildozer.spec` | Tells Buildozer how to package the app as an Android APK |
| `.github/workflows/build.yml` | GitHub Actions workflow that builds the APK in the cloud |
| `requirements.txt` | Python deps, for reference |

---

## Part 1 — Set up the repository (all in the browser, no terminal)

1. Go to [github.com](https://github.com) and log in (or create a free account).
2. Click the **+** icon (top right) → **New repository**.
3. Name it, e.g. `petpal-assistant`. Set it to **Public** or **Private** —
   either works with GitHub Actions on the free tier. Do **not** initialize
   with a README (you'll upload one). Click **Create repository**.
4. On the new, empty repo page, click **uploading an existing file** (the
   blue link in the middle of the page).
5. Drag and drop, or use **choose your files**, to upload these files from
   this project, keeping their names exactly as given:
   - `main.py`
   - `main.kv`
   - `petdata.py`
   - `buildozer.spec`
   - `requirements.txt`
   - `.gitignore`
   - `README.md`
6. **The GitHub web uploader flattens folders**, so `.github/workflows/build.yml`
   needs a separate step (the drag-and-drop box won't preserve that nested
   path reliably from a folder drop). Do this instead:
   - Still on your repo page, click **Add file → Create new file**.
   - In the "Name your file" box, type the **full path**:
     `.github/workflows/build.yml` (typing the slashes automatically creates
     the folders).
   - Open `build.yml` from this project, copy its contents, and paste them
     into GitHub's editor.
   - Scroll down and click **Commit changes...** → **Commit changes**.
7. Back on the repo's main file list, click **Commit changes** for the first
   batch of files too, if you haven't already (Step 5's upload screen has
   its own **Commit changes** button at the bottom).

At this point your repo should show 7 files at the top level plus the
`.github/workflows/build.yml` file nested inside two folders.

---

## Part 2 — Trigger the build

The workflow is already set to run automatically on every push to `main`,
so simply completing Part 1 should have started a build. To trigger it
manually (e.g. to rebuild after a later change):

1. In your repo, click the **Actions** tab.
2. In the left sidebar, click **Build PetPal Assistant APK**.
3. Click the **Run workflow** dropdown (top right of the list) → **Run workflow**
   (leave branch as `main`).
4. A new run will appear in the list within a few seconds. Click it to
   watch progress.

**First build note:** the very first run typically takes **20–40 minutes**
because Buildozer downloads and compiles the Android SDK/NDK toolchain and
python-for-android from scratch. GitHub Actions' free tier gives generous
monthly minutes for public repos, so this is normal — subsequent builds are
faster thanks to the cache step in the workflow.

---

## Part 3 — Download the compiled APK

1. Once the run shows a green checkmark (or even mid-run, once the upload
   step has completed), open that run by clicking its title in the
   **Actions** tab.
2. Scroll to the bottom of the run's summary page to the **Artifacts**
   section.
3. Click **petpal-assistant-debug-apk** to download a `.zip` containing the
   `.apk` file.
4. Unzip it (your OS's built-in unzip / "Extract All" works) to get
   `bin/petpalassistant-0.1.0-arm64-v8a_armeabi-v7a-debug.apk` (exact name
   may vary slightly by version).
5. Transfer that `.apk` to an Android phone (email it to yourself, upload
   to Google Drive, or use a USB cable) and open it there to install.
   You'll need to allow **"Install unknown apps"** for whichever app you
   used to open the file, since it isn't from the Play Store.

This is a **debug APK** — fine for testing on your own device, not signed
for Play Store distribution. Signing for release is a later step once
you're past the prototype stage.

---

## If a build fails

Click the failed run → click the red `build-apk` job → expand the red step
to read the error log. The most common first-build issues are:

- **A step times out / network hiccup during SDK download** — just click
  **Re-run all jobs** (top right of the run page).
- **A dependency version mismatch** — Buildozer and python-for-android move
  fast; if `pip install buildozer==1.5.0 cython==0.29.36` fails, open
  `.github/workflows/build.yml` in GitHub's editor (pencil icon) and try
  removing the `==...` version pins so it installs the latest versions,
  then commit and re-run.

---

## Running it on your own machine (optional, if you do have Python locally)

```
pip install kivy==2.3.0
python main.py
```

This opens the same app in a desktop window for quick iteration, before
you spend Actions minutes on a full APK build.
