import json
import os
import boto3
import uuid
import time 
import re
import ast
from datetime import datetime

# Set TRANSFORMERS_CACHE to /tmp
os.environ["TRANSFORMERS_CACHE"] = "/tmp"

import pandas as pd
import numpy as np 

import s3fs

from food_map import FoodMap
from lambda_containers.extract_ingredients.food_map import FoodMap
# import food_map

# import model interface from Hugging Face model 
from transformers import T5Tokenizer, T5ForConditionalGeneration
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# from transformers import T5Tokenizer, T5ForConditionalGeneration
# # from transformers import DistilBertForTokenClassification

# # HuggingFace path to model
# HF_MODEL_PATH = "google/flan-t5-large"
# # HF_MODEL_PATH = "chambliss/distilbert-for-food-extraction"

# # Load the T5 model and tokenizer from HuggingFace
# tokenizer = T5Tokenizer.from_pretrained(HF_MODEL_PATH)
# model = T5ForConditionalGeneration.from_pretrained(HF_MODEL_PATH)

# # # Download the model from HuggingFace
# # model = DistilBertForTokenClassification.from_pretrained(HF_MODEL_PATH)

# # Specify the directory where you want to save the model
# save_directory = './model/flan-t5-large'
# # save_directory = './model/chambliss-distilbert-for-food-extraction'

# # Save the model and its configuration to the specified directory
# model.save_pretrained(save_directory)
# tokenizer.save_pretrained(save_directory)

# instantiate the FoodMap class (contains the food dictionary with food to category mappings)
food_map = FoodMap()

# food_map.food_catalog
# food_map.categories

# Paths to the T5 model and tokenizer
model_path = './model/flan-t5-large'

# Load the T5 model and tokenizer from HuggingFace
tokenizer = T5Tokenizer.from_pretrained(model_path)
model = T5ForConditionalGeneration.from_pretrained(model_path)

# tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-large")
# model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-large")
# tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
# model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")

# from food_extractor.food_model import FoodModel

# Credit: https://github.com/chambliss/foodbert.git
# Thank you for the model and heurtistics for extracting food ingredients from a list of ingredients! 

# # GitHub Repository: https://github.com/chambliss/foodbert/tree/master

# environment variables
OUTPUT_S3_BUCKET = os.environ.get('OUTPUT_S3_BUCKET')

# # path to saved distilbert FoodModel from Hugging Face
# model_path = './model/chambliss-distilbert-for-food-extraction'

# model_path = './extract_ingredients_lambda/model/chambliss-distilbert-for-food-extraction'

# Load the model from HuggingFace
# model = FoodModel(model_path)
# model = FoodModel("chambliss/distilbert-for-food-extraction")

print(f"Succesfully loaded model from: {model_path}")
print(f"type(model): {type(model)}")

# S3 client
s3 = boto3.client('s3')

# Credit: to recipe_scrapers GitHub repository for the following code
def score_sentence_similarity(first: str, second: str) -> float:
    """Calculate Dice coefficient for two strings.

    The dice coefficient is a measure of similarity determined by calculating
    the proportion of shared bigrams.

    Parameters
    ----------
    first : str
        First string
    second : str
        Second string

    Returns
    -------
    float
        Similarity score between 0 and 1.
        0 means the two strings do not share any bigrams.
        1 means the two strings are identical.
    """

    if first == second:
        # Indentical sentences have maximum score of 1
        return 1

    if len(first) < 2 or len(second) < 2:
        # If either sentence has 0 or 1 character we can't generate bigrams,
        # so the score is 0
        return 0

    first_bigrams = {first[i : i + 2] for i in range(len(first) - 1)}
    second_bigrams = {second[i : i + 2] for i in range(len(second) - 1)}

    intersection = first_bigrams & second_bigrams

    return 2.0 * len(intersection) / (len(first_bigrams) + len(second_bigrams))

# score_sentence_similarity("1/2 cup of sugar", "1 cup of cinnamon")
# score_sentence_similarity("gallons", "gallon")

# get_foods_from_ingredients()
def get_foods_from_ingredients(ingredient_list, model, tokenizer):

    """
    Use the flan T5 model to extract the specific food from each ingredient in the ingredient list and return a list of the extracted foods
    """

    # ingredient_list = ["4 pork chops","1 pinch garlic salt","1 tablespoon vegetable oil", "1 onion, chopped", "2 stalks chopped celery, with leaves",
    #         "12 ounces tomato paste", "1 (15 ounce) can tomato sauce", "3 cups water",
    #         "Butter or margarine (about 1/2 cup)", "2 salmon fillets", "1 chicken breast","3 eggs"
    #]
    # tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-large")
    # model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-large")

    # input_text = f"""Given the following list of ingredients {str(food_list)} can you extract the specific food from each ingredient?"""
    # input_text = f"""Extract {str(food_list)} the specific food from each ingredient?"""
    # input_ids = tokenizer(input_text, return_tensors="pt").input_ids
    # inputs= tokenizer(input_text, return_tensors="pt", padding=True)

    # String to prepend to each food item
    task_prefix = "Extract the specific food from this ingredient: "

    # tokanize the input strings
    inputs = tokenizer([task_prefix + ingredient for ingredient in ingredient_list], return_tensors="pt", padding=True)

    # Generate outputs
    output_sequences = model.generate(
        input_ids=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        # max_length=1500,
        max_length=50,
        do_sample=False,  # disable sampling to test if batching affects output
    )

    foods = tokenizer.batch_decode(output_sequences, skip_special_tokens=True)
    
    # return json.dumps(foods)
    return foods

