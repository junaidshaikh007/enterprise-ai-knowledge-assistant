import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class DummyClient:
    def update_current_span(self, *args, **kwargs):
        pass

def dummy_observe(*args, **kwargs):
    def decorator(func):
        return func
    if len(args) == 1 and callable(args[0]):
        return args[0]
    return decorator

# Check if Langfuse credentials are valid
if settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
    try:
        from langfuse import observe, get_client
    except Exception:
        observe = dummy_observe
        def get_client():
            return DummyClient()
else:
    observe = dummy_observe
    def get_client():
        return DummyClient()
