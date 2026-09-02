# OBSERVED

Owned flag records (no cluster):

timeout=0 wait_for_creation=true for=jsonpath object_exists=true → abort wait-for-creation-requires-timeout, visited false
timeout=0 wait_for_creation=false for=jsonpath object_exists=true → oneshot visit
timeout=0 wait_for_creation=true for=delete object_exists=true → oneshot visit
