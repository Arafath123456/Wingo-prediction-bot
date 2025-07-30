#!/bin/bash

# Check if application is responding
curl -f http://localhost:8000/health || exit 1

# Check database connection
python -c "from database.session import get_session; \
           session = get_session(); \
           session.execute('SELECT 1')" || exit 1

exit 0