# get_foods_from_ingredients()
def get_units_and_quantities(ingredient_list, model, tokenizer):

    """
    Use the flan T5 model to extract the specific food from each ingredient in the ingredient list and return a list of the extracted foods
    """
    # df.columns
    # df.instructions

    # ingredient_list = ["4 pork chops","1 pinch garlic salt","1 tablespoon vegetable oil", "1 onion, chopped", "2 stalks chopped celery, with leaves",
    #         "12 ounces tomato paste", "1 (15 ounce) can tomato sauce", "3 cups water",
    #         "Butter or margarine (about 1/2 cup)", "2 salmon fillets", "1 chicken breast","3 eggs"
    #]
    # tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-large")
    # model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-large")

    # input_text = f"""Given the following list of ingredients {str(food_list)} can you extract the specific food from each ingredient?"""
    # input_text = f"""Extract {str(food_list)} the specific food from each ingredient?"""
    # input_ids = tokenizer(input_text, return_tensors="pt").input_ids
    # inputs= tokenizer(input_text, return_tensors="pt", padding=True)
    ingredient_list = ast.literal_eval(df["ingredients"].values.tolist()[0])
    food_list = df["ingredient_tags"].values.tolist()[0] 

    extracted_list = []
    # iterate through the ingredient list and remove the food items from the ingredient strings of the same index and add them to the extracted list
    for i, food in enumerate(food_list):
        print(f"i: {i}")
        print(f"food: {food}")
        print(f"ingredient_list[i]: {ingredient_list[i]}")

        extracted = ingredient_list[i].replace(food, "").strip()
        print(f"extracted: {extracted}")

        extracted_list.append(extracted)
        print(f"\n")


    df["ingredient_tags"].values.tolist()[0]

    # String to prepend to each food item
    task_prefix = "Extract the specific food from this ingredient: "

    # tokanize the input strings
    inputs = tokenizer([task_prefix + ingredient for ingredient in ingredient_list], return_tensors="pt", padding=True)

    # Generate outputs
    output_sequences = model.generate(
        input_ids=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        # max_length=1500,
        max_length=50,
        do_sample=False,  # disable sampling to test if batching affects output
    )

    foods = tokenizer.batch_decode(output_sequences, skip_special_tokens=True)
    
    # return json.dumps(foods)
    return foods

