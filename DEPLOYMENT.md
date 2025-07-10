# 🚀 Deployment Guide for Nutrient Tracker

## Quick Start (Recommended)

### Option 1: Streamlit Community Cloud (Free & Easy)
1. Push code to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Deploy directly from GitHub repository
4. Select `app.py` as main file
5. Your app is live! 🎉

### Option 2: Railway (Best for databases)
1. Sign up at [railway.app](https://railway.app)
2. Connect GitHub repository
3. Add PostgreSQL database (optional)
4. Deploy automatically
5. Set environment variables if needed

## Environment Variables

Set these on your deployment platform:

```
DATABASE_URL=your_postgresql_url
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py
```

## Files Created for Deployment

- `requirements.txt` - Python dependencies
- `Procfile` - Heroku deployment config
- `railway.json` - Railway deployment config
- `.streamlit/config.toml` - Streamlit configuration
- `.env.example` - Environment variables template

## Platform-Specific Instructions

### Streamlit Cloud
- Free for public repos
- Automatic deployments on git push
- Built-in secrets management

### Railway
- $5/month after free tier
- One-click PostgreSQL
- Great for full-stack apps

### Heroku
- $7/month minimum
- Mature platform
- Many add-ons available

### DigitalOcean
- $5/month minimum
- Good performance
- Managed databases

## Troubleshooting

1. **Port issues**: Make sure your platform supports the port in your config
2. **Dependencies**: All requirements are in `requirements.txt`
3. **Database**: Use PostgreSQL for production (SQLite for development only)
4. **Environment variables**: Set all required variables on your platform

Your app should be ready to deploy! 🚀
