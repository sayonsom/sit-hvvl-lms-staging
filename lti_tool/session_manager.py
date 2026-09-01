# session_manager.py

import threading
import logging

logger = logging.getLogger(__name__)

# Thread-safe state store
state_store = {}
state_lock = threading.Lock()

def store_state(state, data):
    """
    Store state data in the state store.
    """
    with state_lock:
        state_store[state] = data
        logger.debug(f"Stored state data for state: {state}")

def get_state_data(state):
    """
    Retrieve state data by state value.
    """
    with state_lock:
        data = state_store.pop(state, None)  # Remove after retrieving for security
        logger.debug(f"Retrieved and removed state data for state: {state}")
        return data
