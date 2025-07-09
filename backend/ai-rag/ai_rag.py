"""
AI/RAG System for Quality Infrastructure Analysis
This system provides intelligent analysis of digital twin data for quality infrastructure decision-making.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import json
import logging
from datetime import datetime, timedelta
import os

# Database and external service imports
import asyncpg
import redis.asyncio as redis
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# AI/ML imports
import openai
import anthropic
from sentence_transformers import SentenceTransformer
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="QI Digital AI/RAG System",
    description="AI-powered analysis system for Quality Infrastructure digital twins",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://aasx_user:aasx_password@localhost:5432/aasx_data")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Initialize AI clients
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

if ANTHROPIC_API_KEY:
    anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Initialize embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Pydantic models
class AnalysisRequest(BaseModel):
    twin_id: str
    analysis_type: str = Field(..., description="Type of analysis: quality_assessment, risk_analysis, optimization, prediction")
    query: str
    context: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None

class AnalysisResponse(BaseModel):
    analysis_id: str
    twin_id: str
    analysis_type: str
    query: str
    result: Dict[str, Any]
    confidence_score: float
    sources: List[Dict[str, Any]]
    recommendations: List[str]
    timestamp: datetime

class QualityAssessmentRequest(BaseModel):
    twin_id: str
    standards: List[str]
    metrics: List[str]
    timeframe: Optional[str] = "30d"

class RiskAnalysisRequest(BaseModel):
    twin_id: str
    risk_factors: List[str]
    assessment_period: Optional[str] = "90d"

class OptimizationRequest(BaseModel):
    twin_id: str
    optimization_target: str
    constraints: Optional[Dict[str, Any]] = None

# Database connection pool
async def get_db_pool():
    return await asyncpg.create_pool(DATABASE_URL)

# Redis connection
async def get_redis():
    return redis.from_url(REDIS_URL)

# Qdrant client
qdrant_client = QdrantClient(QDRANT_URL)

@app.on_event("startup")
async def startup_event():
    """Initialize connections and create vector collections on startup"""
    try:
        # Create vector collections if they don't exist
        collections = ["twin_data", "standards", "certificates", "research"]
        for collection in collections:
            try:
                qdrant_client.get_collection(collection)
            except:
                qdrant_client.create_collection(
                    collection_name=collection,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
        logger.info("AI/RAG system initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing AI/RAG system: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if we can connect to external services
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "services": {
                "database": "unknown",
                "redis": "unknown", 
                "qdrant": "unknown"
            }
        }
        
        # Try database connection
        try:
            pool = await get_db_pool()
            await pool.close()
            health_status["services"]["database"] = "connected"
        except Exception as e:
            health_status["services"]["database"] = "disconnected"
            logger.warning(f"Database connection failed: {e}")
        
        # Try Redis connection
        try:
            redis_client = await get_redis()
            await redis_client.ping()
            await redis_client.close()
            health_status["services"]["redis"] = "connected"
        except Exception as e:
            health_status["services"]["redis"] = "disconnected"
            logger.warning(f"Redis connection failed: {e}")
        
        # Try Qdrant connection
        try:
            qdrant_client.get_collections()
            health_status["services"]["qdrant"] = "connected"
        except Exception as e:
            health_status["services"]["qdrant"] = "disconnected"
            logger.warning(f"Qdrant connection failed: {e}")
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"status": "unhealthy", "error": str(e), "timestamp": datetime.utcnow()}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_twin(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db_pool=Depends(get_db_pool),
    redis_client=Depends(get_redis)
):
    """Perform AI analysis on digital twin data"""
    try:
        # Generate analysis ID
        analysis_id = f"analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{request.twin_id}"
        
        # Get twin data
        async with db_pool.acquire() as conn:
            twin_data = await conn.fetchrow(
                "SELECT * FROM digital_twins.twin_registry WHERE twin_id = $1",
                request.twin_id
            )
            
            if not twin_data:
                raise HTTPException(status_code=404, detail="Digital twin not found")
        
        # Perform analysis based on type
        if request.analysis_type == "quality_assessment":
            result = await perform_quality_assessment(request, twin_data, db_pool)
        elif request.analysis_type == "risk_analysis":
            result = await perform_risk_analysis(request, twin_data, db_pool)
        elif request.analysis_type == "optimization":
            result = await perform_optimization(request, twin_data, db_pool)
        elif request.analysis_type == "prediction":
            result = await perform_prediction(request, twin_data, db_pool)
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")
        
        # Store analysis result
        background_tasks.add_task(store_analysis_result, analysis_id, request, result, db_pool)
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            twin_id=request.twin_id,
            analysis_type=request.analysis_type,
            query=request.query,
            result=result,
            confidence_score=result.get("confidence_score", 0.8),
            sources=result.get("sources", []),
            recommendations=result.get("recommendations", []),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def perform_quality_assessment(request: AnalysisRequest, twin_data, db_pool):
    """Perform quality assessment analysis"""
    try:
        # Get quality metrics for the twin
        async with db_pool.acquire() as conn:
            metrics = await conn.fetch(
                """
                SELECT * FROM qi_analysis.quality_metrics 
                WHERE twin_id = $1 
                ORDER BY measurement_timestamp DESC 
                LIMIT 100
                """,
                twin_data['id']
            )
            
            # Get compliance assessments
            compliance = await conn.fetch(
                """
                SELECT ca.*, qs.standard_name 
                FROM qi_analysis.compliance_assessments ca
                JOIN qi_analysis.quality_standards qs ON ca.standard_id = qs.id
                WHERE ca.twin_id = $1
                ORDER BY ca.assessment_date DESC
                """,
                twin_data['id']
            )
        
        # Analyze metrics
        metric_analysis = analyze_quality_metrics(metrics)
        
        # Analyze compliance
        compliance_analysis = analyze_compliance(compliance)
        
        # Generate AI insights
        ai_insights = await generate_quality_insights(
            twin_data, metric_analysis, compliance_analysis, request.query
        )
        
        return {
            "metric_analysis": metric_analysis,
            "compliance_analysis": compliance_analysis,
            "ai_insights": ai_insights,
            "confidence_score": 0.85,
            "sources": [{"type": "metrics", "count": len(metrics)}, {"type": "compliance", "count": len(compliance)}],
            "recommendations": generate_quality_recommendations(metric_analysis, compliance_analysis)
        }
        
    except Exception as e:
        logger.error(f"Quality assessment error: {e}")
        raise

async def perform_risk_analysis(request: AnalysisRequest, twin_data, db_pool):
    """Perform risk analysis"""
    try:
        # Get historical data and identify risk patterns
        async with db_pool.acquire() as conn:
            # Get quality metrics for risk assessment
            metrics = await conn.fetch(
                """
                SELECT * FROM qi_analysis.quality_metrics 
                WHERE twin_id = $1 AND metric_type = 'safety'
                ORDER BY measurement_timestamp DESC 
                LIMIT 200
                """,
                twin_data['id']
            )
            
            # Get AI analysis history
            ai_history = await conn.fetch(
                """
                SELECT * FROM qi_analysis.ai_analysis_results 
                WHERE twin_id = $1 AND analysis_type = 'risk_analysis'
                ORDER BY analysis_timestamp DESC 
                LIMIT 50
                """,
                twin_data['id']
            )
        
        # Perform risk assessment
        risk_factors = identify_risk_factors(metrics, request.risk_factors)
        risk_score = calculate_risk_score(risk_factors)
        risk_trends = analyze_risk_trends(ai_history)
        
        # Generate AI risk insights
        ai_insights = await generate_risk_insights(twin_data, risk_factors, request.query)
        
        return {
            "risk_factors": risk_factors,
            "risk_score": risk_score,
            "risk_trends": risk_trends,
            "ai_insights": ai_insights,
            "confidence_score": 0.82,
            "sources": [{"type": "safety_metrics", "count": len(metrics)}],
            "recommendations": generate_risk_recommendations(risk_factors, risk_score)
        }
        
    except Exception as e:
        logger.error(f"Risk analysis error: {e}")
        raise

async def perform_optimization(request: OptimizationRequest, twin_data, db_pool):
    """Perform optimization analysis"""
    try:
        # Get performance data
        async with db_pool.acquire() as conn:
            performance_metrics = await conn.fetch(
                """
                SELECT * FROM qi_analysis.quality_metrics 
                WHERE twin_id = $1 AND metric_type = 'performance'
                ORDER BY measurement_timestamp DESC 
                LIMIT 300
                """,
                twin_data['id']
            )
        
        # Perform optimization analysis
        optimization_opportunities = identify_optimization_opportunities(performance_metrics, request.optimization_target)
        optimization_recommendations = generate_optimization_recommendations(optimization_opportunities, request.constraints)
        
        # Generate AI optimization insights
        ai_insights = await generate_optimization_insights(twin_data, optimization_opportunities, request.query)
        
        return {
            "optimization_opportunities": optimization_opportunities,
            "recommendations": optimization_recommendations,
            "ai_insights": ai_insights,
            "confidence_score": 0.78,
            "sources": [{"type": "performance_metrics", "count": len(performance_metrics)}],
            "recommendations": optimization_recommendations
        }
        
    except Exception as e:
        logger.error(f"Optimization error: {e}")
        raise

async def perform_prediction(request: AnalysisRequest, twin_data, db_pool):
    """Perform prediction analysis"""
    try:
        # Get historical data for prediction
        async with db_pool.acquire() as conn:
            historical_data = await conn.fetch(
                """
                SELECT * FROM qi_analysis.quality_metrics 
                WHERE twin_id = $1 
                ORDER BY measurement_timestamp DESC 
                LIMIT 500
                """,
                twin_data['id']
            )
        
        # Perform time series analysis and predictions
        predictions = generate_predictions(historical_data, request.parameters)
        prediction_confidence = calculate_prediction_confidence(historical_data)
        
        # Generate AI prediction insights
        ai_insights = await generate_prediction_insights(twin_data, predictions, request.query)
        
        return {
            "predictions": predictions,
            "prediction_confidence": prediction_confidence,
            "ai_insights": ai_insights,
            "confidence_score": prediction_confidence,
            "sources": [{"type": "historical_data", "count": len(historical_data)}],
            "recommendations": generate_prediction_recommendations(predictions)
        }
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise

# Helper functions for analysis
def analyze_quality_metrics(metrics):
    """Analyze quality metrics data"""
    if not metrics:
        return {"status": "no_data", "message": "No quality metrics available"}
    
    # Calculate statistics
    metric_values = [m['metric_value'] for m in metrics if m['metric_value'] is not None]
    
    if not metric_values:
        return {"status": "no_valid_data", "message": "No valid metric values"}
    
    return {
        "total_metrics": len(metrics),
        "average_value": np.mean(metric_values),
        "std_deviation": np.std(metric_values),
        "min_value": np.min(metric_values),
        "max_value": np.max(metric_values),
        "trend": calculate_trend(metric_values),
        "anomalies": detect_anomalies(metric_values)
    }

def analyze_compliance(compliance_data):
    """Analyze compliance assessment data"""
    if not compliance_data:
        return {"status": "no_data", "message": "No compliance data available"}
    
    compliance_scores = [c['compliance_score'] for c in compliance_data if c['compliance_score'] is not None]
    
    return {
        "total_assessments": len(compliance_data),
        "average_compliance_score": np.mean(compliance_scores) if compliance_scores else 0,
        "compliance_status": {
            "compliant": len([c for c in compliance_data if c['compliance_status'] == 'compliant']),
            "non_compliant": len([c for c in compliance_data if c['compliance_status'] == 'non_compliant']),
            "partially_compliant": len([c for c in compliance_data if c['compliance_status'] == 'partially_compliant'])
        },
        "standards_coverage": list(set([c['standard_name'] for c in compliance_data]))
    }

def identify_risk_factors(metrics, risk_factors):
    """Identify risk factors from metrics data"""
    risks = []
    
    for factor in risk_factors:
        factor_metrics = [m for m in metrics if factor.lower() in m['metric_name'].lower()]
        
        if factor_metrics:
            values = [m['metric_value'] for m in factor_metrics if m['metric_value'] is not None]
            if values:
                risk_level = "high" if np.mean(values) > 0.8 else "medium" if np.mean(values) > 0.5 else "low"
                risks.append({
                    "factor": factor,
                    "risk_level": risk_level,
                    "average_value": np.mean(values),
                    "metric_count": len(factor_metrics)
                })
    
    return risks

def calculate_risk_score(risk_factors):
    """Calculate overall risk score"""
    if not risk_factors:
        return 0.0
    
    risk_weights = {"high": 0.8, "medium": 0.5, "low": 0.2}
    weighted_risks = [risk_weights.get(r['risk_level'], 0.3) for r in risk_factors]
    
    return np.mean(weighted_risks)

# AI/LLM integration functions
async def generate_quality_insights(twin_data, metric_analysis, compliance_analysis, query):
    """Generate AI insights for quality assessment"""
    if not OPENAI_API_KEY:
        return {"message": "OpenAI API key not configured"}
    
    try:
        prompt = f"""
        Analyze the following quality infrastructure data for digital twin {twin_data['twin_name']}:
        
        Metric Analysis: {json.dumps(metric_analysis, default=str)}
        Compliance Analysis: {json.dumps(compliance_analysis, default=str)}
        
        User Query: {query}
        
        Provide insights on:
        1. Quality trends and patterns
        2. Compliance gaps and opportunities
        3. Recommendations for improvement
        4. Risk areas to monitor
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )
        
        return {"insights": response.choices[0].message.content}
        
    except Exception as e:
        logger.error(f"Error generating AI insights: {e}")
        return {"error": "Failed to generate AI insights"}

