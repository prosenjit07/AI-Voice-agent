import re

def test_patterns():
    """Test the regex patterns to see which one matches"""
    
    test_text = "my email is john@example.com"
    lower_text = test_text.lower().strip()
    
    print(f"Testing text: '{test_text}'")
    print("=" * 50)
    
    # Email patterns
    email_patterns = [
        r"(?:my email is|email is|my email address is|email address)\s+([^\s]+@[^\s]+\.[^\s]+)",
        r"(?:set email to|put email as)\s+([^\s]+@[^\s]+\.[^\s]+)",
        r"(?:email)\s+([^\s]+@[^\s]+\.[^\s]+)"
    ]
    
    print("Testing email patterns:")
    for i, pattern in enumerate(email_patterns):
        match = re.search(pattern, lower_text)
        if match:
            print(f"  ✅ Pattern {i+1} matches: {pattern}")
            print(f"     Captured: '{match.group(1)}'")
        else:
            print(f"  ❌ Pattern {i+1} doesn't match: {pattern}")
    
    # Message patterns
    message_patterns = [
        r"(?:my message is|message is|i want to say|tell them)\s+(.+)",
        r"(?:set message to|put message as)\s+(.+)",
        r"(?:message)\s+(.+)"
    ]
    
    print("\nTesting message patterns:")
    for i, pattern in enumerate(message_patterns):
        match = re.search(pattern, lower_text)
        if match:
            print(f"  ✅ Pattern {i+1} matches: {pattern}")
            print(f"     Captured: '{match.group(1)}'")
        else:
            print(f"  ❌ Pattern {i+1} doesn't match: {pattern}")
    
    # Name patterns
    name_patterns = [
        r"(?:my name is|i am|i'm|name is|call me)\s+([a-zA-Z\s]+)",
        r"(?:set name to|put name as)\s+([a-zA-Z\s]+)",
        r"(?:^name\s+)([a-zA-Z\s]+)"
    ]
    
    print("\nTesting name patterns:")
    for i, pattern in enumerate(name_patterns):
        match = re.search(pattern, lower_text)
        if match:
            print(f"  ✅ Pattern {i+1} matches: {pattern}")
            print(f"     Captured: '{match.group(1)}'")
        else:
            print(f"  ❌ Pattern {i+1} doesn't match: {pattern}")

if __name__ == "__main__":
    test_patterns() 