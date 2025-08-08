import re

def format_for_google_chat(text):
    text = text.replace('<br>', '\n')
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'*_\1_*', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', text)
    text = re.sub(r'\*(.*?)\*', r'_\1_', text)
    return text
