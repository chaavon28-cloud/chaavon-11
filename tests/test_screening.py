import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.screening import clean_name, match_name


def test_clean_name_removes_accents_and_punctuation():
    assert clean_name("José O’Connor") == "JOSE OCONNOR"
    assert clean_name("  Muhammad  Ali ") == "MUHAMMAD ALI"


def test_match_name_returns_expected_match():
    sanctions_list = ["JOHN SMITH", "MARIA GARCIA", "MOHAMMAD KHAN"]
    customer = "John Smith"

    # ✅ Clean the name before matching (same as real pipeline)
    clean_customer = clean_name(customer)

    match, score, flag = match_name(clean_customer, sanctions_list, threshold=85)

    assert match == "JOHN SMITH"
    assert score >= 85
    assert flag is True

import pandas as pd
from src.screening import run_screening

def test_run_screening_end_to_end():
    # Fake sanctions list
    sanctions_list = ["JOHN SMITH", "MARIA GARCIA", "MOHAMMAD KHAN"]

    # Fake customers DataFrame
    customers_df = pd.DataFrame({
        "customer_id": [1, 2, 3],
        "customer_name": ["John Smith", "Alice Brown", "Maria Garcia"]
    })

    # Run screening
    results_df = run_screening(customers_df, sanctions_list, threshold=85)

    # Check structure
    assert "customer_id" in results_df.columns
    assert "customer_name" in results_df.columns
    assert "matched_sanction" in results_df.columns
    assert "score" in results_df.columns
    assert "is_flagged" in results_df.columns

    # Check expected results
    flagged = results_df[results_df["is_flagged"] == True]
    assert "JOHN SMITH" in flagged["matched_sanction"].values
    assert "MARIA GARCIA" in flagged["matched_sanction"].values
    assert "Alice Brown" not in flagged["customer_name"].values
