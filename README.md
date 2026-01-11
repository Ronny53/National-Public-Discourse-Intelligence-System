# National Public Discourse Intelligence System (NIS)

## Overview

The National Public Discourse Intelligence System (NIS) is an AI-powered web application designed to aggregate, analyze, and visualize public sentiment across various social media platforms. By harnessing the power of machine learning and natural language processing, NIS provides real-time insights into public discourse on critical national topics, enabling both government institutions and citizens to track policy effectiveness, identify emerging concerns, and make data-driven decisions.

## The Problem

In today's digital age, public opinion is predominantly expressed through social media platforms. However, this vast landscape of information remains fragmented, making it challenging for policymakers and the public to:

- **Identify Genuine Concerns**: Distinguish authentic public sentiment from coordinated misinformation campaigns
- **Track Policy Impact**: Measure how government initiatives are perceived by citizens over time
- **Early Warning System**: Detect emerging issues before they escalate into major crises
- **Transparency**: Provide a unified, transparent platform where both government and public can access the same data and insights

For instance, India currently faces severe air pollution challenges. Citizens express their concerns, share personal experiences, and organize protests across multiple social media platforms. Without a centralized system, this valuable feedback remains scattered, making it difficult for policymakers to gauge the true magnitude of public concern and the effectiveness of mitigation efforts.

## Our Solution

NIS addresses these challenges by providing:

1. **Multi-Platform Data Aggregation**: Collects data from multiple social media sources (Reddit, Google Trends, and extensible to Twitter, Facebook, etc.)
2. **AI-Powered Analysis**: Utilizes sentiment analysis, emotion detection, and topic clustering to understand public discourse
3. **Integrity Verification**: Implements advanced bot detection algorithms to filter out manipulated content
4. **Risk Assessment**: Calculates escalation risk, trust index, and volatility metrics to identify critical issues
5. **Policy Brief Generation**: Automatically generates actionable insights for relevant government ministries
6. **Transparent Dashboard**: Provides an accessible web interface for both government officials and the public

## Key Features

### 1. Sentiment Analysis & Emotion Detection
- Analyzes posts using VADER sentiment analysis to classify content as positive, negative, or neutral
- Detects emotional states (anger, fear, joy, sadness) to understand the intensity of public concern
- Tracks sentiment trends over time to measure policy effectiveness

### 2. Integrity & Bot Detection
To ensure data authenticity, NIS employs multiple verification mechanisms:

- **Account Age Filtering**: Only processes posts from accounts that meet minimum age thresholds (e.g., accounts older than 6 months)
- **Amplification Detection**: Identifies coordinated campaigns by detecting unusual repetition patterns
- **Coordination Analysis**: Detects synchronized bursts of activity that may indicate bot networks
- **Trust Index Calculation**: Combines integrity metrics to assign trust scores to aggregated data

### 3. Topic Clustering & Issue Identification
- Uses K-Means clustering with TF-IDF vectorization to automatically group related posts
- Identifies emerging topics and their relative prominence in public discourse
- Highlights top keywords and themes within each cluster

### 4. Risk Assessment Indices
- **Escalation Risk**: Predicts the likelihood of an issue escalating based on sentiment, emotion, and volume
- **Trust Index**: Measures the authenticity and reliability of discourse (0-100 scale)
- **Volatility Index**: Tracks rapid changes in sentiment that may indicate instability

### 5. Policy Brief Generation
- Automatically generates executive summaries with recommended actions
- Maps issues to responsible government ministries
- Provides actionable insights for decision-makers

### 6. Email Alert System
- **Automatic Alerts**: Sends email notifications when risk score exceeds threshold (default: 70)
- **Manual Alerts**: Admin users can manually trigger alerts from the dashboard
- **Cooldown Protection**: Prevents alert spam with configurable cooldown periods
- **Admin-Only Access**: Alert management is restricted to admin users only

### 7. Privacy & Ethics
- Redacts personally identifiable information (PII) including emails and phone numbers
- Implements ethical filtering to exclude inappropriate content
- Maintains user privacy while preserving analytical value

## Real-World Example: Air Pollution Crisis

Consider India's ongoing air pollution crisis. Citizens across the country share their experiences, health concerns, and frustrations on social media. NIS would:

