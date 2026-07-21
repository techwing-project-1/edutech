from fastapi import APIRouter, HTTPException
from typing import Dict
from app.domain.schemas.configuration import ConfigurationResponse, FeatureUpdateRequest, FeatureFlag, FeatureResponse
from app.configuration.manager import ConfigurationManager

router = APIRouter()

@router.get("", response_model=ConfigurationResponse, summary="Get Full System Configuration")
def get_configuration():
    return ConfigurationResponse(
        configuration=ConfigurationManager.get_system_configuration(),
        features=ConfigurationManager.get_features()
    )

@router.get("/features", response_model=Dict[FeatureFlag, bool], summary="Get All Feature Flags")
def get_features():
    return ConfigurationManager.get_features()

@router.put("/features/{feature}", response_model=FeatureResponse, summary="Update Feature Flag")
def update_feature(feature: FeatureFlag, request: FeatureUpdateRequest):
    ConfigurationManager.update_feature(feature, request.enabled)
    return FeatureResponse(feature=feature, enabled=request.enabled)
