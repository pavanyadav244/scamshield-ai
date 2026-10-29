import re
import ipaddress
from urllib.parse import urlparse

import streamlit as st
from PIL import Image
import pytesseract

st.set_page_config(page_title="ScamShield AI", page_icon="🛡️", layout="centered")

st.title("🛡️ ScamShield AI")
st.subheader("Cyber-fraud prevention assistant")
st.write("Check suspicious messages, URLs and screenshots before clicking links or making payments.")
language = st.selectbox("Choose language / భాషను ఎంచుకోండి", ["English", "తెలుగు"])
if language == "తెలుగు":
    st.info("సందేహాస్పద సందేశాలు, లింకులు లేదా స్క్రీన్‌షాట్‌లను తనిఖీ చేయండి.")
st.caption("Educational prototype. Results are warning indicators, not proof of fraud.")

RULES = [
    ("Urgency or threats", r"\b(urgent|immediately|suspend(?:ed)?|blocked|expire[sd]?|within\s+24\s+hours|act\s+now|last\s+chance|final\s+warning)\b", 2),
    ("Sensitive information requested", r"\b(otp|one[- ]time password|pin|password|cvv|bank details|card details|verification code|upi pin)\b", 3),
    ("Upfront payment or fee", r"\b(registration fee|processing fee|pay\s+(?:now|first)|advance fee|security deposit|activation fee)\b", 3),
    ("Unrealistic reward or guaranteed return", r"\b(lottery|you(?:'| a)?ve won|prize money|guaranteed profit|double your money|risk[- ]free return|claim your reward|free gift)\b", 2),
    ("Job or investment offer", r"\b(work from home|daily income|no experience required|investment opportunity|limited vacancies|earn \d+)\b", 1),
    ("Telugu scam-related wording", r"(ఓటీపీ|పిన్|పాస్‌వర్డ్|బహుమతి|వెంటనే|ఖాతా బ్లాక్|డబ్బులు పంపండి|రిజిస్ట్రేషన్ ఫీజు|గెలుచుకున్నారు|లింక్ క్లిక్ చేయండి|బ్యాంక్ ఖాతా)", 2),
    ("Remote-access or screen-sharing request", r"\b(install anydesk|install teamviewer|screen sharing|remote access app|share your screen)\b", 3),
]

def extract_urls(text):
    found = re.findall(r"(?i)\b(?:https?://|www\.)[^\s<>\"']+", text)
    result = []
    for item in found:
        item = item.rstrip(".,!?;:)]}")
        if item and item not in result:
            result.append(item)
    return result

def inspect_url(raw_url):
    candidate = raw_url.strip()
    if candidate.lower().startswith("www."):
        candidate = "http://" + candidate
    parsed = urlparse(candidate)
    host = (parsed.hostname or "").lower().rstrip(".")
    findings = []
    if parsed.scheme.lower() == "http":
        findings.append(("Link uses HTTP rather than HTTPS", 1))
    if not host:
        findings.append(("Could not parse the URL hostname", 1))
        return findings
    if parsed.username is not None or parsed.password is not None or "@" in parsed.netloc:
        findings.append(("URL contains user-info or an @ symbol that can be deceptive", 3))
    try:
        ipaddress.ip_address(host)
        findings.append(("URL uses a raw IP address instead of a regular domain", 2))
    except ValueError:
        pass
    if host.startswith("xn--") or ".xn--" in host:
        findings.append(("Domain contains an internationalized/punycode label", 2))
    if len(host) > 50:
        findings.append(("Unusually long hostname", 1))
    if host.count("-") >= 3:
        findings.append(("Hostname contains many hyphens", 1))
    if re.search(r"\d{5,}", host):
        findings.append(("Hostname contains a long numeric sequence", 1))
    if host in {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "cutt.ly", "rb.gy"}:
        findings.append(("URL uses a link-shortening service; destination is hidden", 2))
    return findings

def analyse_message(text):
    indicators, categories, score = [], [], 0
    for label, pattern, points in RULES:
        if re.search(pattern, text, re.I):
            indicators.append(label)
            categories.append(label)
            score += points
    urls = extract_urls(text)
    for url in urls:
        for label, points in inspect_url(url):
            item = f"{label}: {url}"
            if item not in indicators:
                indicators.append(item)
                score += points
    risk = "HIGH" if score >= 6 else "CAUTION" if score >= 2 else "UNCERTAIN"
    return risk, score, indicators, urls, categories

def show_analysis(text):
    risk, score, indicators, urls, categories = analyse_message(text)
    st.subheader("Analysis result")
    if risk == "HIGH":
        st.error("HIGH RISK — Several strong warning signs were detected.")
    elif risk == "CAUTION":
        st.warning("CAUTION — One or more warning signs were detected.")
    else:
        st.info("UNCERTAIN — Few configured warning signs were detected. This does not mean the message is safe.")
    st.metric("Heuristic warning score", f"{score} points")
    st.caption("This score uses transparent rules; it is not a probability of fraud or a verified AI prediction.")
    if categories:
        st.write("**Possible scam patterns**")
        for category in categories:
            st.write(f"- {category}")
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
        st.caption("The app checks visible URL patterns only. It does not visit links or verify domain reputation.")
    st.write("**Safety guidance**")
    st.write("- Never share OTPs, UPI PINs, PINs or passwords.")
    st.write("- Verify requests using the organisation's official app or website.")
    st.write("- Do not pay unexpected fees to receive a job, prize or loan.")
    st.write("- Do not install remote-access apps at a caller's request.")
    st.write("- In India, if money is lost to cyber fraud, call 1930 promptly and report through the official National Cyber Crime Reporting Portal.")
    st.caption("A warning does not prove fraud, and no warning does not prove safety. Verify independently.")

tab_message, tab_image = st.tabs(["📝 Message / URL", "🖼️ Screenshot Scanner (OCR)"])
with tab_message:
    message = st.text_area("Paste suspicious message, email or URL", height=160, key="message_input")
    if st.button("Analyse Message", type="primary"):
        if message.strip():
            show_analysis(message.strip())
        else:
            st.warning("Please enter a message first.")

with tab_image:
    uploaded_image = st.file_uploader("Upload a screenshot of a suspicious message", type=["png", "jpg", "jpeg"])
    if uploaded_image:
        try:
            image = Image.open(uploaded_image).convert("RGB")
            st.image(image, caption="Uploaded screenshot", use_container_width=True)
            if st.button("Extract Text and Analyse", type="primary"):
                try:
                    extracted_text = pytesseract.image_to_string(image, lang="eng")
                    st.subheader("Extracted text")
                    st.text_area("Review the extracted text", value=extracted_text, height=160, key="ocr_extracted_text")
                    if extracted_text.strip():
                        show_analysis(extracted_text)
                    else:
                        st.warning("No readable text found. Try a clearer screenshot.")
                except Exception as exc:
                    st.error("OCR is not available on the server. Check that Tesseract OCR is installed and available in PATH.")
                    st.caption(f"Technical detail: {type(exc).__name__}")
        except Exception:
            st.error("The uploaded file could not be opened. Try a PNG or JPG image.")

st.divider()
st.caption("ScamShield AI is an educational prototype. It can make mistakes and does not replace official verification.")
