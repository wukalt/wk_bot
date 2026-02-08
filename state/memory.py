from collections import defaultdict, deque


sessions = {}
extract_mode = {}
chat_memory = defaultdict(lambda: deque(maxlen=50))
