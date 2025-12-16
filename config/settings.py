import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Belevita Client Configuration
AGENT_ID = 19
CLIENT_ID = 6

# Supabase Configuration (via MCP)
SUPABASE_PROJECT_REF = "usszdhgupdbdfhdtjmpb"

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Error Detection Configuration
ERROR_DETECTION_SAMPLE_RATE = 0.15  # 15% of conversations for AI analysis
AI_ANALYSIS_BATCH_SIZE = 50  # Number of parallel API calls
AI_MODEL = "gemini-2.5-flash"  # Model for conversation analysis

# Performance Configuration
CACHE_ENABLED = True
BATCH_SIZE = 10000  # Records per batch for Supabase queries
OUTPUT_DIR = "output/data"
CACHE_DIR = "output/cache"

# Error Detection Weights
ERROR_WEIGHTS = {
    "phrase_matching": 0.30,
    "behavioral_patterns": 0.25,
    "ai_analysis": 0.35,
    "sentiment_correlation": 0.10
}

# Error Confidence Thresholds
ERROR_THRESHOLDS = {
    "high": 70,  # >70% = high confidence error
    "medium": 40,  # 40-70% = medium confidence error
    # <40% = low confidence error
}

# Metrics Configuration
RESPONSE_TIME_OUTLIER_THRESHOLD = 300  # 5 minutes in seconds
SHORT_CONVERSATION_THRESHOLD = 3  # messages
RAPID_ABANDONMENT_THRESHOLD = 120  # 2 minutes in seconds
STUCK_SESSION_THRESHOLD = 1800  # 30 minutes in seconds
