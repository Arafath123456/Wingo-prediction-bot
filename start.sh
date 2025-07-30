#!/bin/bash

# Initialize database
python -c "from database.session import init_db; init_db()"

# Train initial models (if not exists)
if [ ! -f "ml_engine/models/xgboost_color.pkl" ]; then
  echo "Training initial models..."
  python -c "from ml_engine.model_training import train_all_models; \
             from database.crud import get_latest_rounds; \
             from database.session import get_session; \
             train_all_models(get_latest_rounds(get_session(), 500))"
fi

# Start the main application
exec python main.py