def get_categories_from_foods(food_list = None,
                              food_dictionary = None, 
                              primary_options = None,
                              secondary_options = None, 
                              model = None, 
                              tokenizer = None):

    """
    Use the flan T5 model to classify the food items into categories and return a list of the inferred food group categories
    Args:
    food_list: list of food items to classify
    food_dictionary: dictionary of food categories (import from food_map.py, FoodMap class)
    primary_options: list of primary food group categories to classify the food items into
    secondary_options: dictionary of secondary food group categories to further classify the food items into (keys are list elements from primary_options, values are lists of secondary categories for each primary category)
    model: HuggingFace T5 model
    tokenizer: HuggingFace T5 tokenizer

    Returns:
    output_categories: list of the inferred food group categories for each food item in the food_list
    """

    # ##################################################################
    # ##################################################################
    # # tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-large")
    # # model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")
    
    # food_list = df["ingredient_tags"].values.tolist()[6]
    # food_list

    # food_dictionary = food_map
    # primary_options = list(food_dictionary.categories.keys())
    # secondary_options = food_dictionary.categories

    # # [food.lower() if food.lower() in food_map.food_map else "NA" for food in food_list]
    # # categories = [food_map.food_catalog[food.lower()] if food.lower() in food_map.food_catalog else None for food in food_list]
    # # food_list = food_list[0:3]
    # ##################################################################
    # ##################################################################

    # simple_foods = df["ingredient_tags"].values.tolist()[3]
    # food_list = ast.literal_eval(df["ingredients"].values.tolist()[2])

    # first check if any of the food items are in the food dictionary
    categories = []
    model_categories = []
    # modelMap = {}
    foods_to_model = []

    for i, food in enumerate(food_list):
        # print(f"Food: {food}")
        # print(f"i: {i}")
        if food.lower() in food_dictionary.food_catalog:
            categories.append(food_dictionary.food_catalog[food.lower()])
        else:
            categories.append(None)
            model_categories.append({"index": i, "food": food, "primary_category": None, "secondary_category": None})
            foods_to_model.append(food)

    # print(f"categories: {categories}")

    if foods_to_model:

        print(f"Modeling the following {len(foods_to_model)} food items:\n > {foods_to_model}")

        # categories = model_food_to_categories(foods_to_model, food_map, model, tokenizer)

        # # Get the primary and secondary categories for the food items as a nested list (NOT in place method)
        # model_outputs = model_food_to_categories(foods_to_model, food_map, primary_options, secondary_options, model, tokenizer)

        # insert the primary and secondary categories into the model_categories dictionary (IN PLACE method)
        model_food_to_categories_inplace(model_categories, food_map, primary_options, secondary_options, model, tokenizer)

        # insert the primary and secondary categories into the categories dictionary
        for i, category_map in enumerate(model_categories):
            # print(f"i: {i}")
            # print(f"category_map: {category_map}")

            # Take values from the model_outputs list and insert them into the categories list (NOT in place method)
            # categories[category_map["index"]] = model_outputs[i]
            
            # Take values from the model_categories list and insert them into the categories list (IN PLACE method)
            categories[category_map["index"]] = [category_map["primary_category"], category_map["secondary_category"]]

            # categories[catMap["index"]] = [catMap["primary_category"], catMap["secondary_category"]]
            # print(f"\n")

    # return the inferred food group category
    output_categories = [f"{cats[0]}/{cats[1]}" for cats in categories]

    return output_categories

    # # [common_foods_dict[food.lower()] if food.lower() in common_foods_dict else "NA" for food in food_list]

    # # len(food_list)

    # #     prompts = [f"""Question: Provide the food group category for "{query.lower()}". Context * {" * ".join(options)}""" for query in food_list]
    # #     return prompts

    # # # First set of categories to classify the food items into (version 2)
    # # primary_options = ["vegetable", "fruit", "grain", "dairy", "meat", "seafood", "nut", "legume", "spice", "oil", "sweetener", "beverage", "condiment/sauce", "other"]

    # # # Secondary categories to further classify the food items into  (version 2)
    # # secondary_options = {
    # #     "vegetable": ["leafy", "root", "cruciferous", "stem", "flower", "tuber", "bulb"],
    # #     "fruit": ["berry", "citrus", "tropical", "stone", "pome", "melon", "drupe"],
    # #     "grain": ["cereal", "pasta", "bread", "rice", "other grains"],
    # #     "dairy": ["milk", "cheese", "butter", "cream", "yogurt"],
    # #     "meat": ["poultry", "beef", "fish", "pork", "other meats"],
    # #     "seafood": ["fish", "shellfish", "other seafood"],
    # #     # "nut": ["almond", "cashew", "peanut", "walnut", "pecan", "pistachio", "macadamia", "hazelnut", "chestnut", "pine nut"],
    # #     "nut": ["nut", "seed", "nut butter"],
    # #     "legume": ["bean", "lentil", "pea", "chickpea", "soybean"],
    # #     "spice": ["salt", "pepper", "herb", "bark", "root", "other"],
    # #     # "spice": ["salt", "herb", "seed", "bark", "root", "other"],
    # #     "oil": ["vegetable-based", "seed-based", "nut-based", "animal-based"],
    # #     "sweetener": ["sugar", "honey", "nectar", "syrup", "sugar alcohol", "sugar substitute"],
    # #     "beverage": ["juice", "milk", "water", "soda", "tea", "coffee", "milk substitute", "alcohol", "soup"],
    # #     "condiment/sauce": ["ketchup", "mustard", "mayonnaise", "soy sauce", "vinegar", "hot sauce", "BBQ sauce", "salad dressing"]
    # # }
    # # primary and secondary categories to prompt the model to classify the food items into
    # primary_options = list(food_map.categories.keys())
    # secondary_options = food_map.categories

    # # # Secondary categories to further classify the food items into  (version 1)
    # # secondary_options = {
    # #     "vegetable" : ["leafy", "root", "cruciferous", "fungi", "stem", "flower", "tuber", "bulb"],
    # #     "fruit" : ["berry", "citrus", "tropical", "stone", "pome", "melon", "drupe"],
    # #     "grain" : ["cereal", "pasta", "bread", "rice", "oat", "barley", "wheat", "corn", "rye"],
    # #     "dairy" : ["milk",  "cheese", "butter", "cream", "yogurt"],
    # #     "meat" : ["poultry", "beef", "fish", "pork", "seafood", "egg"],
    # #     "nut" : ["almond", "cashew", "peanut", "walnut", "pecan", "pistachio", "macadamia", "hazelnut", "chestnut", "pine nut"],
    # #     "legume" : ["bean", "lentil", "pea", "chickpea", "soybean"],
    # #     "spice" : ["salt", "herb", "seed", "bark", "root", "flower"],
    # #     "oil" : ["vegatable based", "seed based", "nut based", "animal based"],
    # #     "sweetener" : ["sugar", "honey", "nectare", "syrup", "sugar alcohol", "sugar substitute"],
    # #     "beverage" : ["juice", "milk", "water", "soda", "tea", "coffee", "milk substitute", "alcohol", "soup"]
    # # }
    # # ---- Primary categories ---- 
    # primary_prompts = [f"""Question: Provide the food group category for "{food_list[i["index"]].lower()}". Context * {" * ".join(primary_options)}""" for i in model_categories]
    # # primary_prompts = [f"""Question: Provide the food group category for "{query.lower()}". Context * {" * ".join(primary_options)}""" for query in food_list]
    # # primary_prompts = category_prompts(food_list, primary_options)
    # # primary_prompts = [f"""Question: Provide the food group category for "{food_list[i].lower()}". Context * {" * ".join(primary_options)}""" for i in model_categories]
    # # [food_list[i] for i in model_categories]
    # # primary_prompts = [f"""Question: Provide the food group category for "{food[0].lower()}". Context * {" * ".join(primary_options)}""" for food in list(modelMap.values())]
    # # [i["index"] for i in model_categories]
    # # [food[0] for food in list(modelMap.values())]

    # # tokanize the input strings
    # primary_inputs = tokenizer(primary_prompts, return_tensors="pt", padding=True)

    # # Generate outputs
    # primary_outputs = model.generate(
    #     input_ids=primary_inputs["input_ids"],
    #     attention_mask=primary_inputs["attention_mask"],
    #     max_length=15,
    #     do_sample=False,
    # )

    # # extract the primary categories from the model outputs
    # primary_categories = tokenizer.batch_decode(primary_outputs, skip_special_tokens=True)

    # for i, category in enumerate(primary_categories):
    #     print(f"i: {i}")
    #     # insert the primary category into the model_categories list
    #     model_categories[i]["primary_category"] = category
    #     print(f"\n")

    # # model_categories = dict(zip(model_categories, primary_categories))

    # # [f"""Question: Classify "{food_list[k[0]].lower()}" into one of following categories of "{k[1]}". Context * {" * ".join(secondary_options[k[1]])}""" for k in model_categories.items()]
    # # ---- Secondary categories ----
    # # secondary_prompts = [f"""Question: Provide the food group category for "{query.lower()}". Context * {" * ".join(secondary_options[primary_categories[i]])}""" for i, query in enumerate(food_list)]
    # # secondary_prompts = [f"""Question: Classify "{query.lower()}" into one of following categories of "{primary_categories[i]}". Context * {" * ".join(secondary_options[primary_categories[i]])}""" for i, query in enumerate(food_list)]
    # # secondary_prompts = [f"""Question: Classify "{food_list[i].lower()}" into one of following categories of "{primary_categories[i]}". Context * {" * ".join(secondary_options[primary_categories[i]])}""" for i in model_categories]
    # # secondary_prompts = [f"""Question: Classify "{food_list[i].lower()}" into one of following categories of "{primary_categories[i]}". Context * {" * ".join(secondary_options[primary_categories[i]])}""" for i in enumerate(food_list)]
    # # secondary_prompts = [f"""Question: Classify "{food_list[k[0]].lower()}" into one of following categories of "{k[1]}". Context * {" * ".join(secondary_options[k[1]])}""" for k in model_categories.items()]
    # secondary_prompts = [f"""Question: Classify "{food_list[i["index"]].lower()}" into one of following categories of "{i["primary_category"]}". Context * {" * ".join(secondary_options[i["primary_category"]])}""" for i in model_categories]

    # # tokanize the input strings
    # secondary_inputs = tokenizer(secondary_prompts, return_tensors="pt", padding=True)

    # # Generate outputs
    # secondary_outputs = model.generate(
    #     input_ids=secondary_inputs["input_ids"],
    #     attention_mask=secondary_inputs["attention_mask"],
    #     max_length=15,
    #     do_sample=False,
    # )

    # # extract the secondary categories from the model outputs
    # secondary_categories = tokenizer.batch_decode(secondary_outputs, skip_special_tokens=True)

    # # insert the secondary category into the model_categories list
    # for i, category in enumerate(secondary_categories):
    #     print(f"i: {i}")
    #     model_categories[i]["secondary_category"] = category
    #     print(f"\n")

    # # insert the primary and secondary categories into the categories dictionary
    # for i, catMap in enumerate(model_categories):
    #     print(f"i: {i}")
    #     print(f"catMap: {catMap}")
    #     categories[catMap["index"]] = [catMap["primary_category"], catMap["secondary_category"]]
    #     print(f"\n")

    # [f"{cats[0]}/{cats[1]}" for cats in categories]

    # # return the inferred food group category
    # output_categories = [f"{cats[0]}/{cats[1]}" for cats in categories]
    # # output_categories = [f"{primary_categories[i]}/{secondary_categories[i]}" for i in range(len(food_list))]

    # for i in range(len(food_list)):
    #     print(f"Food: {food_list[i]} -> Category: {output_categories[i]}")
    #     print(f"\n")

    # # return the inferred food group category
    # # return json.dumps(output_categories)
    # return output_categories