1. **Aggregate Concerns**: Collect posts from multiple platforms mentioning air quality, pollution, health impacts, etc.
2. **Analyze Sentiment**: Identify that 78% of posts express negative sentiment with high anger and fear emotions
3. **Detect Authenticity**: Filter out bot-generated content, ensuring only genuine citizen voices are represented
4. **Calculate Risk**: Assign a "High" escalation risk score, alerting policymakers to the urgency
5. **Track Effectiveness**: Monitor how sentiment changes after government implements new policies (e.g., odd-even vehicle schemes, industrial regulations)
6. **Generate Insights**: Automatically create a policy brief for the Ministry of Environment, Forest and Climate Change with recommended actions

Over time, both government and citizens can track:
- Whether new policies are working (sentiment becoming more positive)
- Geographic distribution of concerns (which regions need more attention)
- Long-term trends (is the situation improving or worsening)

This creates a feedback loop where policy decisions are informed by authentic public sentiment, and their effectiveness is measured transparently.

## Technical Architecture

### Backend
- **Framework**: FastAPI (Python)
- **NLP Libraries**: VADER Sentiment, TextBlob
- **ML Libraries**: scikit-learn (clustering, vectorization)
- **Data Sources**: Reddit API (PRAW), Google Trends (pytrends)
- **Data Processing**: Pandas, NumPy

### Frontend
- **Framework**: React with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Routing**: React Router

### Key Components

```
backend/
├── api/              # FastAPI routes and schemas
├── ingestion/        # Data collection from social media
├── preprocessing/    # Text cleaning and deduplication
├── nlp/              # Sentiment and emotion analysis
├── integrity/        # Bot detection and amplification analysis
├── clustering/       # Topic clustering algorithms
├── indices/          # Risk, trust, and volatility calculations
└── policy/           # Policy brief generation

frontend/
├── pages/            # Dashboard, Analytics, Policy Brief, Trends
├── components/       # Reusable UI components
└── services/         # API integration
```

## Advantages & Benefits

### For Government
1. **Evidence-Based Policy Making**: Access real-time, authentic public sentiment to inform decisions
2. **Early Warning System**: Identify emerging issues before they become crises
3. **Policy Effectiveness Tracking**: Measure how initiatives are perceived over time
4. **Resource Allocation**: Prioritize resources based on data-driven risk assessments
5. **Transparency**: Demonstrate accountability by making insights publicly available

### For Citizens
1. **Voice Amplification**: Ensure genuine public concerns are heard at the policy level
2. **Transparency**: Access the same data and insights as government officials
3. **Accountability**: Track whether government actions are addressing public concerns
4. **Informed Participation**: Make better decisions based on aggregated national sentiment
5. **Democracy**: Strengthen democratic processes through data-driven discourse

### For Society
1. **Reduced Misinformation**: Bot detection ensures only authentic voices influence policy
2. **Better Governance**: Improved decision-making leads to more effective policies
3. **Crisis Prevention**: Early detection of issues prevents escalation
4. **Social Cohesion**: Understanding public sentiment helps bridge gaps between citizens and government
5. **Innovation**: Creates a new model for public-private collaboration in governance

## Email Alert System

The Email Alert System provides automatic and manual email notifications for high-risk situations.

### Features
- **Automatic Alerts**: Triggers when escalation risk score exceeds the configured threshold (default: 70)
- **Manual Alerts**: Admin users can send alerts manually from the Alerts tab
- **Cooldown Protection**: Prevents alert spam with a configurable cooldown period (default: 15 minutes)
- **Test Email**: Verify email configuration with a test email function
- **Admin-Only Access**: The Alerts tab is only visible to users with admin role

### Configuration
Email alerts are configured via environment variables in `backend/.env`:
- `EMAIL_HOST`: SMTP server (default: smtp.gmail.com)
- `EMAIL_PORT`: SMTP port (default: 587)
- `EMAIL_USER`: Sender email address
- `EMAIL_APP_PASSWORD`: Gmail App Password (not regular password)
- `EMAIL_RECIPIENTS`: JSON array of recipient email addresses
- `ALERT_THRESHOLD`: Risk score threshold for auto-alerts (default: 70)
- `ALERT_COOLDOWN_MINUTES`: Minimum time between alerts (default: 15)

