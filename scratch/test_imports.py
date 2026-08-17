import sys
import os

print("Step 1: Starting test...", flush=True)

print("Step 2: Importing app.core.config...", flush=True)
import app.core.config
print("Step 2: Done!", flush=True)

print("Step 3: Importing app.core.database...", flush=True)
import app.core.database
print("Step 3: Done!", flush=True)

print("Step 4: Importing app.core.vector_store...", flush=True)
import app.core.vector_store
print("Step 4: Done!", flush=True)

print("Step 5: Importing app.services.embedding_service...", flush=True)
import app.services.embedding_service
print("Step 5: Done!", flush=True)

print("Step 6: Importing app.services.llm_service...", flush=True)
import app.services.llm_service
print("Step 6: Done!", flush=True)

print("Step 7: Importing app.api.v1.auth...", flush=True)
import app.api.v1.auth
print("Step 7: Done!", flush=True)

print("Step 8: Importing app.api.v1.documents...", flush=True)
import app.api.v1.documents
print("Step 8: Done!", flush=True)

print("Step 9: Importing app.api.v1.chat...", flush=True)
import app.api.v1.chat
print("Step 9: Done!", flush=True)

print("Step 10: Importing app.main...", flush=True)
import app.main
print("Step 10: ALL SUCCESS!", flush=True)