def model_food_to_categories(foods_to_model = None, 
                             food_dictionary = None, 
                             primary_options = None, 
                             secondary_options = None, 
                             model = None, 
                             tokenizer = None):

    """
    Use the flan T5 model to classify the food items into categories and return a list of the inferred food group categories
    Args:
    foods_to_model: list of food items to classify
    food_dictionary: dictionary of food categories (import from food_map.py, FoodMap class)
    primary_options: list of primary food group categories to classify the food items into
    secondary_options: dictionary of secondary food group categories to further classify the food items into (keys are list elements from primary_options, values are lists of secondary categories for each primary category)
    model: HuggingFace T5 model
    tokenizer: HuggingFace T5 tokenizer

    Returns:
    categories: nested list of the inferred food group categories for each food item in the foods_to_model list [[primary_category, secondary_category], [primary_category, secondary_category], ...]
    """

    # foods_to_model = model_categories

    # print(f"Modeling {len(foods_to_model)} foods item(s): \n > {foods_to_model}")

    # primary and secondary categories to prompt the model to classify the food items into
    # if primary_options is not provided, use the primary categories from the food_dictionary
    if not primary_options or primary_options is None:
        # primary and secondary categories to prompt the model to classify the food items into
        primary_options = list(food_dictionary.categories.keys())
    
    # use the food_dictionary class to get the primary categories
    if not secondary_options or secondary_options is None:
        secondary_options = food_dictionary.categories

    # # Secondary categories to further classify the food items into  (version 1)
    # secondary_options = {
    #     "vegetable" : ["leafy", "root", "cruciferous", "fungi", "stem", "flower", "tuber", "bulb"],
    #     "fruit" : ["berry", "citrus", "tropical", "stone", "pome", "melon", "drupe"],
    #     "grain" : ["cereal", "pasta", "bread", "rice", "oat", "barley", "wheat", "corn", "rye"],
    #     "dairy" : ["milk",  "cheese", "butter", "cream", "yogurt"],
    #     "meat" : ["poultry", "beef", "fish", "pork", "seafood", "egg"],
    #     "nut" : ["almond", "cashew", "peanut", "walnut", "pecan", "pistachio", "macadamia", "hazelnut", "chestnut", "pine nut"],
    #     "legume" : ["bean", "lentil", "pea", "chickpea", "soybean"],
    #     "spice" : ["salt", "herb", "seed", "bark", "root", "flower"],
    #     "oil" : ["vegatable based", "seed based", "nut based", "animal based"],
    #     "sweetener" : ["sugar", "honey", "nectare", "syrup", "sugar alcohol", "sugar substitute"],
    #     "beverage" : ["juice", "milk", "water", "soda", "tea", "coffee", "milk substitute", "alcohol", "soup"]
    # }

    # ----- MODEL primary food category ----- 
    # ---- Primary categories ---- 
    # print(f"Getting primary categories...")
    primary_prompts = [f"""Question: Provide the food group category for "{food.lower()}". Context * {" * ".join(primary_options)}""" for food in foods_to_model]
    # primary_prompts = [f"""Question: Provide the food group category for "{i["food"].lower()}". Context * {" * ".join(primary_options)}""" for i in model_categories]
    # primary_prompts = [f"""Question: Provide the food group category for "{food_list[i["index"]].lower()}". Context * {" * ".join(primary_options)}""" for i in model_categories]
    # primary_prompts = [f"""Question: Provide the food group category for "{query.lower()}". Context * {" * ".join(primary_options)}""" for query in food_list]
    # primary_prompts = category_prompts(food_list, primary_options)
    # primary_prompts = [f"""Question: Provide the food group category for "{food_list[i].lower()}". Context * {" * ".join(primary_options)}""" for i in model_categories]
    # [food_list[i] for i in model_categories]
    # primary_prompts = [f"""Question: Provide the food group category for "{food[0].lower()}". Context * {" * ".join(primary_options)}""" for food in list(modelMap.values())]
    # [i["index"] for i in model_categories]
    # [food[0] for food in list(modelMap.values())]

    # tokanize the input strings
    primary_inputs = tokenizer(primary_prompts, return_tensors="pt", padding=True)

    # Generate outputs
    primary_outputs = model.generate(
        input_ids=primary_inputs["input_ids"],
        attention_mask=primary_inputs["attention_mask"],
        max_length=15,
        do_sample=False,
    )

    # extract the primary categories from the model outputs
    primary_categories = tokenizer.batch_decode(primary_outputs, skip_special_tokens=True)

    # for i, category in enumerate(primary_categories):
    #     print(f"i: {i}")
    #     # insert the primary category into the model_categories list
    #     model_categories[i]["primary_category"] = category
    #     print(f"\n")


    # model_categories = dict(zip(model_categories, primary_categories))
    # ----- MODEL secondary food category ----- 
    # ---- Secondary categories ----
    # print(f"Getting secondary categories...")
    secondary_prompts = [f"""Question: Classify "{i[0].lower()}" into one of following categories of "{i[1]}". Context * {" * ".join(secondary_options[i[1]])}""" for i in zip(foods_to_model, primary_categories)]
    # secondary_prompts = [f"""Question: Classify "{i["food"].lower()}" into one of following categories of "{i["primary_category"]}". Context * {" * ".join(secondary_options[i["primary_category"]])}""" for i in model_categories]

    # [f"""Question: Classify "{food_list[k[0]].lower()}" into one of following categories of "{k[1]}". Context * {" * ".join(secondary_options[k[1]])}""" for k in model_categories.items()]
    # secondary_prompts = [f"""Question: Provide the food group category for "{query.lower()}". Context * {" * ".join(secondary_options[primary_categories[i]])}""" for i, query in enumerate(food_list)]
    # secondary_prompts = [f"""Question: Classify "{query.lower()}" into one of following categories of "{primary_categories[i]}". Context * {" * ".join(secondary_options[primary_categories[i]])}""" for i, query in enumerate(food_list)]
    # secondary_prompts = [f"""Question: Classify "{food_list[i].lower()}" into one of following categories of "{primary_categories[i]}". Context * {" * ".join(secondary_options[primary_categories[i]])}""" for i in model_categories]
    # secondary_prompts = [f"""Question: Classify "{food_list[i].lower()}" into one of following categories of "{primary_categories[i]}". Context * {" * ".join(secondary_options[primary_categories[i]])}""" for i in enumerate(food_list)]
    # secondary_prompts = [f"""Question: Classify "{food_list[k[0]].lower()}" into one of following categories of "{k[1]}". Context * {" * ".join(secondary_options[k[1]])}""" for k in model_categories.items()]

    # tokanize the input strings
    secondary_inputs = tokenizer(secondary_prompts, return_tensors="pt", padding=True)

    # Generate outputs
    secondary_outputs = model.generate(
        input_ids=secondary_inputs["input_ids"],
        attention_mask=secondary_inputs["attention_mask"],
        max_length=15,
        do_sample=False,
    )

    # extract the secondary categories from the model outputs
    secondary_categories = tokenizer.batch_decode(secondary_outputs, skip_special_tokens=True)

    # # insert the secondary category into the model_categories list
    # for i, category in enumerate(secondary_categories):
    #     print(f"i: {i}")
    #     model_categories[i]["secondary_category"] = category
    #     print(f"\n")
    # print(f"Generating final categories...")
    categories = [[i[0], i[1]] for i in zip(primary_categories, secondary_categories)]

    return categories

