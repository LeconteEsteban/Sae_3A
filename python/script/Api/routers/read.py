from fastapi import APIRouter, HTTPException
from typing import List
from services.servicebdd import bddservice


router = APIRouter()


@router.get("")