from fastapi import APIRouter

from .endpoints import get_directions_by_dish_id, get_dishes_by_dish_id, get_dishes_by_ingredients, get_ingredients_by_dishes, get_suggested_ingredients

router = APIRouter()

# Get directions by ID route
router.include_router(get_directions_by_dish_id.router, prefix="/directions-by-dish_id", tags=["DirectionsByDishID"])

# Get dishes by ID route
router.include_router(get_dishes_by_dish_id.router, prefix="/dishes-by-dish_id", tags=["DishesByDishID"])

# Get dishes by ingredients route
router.include_router(get_dishes_by_ingredients.router, prefix="/dishes-by-ingredients", tags=["DishesByIngredients"])

# Get ingredients by dishes route
router.include_router(get_ingredients_by_dishes.router, prefix="/ingredients-by-dishes", tags=["IngredientsByDishes"])

# Get suggested ingredients route
router.include_router(get_suggested_ingredients.router, prefix="/suggested-ingredients", tags=["SuggestedIngredients"])