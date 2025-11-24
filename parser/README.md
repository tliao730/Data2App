#  DSCI 551 Final Project — Spotify Data Analytics (SQL + NoSQL)

**Team Members:** Eric Tsai, Brian, Angus  
**Course:** DSCI 551 — Foundations of Data Management  
**Instructor:** Prof. Gon glin Chen  

---

# 1.  Project Overview

This project implements a complete **SQL-style and NoSQL-style data processing system from scratch**, **without using external libraries such as Pandas, MongoDB, or csv/json helpers**.  
All data loading, filtering, projection, grouping, aggregation, and joining operations are built using **our own custom modules**.

We applied our engine to a real dataset:  
✔ **30k+ Spotify audio & popularity dataset** (CSV)  
✔ **500-record synthetic Spotify reviews dataset** (JSON)

We further developed multiple **interactive applications** using `ipywidgets`, including:  
- **Underrated Spotify Songs Finder**  
- **Overrated Spotify Songs Finder**  
- **Audio Feature Explorer** (scatter visualization & filtering)

---

# 2.  Directory Structure

Below is the complete project directory (auto-aligned, will not break in Markdown):

Data2App/
│
├── parser/
│   ├── core.py
│   ├── io_module.py
│   ├── utils.py
│   ├── processing.py
│   ├── nosql_module.py
│   ├── main.ipynb
│
├── data/
│   ├── spotify_songs.csv
│   ├── spotify_reviews.json
│
├── README.md
├── requirements.txt

---

# 3.  Custom Modules Implemented

## SQL Engine (CSV-based)
### Implemented by: **Eric + Brian + Angus**
- Custom CSV parser  
- DataFrame engine supporting:
  - filter()  
  - select() (projection)  
  - groupby() + aggregate()  
  - join()  
  - `head()`, `tail()`, `shape()`, info()  
- Chunk-based processing for large datasets (`ChunkReader`, `ChunkProcessor`)
- All logic implemented manually — no Pandas, no csv module

---

## NoSQL Engine (JSON-based)
### Implemented by: **Eric**
- JSON loading (without using `json.load()`)
- JSON-level operations:
  - filter_json()
  - project_json()
  - group_and_aggregate()
- Synthetic review dataset generation (500 records)

---

# 4. Applications (ipywidgets Interactive UI)

All apps run inside **`parser/main.ipynb`**.

### 4.1  Underrated Spotify Songs Finder  
Filters songs with:
- High user rating  
- Low Spotify popularity  
- Minimum number of reviews  
- Adjustable Top-N  
Provides an interactive ranking of hidden gems.

### 4.2  Overrated Spotify Songs Finder  
Filters the opposite:
- Low rating  
- High Spotify popularity  
- Adjustable Top-N  
Helps identify possibly overhyped songs.

### 4.3  Audio Feature Explorer  
Interactive plots with:
- Energy vs. Danceability  
- Popularity filters  
- Genre filters  
- Real-time scatterplot updates  

Allows exploration of Spotify's audio features in a visual way.

---

# 5.  Installation

### Environment
This project supports:
- Python 3.11+
- Jupyter Notebook
- ipywidgets 8+

Install dependencies:

bash
pip install -r requirements.txt

If ipywidgets needs manual enabling:

bash
pip install ipywidgets
jupyter nbextension enable --py widgetsnbextension --sys-prefix

---

# 6.  How to Run

### Step 1 — Navigate to project root
bash
cd Data2App

### Step 2 — Start Jupyter Notebook
bash
jupyter notebook

### Step 3 — Open:
parser/main.ipynb

### Step 4 — Run all cells  
The interactive UI will appear at the bottom of the notebook.

---

# 7.  Demo Screenshots (to insert before submission)

(You can paste these later)
- Underrated Songs Finder (UI + result)
- Overrated Songs Finder (UI + result)
- Audio Feature Explorer scatter plot
- Example groupby and chunk processing output

---

# 8.  Notes & Limitations

- All SQL/NoSQL operations were manually implemented.
- No external data-processing libraries (Pandas, NumPy, csv, json, MongoDB) were used.
- Certain operations are optimized but may not match industrial engines.

---

# 9.  Academic Integrity

This project was designed and implemented by Eric, Brian, and Angus  
for USC DSCI 551 Fall 2025.  
All code is original unless otherwise specified.

---

# 10.  Final Submission Checklist

- [x] README.md complete  
- [x] Directory structured correctly  
- [x] All notebooks and .py modules included  
- [x] No large unused files  
- [x] ZIP created and uploaded to Brightspace  

---

 **Thank you for reviewing our project!**