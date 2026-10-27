import re
import streamlit as st
from urllib.parse import urlparse

st.set_page_config(
    page_title="ScamShield AI",
    page_icon="🛡️",
    layout="centered"
)

st.title("🛡️ ScamShield AI")
st.subheader("Your AI-powered cyber-fraud prevention assistant")
st.write(
    "Check suspicious messages before clicking links, "
    "sharing personal information, or making payments."
)

language = st.selectbox("Choose language / భాషను ఎంచుకోండి", [
    "English", "తెలుగు"
])

if language == "తెలుగు":
    st.info("సందేహాస్పద సందేశాలు మరియు లింకులను తనిఖీ చేయండి.")
    input_label = "సందేహాస్పద సందేశాన్ని ఇక్కడ నమోదు చేయండి"
    button_label = "తనిఖీ చేయండి"
else:
    input_label = "Paste a suspicious message, email, or URL"
    button_label = "Analyse Message"

message = st.text_area(input_label, height=180)

st.caption(
    "Demo version: results are based on indicators, "
    "not a definitive determination of fraud."
)

def analyse_message(text):
    text_lower = text.lower()
    indicators = []

    patterns = {
        "Urgent or threatening language":
            r"\b(urgent|immediately|suspend|blocked|expire|"
            r"within 24 hours|act now)\b",

        "Request for sensitive information":
            r"\b(otp|pin|password|cvv|bank details|"
            r"card details|verification code)\b",

        "Financial pressure or unrealistic rewards":
            r"\b(prize|lottery|won|reward|guaranteed profit|"
            r"double your money|claim now|processing fee)\b",

        "Job or investment-related offer":
            r"\b(easy money|work from home|daily income|"
            r"investment opportunity|risk-free return)\b"
    }

    for description, pattern in patterns.items():
        if re.search(pattern, text_lower):
            indicators.append(description)

    urls = re.findall(r"https?://[^\s]+|www\.[^\s]+", text)

    for url in urls:
        cleaned = url.rstrip(".,!?;:)")
        parsed = urlparse(
            cleaned if cleaned.startswith("http") else "https://" + cleaned
        )
        domain = parsed.netloc.lower()

        if parsed.scheme == "http":
            indicators.append("Link uses unencrypted HTTP")

        if re.search(r"\d{5,}", domain):
            indicators.append("URL contains an unusual numeric domain")

        if "@" in parsed.netloc:
            indicators.append("URL contains a potentially deceptive @ symbol")

    unique_indicators = list(dict.fromkeys(indicators))

    if len(unique_indicators) >= 3:
        risk = "HIGH"
    elif len(unique_indicators) >= 1:
        risk = "CAUTION"
    else:
        risk = "UNCERTAIN"

    return risk, unique_indicators, urls


if st.button(button_label, type="primary"):
    if not message.strip():
        st.warning("Please enter a message first.")
    else:
        risk, indicators, urls = analyse_message(message)

        st.divider()
        st.subheader("Analysis Result")

        if risk == "HIGH":
            st.error("⚠️ HIGH RISK — Multiple suspicious indicators found.")
        elif risk == "CAUTION":
            st.warning("⚠️ CAUTION — Suspicious indicators were found.")
        else:
            st.info(
                "No configured indicators were detected. "
                "This does NOT mean the message is safe."
            )

        st.write("### Why did we flag this?")

        if indicators:
            for item in indicators:
                st.write(f"🔎 {item}")
        else:
            st.write("No indicators from our current rules were detected.")

        if urls:
            st.write("### Links found")
            for url in urls:
                st.code(url)
            st.caption(
                "Links are displayed for inspection only; this demo "
                "does not verify whether a website is malicious."
            )

        st.write("### Recommended safety actions")
        st.write("- Do not share OTPs, PINs, or passwords.")
        st.write("- Avoid clicking unexpected links.")
        st.write("- Verify claims through the organisation's official app or website.")
        st.write("- Never pay an unexpected fee to receive a prize or job.")
        st.write(
            "- If you have lost money to cyber fraud in India, "
            "call 1930 promptly and use the official "
            "National Cyber Crime Reporting Portal."
        )

        st.caption(
            "ScamShield AI is an educational prototype. "
            "It can make mistakes and does not replace official verification."
        )