def model_food_to_categories_inplace(model_categories = None, 
                                     food_dictionary = None, 
                                     primary_options = None, 
                                     secondary_options = None, 
                                     model = None, 
                                     tokenizer = None):

    """
    Use the flan T5 model to classify the food items into categories and return a list of the inferred food group categories
    Args:
        model_categories: list of food items to classify, each item is a dictionary with the following keys: "index", "food", "primary_category", "secondary_category"
        food_dictionary: dictionary of food categories (import from food_map.py, FoodMap class)
        primary_options: list of primary food group categories to classify the food items into
        secondary_options: dictionary of secondary food group categories to further classify the 
            food items into (keys are list elements from primary_options, values are lists of secondary categories for each primary category)
        model: HuggingFace T5 model
        tokenizer: HuggingFace T5 tokenizer
    Returns:
    None: modifies the input model_categories list in place to include the primary and secondary food group categories
    """

    # food_words = [i["food"] for i in model_categories]
    # print(f"Modeling {len(model_categories)} foods item(s): \n > {food_words}")
    
    # if primary_options is not provided, use the primary categories from the food_dictionary
    if not primary_options or primary_options is None:
        # primary and secondary categories to prompt the model to classify the food items into
        primary_options = list(food_dictionary.categories.keys())
    
    # use the food_dictionary class to get the primary categories
    if not secondary_options or secondary_options is None:
        secondary_options = food_dictionary.categories

    # # Secondary categories to further classify the food items into  (version 1)
    # secondary_options = {
    #     "vegetable" : ["leafy", "root", "cruciferous", "fungi", "stem", "flower", "tuber", "bulb"],
    #     "fruit" : ["berry", "citrus", "tropical", "stone", "pome", "melon", "drupe"],
    #     "grain" : ["cereal", "pasta", "bread", "rice", "oat", "barley", "wheat", "corn", "rye"],
    #     "dairy" : ["milk",  "cheese", "butter", "cream", "yogurt"],
    #     "meat" : ["poultry", "beef", "fish", "pork", "seafood", "egg"],
    #     "nut" : ["almond", "cashew", "peanut", "walnut", "pecan", "pistachio", "macadamia", "hazelnut", "chestnut", "pine nut"],
    #     "legume" : ["bean", "lentil", "pea", "chickpea", "soybean"],
    #     "spice" : ["salt", "herb", "seed", "bark", "root", "flower"],
    #     "oil" : ["vegatable based", "seed based", "nut based", "animal based"],
    #     "sweetener" : ["sugar", "honey", "nectare", "syrup", "sugar alcohol", "sugar substitute"],
    #     "beverage" : ["juice", "milk", "water", "soda", "tea", "coffee", "milk substitute", "alcohol", "soup"]
    # }

    # ----- MODEL primary food category ----- 
    # ---- Primary categories ---- 
    # print(f"Getting primary categories...")
    primary_prompts = [f"""Question: Provide the food group category for "{i["food"].lower()}". Context * {" * ".join(primary_options)}""" for i in model_categories]
    # primary_prompts = [f"""Question: Provide the food group category for "{food_list[i["index"]].lower()}". Context * {" * ".join(primary_options)}""" for i in model_categories]
    # primary_prompts = [f"""Question: Provide the food group category for "{query.lower()}". Context * {" * ".join(primary_options)}""" for query in food_list]
    # primary_prompts = category_prompts(food_list, primary_options)
    # primary_prompts = [f"""Question: Provide the food group category for "{food_list[i].lower()}". Context * {" * ".join(primary_options)}""" for i in model_categories]
    # [food_list[i] for i in model_categories]
    # primary_prompts = [f"""Question: Provide the food group category for "{food[0].lower()}". Context * {" * ".join(primary_options)}""" for food in list(modelMap.values())]
    # [i["index"] for i in model_categories]
    # [food[0] for food in list(modelMap.values())]

    # tokanize the input strings
    primary_inputs = tokenizer(primary_prompts, return_tensors="pt", padding=True)

    # Generate outputs
    primary_outputs = model.generate(
        input_ids=primary_inputs["input_ids"],
        attention_mask=primary_inputs["attention_mask"],
        max_length=15,
        do_sample=False,
    )

    # extract the primary categories from the model outputs
    primary_categories = tokenizer.batch_decode(primary_outputs, skip_special_tokens=True)

    # for i, category in enumerate(primary_categories):
    #     print(f"i: {i}")
    #     # insert the primary category into the model_categories list
    #     model_categories[i]["primary_category"] = category
    #     print(f"\n")

    # model_categories = dict(zip(model_categories, primary_categories))
    # ----- MODEL secondary food category ----- 
    # ---- Secondary categories ----
    # print(f"Getting secondary categories...")
    secondary_prompts = [f"""Question: Classify "{cat["food"].lower()}" into one of following categories of "{primary_categories[i]}". Context * {" * ".join(secondary_options[primary_categories[i]])}""" for i, cat in enumerate(model_categories)]
    # secondary_prompts = [f"""Question: Classify "{i[0].lower()}" into one of following categories of "{i[1]}". Context * {" * ".join(secondary_options[i[1]])}""" for i in zip(foods_to_model, primary_categories)]
    # secondary_prompts = [f"""Question: Classify "{i["food"].lower()}" into one of following categories of "{i["primary_category"]}". Context * {" * ".join(secondary_options[i["primary_category"]])}""" for i in model_categories]
    # [f"""Question: Classify "{food_list[k[0]].lower()}" into one of following categories of "{k[1]}". Context * {" * ".join(secondary_options[k[1]])}""" for k in model_categories.items()]
    # secondary_prompts = [f"""Question: Provide the food group category for "{query.lower()}". Context * {" * ".join(secondary_options[primary_categories[i]])}""" for i, query in enumerate(food_list)]
    # secondary_prompts = [f"""Question: Classify "{query.lower()}" into one of following categories of "{primary_categories[i]}". Context * {" * ".join(secondary_options[primary_categories[i]])}""" for i, query in enumerate(food_list)]
    # secondary_prompts = [f"""Question: Classify "{food_list[i].lower()}" into one of following categories of "{primary_categories[i]}". Context * {" * ".join(secondary_options[primary_categories[i]])}""" for i in model_categories]
    # secondary_prompts = [f"""Question: Classify "{food_list[i].lower()}" into one of following categories of "{primary_categories[i]}". Context * {" * ".join(secondary_options[primary_categories[i]])}""" for i in enumerate(food_list)]
    # secondary_prompts = [f"""Question: Classify "{food_list[k[0]].lower()}" into one of following categories of "{k[1]}". Context * {" * ".join(secondary_options[k[1]])}""" for k in model_categories.items()]

    # tokanize the input strings
    secondary_inputs = tokenizer(secondary_prompts, return_tensors="pt", padding=True)

    # Generate outputs
    secondary_outputs = model.generate(
        input_ids=secondary_inputs["input_ids"],
        attention_mask=secondary_inputs["attention_mask"],
        max_length=15,
        do_sample=False,
    )

    # extract the secondary categories from the model outputs
    secondary_categories = tokenizer.batch_decode(secondary_outputs, skip_special_tokens=True)

    # print(f"Inserting primary and secondary categories into the model_categories list...")
    # insert the primary and secondary categories into the model_categories input dictionary (IN PLACE)
    for i, category_map in enumerate(model_categories):
        # print(f"i: {i}")
        # print(f"catMap: {catMap}")
        category_map["primary_category"] = primary_categories[i]
        category_map["secondary_category"] = secondary_categories[i]

    return

