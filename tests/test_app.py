import pytest
from pathlib import Path
from streamlit.testing.v1 import AppTest

# Locate app.py in the main repository folder
APP_PATH = Path(__file__).resolve().parents[1] / "app.py"

TEST_CASES = [
    (
        "Your bank account is blocked. Share your OTP immediately.",
        "Banking / OTP fraud",
    ),
    (
        "Your UPI refund is pending. Scan QR and enter UPI PIN to receive money.",
        "UPI / payment fraud",
    ),
    (
        "Work from home. Earn 50000 monthly. Pay 999 registration fee today.",
        "Fake job offer",
    ),
    (
        "Invest now and get guaranteed profit with double your money.",
        "Investment scam",
    ),
    (
        "Congratulations! You won a lottery prize. Pay processing fee to claim.",
        "Prize / lottery scam",
    ),
    (
        "Click here to update your KYC and verify your account.",
        "Banking / OTP fraud",
    ),
]

@pytest.mark.parametrize("message, expected_category", TEST_CASES)
def test_scam_category_classification(message, expected_category):

    app = AppTest.from_file(str(APP_PATH))
    app.run()

    app.text_area[0].set_value(message)
    app.button[0].click()
    app.run()

    displayed_text = "\n".join(
        element.value for element in app.markdown
    )

    assert expected_category in displayed_text
