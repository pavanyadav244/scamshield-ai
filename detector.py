import re
from urllib.parse import urlparse


CATEGORY_RULES = {
    "Banking / OTP fraud": [
        r"\b(bank account|account blocked|kyc|otp|one[- ]time password|cvv|bank details|debit card|credit card)\b",
        r"(బ్యాంక్ ఖాతా|ఖాతా బ్లాక్|ఓటీపీ|పిన్|కేవైసీ)",
    ],

    "UPI / payment fraud": [
        r"\b(upi|payment request|collect request|scan (?:the )?qr|qr code|upi pin|refund pending|payment failed)\b",
        r"(యూపీఐ|క్యూఆర్|చెల్లింపు|డబ్బులు పంపండి|రిఫండ్)",
    ],

    "Fake job offer": [
        r"\b(job offer|work from home|registration fee|joining fee|job selected|no interview|required fee|daily income|vacancy)\b",
        r"(ఉద్యోగం|జాబ్|రిజిస్ట్రేషన్ ఫీజు|జాయినింగ్ ఫీజు)",
    ],

    "Investment scam": [
        r"\b(investment|guaranteed profit|risk[- ]free return|double your money|trading signals|crypto profit|daily returns)\b",
        r"(పెట్టుబడి|లాభం|డబ్బు రెట్టింపు)",
    ],

    "Prize / lottery scam": [
        r"\b(lottery|you(?:'| a)?ve won|winner|prize money|claim your reward|lucky draw|free gift)\b",
        r"(లాటరీ|బహుమతి|గెలుచుకున్నారు|లక్కీ డ్రా)",
    ],

    "Suspicious link / phishing": [
        r"\b(click here|verify your account|update kyc|login now|password reset|confirm your details|http://|www\.)\b",
        r"(లింక్ క్లిక్ చేయండి|వివరాలు నమోదు చేయండి|కేవైసీ అప్డేట్)",
    ],
}


def extract_urls(text):
    found = re.findall(
        r"(?i)\b(?:https?://|www\.)[^\s<>\"']+",
        text
    )

    return [
        item.rstrip(".,!?;:)]}")
        for item in found
    ]


def classify_categories(text):

    categories = []

    for category, patterns in CATEGORY_RULES.items():

        if any(
            re.search(pattern, text, re.I)
            for pattern in patterns
        ):
            categories.append(category)

    urls = extract_urls(text)

    if urls and "Suspicious link / phishing" not in categories:
        categories.append("Link present — inspect carefully")

    return categories or ["No category confidently identified"]


def predict_category(text):

    categories = classify_categories(text)

    # Select the first matching category for single-label evaluation.
    return categories[0]