# # # function to extract food ingredients from a list of ingredients using the FoodModel
# def generate_tags(model, ingredient_list):

#     food_tags = []

#     input = " ... ".join(ingredient_list)

#     model_output = model.extract_foods(input)

#     for food in model_output[0]["Ingredient"]:
#         food_tags.append(food['text'].lower())
        
#     # return food_tags
#     return json.dumps(food_tags)

def clean_scraped_data(df):
    
    # df = pd.read_csv(s3_path_string)
    # df["sorted_ingredient_tags"] = '[]' 
    # df.drop(columns=['uid'], inplace=True)

    # list of columns to keep
    cols_to_keep = ["author", "category", "cook_time", "cuisine", 
                           "description", "host", "image", "ingredient_tags", "ingredients", 
                           "instructions", "prep_time", "ratings", 
                           "sorted_ingredient_tags", "timestamp", "title", "total_time", 
                           "url", "yields"]
    
    # drop any columns that are not in the cols_to_keep list
    df = df[cols_to_keep]

    # list of columns that will end up as jsonb columns in postgres database
    jsonb_columns = ['category', 'ingredients', 'instructions', 'cuisine', 
                     'ingredient_tags', 'sorted_ingredient_tags']
    # jsonb_columns = ['category', 'ingredients', 'instructions', 'cuisine', 'ingredient_tags']

    # list of columns that will end up as text columns in postgres database
    text_columns = ['title', 'host', 'yields', 'image', 'author', 'description', 'url']
    # text_columns = ['title', 'host', 'yields', 'image', 'author', 'description', 'uid', 'url']

    # list of columns that will end up as integer columns in postgres database
    integer_columns = ['timestamp', 'total_time', 'cook_time', 'prep_time']

    # list of columns that will end up as float columns in postgres database
    float_columns = ['ratings']
    
    print(f"Convert jsonb columns to lists...")

    # loop over json columns and use "ast" to convert stringified list into a list for all jsonb columns
    for column in jsonb_columns:
        df[column] = df[column].apply(ast.literal_eval)

    print(f"Strip any trailing/leading whitespaces...")

    # loop through jsonb columns and strip away any trailing/leading whitespaces
    for column in jsonb_columns:
        df[column] = df[column].apply(lambda x: [s.strip() for s in x])
    
    # df.ingredients
    # df.ingredient_tags
    # df.ingredient_tags.values.tolist()[0]
    # # loop through jsonb columns and remove any non alpha numerics and strip away any trailing/leading whitespaces
    # for column in jsonb_columns:
    #     df[column] = df[column].apply(lambda x: [re.sub('[^A-Za-z ]', '', s).strip() for s in x])
    
    print(f"Removing any unicode values in list columns...")

    # loop through jsonb columns and santize list columns by removing unicode values
    for column in jsonb_columns:
        df[column] = df[column].apply(lambda x: [re.sub('[\x00-\x19]', '', s) for s in x])
    
    # df.ingredients
    # df.ingredient_tags
    # df.ingredient_tags.values.tolist()[0]

    print(f"Coercing integer columns to Int64 and replacing missing/NaN values with 0...")

    # coerce integer columns to Int64 and replace missing/NaN values with 0
    for column in integer_columns:
        df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64').fillna(0)

    print(f"Coercing float columns to float64 and replacing missing/NaN values with 0...")
    # loop through float_columns coerce all ratings values to float64 and replace missing/NaN values with 0
    for column in float_columns:
        df[column] = pd.to_numeric(df[column], errors='coerce').astype('float64').fillna(0)

    # sort by lowercased values
    def lowercase_sort(lst):
        return sorted(lst, key=lambda x: x.lower()) 
    
    print(f"Sort the ingredients in each recipe...")
    # sort the ingredient_tags and make a new sorted_ingredient_tags column
    df = df.assign(sorted_ingredient_tags = lambda x: (x["ingredient_tags"].apply(lowercase_sort)))

    # convert a dictionary column to json  function:
    def dict2json(dictionary):
        return json.dumps(dictionary, ensure_ascii=False)
    
    print(f"Convert jsonb columns to dictionaries...")
    # loop through jsonb columns and convert list columns into dictonary columns
    for column in jsonb_columns:
        df[column] = df.apply(lambda row: {column:row[column]}, axis=1)

    print(f"Convert dictionary columns to json columns...")
    # loop thorugh jsonb columns and convert dictionary columns to json columns
    for column in jsonb_columns:
        df[column] = df[column].map(dict2json)
    
    print(f"Arranging columns in alphabetical order...")
    # Sort columns by alphabetical order
    df = df.sort_index(axis=1)

    print(f"Checking all needed columns are present...")
    # make a set of the dataframe columns to make sure all columns are present
    df_cols = set(df.columns)

    # final output columns to make sure all columns are present
    output_columns = set(cols_to_keep)
    
    # TODO: RAISE an error here for missing columns and process the error in the lambda_handler
    # TODO: If all output columns are not present, then the data may need to be set aside and checked out down the road
    # check if all columns are present
    if output_columns != df_cols:
        missing_cols = output_columns.difference(df_cols)
        print(f"MISSING COLUMNS in df: {missing_cols}")
        print(f"Adding missing columns to df...")
        add_missing_columns(df, missing_cols)
    else:
        print(f"No missing columns in df")

    # manually select and order columns for final output in alphabetical order
    df = df[['author', 'category', 'cook_time', 'cuisine', 'description', 'host',
            'image', 'ingredient_tags', 'ingredients', 'instructions', 'prep_time',
            'ratings', 'sorted_ingredient_tags', 'timestamp', 'title', 'total_time', 'url',
            'yields']]
    
    print(f"Fill any NaN with default values...")

    # fill any NaN with default values for each column
    df = fillna_default_vals(df)

    # output row and column count
    print(f"number of rows: {df.shape[0]}")
    print(f"number of cols: {df.shape[1]}")

    print(f"----> SUCCESS, data cleaning complete!")

    return df

