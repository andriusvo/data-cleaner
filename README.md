# Turing Data Cleaner

Welcome to the Turing Data Cleaner App! This project is a web application built with Python and Streamlit that provides a platform to clean the data.

## Features

- **CSV & XLSX Files upload:** Upload CSV and XLSX files to process them
- **Detect & Remove outliers** Detect and remove outliers
- **Remove duplicates** Remove duplicates from file
- **Drop missing values** Drop invalid rows
- **Fill missing values** Fill missing values with mean

## Preview live

[Click here to preview](https://chatbot-a5jkxdvm6wburdsrkjeym3.streamlit.app/)

---

## Getting Started

Follow these steps to set up and run the application on your local machine.

### Prerequisites

Ensure you have the following installed:

- Python 3.8 or later
- pip (Python package manager)

### Installation

1. Clone the repository:

   ```bash
   git clone git@github.com:TuringCollegeSubmissions/avoito-AE.3.5.git turing-data-cleaner
   cd turing-data-cleaner
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Change secrets:

   ```bash
   Adjust secrets.toml with API Keys for specific LLMs
   ```

### Running the App

1. Launch the Streamlit app:

   ```bash
   streamlit run cleaner.py
   ```

2. Open your browser and go to:

   [http://localhost:8501](http://localhost:8501)
