#!/bin/bash

# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Create new project if doesn't exist
if ! railway project list | grep -q "WinGoBot"; then
  railway project create WinGoBot
fi

# Link to project
railway link WinGoBot

# Set environment variables
railway variables set \
  BOT_TOKEN=$BOT_TOKEN \
  USER_WHITELIST=$USER_WHITELIST \
  SENTRY_DSN=$SENTRY_DSN \
  RAILWAY_ENVIRONMENT=production

# Deploy application
railway up --detach