# Add any missing columns in pandas dataframe with the correct type and default values, 
# then reorder the columns to be alphabetical (all of this is done IN PLACE)
def add_missing_columns(df, missing_columns):
    # create a dictionary of the keys and their data types
    keys_to_type_map = {
        "host": object,
        "title": object,
        "category": object,
        "total_time": np.int64,
        "cook_time": np.int64,
        "prep_time": np.int64,
        "yields": object,
        "image": object,
        "ingredients": object,
        "instructions": object,
        "ratings": np.float64,
        "author": object,
        "cuisine": object,
        "description": object,
        # "uid": str,
        "url": object,
        "ingredient_tags": object,
        "sorted_ingredient_tags": object,
        "timestamp": np.int64
        }
    
    # create a dictionary of the keys and their data types
    default_vals_map = {
        "host": "",
        "title": "",
        "category": '{"category": [""]}',
        "total_time": 0,
        "cook_time": 0,
        "prep_time": 0,
        "yields": "",
        "image": "",
        "ingredients": '{"ingredients": [""]}',
        "instructions": '{"instructions": [""]}',
        "ratings": 0,
        "author": "",
        "cuisine": '{"cuisine": [""]}',
        "description": "",
        "url": "",
        "ingredient_tags": '{"ingredient_tags": [""]}',
        "sorted_ingredient_tags": '{"sorted_ingredient_tags": [""]}',
        "timestamp": 0
        }

    # Iterate over missing columns and add them to the DataFrame with appropriate data type
    for column in missing_columns:
        

        print(f"Adding column: {column}")
        try:

            data_type = keys_to_type_map.get(column, object)  # default to object type if not found in the map
            print(f"data_type: {data_type}")
            # default_value = default_vals_map.get(column, "")  # default to empty string if not found in the map
            # print(f"default_value: {default_value}")

            # Add a new column with the correct data type and default value
            df[column] = pd.Series(dtype=data_type)
            # df[column] = pd.Series([default_value for i in range(len(df))], dtype=data_type)
        except Exception as e:
            print(f"Error adding column: {e}")
            print(f"Skipping column: {column}")

    # Sort columns by alphabetical order
    df.sort_index(axis=1, inplace=True)

# create a function to use pandas fill na to fill all missing values in dataframe with specified default values from default value map
def fillna_default_vals(df):

    # create a dictionary of the keys and their data types
    default_vals_map = {
        "host": "",
        "title": "",
        "category": '{"category": [""]}',
        "total_time": 0,
        "cook_time": 0,
        "prep_time": 0,
        "yields": "",
        "image": "",
        "ingredients": '{"ingredients": [""]}',
        "instructions": '{"instructions": [""]}',
        "ratings": 0,
        "author": "",
        "cuisine": '{"cuisine": [""]}',
        "description": "",
        "url": "",
        "ingredient_tags": '{"ingredient_tags": [""]}',
        "sorted_ingredient_tags": '{"sorted_ingredient_tags": [""]}',
        "timestamp": 0
        }
    
    df = df.fillna(value=default_vals_map, inplace=False)

    return df

def get_csv_from_s3(message):

    print(f'---->\n Value of message: {message}')

    # s3_event = message["body"]
    s3_event = json.loads(message["body"])
    # s3_event = json.loads(message)["body"]

    print(f'---->\n Value of s3_event: {s3_event}')


    # # Extract the S3 bucket and the filename from the S3 event notification JSON object
    S3_BUCKET    = s3_event['Records'][0]['s3']['bucket']['name']
    S3_FILE_NAME = s3_event['Records'][0]['s3']['object']['key']

    print(f"- S3_BUCKET: {S3_BUCKET}")
    print(f"- S3_FILE_NAME: {S3_FILE_NAME}")

    print(f"Gathering CSV file from S3...")
    
    try:

        # get the object from S3
        s3_obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_FILE_NAME)
    except Exception as e:
        print(f"Error getting CSV file from S3: {e}")
        # Handle the exception here, or raise a specific error
        raise Exception(f"Error processing element: {e}")

    # read the CSV file into a pandas dataframe
    csv_df = pd.read_csv(s3_obj["Body"])
    
    print(f"csv_df: {csv_df}")
    print(f"csv_df.shape: {csv_df.shape}")

    return csv_df

