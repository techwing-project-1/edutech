from fastapi import APIRouter, HTTPException
from app.modules.hod_analytics.request_models import HODAnalyticsRequest
from app.modules.hod_analytics.response_models import HODAnalysisResponse
from app.modules.hod_analytics.analytics_service import HODAnalyticsService
from app.modules.hod_analytics.exceptions import HODValidationException, HODLLMException

router = APIRouter()
service = HODAnalyticsService()

@router.post(
    "/analyze", 
    response_model=HODAnalysisResponse,
    summary="Generate Department Summary & Insights",
    description="Analyzes the structured HOD department data and returns AI-generated insights."
)
async def analyze_department(request: HODAnalyticsRequest):
    try:
        return await service.analyze(request)
    except HODValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HODLLMException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post(
    "/report", 
    response_model=HODAnalysisResponse,
    summary="Generate Formal Department Report",
    description="Generates a structured, formal Department Performance Report suitable for executive review."
)
async def generate_report(request: HODAnalyticsRequest):
    try:
        return await service.generate_report(request)
    except HODValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HODLLMException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post(
    "/recommendations", 
    response_model=HODAnalysisResponse,
    summary="Generate Actionable Recommendations",
    description="Generates highly actionable Recommendations and Priority Actions for the HOD."
)
async def generate_recommendations(request: HODAnalyticsRequest):
    try:
        return await service.generate_recommendations(request)
    except HODValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HODLLMException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
