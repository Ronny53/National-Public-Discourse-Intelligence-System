"""
Time-series forecasting service for predicting future sentiment trends.
Uses historical sentiment data to forecast future patterns.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from backend.database.models import PostAnalysis, DashboardSummary

logger = logging.getLogger(__name__)


class SentimentForecaster:
    """
    Forecasts future sentiment trends based on historical data.
    Uses multiple forecasting methods for robust predictions.
    """
    
    def __init__(self):
        self.forecast_horizon_days = 7  # Predict next 7 days by default
    
    def forecast_sentiment_trends(
        self,
        db: Session,
        days_ahead: int = 7,
        use_prophet: bool = True
    ) -> Dict[str, Any]:
        """
        Forecast sentiment trends for the next N days based on historical data.
        
        Args:
            db: Database session
            days_ahead: Number of days to forecast (default: 7)
            use_prophet: Whether to use Prophet (more accurate but slower)
        
        Returns:
            Dictionary with forecast data including:
            - forecast_dates: List of future dates
            - predicted_sentiment: Predicted sentiment scores
            - confidence_intervals: Upper and lower bounds
            - trend_direction: "improving", "declining", or "stable"
        """
        try:
            # Get historical sentiment data
            historical_data = self._get_historical_sentiment(db, days=30)
            
            if len(historical_data) < 7:
                logger.warning("Insufficient historical data for forecasting. Need at least 7 days.")
                return self._generate_default_forecast(days_ahead)
            
            # Convert to time series
            df = pd.DataFrame(historical_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date').sort_index()
            
            # Forecast using appropriate method
            if use_prophet and len(df) >= 14:
                forecast = self._forecast_with_prophet(df, days_ahead)
            else:
                forecast = self._forecast_with_simple_method(df, days_ahead)
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error in sentiment forecasting: {e}")
            return self._generate_default_forecast(days_ahead)
    
    def _get_historical_sentiment(self, db: Session, days: int = 30) -> List[Dict[str, Any]]:
        """Retrieve historical sentiment data from database."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get daily aggregated sentiment scores
            results = db.query(
                func.date(PostAnalysis.analyzed_at).label('date'),
                func.avg(PostAnalysis.sentiment_score).label('avg_sentiment'),
                func.count(PostAnalysis.id).label('post_count')
            ).filter(
                PostAnalysis.analyzed_at >= cutoff_date
            ).group_by(
                func.date(PostAnalysis.analyzed_at)
            ).order_by(
                func.date(PostAnalysis.analyzed_at)
            ).all()
            
            historical = []
            for result in results:
                historical.append({
                    'date': result.date.isoformat() if hasattr(result.date, 'isoformat') else str(result.date),
                    'sentiment': float(result.avg_sentiment),
                    'post_count': int(result.post_count)
                })
            
            # If no data from analyses, try dashboard summaries
            if not historical:
                logger.info("No post analysis data found, using dashboard summaries")
                summaries = db.query(DashboardSummary).filter(
                    DashboardSummary.created_at >= cutoff_date
                ).order_by(DashboardSummary.created_at).all()
                
                for summary in summaries:
                    # Estimate sentiment from escalation risk (inverse relationship)
                    estimated_sentiment = 1.0 - (summary.escalation_risk_score / 10.0)  # Normalize
                    historical.append({
                        'date': summary.created_at.date().isoformat(),
                        'sentiment': estimated_sentiment,
                        'post_count': summary.total_posts_analyzed
                    })
            
            return historical
            
        except Exception as e:
            logger.error(f"Error retrieving historical sentiment: {e}")
            return []
    
    def _forecast_with_prophet(self, df: pd.DataFrame, days_ahead: int) -> Dict[str, Any]:
        """Use Facebook Prophet for advanced time-series forecasting."""
        try:
            from prophet import Prophet
            
            # Prepare data for Prophet
            prophet_df = pd.DataFrame({
                'ds': df.index,
                'y': df['sentiment'].values
            })
            
            # Initialize and fit model
            model = Prophet(
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=False,
                changepoint_prior_scale=0.05
            )
            model.fit(prophet_df)
            
            # Create future dates
            future = model.make_future_dataframe(periods=days_ahead)
            forecast = model.predict(future)
            
            # Extract forecast for future dates only
            future_forecast = forecast.tail(days_ahead)
            
            return {
                'forecast_dates': [d.isoformat() for d in future_forecast['ds']],
                'predicted_sentiment': future_forecast['yhat'].tolist(),
                'confidence_upper': future_forecast['yhat_upper'].tolist(),
                'confidence_lower': future_forecast['yhat_lower'].tolist(),
                'trend_direction': self._determine_trend_direction(
                    future_forecast['yhat'].iloc[0],
                    future_forecast['yhat'].iloc[-1]
                ),
                'method': 'prophet'
            }
            
        except ImportError:
            logger.warning("Prophet not available, falling back to simple method")
            return self._forecast_with_simple_method(df, days_ahead)
        except Exception as e:
            logger.error(f"Prophet forecasting error: {e}")
            return self._forecast_with_simple_method(df, days_ahead)
    
    def _forecast_with_simple_method(self, df: pd.DataFrame, days_ahead: int) -> Dict[str, Any]:
        """Simple linear regression-based forecasting."""
        try:
            from sklearn.linear_model import LinearRegression
            
            # Prepare data
            dates_numeric = np.array([(d - df.index[0]).days for d in df.index]).reshape(-1, 1)
            sentiment_values = df['sentiment'].values
            
            # Fit linear model
            model = LinearRegression()
            model.fit(dates_numeric, sentiment_values)
            
            # Generate future dates
            last_date = df.index[-1]
            future_dates = [last_date + timedelta(days=i+1) for i in range(days_ahead)]
            future_dates_numeric = np.array([(d - df.index[0]).days for d in future_dates]).reshape(-1, 1)
            
            # Predict
            predictions = model.predict(future_dates_numeric)
            
            # Calculate confidence intervals (simple: based on historical variance)
            historical_std = np.std(sentiment_values)
            confidence_upper = predictions + 1.96 * historical_std
            confidence_lower = predictions - 1.96 * historical_std
            
            return {
                'forecast_dates': [d.isoformat() for d in future_dates],
                'predicted_sentiment': predictions.tolist(),
                'confidence_upper': confidence_upper.tolist(),
                'confidence_lower': confidence_lower.tolist(),
                'trend_direction': self._determine_trend_direction(predictions[0], predictions[-1]),
                'method': 'linear_regression'
            }
            
        except Exception as e:
            logger.error(f"Simple forecasting error: {e}")
            return self._generate_default_forecast(days_ahead)
    
    def _determine_trend_direction(self, start_value: float, end_value: float) -> str:
        """Determine if sentiment is improving, declining, or stable."""
        threshold = 0.05  # 5% change threshold
        change = end_value - start_value
        
        if change > threshold:
            return "improving"
        elif change < -threshold:
            return "declining"
        else:
            return "stable"
    
    def _generate_default_forecast(self, days_ahead: int) -> Dict[str, Any]:
        """Generate a default forecast when insufficient data is available."""
        future_dates = [datetime.utcnow() + timedelta(days=i+1) for i in range(days_ahead)]
        
        return {
            'forecast_dates': [d.isoformat() for d in future_dates],
            'predicted_sentiment': [0.0] * days_ahead,  # Neutral sentiment
            'confidence_upper': [0.2] * days_ahead,
            'confidence_lower': [-0.2] * days_ahead,
            'trend_direction': 'stable',
            'method': 'default',
            'note': 'Insufficient historical data for accurate forecasting'
        }
    
    def predict_escalation_risk(
        self,
        db: Session,
        days_ahead: int = 7
    ) -> Dict[str, Any]:
        """
        Predict escalation risk based on historical patterns.
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            # Get historical escalation risk data
            summaries = db.query(DashboardSummary).filter(
                DashboardSummary.created_at >= cutoff_date
            ).order_by(DashboardSummary.created_at).all()
            
            if len(summaries) < 7:
                return {
                    'predicted_risk': 'medium',
                    'risk_score': 5.0,
                    'confidence': 'low',
                    'note': 'Insufficient historical data'
                }
            
            # Extract risk scores
            risk_scores = [s.escalation_risk_score for s in summaries]
            
            # Simple trend analysis
            recent_avg = np.mean(risk_scores[-7:])
            older_avg = np.mean(risk_scores[:-7]) if len(risk_scores) > 7 else recent_avg
            
            trend = recent_avg - older_avg
            
            # Predict future risk
            predicted_score = recent_avg + (trend * 0.5)  # Dampened trend
            predicted_score = max(0.0, min(10.0, predicted_score))  # Clamp to 0-10
            
            # Determine risk level
            if predicted_score >= 7.0:
                risk_level = 'high'
            elif predicted_score >= 4.0:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            return {
                'predicted_risk': risk_level,
                'risk_score': float(predicted_score),
                'trend': 'increasing' if trend > 0.5 else 'decreasing' if trend < -0.5 else 'stable',
                'confidence': 'medium' if len(summaries) >= 14 else 'low'
            }
            
        except Exception as e:
            logger.error(f"Error predicting escalation risk: {e}")
            return {
                'predicted_risk': 'medium',
                'risk_score': 5.0,
                'confidence': 'low',
                'error': str(e)
            }