# Create a list of the [year, month, day] when the function is run (YYYY, MM, DD)
# Use the [year, month, day] in prefix of the uploaded S3 object
def get_event_date():

    # Use the current date and time as the default
    event_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # Parse the eventTime string into a datetime object
    parsed_event_time = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%S.%fZ")

    # Extract month, day, and year
    month = parsed_event_time.strftime("%m")
    day   = parsed_event_time.strftime("%d")
    year  = str(parsed_event_time.year)

    # create a date_key string
    print(f"Year: {year}, Month: {month}, Day: {day}")

    return [year, month, day]

# lambda handler function
def extract_ingredients_lambda(event, context):
    S3_URIS = ["s3://recipes-scraped-data-bucket/1457948d58014de9921621c1caf5638a_1708179436.csv", 
               "s3://recipes-scraped-data-bucket/c828f83bc212486abc6b8d725473ca4d_1708179432.csv", 
               "s3://recipes-scraped-data-bucket/059b692ae87745929cad982bc2ab1561_1707926862.csv"]
    message_count = 0
    
    batch_item_failures = []
    sqs_batch_response = {}
    
    output_data = []

    # for message in event["Records"]:
    # for message in scraped_list:
    for message in S3_URIS:
        message_count += 1
        print(f"==== PROCESSING MESSAGE: {message_count} ====")
        # print(f"message {message_count}: {message}")
        try:

            # s3_csv = get_csv_from_s3(message)
            s3_csv = pd.read_csv(message)
            
            print(f"s3_csv.shape: {s3_csv.shape}")

            output_data.append(s3_csv)

            # output_json = extract_ingredients_from_s3_event(message)
            # output_data.append(output_json)

        except Exception as e:
            print(f"Exception raised from messageId {message['messageId']}\n: {e}")
            batch_item_failures.append({"itemIdentifier": message['messageId']})


    print(f"Concating output_data...")
    print(f"len(output_data): {len(output_data)}")

    # Convert list of dictionaries to pandas dataframe
    df = pd.concat(output_data)

    # df.drop(columns=['uid'], inplace=True)
    # df["sorted_ingredient_tags"] = "['']" 

    # # Convert list of dictionaries to pandas dataframe
    # df = pd.DataFrame(output_data)

    print(f"df.shape: {df.shape}")
    print(f"df: {df}")

    print(f"Applying T5 model to generate ingredient tags and food categories...")
    
    # df['ingredients'].values.tolist()[0]

    # # # convert the stringified list into a list for the ingredients, NER, and directions columns
    # df['ingredients'] = df['ingredients'].apply(ast.literal_eval)
    
    # # Add ingredient tags to dataframe
    # df["ingredient_tags"] = df["ingredients"].apply(lambda x: generate_tags(model, x))
    df["ingredients"].apply(ast.literal_eval).apply(lambda x: get_foods_from_ingredients(x, model, tokenizer))

    # df = df[0:1]

    print(f"Extracting food ingredients from the ingredients column...")
    # # create ingredients tags list from the ingredients column, then create a new column with category tags for each food in the ingredients list
    df["ingredient_tags"] = df["ingredients"].apply(ast.literal_eval).apply(lambda x: get_foods_from_ingredients(x, model, tokenizer))

    print(f"Categorizing food ingredients...")
    # Get the categories for each food in the ingredient_tags column using the food_map dictionary and the HuggingFace T5 model
    df["categories"] = df["ingredient_tags"].apply(lambda x: get_categories_from_foods(x, food_map, list(food_map.categories.keys()), food_map.categories, model, tokenizer))
    # food_list = df["ingredient_tags"].values.tolist()[6]
    # food_list

    # food_dictionary = food_map
    # primary_options = list(food_dictionary.categories.keys())
    # secondary_options = food_dictionary.categories
    # df["categories"]
    # create a new tags_to_categories column that maps the tags to the categories in the categories column with the column value being a list [{tag: category}]
    df["tags_to_categories"] = df.apply(lambda x: [{x["ingredient_tags"][i]: x["categories"][i] for i in range(len(x["ingredient_tags"]))}], axis=1)

    df["ingredients_to_tags"] = df.apply(lambda x: {x["ingredients"][i]: x["ingredient_tags"][i] for i in range(len(x["ingredients"]))}, axis=1)
    df["ingredients_to_categories"] = df.apply(lambda x: {x["ingredients"][i]: x["categories"][i] for i in range(len(ast.literal_eval(x["ingredients"])))}, axis=1)

    df["ingredient_tags"].apply(lambda x: get_categories_from_foods(x, model, tokenizer))
    df["ingredient_tags"].apply(lambda x: is_animal_product(x, model, tokenizer))


    # Add ingredient tags to dataframe using HuggingFace BERT FoodModel
    df["ingredient_tags"] = df["ingredients"].apply(ast.literal_eval).apply(lambda x: generate_tags(model, x))

    print(f"---- Cleaning scraped data ----")

    # clean the scraped dataframe
    df = clean_scraped_data(df)
    
    # get the current year, month, and day
    year, month, day = get_event_date()

    # generate a random UUID to add to the OUTPUT_S3_OBJECT_NAME
    unique_id = f"{uuid.uuid4().hex}"

    # Use uuid.uuid4() and current timestamp to create a unique filename
    csv_key = f"{unique_id}_{int(time.time())}.csv"

    # create the S3 filename
    OUTPUT_S3_FILENAME = f"s3://{OUTPUT_S3_BUCKET}/{year}/{month}/{day}/{csv_key}"
    # OUTPUT_S3_FILENAME = f"s3://{OUTPUT_S3_BUCKET}/{csv_key}"

    print(f"Saving dataframe to S3:\n - OUTPUT_S3_FILENAME: '{OUTPUT_S3_FILENAME}'")

    # save the dataframe to S3
    df.to_csv(OUTPUT_S3_FILENAME, index=False)

    sqs_batch_response["batchItemFailures"] = batch_item_failures

    print(f"sqs_batch_response: {sqs_batch_response}")

    return sqs_batch_response
