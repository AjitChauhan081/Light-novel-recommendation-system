# 🕸️ Web Light Novel Data Scraper (Educational Project)

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-WebDriver-orange)](https://www.selenium.dev/)
[![pandas](https://img.shields.io/badge/pandas-2.1.0-blue)](https://pandas.pydata.org/)
[![undetected_chromedriver](https://img.shields.io/badge/undetected--chromedriver-latest-lightgrey)](https://pypi.org/project/undetected-chromedriver/)


This repository demonstrates how to build a **structured web scraper** using **Python**, **Selenium** And **undetected_chromedriver**.  
It collects structured metadata from web light novel websites for **research and learning purposes**.

---

## Features

- Scrapes metadata like:
  - `title`, `genres`, `tags`
  - `total_rating`, `average_rating`
  - `total_chapters`, `chapter_urls`
  - `author` and more
- Handles **paginated web pages**
- Stores data in **CSV format** (`links.csv`, `Success.csv`, `skip.csv`)
- Processes large datasets in **batches** to bypass verification challenges
- Demonstrates combining **Selenium** (dynamic content) and **BeautifulSoup** (HTML parsing)

---

## How It Works

### 1️⃣ Step 1: Collect Novel Links
- Script scrapes all novel URLs and saves them in `links.csv`.

### 2️⃣ Step 2: Scrape Novel Data
- Reads URLs from `links.csv`.
- Scrapes detailed metadata for each novel.
- Saves successfully scraped data in `Success.csv`.
- Failed URLs (e.g., blocked by Cloudflare) are saved in `skip.csv`.

### 3️⃣ Batch Processing
- Scrapes links in **batches of 1000**.
- Helps avoid wasting time on pages blocked by verification.

---

## 🚀 Features

- Extracts structured data (titles, genres, tags,total_rating,average,rating,total,chapter,urls,author)
- Supports pagination and dynamic content loading
- Automatically stores data in CSV format
- Modular and easily customizable for other sites
- Includes sample synthetic data for safe experimentation

---

## 🧠 Tech Stack

| Component | Description |
|------------|-------------|
| **Python 3.x** | Core programming language |
| **Selenium / BeautifulSoup** | HTML parsing and scraping |
| **Pandas** | Data cleaning and saving (CSV) |

---

## ⚙️ Installation & Usage

### 1️⃣ Clone the repository
```bash
git clone https://github.com/AjitChauhan081/Light-novel-recommendation-system.git
cd '1. Data Scraping'

pip install -r requirements.txt
```
---
##  🧪 Synthetic Dataset

This repository includes a synthetic dataset (sample_synthetic.csv) with randomly generated data that mimics real-world 
structures.
It’s provided so that others can test models or data analysis pipelines without using scraped data.

---

## ⚖️ Legal & Ethical Notice

Disclaimer:
This project is for educational and research purposes only.
Do not use this code to scrape or republish copyrighted or proprietary data.
Always check and respect a website’s robots.txt file and Terms of Service before scraping.
The author does not encourage or endorse scraping of any specific website.
Any data shared in this repo (e.g., sample_synthetic.csv) is synthetic and non-real.

---

## 🧑‍💻 Author

**Ajit Chauhan**

🎓 B.Tech Computer Science & Engineering

💡 Passionate about Data Engineering, Machine Learning, and Automation

📫 [LinkedIn](https://www.linkedin.com/in/ajitchauhan081) | [GitHub](https://github.com/AjitChauhan081)

---

## ⭐ Contributing

Contributions and suggestions are welcome!
If you’d like to extend the scraper or improve its modularity, feel free to:

Fork this repo

Create a new branch

Submit a pull request

---

## 🧭 Summary

This project teaches:

How to build scalable scrapers safely

How to clean and structure extracted data

How to use synthetic datasets responsibly

Use it to learn — not to exploit websites.

---

