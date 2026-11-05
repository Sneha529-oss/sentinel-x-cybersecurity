"""
SENTINEL X - Cybersecurity Detection Rules
PRN: 202401110046

Educational pattern-matching rules for cybersecurity threats.
Each rule defines the regex pattern, target category, detailed component breakdown,
and 5 matching + 5 non-matching test cases.
"""

DETECTION_RULES = [
    {
        "id": "RULE-01",
        "name": "SQL Injection Indicators",
        "category": "SQL Injection",
        "pattern": r"(?i)(union\s+select|or\s+1=1|drop\s+table)",
        "flags": "IGNORECASE",
        "severity": "HIGH",
        "mitre_id": "CWE-89 / T1190",
        "purpose": "Detect common SQL injection indicators such as query stacking, tautology bypasses (1=1), and destructive DDL statements.",
        "explanation": (
            "Identifies classic SQL injection signatures: "
            "'union\\s+select' matches UNION-based data extraction; "
            "'or\\s+1=1' matches tautology conditions used for authentication bypass; "
            "'drop\\s+table' matches destructive schema manipulation commands. "
            "Case-insensitive matching is enabled via (?i)."
        ),
        "components": [
            {"token": "(?i)", "meaning": "Inline case-insensitivity flag; matches uppercase, lowercase, or mixed case like UnIoN SeLeCt."},
            {"token": "(...|...|...)", "meaning": "Alternation group; matches any of the three SQL injection patterns separated by the pipe symbol."},
            {"token": "union\\s+select", "meaning": "Matches 'union' followed by one or more whitespace characters (\\s+) and 'select'."},
            {"token": "or\\s+1=1", "meaning": "Matches the boolean tautology 'or' followed by whitespace and '1=1', frequently used to bypass SQL login WHERE clauses."},
            {"token": "drop\\s+table", "meaning": "Matches the DDL command 'drop' followed by whitespace and 'table', used for data destruction."}
        ],
        "matching_cases": [
            "admin' OR 1=1 --",
            "SELECT * FROM users WHERE id=1 UNION  SELECT username, password FROM admin",
            "'; DROP TABLE employees; --",
            "user' oR   1=1#",
            "1 UNION    SELECT credit_card, cvv FROM payments"
        ],
        "non_matching_cases": [
            "SELECT * FROM users WHERE username='alice'",
            "The European Union summit will select a new president.",
            "Please drop the table cloth on the dining table.",
            "order_number = 101 AND user_id = 45",
            "Hello, welcome to our academic portal."
        ]
    },
    {
        "id": "RULE-02",
        "name": "Script Injection Indicators",
        "category": "Script Injection",
        "pattern": r"(?i)(<script|javascript:|onerror\s*=)",
        "flags": "IGNORECASE",
        "severity": "HIGH",
        "mitre_id": "CWE-79 / T1059.007",
        "purpose": "Identify common Cross-Site Scripting (XSS) and script injection indicators in client payloads or web requests.",
        "explanation": (
            "Detects primary web script injection vectors: "
            "'<script' identifies raw HTML script tags; "
            "'javascript:' identifies URI schemes designed to execute arbitrary code in href or src attributes; "
            "'onerror\\s*=' identifies inline DOM event handler attributes commonly used to trigger payloads via broken image tags."
        ),
        "components": [
            {"token": "(?i)", "meaning": "Case-insensitive flag allowing matching of <SCRIPT>, Javascript:, etc."},
            {"token": "<script", "meaning": "Matches the opening HTML script tag identifier, indicating potential inline or external script loading."},
            {"token": "javascript:", "meaning": "Matches pseudo-protocol URI scheme used to execute JavaScript code when clicked or loaded."},
            {"token": "onerror\\s*=", "meaning": "Matches the 'onerror' event handler attribute followed by zero or more whitespace characters and '='."}
        ],
        "matching_cases": [
            "<script>alert(1)</script>",
            "<a href=\"javascript:stealCookies()\">Click here</a>",
            "<img src=\"invalid.jpg\" onerror = \"alert('XSS')\" />",
            "<SCRIPT SRC=\"https://evil-attacker.com/payload.js\"></SCRIPT>",
            "<body onload=\"javascript:void(0)\" onerror=console.log(document.cookie)>"
        ],
        "non_matching_cases": [
            "The movie script was written by an acclaimed author.",
            "Please visit https://example.com/login for authentication.",
            "We encountered an error in module payment_gateway.",
            "print('Hello world from Python script')",
            "Check out our new JavaScript framework tutorial."
        ]
    },
    {
        "id": "RULE-03",
        "name": "Directory Traversal",
        "category": "Directory Traversal",
        "pattern": r"(\.\./|\.\.\\)",
        "flags": "STANDARD",
        "severity": "CRITICAL",
        "mitre_id": "CWE-22 / T1083",
        "purpose": "Identify directory and path traversal sequences attempting to break out of root web or application directories.",
        "explanation": (
            "Detects directory traversal path manipulation attempts using parent directory references: "
            "'\\.\\./' matches Unix-style parent directory references (../); "
            "'\\.\\.\\\\' matches Windows-style parent directory references (..\\). "
            "Escaped dots ensure literal periods are matched rather than any character."
        ),
        "components": [
            {"token": "\\.\\./", "meaning": "Matches two literal dots followed by a forward slash ('../'), the Unix parent directory operator."},
            {"token": "|", "meaning": "Alternation operator matching either the Unix or Windows separator pattern."},
            {"token": "\\.\\.\\\\", "meaning": "Matches two literal dots followed by a backslash ('..\\\\'), the Windows parent directory operator."}
        ],
        "matching_cases": [
            "../../etc/passwd",
            "..\\..\\Windows\\System32\\cmd.exe",
            "GET /download?file=../../../secrets.txt HTTP/1.1",
            "upload/avatar/../../config/database.yml",
            "C:\\inetpub\\wwwroot\\..\\..\\boot.ini"
        ],
        "non_matching_cases": [
            "/var/www/html/index.php",
            "C:\\Program Files\\SentinelX\\app.py",
            "Documentation version 2.0.1 is now live.",
            "The score was 3..2 in the final match.",
            "https://portal.university.edu/dashboard"
        ]
    },
    {
        "id": "RULE-04",
        "name": "Suspicious Command Indicators",
        "category": "Command Injection",
        "pattern": r"(?i)(rm\s+-rf|powershell\s+-enc|cmd\.exe)",
        "flags": "IGNORECASE",
        "severity": "CRITICAL",
        "mitre_id": "CWE-78 / T1059",
        "purpose": "Identify selected suspicious operating system commands and administrative shell invocations.",
        "explanation": (
            "Flags high-risk system commands commonly embedded in command injection or exploit delivery payloads: "
            "'rm\\s+-rf' matches recursive forced file deletion in Unix-like systems; "
            "'powershell\\s+-enc' matches PowerShell invocation with base64 encoded command arguments (heavily used by malware); "
            "'cmd\\.exe' matches direct Windows command prompt shell execution."
        ),
        "components": [
            {"token": "(?i)", "meaning": "Case-insensitive flag to match CMD.EXE, PowerShell -ENC, etc."},
            {"token": "rm\\s+-rf", "meaning": "Matches Unix command 'rm' followed by whitespace and recursive force flag '-rf'."},
            {"token": "powershell\\s+-enc", "meaning": "Matches PowerShell invocation flag '-enc' used to pass obfuscated Base64 commands."},
            {"token": "cmd\\.exe", "meaning": "Matches explicit invocation of Windows Command Processor (cmd.exe)."}
        ],
        "matching_cases": [
            "rm -rf /important-directory",
            "; powershell -enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGo...",
            "&& C:\\Windows\\System32\\cmd.exe /c whoami",
            "sudo rm   -rf /var/log/*",
            "cmd.exe /c net user hacker Password123 /add"
        ],
        "non_matching_cases": [
            "echo 'Compilation successful'",
            "The company will transform its powershell training program.",
            "Please confirm if the meeting is rescheduled.",
            "git commit -m 'Fixed bug in command parser'",
            "docker run -d --name webserver nginx:alpine"
        ]
    },
    {
        "id": "RULE-05",
        "name": "Suspicious URL Indicators",
        "category": "Phishing / Malicious URL",
        "pattern": r"(?i)(https?://[^\s]*(login|verify|secure)[^\s]*)",
        "flags": "IGNORECASE",
        "severity": "MEDIUM",
        "mitre_id": "CWE-20 / T1566.002",
        "purpose": "Identify URLs containing selected potentially suspicious authentication or verification keywords often used in phishing lures.",
        "explanation": (
            "Flags web addresses incorporating sensitive authentication triggers: "
            "'https?://' matches HTTP or HTTPS protocol prefixes; "
            "'[^\\s]*' matches any non-whitespace domain and path characters; "
            "'(login|verify|secure)' flags keywords commonly abused in phishing, credential harvesting, or fake portals."
        ),
        "components": [
            {"token": "https?://", "meaning": "Matches URL scheme: 'http://' or 'https://' (? makes 's' optional)."},
            {"token": "[^\\s]*", "meaning": "Matches zero or more non-whitespace characters leading up to keyword."},
            {"token": "(login|verify|secure)", "meaning": "Matches key credential-harvesting keywords: 'login', 'verify', or 'secure'."},
            {"token": "[^\\s]*", "meaning": "Matches any remaining non-whitespace URL parameters, query strings, or path segments."}
        ],
        "matching_cases": [
            "http://paypa1-account-verify.suspicious-domain.ru/auth",
            "https://bankofamerica.secure-update-notice.com/login.html",
            "http://internal-portal-login.xyz/credential_check",
            "https://office365-secure-password-reset.net/verify?token=9382",
            "http://update-secure-banking-access.com"
        ],
        "non_matching_cases": [
            "ftp://files.university.edu/public/cs201_syllabus.pdf",
            "Just sent the invoice to your corporate email.",
            "Visit our blog at https://techblog.dev/articles/toc-automata",
            "The security perimeter was verified by our audit team.",
            "User account verified successfully on local database."
        ]
    }
]

def get_rule_by_id(rule_id):
    """Retrieve rule configuration by rule ID."""
    for rule in DETECTION_RULES:
        if rule["id"].lower() == rule_id.lower():
            return rule
    return None

def get_rules_by_category(category):
    """Filter detection rules by category or return all if 'all'."""
    if not category or category.lower() in ["all", "all categories"]:
        return DETECTION_RULES
    return [r for r in DETECTION_RULES if r["category"].lower() == category.lower()]

