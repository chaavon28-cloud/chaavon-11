Sanctions \& PEP Screening Demo



Problem

Financial institutions must screen clients against sanctions and Politically Exposed Persons (PEP) lists every day.  

Exact matching often fails because of spelling mistakes, different formats, or special characters.  

This project shows how to use fuzzy matching to detect possible matches.



Data



\- Sanctions list: OFAC SDN list (public data)

\- Customers: Fake names generated with Python Faker



Approach



1\. Take names from sanctions list

2\. Generate fake customer names

3\. Clean the names (uppercase, remove accents, punctuation, extra spaces)

4\. Use rapidfuzz to calculate similarity scores

5\. Flag customers if score is above a threshold (e.g. 85)

6\. Show results in a Streamlit dashboard



Repo Structure

sanctions\_pep\_screening/

&nbsp; README.md

&nbsp; requirements.txt

&nbsp; .gitignore

&nbsp; LICENSE

&nbsp; data/

&nbsp;   sdn.csv

&nbsp;   sanctioned\_names.csv

&nbsp;   customers.csv

&nbsp; src/

&nbsp;   screening.py

&nbsp; dashboards/

&nbsp;   streamlit\_app.py

&nbsp; docs/

&nbsp;   screenshot.png  

&nbsp; tests/

&nbsp;   test\_screening.py



How to Run

----------

1\. Clone the repo and go into the folder



&nbsp;  git clone <your-repo-url>

&nbsp;  cd sanctions\_pep\_screening



2\. Create a virtual environment



&nbsp;  python -m venv .venv

&nbsp;  .venv\\Scripts\\activate   (Windows)

&nbsp;  source .venv/bin/activate   (Mac/Linux)



3\. Install requirements



&nbsp;  pip install -r requirements.txt



4\. Run the app



&nbsp;  streamlit run dashboards/streamlit\_app.py



5\. Run tests



&nbsp;  pytest -v