### Accessing the Alerts Tab
1. Log in with an admin account (`admin@nis.gov.in` / `admin123`)
2. Navigate to the "Alerts" tab in the navigation bar
3. View current risk status, send manual alerts, or test email configuration

**Note**: This system is for academic and demonstration purposes only. Recipients are treated as sub-branch/demo contacts, not official authorities.

## Enhanced Features & Future Improvements

Beyond the core functionality, the system includes several advanced features and potential enhancements:

### Current Enhancements
1. **Multi-Source Integration**: Extensible architecture allows easy addition of new social media platforms
2. **Synthetic Data Fallback**: Gracefully handles API limitations during development/demo phases
3. **Real-Time Updates**: Background task processing ensures dashboard remains responsive
4. **Role-Based Access**: Different user roles (admin, analyst, demo) for flexible access control
5. **Email Alert System**: Automated and manual email notifications for high-risk situations

### Recommended Future Enhancements

1. **Geographic Analysis**: Add location-based sentiment mapping to identify regional concerns
2. **Temporal Analysis**: Implement time-series forecasting to predict future sentiment trends
3. **Comparative Analysis**: Compare sentiment across different policy implementations or regions
4. **Language Support**: Extend NLP capabilities to regional languages (Hindi, Tamil, Bengali, etc.)
5. **Advanced Bot Detection**: 
   - Network graph analysis to identify bot clusters
   - Behavioral pattern recognition (posting frequency, time patterns)
   - Machine learning models trained on verified bot accounts
6. **Interactive Visualizations**: Enhanced charts with drill-down capabilities for deeper insights
7. **Alert System**: Automated notifications when critical risk thresholds are crossed
8. **API Access**: Provide public APIs for researchers and developers
9. **Historical Data**: Long-term storage and analysis of discourse trends
10. **Collaboration Features**: Allow citizens to flag important issues for priority analysis

## Getting Started

### Prerequisites

