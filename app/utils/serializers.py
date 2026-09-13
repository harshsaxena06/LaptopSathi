"""Shared helper(s) used across routers to serialize ORM objects to API schemas."""
from app.models.db_models import Laptop
from app.schemas.schemas import LaptopOut


def laptop_to_out(lp: Laptop) -> LaptopOut:
    return LaptopOut(
        id=lp.id,
        model_name=lp.model_name,
        brand=lp.brand.name if lp.brand else "Unknown",
        cpu_name=lp.cpu_bench.cpu_name if lp.cpu_bench else None,
        gpu_name=lp.gpu_bench.gpu_name if lp.gpu_bench else None,
        ram_gb=lp.ram_gb,
        storage_gb=lp.storage_gb,
        storage_type=lp.storage_type,
        display_size_inch=lp.display_size_inch,
        display_resolution=lp.display_resolution,
        refresh_rate_hz=lp.refresh_rate_hz,
        battery_life_hours=lp.battery_life_hours,
        weight_kg=lp.weight_kg,
        price_inr=lp.price_inr,
        release_year=lp.release_year,
        scores={
            "programming_score": lp.programming_score,
            "ai_ml_score": lp.ai_ml_score,
            "gaming_score": lp.gaming_score,
            "video_editing_score": lp.video_editing_score,
            "battery_score": lp.battery_score,
            "portability_score": lp.portability_score,
            "business_score": lp.business_score,
            "student_score": lp.student_score,
            "future_proof_score": lp.future_proof_score,
        },
    )