async def generate_risk_insights(twin_data, risk_factors, query):
    """Generate AI insights for risk analysis"""
    if not OPENAI_API_KEY:
        return {"message": "OpenAI API key not configured"}
    
    try:
        prompt = f"""
        Analyze the following risk factors for digital twin {twin_data['twin_name']}:
        
        Risk Factors: {json.dumps(risk_factors, default=str)}
        User Query: {query}
        
        Provide insights on:
        1. Risk assessment and prioritization
        2. Mitigation strategies
        3. Monitoring recommendations
        4. Early warning indicators
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )
        
        return {"insights": response.choices[0].message.content}
        
    except Exception as e:
        logger.error(f"Error generating risk insights: {e}")
        return {"error": "Failed to generate risk insights"}

# Utility functions
def calculate_trend(values):
    """Calculate trend in time series data"""
    if len(values) < 2:
        return "insufficient_data"
    
    slope = np.polyfit(range(len(values)), values, 1)[0]
    
    if slope > 0.01:
        return "increasing"
    elif slope < -0.01:
        return "decreasing"
    else:
        return "stable"

def detect_anomalies(values, threshold=2):
    """Detect anomalies using z-score method"""
    if len(values) < 3:
        return []
    
    mean = np.mean(values)
    std = np.std(values)
    
    if std == 0:
        return []
    
    z_scores = [(v - mean) / std for v in values]
    anomalies = [i for i, z in enumerate(z_scores) if abs(z) > threshold]
    
    return anomalies

def generate_quality_recommendations(metric_analysis, compliance_analysis):
    """Generate quality improvement recommendations"""
    recommendations = []
    
    if metric_analysis.get("trend") == "decreasing":
        recommendations.append("Investigate declining quality metrics trend")
    
    if compliance_analysis.get("compliance_status", {}).get("non_compliant", 0) > 0:
        recommendations.append("Address non-compliance issues immediately")
    
    if metric_analysis.get("anomalies"):
        recommendations.append("Investigate detected anomalies in quality metrics")
    
    return recommendations

def generate_risk_recommendations(risk_factors, risk_score):
    """Generate risk mitigation recommendations"""
    recommendations = []
    
    if risk_score > 0.7:
        recommendations.append("Implement immediate risk mitigation measures")
    
    high_risks = [r for r in risk_factors if r['risk_level'] == 'high']
    if high_risks:
        recommendations.append(f"Focus on {len(high_risks)} high-risk factors")
    
    return recommendations

async def store_analysis_result(analysis_id: str, request: AnalysisRequest, result: dict, db_pool):
    """Store analysis result in database"""
    try:
        async with db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO qi_analysis.ai_analysis_results 
                (twin_id, analysis_type, analysis_model, analysis_input, analysis_output, confidence_score, created_by)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                request.twin_id,
                request.analysis_type,
                "ai_rag_system",
                json.dumps({"query": request.query, "context": request.context}),
                json.dumps(result),
                result.get("confidence_score", 0.8),
                "ai_system"
            )
    except Exception as e:
        logger.error(f"Error storing analysis result: {e}")

# Additional endpoints for specific analysis types
@app.post("/quality-assessment")
async def quality_assessment(request: QualityAssessmentRequest, db_pool=Depends(get_db_pool)):
    """Perform comprehensive quality assessment"""
    analysis_request = AnalysisRequest(
        twin_id=request.twin_id,
        analysis_type="quality_assessment",
        query=f"Quality assessment for standards: {', '.join(request.standards)} and metrics: {', '.join(request.metrics)}"
    )
    
    return await analyze_twin(analysis_request, BackgroundTasks(), db_pool, Depends(get_redis))

@app.post("/risk-analysis")
async def risk_analysis(request: RiskAnalysisRequest, db_pool=Depends(get_db_pool)):
    """Perform comprehensive risk analysis"""
    analysis_request = AnalysisRequest(
        twin_id=request.twin_id,
        analysis_type="risk_analysis",
        query=f"Risk analysis for factors: {', '.join(request.risk_factors)}"
    )
    
    return await analyze_twin(analysis_request, BackgroundTasks(), db_pool, Depends(get_redis))

@app.get("/analysis-history/{twin_id}")
async def get_analysis_history(twin_id: str, db_pool=Depends(get_db_pool)):
    """Get analysis history for a digital twin"""
    try:
        async with db_pool.acquire() as conn:
            results = await conn.fetch(
                """
                SELECT * FROM qi_analysis.ai_analysis_results 
                WHERE twin_id = $1 
                ORDER BY analysis_timestamp DESC 
                LIMIT 50
                """,
                twin_id
            )
        
        return [dict(r) for r in results]
        
    except Exception as e:
        logger.error(f"Error fetching analysis history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 