Before running the application, make sure you have the following installed:
- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16 or higher** - [Download Node.js](https://nodejs.org/)
- **pip** (Python package manager) - Usually comes with Python
- **npm** (Node package manager) - Usually comes with Node.js
- **Reddit API credentials** (optional) - The system will use synthetic data if Reddit credentials are not provided

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd National-Public-Discourse-Intelligence-System
```

### Step 2: Backend Setup

1. Navigate to the backend directory to install dependencies:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(On some systems, you may need to use `pip3` instead of `pip`)*

3. Configure environment variables:
   - While still in the `backend` directory, create a `.env` file (or copy `env.example` to `.env`)
   - Add the following configuration:
     ```
     # Email Alert Configuration (Required for email alerts)
     EMAIL_HOST=smtp.gmail.com
     EMAIL_PORT=587
     EMAIL_USER=your_email@gmail.com
     EMAIL_APP_PASSWORD=your_app_password
     EMAIL_RECIPIENTS=["recipient1@email.com","recipient2@email.com"]
     ALERT_THRESHOLD=70
     ALERT_COOLDOWN_MINUTES=15
     
     # Reddit API Credentials (Optional)
     REDDIT_CLIENT_ID=your_client_id
     REDDIT_CLIENT_SECRET=your_client_secret
     REDDIT_USER_AGENT=your_user_agent
     ```
   - **Email Setup**: For Gmail, you'll need to generate an App Password:
     1. Go to your Google Account settings
     2. Enable 2-Step Verification
     3. Generate an App Password for "Mail"
     4. Use this App Password (not your regular password) in `EMAIL_APP_PASSWORD`
   - If you skip Reddit credentials, the system will automatically use synthetic data for demonstration

4. **Important**: Go back to the root directory (where both `backend` and `frontend` folders are located):
   ```bash
   cd ..
   ```

5. Run the backend server from the root directory:
   ```bash
   python -m uvicorn backend.api.main:app --reload
   ```
   *(On some systems, you may need to use `python3` instead of `python`)*
   
   **Note**: The command must be run from the root directory (project root), not from inside the `backend` folder.

   The backend API will start at `http://localhost:8000`

### Step 3: Frontend Setup

1. Open a new terminal window (keep the backend server running)

2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

3. Install Node.js dependencies:
   ```bash
   npm install
   ```

4. Run the frontend development server:
   ```bash
   npm run dev
   ```

   The frontend application will start at `http://localhost:5173`

### Step 4: Access the Application

1. Open your web browser and navigate to `http://localhost:5173`
2. You should see the login page

### Default Login Credentials

For demo purposes, you can use any of the following accounts:
- **Admin Account** (Full access including Email Alerts): 
  - Email: `admin@nis.gov.in`
  - Password: `admin123`
- **Analyst Account**: 
  - Email: `analyst@nis.gov.in`
  - Password: `analyst123`
- **Demo Account**: 
  - Email: `demo@nis.gov.in`
  - Password: `demo123`

### Quick Start Scripts (Windows)

For Windows users, you can use the provided batch scripts:

1. **Setup**: Run `setup.bat` to install all dependencies
2. **Run**: Run `run.bat` to start both backend and frontend servers

These scripts will:
- Set up Python virtual environment
- Install backend dependencies
- Install frontend dependencies
- Create `.env` file from template
- Start both servers in separate windows

### Troubleshooting

- **`ModuleNotFoundError: No module named 'backend'`**: This error occurs if you run the uvicorn command from inside the `backend` directory. Make sure you're in the root directory (project root) when running `python -m uvicorn backend.api.main:app --reload`. The root directory is where both `backend` and `frontend` folders are located.
- **Backend won't start**: Make sure all Python dependencies are installed correctly. You should run `pip install -r requirements.txt` from inside the `backend` directory, but run the uvicorn command from the root directory.
- **Frontend won't start**: Ensure Node.js and npm are installed, and run `npm install` again from inside the `frontend` directory
- **Port already in use**: If port 8000 or 5173 is already in use, stop the application using those ports first, or change the ports in the configuration
- **API connection errors**: Make sure the backend server is running before starting the frontend, and that it's accessible at `http://localhost:8000`

## Project Structure

```
National-Public-Discourse-Intelligence-System/
├── backend/              # Python FastAPI backend
│   ├── api/             # API routes and schemas
│   │   └── routes/
│   │       ├── dashboard.py  # Dashboard endpoints
│   │       └── alerts.py     # Email alert endpoints
│   ├── clustering/      # Topic clustering
│   ├── config/          # Configuration settings
│   ├── database/        # Database models and services
│   │   └── alert_history.py  # Alert cooldown tracking
│   ├── email/           # Email alert service
│   │   └── email_service.py  # SMTP email functionality
│   ├── indices/         # Risk calculations
│   ├── ingestion/       # Data collection
│   ├── integrity/       # Bot detection
│   ├── nlp/             # NLP analysis
│   ├── policy/           # Policy brief generation
│   ├── preprocessing/   # Data cleaning
│   ├── env.example      # Environment variables template
│   └── requirements.txt # Python dependencies
├── frontend/            # React TypeScript frontend
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── pages/       # Page components
│   │   │   └── Alerts.tsx  # Email alerts page (admin only)
│   │   ├── services/    # API services
│   │   └── types/       # TypeScript types
│   └── public/          # Static assets
├── setup.bat            # Windows setup script
├── run.bat              # Windows run script
└── README.md           # This file
```

## Hackathon Context

This project was developed for a hackathon focusing on:
- **Governance**: Creating tools to improve democratic processes and policy-making
- **Web Application**: Building a modern, responsive web platform
- **AI/ML**: Leveraging machine learning and natural language processing for insights

## Future Development

This is currently a hackathon prototype. As we move towards production deployment, we plan to implement:
- Comprehensive authentication and authorization systems
- Proper database storage (currently using in-memory caching for the prototype)
- Enhanced error handling and logging mechanisms
- Rate limiting for API endpoints to ensure fair usage
- CI/CD pipelines for automated testing and deployment
- Comprehensive test coverage including unit, integration, and end-to-end tests
- Full compliance with data protection regulations and privacy laws

## License

This project is developed as part of a hackathon submission. All rights reserved.

## Contact

For questions or inquiries about this project, please refer to the hackathon submission details.

---

**Note**: This system is currently running on synthetic/dummy data due to API access limitations. In production, it would integrate with official social media APIs to process real-time public discourse data.

## Disclaimer

**This system is for academic and demonstration purposes only.** The Email Alert System and all features are designed for educational use in a hackathon context. Recipients of email alerts are treated as sub-branch/demo contacts, not official authorities.
