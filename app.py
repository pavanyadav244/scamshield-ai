
import re
import streamlit as st
from urllib.parse import urlparse
from PIL import Image
import pytesseract

st.set_page_config(
    page_title="ScamShield AI",
    page_icon="🛡️",
    layout="centered"
)

st.title("🛡️ ScamShield AI")
st.subheader("Cyber-fraud prevention assistant")
st.write(
    "Check suspicious messages, URLs and screenshots "
    "before clicking links or making payments."
)

language = st.selectbox(
    "Choose language / భాషను ఎంచుకోండి",
    ["English", "తెలుగు"]
)

if language == "తెలుగు":
    st.info("సందేహాస్పద సందేశాలు లేదా స్క్రీన్‌షాట్‌లను తనిఖీ చేయండి.")

st.caption(
    "Educational prototype. Results are indicators, not proof of fraud."
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
            r"investment opportunity|risk-free return)\b",
        "Telugu fraud-related wording":
            r"(ఓటీపీ|పిన్|పాస్‌వర్డ్|బహుమతి|వెంటనే|ఖాతా బ్లాక్)"
    }

    for label, pattern in patterns.items():
        if re.search(pattern, text_lower):
            indicators.append(label)

    urls = re.findall(r"https?://[^\s]+|www\.[^\s]+", text)

    for url in urls:
        cleaned = url.rstrip(".,!?;:)")
        parsed = urlparse(
            cleaned if cleaned.startswith("http")
            else "https://" + cleaned
        )
        if parsed.scheme == "http":
            indicators.append("Link uses unencrypted HTTP")
        if "@" in parsed.netloc:
            indicators.append("URL contains a potentially deceptive @ symbol")
        if re.search(r"\d{5,}", parsed.netloc):
            indicators.append("URL contains an unusual numeric domain")

    indicators = list(dict.fromkeys(indicators))

    if len(indicators) >= 3:
        risk = "HIGH"
    elif indicators:
        risk = "CAUTION"
    else:
        risk = "UNCERTAIN"

    return risk, indicators, urls

def show_analysis(text):
    risk, indicators, urls = analyse_message(text)
    st.subheader("Analysis result")

    if risk == "HIGH":
        st.error("HIGH RISK — Multiple warning signs detected.")
    elif risk == "CAUTION":
        st.warning("CAUTION — A potential warning sign was detected.")
    else:
        st.info("No configured warning signs detected; this does not mean safe.")

    st.write("**Why was it flagged?**")
    if indicators:
        for item in indicators:
            st.write(f"- {item}")
    else:
        st.write("No indicators from the current rules were found.")

    if urls:
        st.write("**Links found**")
        for url in urls:
            st.code(url)
        st.caption("This prototype does not verify website reputation.")

    st.write("**Safety guidance**")
    st.write("- Never share OTPs, PINs or passwords.")
    st.write("- Verify requests using the organisation's official app or website.")
    st.write("- Do not pay unexpected fees to receive prizes or jobs.")
    st.write(
        "- In India, if money is lost to cyber fraud, call 1930 promptly "
        "and use the official National Cyber Crime Reporting Portal."
    )

tab_message, tab_image = st.tabs(
    ["📝 Message / URL", "🖼️ Screenshot Scanner (OCR)"]
)

with tab_message:
    message = st.text_area(
        "Paste suspicious message, email or URL",
        height=160,
        key="message_input"
    )
    if st.button("Analyse Message"):
        if message.strip():
            show_analysis(message)
        else:
            st.warning("Please enter a message first.")

with tab_image:
    uploaded_image = st.file_uploader(
        "Upload a screenshot of a suspicious message",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_image:
        image = Image.open(uploaded_image).convert("RGB")
        st.image(image, caption="Uploaded screenshot", use_container_width=True)

        if st.button("Extract Text and Analyse"):
            try:
                extracted_text = pytesseract.image_to_string(image)
                st.subheader("Extracted text")
                st.text_area(
                    "Review the extracted text",
                    value=extracted_text,
                    height=160
                )

                if extracted_text.strip():
                    show_analysis(extracted_text)
                else:
                    st.warning(
                        "No readable text found. Try a clearer screenshot."
                    )
            except Exception:
                st.error(
                    "OCR is not configured on the server yet. "
                    "We need to install the Tesseract OCR engine before "
                    "screenshot scanning can work."
                )

st.caption(
    "ScamShield AI is a prototype, can make mistakes, and does not "
    "replace official verification."
)
