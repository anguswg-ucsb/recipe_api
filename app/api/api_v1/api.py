from fastapi import APIRouter

from .endpoints import dishes_by_ingredients, dishes_by_id, directions_by_id

router = APIRouter()

# dishes by ingredients route
router.include_router(dishes_by_ingredients.router, prefix="/dishes-by-ingredients", tags=["DishesByIngredients"])

# dishes by id route
router.include_router(dishes_by_id.router, prefix="/dishes-by-id", tags=["DishesByID"])

# directions route
router.include_router(directions_by_id.router, prefix="/directions-by-id", tags=["DirectionsByID"])