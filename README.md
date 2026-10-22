# 🧹 Data Cleaning & Exploration Tool

A Python + Streamlit web app that lets you upload a messy CSV/Excel file and:
1. Fix missing values and remove duplicate rows
2. Standardise messy dates and group similar text values (e.g. "NY" / "N.Y." / "New York")
3. Reduce many numeric columns down to a few with PCA
4. Visualize everything with heatmaps, correlation matrices, and an interactive PCA scatter plot
5. Download the cleaned result as a CSV

This README assumes **zero prior setup** — follow it top to bottom and you'll have
the app running in your browser.

---

## 1. What you need before starting

- A computer (Windows, Mac, or Linux)
- **Python 3.11 or newer** installed
  - Check if you already have it: open a terminal (see step 2) and type:
    ```
    python3 --version
    ```
    or on Windows:
    ```
    python --version
    ```
  - If that fails or shows a version below 3.9, download Python from
    https://www.python.org/downloads/ and install it.
    **Windows users:** during install, tick the box "Add Python to PATH" — this
    step trips up a lot of beginners, don't skip it.

---

## 2. Open a terminal

- **Windows:** press `Win`, type `PowerShell`, press Enter.
- **Mac:** press `Cmd + Space`, type `Terminal`, press Enter.
- **Linux:** you probably already know how — any terminal emulator works.

---

## 3. Unzip and enter the project folder

1. Unzip the file you downloaded (`data_cleaning_app.zip`) anywhere you like,
   e.g. your Desktop.
2. In the terminal, move into that folder. Example (adjust the path to where
   you unzipped it):

   **Mac/Linux:**
   ```
   cd ~/Desktop/data_cleaning_app
   ```

   **Windows:**
   ```
   cd Desktop\data_cleaning_app
   ```

3. Confirm you're in the right place — this should list files including
   `app.py` and `requirements.txt`:
   ```
   ls          # Mac/Linux
   dir         # Windows
   ```

---

## 4. Create a virtual environment (keeps this project's libraries separate)

A virtual environment is just an isolated folder of Python packages so this
project doesn't interfere with other Python projects on your machine.

**Mac/Linux:**
```
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```
python -m venv venv
venv\Scripts\Activate.ps1
```
*(If PowerShell blocks the script with a "running scripts is disabled" error,
run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
once, then try activating again.)*

**Windows (Command Prompt):**
```
python -m venv venv
venv\Scripts\activate.bat
```

You'll know it worked because your terminal prompt now starts with `(venv)`.

> You need to run the "activate" command every time you open a new terminal
> to work on this project. If you close the terminal and come back later,
> just `cd` into the folder again and re-run the activate command.

---

## 5. Install the required libraries

With your virtual environment activated (you see `(venv)` in the prompt):

```
pip install -r requirements.txt
```

This installs everything listed in `requirements.txt`: Streamlit, pandas,
numpy, scikit-learn, matplotlib, seaborn, plotly, and a few others. It may
take a minute or two — that's normal.

---

## 6. Run the app

```
streamlit run app.py
```

Your default web browser should open automatically to something like
`http://localhost:8501`. If it doesn't open automatically, copy that address
from the terminal and paste it into your browser manually.

To stop the app, go back to the terminal and press `Ctrl + C`.

---

## 7. Try it out with the included sample data

The app includes a small messy sample file at `sample_data/messy_sample.csv`
(it has missing ages, duplicate rows, inconsistent city spellings like "NY" /
"N.Y." / "New York", and dates in several different formats — on purpose).

1. In the app's sidebar, make sure you're on **"1. Upload Data"**.
2. Click **Browse files** and select `sample_data/messy_sample.csv` from the
   project folder.
3. Walk through steps 2–6 in the sidebar in order — each step explains what
   it does.

---

## 8. Project structure (what each file/folder is for)

```
data_cleaning_app/
├── app.py                          <- Module 5: the Streamlit web app (run this)
├── requirements.txt                <- list of Python libraries this project needs
├── README.md                       <- this file
├── .streamlit/
│   └── config.toml                 <- app color theme
├── modules/                        <- all the "logic" — no UI code lives here
│   ├── module1_cleaning.py         <- missing values + duplicate removal
│   ├── module2_standardisation.py  <- date formats + fuzzy text grouping
│   ├── module3_reduction.py        <- PCA dimensionality reduction
│   └── module4_visualization.py    <- charts (heatmap, correlation, PCA plot)
├── tests/                          <- automated tests, one file per module
│   ├── test_module1_cleaning.py
│   ├── test_module2_standardisation.py
│   ├── test_module3_reduction.py
│   └── test_module4_visualization.py
└── sample_data/
    └── messy_sample.csv            <- practice file with realistic messy data
```

**Why split it like this?** Each module in `modules/` only contains logic —
it takes a DataFrame in and returns a DataFrame (or chart) out. `app.py` is
the only file that contains UI code. This means you can test and fix each
module completely on its own without touching the web app, which is exactly
what the `tests/` folder does.

---

## 9. Running the automated tests

This confirms all the logic works correctly, independent of the web app.
With your virtual environment activated:

```
pytest tests/ -v
```

You should see 17 tests, all `PASSED`. If you ever change code inside
`modules/`, re-run this command to make sure you didn't break anything.

---

## 10. Common problems & fixes

| Problem | Likely fix |
|---|---|
| `command not found: python3` | Python isn't installed, or isn't on PATH. Reinstall from python.org and tick "Add to PATH" on Windows. |
| `pip: command not found` | Try `python3 -m pip install -r requirements.txt` instead. |
| `ModuleNotFoundError: No module named 'streamlit'` | Your virtual environment isn't activated, or step 5 (`pip install -r requirements.txt`) wasn't run inside it. Re-do steps 4 and 5. |
| Browser doesn't open automatically | Manually go to the URL printed in the terminal, usually `http://localhost:8501`. |
| PowerShell won't let you activate the venv | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once (see step 4). |
| Port 8501 already in use | Another Streamlit app is running. Either close it, or run this one on a different port: `streamlit run app.py --server.port 8502` |

---

## 11. Next steps (once it's running locally)

- **Put it on GitHub:** `git init`, `git add .`, `git commit -m "Initial commit"`,
  then create a repo on GitHub and push. This gives you a portfolio link.
- **Deploy it for free:** go to https://streamlit.io/cloud, connect your
  GitHub repo, and point it at `app.py`. You'll get a public URL you can
  share (e.g. with recruiters).
- **Add your own test data:** try uploading real messy datasets from Kaggle
  ("messy data" is a good search term) to stress-test the cleaning logic.

---

## 12. License / usage

This is your own project — do whatever you like with it (personal use,
portfolio, resume project, further development).
