import re
import html

class TextCleaner:
    def __init__(self):
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.whitespace_pattern = re.compile(r'\s+')

    def clean(self, text: str) -> str:
        if not text:
            return ""
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove URLs
        text = self.url_pattern.sub('', text)
        
        # Normalize whitespace
        text = self.whitespace_pattern.sub(' ', text).strip()
        
        return text
