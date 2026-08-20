import os
from os import getenv as take

KEY = "DUE_CONST"

# owed
port = os.environ["DUE_PORT"]
key = os.getenv("DUE_API_KEY", "")
const = take(KEY)

# store is not a need
os.environ["DUE_INTERNAL"] = "set-by-app"
