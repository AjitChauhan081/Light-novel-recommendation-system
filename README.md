# 📚 Light Novel Recommendation System

This repository demonstrates an end-to-end pipeline for a **Light Novel Recommendation System**, from data scraping to model deployment.  
Currently, the **Data Scraping** stage is completed. Other stages are planned and will be added sequentially.

---

## Repository Structure

LN-Recommendation-System/
│
├── 1. Data Scraping/ # ✅ Completed
│ └── Scripts to scrape light novel metadata (titles, genres, ratings, chapters, authors, etc.)
│
├── 2. Data Cleaning/ # ⏳ In Progress
│ └── Scripts to preprocess and normalize scraped data
│
├── 3. Feature Engineering/ # ⏳ Planned
│ └── Convert cleaned data into features suitable for recommendation models
│
├── 4. Model/ # ⏳ Planned
│ └── Scripts to train, evaluate, and test recommendation models
│
├── 5. Deployment/ # ⏳ Planned
│ └── Scripts to deploy the recommendation system as a web app or API
│
├── requirements.txt # Python dependencies
├── README.md # Project overview
└── LICENSE(Planned)


---

## 🛠️ Workflow

1. **Data Scraping**  
   - Collect light novel metadata (titles, genres, tags, ratings, chapters, authors).  
   - Output stored in CSV for processing in later stages.

2. **Data Cleaning**  
   - Handle missing values, duplicates, and inconsistent data.  
   - Normalize text fields and prepare structured datasets.

3. **Feature Engineering**  
   - Transform textual and categorical features into numerical representations.  
   - Example: TF-IDF for summaries, one-hot encoding for genres, etc.

4. **Model**  
   - Train recommendation models such as:
     - **Content-Based Filtering**  
     - **Collaborative Filtering**  
     - **Hybrid Models**  
   - Evaluate model performance with standard metrics.

5. **Deployment**  
   - Optional web app or API to serve personalized light novel recommendations.  
   - Could use **Flask** or **FastAPI** with front-end templates.

---

## Current Status

- ✅ Data Scraping: Completed  
- ⏳ Data Cleaning: In progress  
- ⏳ Feature Engineering: Planned  
- ⏳ Model: Planned  
- ⏳ Deployment: Planned  

---

## 📦 Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/LN-Recommendation-System.git
cd LN-Recommendation-System

pip install -r requirements.txt

```
---

## Author

**Ajit Chauhan**

-Passionate about Python, Web Scraping, and Recommendation Systems

-[LinkedIn](https://www.linkedin.com/in/chauhanajit/) | [GitHub](https://github.com/AjitChauhan081)
