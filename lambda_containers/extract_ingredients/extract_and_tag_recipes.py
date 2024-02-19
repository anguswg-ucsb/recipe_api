import google.generativeai as genai
import os
import json
import re
import pandas as pd
import numpy as np 
import ast
import uuid
import time
from datetime import datetime

from config import Config

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

########
import ast
from transformers import T5Tokenizer, T5ForConditionalGeneration
# from transformers import T5Tokenizer, T5ForConditionalGeneration, AutoTokenizer, FlaxAutoModelForSeq2SeqLM

tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-large")
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-large")

# tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
# model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")

# # create ingredients tags list from the ingredients column, then create a new column with category tags for each food in the ingredients list
# df["ingredient_tags"] = df["ingredients"].apply(ast.literal_eval).apply(lambda x: get_foods_from_ingredients(x, model, tokenizer))
# df["categories"] = df["ingredient_tags"].apply(lambda x: get_categories_from_foods(x, model, tokenizer))

# # create a new tags_to_categories column that maps the tags to the categories in the categories column with the column value being a list [{tag: category}]
# df["tags_to_categories"] = df.apply(lambda x: [{x["ingredient_tags"][i]: x["categories"][i] for i in range(len(x["ingredient_tags"]))}], axis=1)

# df["ingredients_to_tags"] = df.apply(lambda x: {x["ingredients"][i]: x["ingredient_tags"][i] for i in range(len(x["ingredients"]))}, axis=1)
# df["ingredients_to_categories"] = df.apply(lambda x: {x["ingredients"][i]: x["categories"][i] for i in range(len(ast.literal_eval(x["ingredients"])))}, axis=1)

# df["ingredient_tags"].apply(lambda x: get_categories_from_foods(x, model, tokenizer))
# df["ingredient_tags"].apply(lambda x: is_animal_product(x, model, tokenizer))

# get_foods_from_ingredients()
def get_foods_from_ingredients(ingredient_list, model, tokenizer):

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
        max_length=1500,
        do_sample=False,  # disable sampling to test if batching affects output
    )

    foods = tokenizer.batch_decode(output_sequences, skip_special_tokens=True)

    return foods

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")

def get_categories_from_foods(food_list, model, tokenizer):

    # tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-large")
    # model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")

    # food_list = df["ingredient_tags"].values.tolist()[4]
    
    # def category_prompts(food_list, options):
    #     prompts = [f"""Question: Provide the food group category for "{query.lower()}". Context * {" * ".join(options)}""" for query in food_list]
    #     return prompts

    # First set of categories to classify the food items into
    primary_options = ["vegetable", "fruit", "grain", "dairy", "meat", "nut", "legume", "spice", "oil", "sweetener", "beverage", "other"]
    # primary_options = ["vegetable", "fruit", "grain", "dairy", "meat", "nut", "legume", "spice", "oil", "sweetener", "beverage", "substitute", "other"]
    # primary_options = ["vegetable", "fruit", "grain", "dairy", "meat", "nut", "legume", "spice", "fat/oil", "sweetener", "beverage", "other"]

    # Secondary categories to further classify the food items into
    secondary_options = {
        "vegetable" : ["leafy", "root", "cruciferous", "fungi", "stem", "flower", "tuber", "bulb"],
        "fruit" : ["berry", "citrus", "tropical", "stone", "pome", "melon", "drupe"],
        "grain" : ["cereal", "pasta", "bread", "rice", "oat", "barley", "wheat", "corn", "rye"],
        "dairy" : ["milk",  "cheese", "butter", "cream", "yogurt"],
        "meat" : ["poultry", "beef", "fish", "pork", "seafood", "egg"],
        "nut" : ["almond", "cashew", "peanut", "walnut", "pecan", "pistachio", "macadamia", "hazelnut", "chestnut", "pine nut"],
        "legume" : ["bean", "lentil", "pea", "chickpea", "soybean"],
        "spice" : ["salt", "herb", "seed", "bark", "root", "flower"],
        "oil" : ["vegatable based", "seed based", "nut based", "animal based"],
        "sweetener" : ["sugar", "honey", "nectare", "syrup", "sugar alcohol", "sugar substitute"],
        "beverage" : ["juice", "milk", "water", "soda", "tea", "coffee", "milk substitute", "alcohol", "soup"]
    }

    # ---- Primary categories ---- 
    primary_prompts = [f"""Question: Provide the food group category for "{query.lower()}". Context * {" * ".join(primary_options)}""" for query in food_list]
    # primary_prompts = category_prompts(food_list, primary_options)

     # tokanize the input strings
    primary_inputs = tokenizer(primary_prompts, return_tensors="pt", padding=True)

    # Generate outputs
    primary_outputs = model.generate(
        input_ids=primary_inputs["input_ids"],
        attention_mask=primary_inputs["attention_mask"],
        max_length=15,
        do_sample=False,  # disable sampling to test if batching affects output
    )
    
    # extract the primary categories from the model outputs
    primary_categories = tokenizer.batch_decode(primary_outputs, skip_special_tokens=True)
    
    # ---- Secondary categories ----
    secondary_prompts = [f"""Question: Provide the food group category for "{query.lower()}". Context * {" * ".join(secondary_options[primary_categories[i]])}""" for i, query in enumerate(food_list)]

    # tokanize the input strings
    secondary_inputs = tokenizer(secondary_prompts, return_tensors="pt", padding=True)

    # Generate outputs
    secondary_outputs = model.generate(
        input_ids=secondary_inputs["input_ids"],
        attention_mask=secondary_inputs["attention_mask"],
        max_length=15,
        do_sample=False,  # disable sampling to test if batching affects output
    )

    # extract the secondary categories from the model outputs
    secondary_categories = tokenizer.batch_decode(secondary_outputs, skip_special_tokens=True)

    # return the inferred food group category
    output_categories = [f"{primary_categories[i]}/{secondary_categories[i]}" for i in range(len(food_list))]

    # return the inferred food group category
    return output_categories

def is_animal_product(food_list, model, tokenizer):

    # tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-large")
    # model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")

    def query_is_animal_product(query):
        # options = ["vegetable", "fruit", "grain", "meat", "dairy", "nut", "spice", "oil", "sweetener", "beverage", "other"]
        # t5query = f"""Question: Select the item from this list which is a "{query}". Context: * {" * ".join(options)}"""

        
        # prompt to get the food group category for a given food item
        prompt = f"""Question: Is "{query}" an animal product?"""

        inputs = tokenizer(prompt, return_tensors="pt")
        outputs = model.generate(**inputs, max_new_tokens=20)

        # return the inferred food group category
        return tokenizer.batch_decode(outputs, skip_special_tokens=True)

    # query_from_list(food_list[6], options)
    query_results = []

    for i in range(len(food_list)):
        is_animal_product = query_is_animal_product(food_list[i])

        # category_map = {food_list[i] : category}
        query_results.append(is_animal_product)

    return query_results


######### ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##  

def remove_trailing_commas(json_like_string):
    # Define a regular expression pattern to match trailing commas
    pattern = r',(?=\s*[\]}])'

    # Replace any trailing commas with an empty string
    result = re.sub(pattern, '', json_like_string)

    return result

def make_prompt(ingredients_list, prompt_type="categories"):
    if prompt_type == "categories":
        prompt = f"""
        You have to identify different types of foods in a list of ingredients.
        The system should accurately detect and label various foods in a list of ingredients, providing the name
        of the food. Additionally, the system should categorize the type of food (e.g., fruits, vegetables, grains, etc.) and remove any information about the units and/or quantities.
        If an ingredients is part of a larger category of ingredients, then you should add another element to the ingredient's key value list for the category(s). For example, foods labelled as "meat" could also fall into the subcategory of "beef", "pork", "poultry", "lamb", "game meats", "fish", "processed meats", or "offal".
        The output should be a JSON formatted response with the following structure:
        {{
        "ingredient1" : ["food_name1", "food_category1"],
        "ingredient2" : ["food_name2", "food_category2A", "food_category2B"],
        "ingredient3 or ingredient4" : [
            ["food_name3", "food_category3"],
            ["food_name4", "food_category4"]
            ],
        "ingredient5 (or use ingredient6)" : [
            ["food_name5", "food_category5"],
            ["food_name6", "food_category6"]
            ]    
        ...
        }}
        
        All values in the list should be strings, and if a value is not present or cannot be identified, use an empty string as a default value.
        If an ingredient specifies that there is a substitute for the ingredient then you should add another element to the ingredient's key value list for the substitute(s). 
        (Substitute ingredient(s) may be detected when language like "or" is used in the ingredient, if a delimiter such as a "/" separates the ingredient, if a set of parentheses is used describing possible substitutes, etc.)
        The output JSON string has to be a valid JSON that is parsable and does not contain errors.

        For example, given the input list of ingredients:
        [
        "4 pork chops",
        "1 pinch garlic salt",
        "1 tablespoon vegetable oil",
        "1 onion, chopped",
        "2 stalks chopped celery, with leaves",
        "12 ounces tomato paste",
        "1 (15 ounce) can tomato sauce",
        "3 cups water",
        "Butter or margarine (about 1/2 cup)"
        "2 salmon fillets",
        "1 chicken breast",
        "3 eggs"
        ]

        The output should be:
        {{
        "4 pork chops" : ["pork chops", "meat", "pork"],
        "1 pinch garlic salt": ["garlic salt", "spice"],
        "1 tablespoon vegetable oil": ["vegetable oil", "oil"],
        "1 onion, chopped": ["onion", "vegetable"],
        "2 stalks chopped celery, with leaves": ["celery", "vegetable"],
        "12 ounces tomato paste": ["tomato paste", "canned vegetable"],
        "1 (15 ounce) can tomato sauce": ["tomato sauce", "canned vegetable"],
        "3 cups water": ["water", "water"],
        "Butter or margarine (about 1/2 cup)": [
            ["Butter", "dairy"],
            ["margarine", "dairy"]
            ],
        "3 eggs": ["eggs", "meat"]
        "2 salmon fillets": ["salmon", "meat", "fish"]
        "1 chicken breast": ["chicken", "meat", "poultry"]
        }}
        Input list of ingredients: {str(list(set(ingredients_list)))}
        Ouput: 
        """
    elif prompt_type == "details":
        prompt = f"""You have to identify different types of foods in a list of ingredients.
        The system should accurately detect and label various foods in a list of ingredients, providing the name
        of the food. Additionally, the system should categorize the type of food (e.g., fruits, vegetables, grains, etc.) and extract any information about the units and/or quantities.
        The output should be a JSON formatted response with the following structure:
        {{
        "ingredient1" : [["food_name1", "food_category1", ["quantity_and_units1A", "quantity_and_units1B"]]],
        "ingredient2" : [["food_name2", "food_category2", ["quantity_and_units1A"]]],
        "ingredient3 or ingredient4" : [
            ["food_name3", "food_category3", ["quantity_and_units3A"]],
            ["food_name4", "food_category4", ["quantity_and_units4A"]]
            ],
        "ingredient5 (or use ingredient6)" : [
            ["food_name5", "food_category5", ["quantity_and_units5A"]],
            ["food_name6", "food_category6", ["quantity_and_units6A"]]
            ]    
        ...
        }}

        All values in the list should be strings, and if a value is not present or cannot be identified, use an empty string as a default value.
        If an ingredient specifies that there is a substitute for the ingredient then you should add another element to the ingredient's key value list for the substitute(s). 
        (Substitute ingredient(s) may be detected when language like "or" is used in the ingredient, if a delimiter such as a "/" separates the ingredient, if a set of parentheses is used describing possible substitutes, etc.)
        The output JSON string has to be a valid JSON that is parsable and does not contain errors and does not contain any trailing commas.

        For example, given the input list of ingredients:
        [
        "4 pork chops",
        "1 pinch garlic salt",
        "1 tablespoon vegetable oil",
        "1 onion, chopped",
        "2 stalks chopped celery, with leaves",
        "12 ounces tomato paste",
        "1 (15 ounce) can tomato sauce",
        "3 cups water",
        "Butter or margarine (about 1/2 cup)"
        "3 eggs"
        ]

        The output should be:
        {{
        "4 pork chops" : [["pork chops", "meat", ["chops", "4"]]],
        "1 pinch garlic salt": [["garlic salt", "spice", ["pinch", "1"]]],
        "1 tablespoon vegetable oil": [["vegetable oil", "oil", ["tablespoon", "1"]]],
        "1 onion, chopped": [["onion", "vegetable", ["chopped", "1"]]],
        "2 stalks chopped celery, with leaves": [["celery", "vegetable", ["stalks", "2"]]],
        "12 ounces tomato paste": [["tomato paste", "canned vegetable", ["ounces", "12"]]],
        "1 (15 ounce) can tomato sauce": [["tomato sauce", "canned vegetable", [["can", "1"], ["ounces", "15"]]],
        "3 cups water": [["water", "water", ["cups", "3"]]],
        "Butter or margarine (about 1/2 cup)": [
            ["Butter", "dairy", ["cup", "1/2"]],
            ["margarine", "dairy", ["cup", "1/2"]]
            ],
        "3 eggs": [["eggs", "meat", ["eggs", "3"]]]
        }}
        Input list of ingredients: {str(list(set(ingredients_list)))}
        Ouput:"""
    else: 
        prompt = f"""Given a comma-separated list of strings representing ingredients from a recipe, return a JSON-formatted response where each original ingredient is a field in the JSON. 
        The values should include the extracted food words, the food category, and any relevant subcategories. For example, if the input list of ingredients is:

    [
        "4 pork chops",
        "1 pinch garlic salt",
        "1 tablespoon vegetable oil",
        "1 onion, chopped",
        "2 stalks chopped celery, with leaves",
        "12 ounces tomato paste",
        "1 (15 ounce) can tomato sauce",
        "3 cups water",
        "Butter or margarine (about 1/2 cup)",
        "2 salmon fillets",
        "1 chicken breast",
        "3 eggs"
    ]

    The output should resemble:
    {{
        "4 pork chops": ["pork chops", "meat", "pork"],
        "1 pinch garlic salt": ["garlic salt", "spice"],
        "1 tablespoon vegetable oil": ["vegetable oil", "oil"],
        "1 onion, chopped": ["onion", "vegetable"],
        "2 stalks chopped celery, with leaves": ["celery", "vegetable"],
        "12 ounces tomato paste": ["tomato paste", "canned vegetable"],
        "1 (15 ounce) can tomato sauce": ["tomato sauce", "canned vegetable"],
        "3 cups water": ["water", "water"],
        "Butter or margarine (about 1/2 cup)": [
            ["Butter", "dairy"],
            ["margarine", "dairy"]
        ],
        "2 salmon fillets": ["salmon", "meat", "fish"],
        "1 chicken breast": ["chicken", "meat", "poultry"],
        "3 eggs": ["eggs", "meat"]
    }}
    Input list of ingredients: {str(list(set(ingredients_list)))}
    """

    return prompt

# # function to extract food ingredients from a list of ingredients using the FoodModel
def ingredients_to_tags(ingredients_map, ingredient_list):
    # ingredients_map = json_response
    # ingredient_list = json.loads(df["ingredients"].values.tolist()[1])
    # ingredient_list = ingredient_list["ingredients"]
    # print(f"=========")
    # print(f"ingredient_list: {ingredient_list}")
    # print(f"=========")
    # food_tags = []
    # ingredient_list = df["ingredients"].apply(ast.literal_eval).values.tolist()[6]
    # ingredients_map = json_response

    # [i for i in ingredient_list]
    # ingredients_map['3 tablespoons vegetable oil'][1]
    # [i for i in ingredient_list]
    # ingredients_map.keys()

    # for i in range(len(ingredient_list)):
    #     ingred = ingredient_list[i]
    #     print(f"i: {i}")
    #     print(f"inred: {ingred}")
    #     ingredients_map[ingred]
    #     # if ingred in ingredients_map:
    #     #     print(f"'{ingred}' found in map - ingredients_map[ingred]: {ingredients_map[ingred]}")
    #     if ingred not in ingredients_map:
    #         print(f"------")
    #         print(f"----> ingred {ingred} NOT FOUND in ingredients_map")
    #         print(f"------")
    #         # print(f"i: {i}, not found in ingredients_map")
    #     else:
    #         print(f"Ingredients value in map: \n{ingredients_map[ingred]}")

    #     print(f"=========" * 4)
    # ingredients_map[i]
    # ingredients_map.get("2 large baking sheets")

    # tags = {i : ingredients_map[i] for i in ingredient_list}

    tagged_foods = {i : ingredients_map[i][0] for i in ingredient_list if ingredients_map[i]}
    tagged_categories = {i : ingredients_map[i][1] for i in ingredient_list if ingredients_map[i]}
    # tagged_foods = {i : ingredients_map[i][0] for i in ingredient_list}
    # tagged_categories = {i : ingredients_map[i][1] for i in ingredient_list}

    # tags_to_categories = {ingredients_map[i][0][0] : ingredients_map[i][0][1] for i in ingredient_list}
    # tagged_quantities = {i : ingredients_map[i][0][2] for i in ingredient_list}

    # tagged_foods = {i : ingredients_map[i][0][0] for i in ingredient_list}
    # tagged_categories = {i : ingredients_map[i][0][1] for i in ingredient_list}
    # tags_to_categories = {ingredients_map[i][0][0] : ingredients_map[i][0][1] for i in ingredient_list}
    # tagged_quantities = {i : ingredients_map[i][0][2] for i in ingredient_list}

    # input = " ... ".join(ingredient_list)

    # model_output = model.extract_foods(input)

    # for food in model_output[0]["Ingredient"]:
    #     food_tags.append(food['text'].lower())
        
    # return food_tags
    # return tagged_foods, tagged_categories, tags_to_categories, tagged_quantities
    return json.dumps(tagged_foods)

def get_ingredient_predictions(df, gemini_api_key):

    genai.configure(api_key=gemini_api_key)

    # get all the ingredients from the dataframe
    ingredient_lists = [ast.literal_eval(df.ingredients.values.tolist()[i]) for i in range(0, len(df))]
    # ingredient_lists = [json.loads(df.ingredients.values.tolist()[i])["ingredients"] for i in range(1, len(df))]
    # ingredient_lists = [json.loads(df.ingredients.values.tolist()[i])["ingredients"] for i in range(len(df))]

    # Merge all lists into a single list
    ingredients = [item for sublist in ingredient_lists for item in sublist]

    # create a prompt for the model
    prompt = make_prompt(ingredients, "others")
    # prompt = make_prompt(ingredients, "details")

    model = genai.GenerativeModel('gemini-pro')
    
    genai.get_model("models/gemini-pro")
    # Get the model's response
    response = model.generate_content(prompt,
            generation_config=genai.types.GenerationConfig(
            candidate_count=1,
            max_output_tokens = 4000,
            temperature=1.0
            ))
    
    # Get the response as a string
    response_text = response.text
    
    # Remove trailing commas from the response
    json_response = json.loads(response_text)
    # json_response =  json.loads(response_text.replace("json", "").replace("```", ""))
    # df["ingredients"].values.tolist()[4]

    # # Add ingredient tags to dataframe using HuggingFace BERT FoodModel
    # # tmp = df["ingredients"].apply(ast.literal_eval).values.tolist()[0]
    # # ingredients_map = json_response

    # df["ingredients"].apply(ast.literal_eval).apply(lambda x: ingredients_to_tags(json_response, x))
    # df["ingredient_tags"] = df["ingredients"].apply(ast.literal_eval).apply(lambda x: ingredients_to_tags(json_response, x))
    return json_response

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

    # df["ingredient_tags"] = df["ingredients"].apply(ast.literal_eval).apply(lambda x: generate_tags(model, x))
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

    message_count = 0
    
    batch_item_failures = []
    sqs_batch_response = {}
    
    output_data = []

    for message in event["Records"]:
    # for message in S3_URIS:

        message_count += 1
        print(f"==== PROCESSING MESSAGE: {message_count} ====")
        # print(f"message {message_count}: {message}")
        try:

            s3_csv = get_csv_from_s3(message)
            # s3_csv = pd.read_csv(message)
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

    print(f"Applying FoodModel to generate ingredient tags...")
    
    # df['ingredients'].values.tolist()[0]

    # # # convert the stringified list into a list for the ingredients, NER, and directions columns
    # df['ingredients'] = df['ingredients'].apply(ast.literal_eval)
    
    # # Add ingredient tags to dataframe
    # df["ingredient_tags"] = df["ingredients"].apply(lambda x: generate_tags(model, x))

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

# def tag_foods(df):


#     # Or use `os.getenv('GOOGLE_API_KEY')` to fetch an environment variable.
#     # GEMINI_API_KEY=os.getenv('GEMINI_API_KEY')
#     # GEMINI_API_KEY= os.environ.get("GEMINI_API_KEY")

#     genai.configure(api_key=Config.GEMINI_API_KEY)

#     print(f"Following models support content generation:")
#     for m in genai.list_models():
#         # print(model)
#         if 'generateContent' in m.supported_generation_methods:
#             print(f"- {m.name}")
#             # print(model.name)

#     # get all the ingredients from the dataframe
#     ingredient_lists = [json.loads(df.ingredients.values.tolist()[i])["ingredients"] for i in range(1, len(df))]
#     # ingredient_lists = [json.loads(df.ingredients.values.tolist()[i])["ingredients"] for i in range(len(df))]

#     # Merge all lists into a single list
#     ingredients = [item for sublist in ingredient_lists for item in sublist]

#     ingredients = ['4 pork chops', '1 pinch garlic salt', '1 tablespoon vegetable oil', '1 onion, chopped', '2 stalks chopped celery, with leaves', '12 ounces tomato paste', '1 (15 ounce) can tomato sauce', '3 cups water']
#     tag_foods_prompt = f"""Given the following list of ingredients from a recipe: ["vegan", "not_vegan", "dairy", "dairy_free", "meat", "no_meat", "contains_peanuts", "contains_nuts", "vegetarian", "sugar_free", "gluten-free", "has_gluten"], provide a list of food words. The model will label each food word with none, one, or more of the appropriate labels and return the food words as fields in a JSON document with the value of the field being a list of appropriate labels.
# Please label the following food words: {str(food_list2)}. Your response should only include the information between the curly braces:
# {{"food_name": [food categorie(s), unit]}}""" 

#     {
#         "pork", ["meat", "4 chops"],
#         "garlic salt" : ["spice", "1 pinch"],
#         "vegetable oil" : ["oil", "1 tablespoon"],
#         "onion" : ["vegetable", "1 chopped"],
#         "celery" : ["vegetable", "2 stalks"],
#         "tomato paste" : ["canned food", "12 ounces"],
#         "tomato sauce" : ["canned food", "1 can/15 ounces"],
#         "water" : ["water", "3 cups"],
#     }
#     input_prompt = """
#     You have to identify different types of foods in a list of ingredients. 
#     The system should accurately detect and label various foods in the list of ingredients, providing the name 
#     of the food. Additionally, 
#     the system should categorize the type of food (e.g., fruits, vegetables, grains, etc.) and extract any information about the units and/or quantities. 
#     The output should be a JSON formatted response with the JSON keys being the extracted food names, and the values being a list of length 2 containing the food category and the units and/or quantities strings.
#     """
#     ingredients = [json.loads(df.ingredients.values.tolist()[i])["ingredients"] for i in range(len(df))]

#     input_prompt = f"""
#     You have to identify different types of foods in a list of ingredients. 
#     The system should accurately detect and label various foods in a list of ingredients, providing the name 
#     of the food. Additionally, the system should categorize the type of food (e.g., fruits, vegetables, grains, etc.) and extract any information about the units and/or quantities. 
#     The output should be a JSON formatted response with the JSON keys being the extracted food names, and the values being a list of length 3 containing the food category and the units, and the quantity of units.
#     All of the values in the list are string and if a value is not present or can not be identified, use an empty string as a default value. 
#     If there are multiple units, create a nested list with an inner list for each of the units and quantities.  Your response should only include the information between the curly braces:
#     Input list of ingredients: {str(ingredients[0])}
#     Ouput: {{"pork", ["meat", "4" "chops"],
#     "garlic salt" : ["spice", "1" "pinch"],
#     "vegetable oil" : ["oil", "1" "tablespoon"],
#     "onion" : ["vegetable", "1",  "chopped"],
#     "celery" : ["vegetable", "2" "stalks"],
#     "tomato paste" : ["canned vegetable", "12" "ounces"],
#     "tomato sauce" : ["canned vegetable", [["1" "can"], ["15", "ounces"]],
#     "water" : ["water", "3" "cups"]
#     }}

#     Input list of ingredients: {str(ingredients[1])}
#     Ouput: 
#     """
#     input_prompt = f"""
#     You have to identify different types of foods in a list of ingredients.
#     The system should accurately detect and label various foods in a list of ingredients, providing the name
#     of the food. Additionally, the system should categorize the type of food (e.g., fruits, vegetables, grains, etc.) and extract any information about the units and/or quantities, and provide the numeric 0-indexed location of the element the food was extracted from in the input list.
#     The output should be a JSON formatted response with the following structure:
#     {{
#     "ingredient1" : {{"food_name1": ["food_category1", index, [["quantity_units1", "quantity_value1"], ["quantity_units2", "quantity_value2"]]]}},
#     "ingredient2" :{{"food_name2": ["food_category2", index, [["quantity_units1", "quantity_value1"]]]}},
#     ...
#     }}
#     All values in the list should be strings, and if a value is not present or cannot be identified, use an empty string as a default value.
#     If there are multiple units, create a nested list with an inner list for each unit and quantity. The output JSON string has to be a valid JSON that is parsable and does not contain errors.

#     For example, given the input list of ingredients:
#     [
#     '4 pork chops',
#     '1 pinch garlic salt',
#     '1 tablespoon vegetable oil',
#     '1 onion, chopped',
#     '2 stalks chopped celery, with leaves',
#     '12 ounces tomato paste',
#     '1 (15 ounce) can tomato sauce',
#     '3 cups water'
#     ]

#     The output should be:
#     {{
#     "pork chops": ["meat", 0, [["chops", "4"]]],
#     "garlic salt": ["spice", 1, [["pinch", "1"]]],
#     "vegetable oil": ["oil", 2, [["tablespoon", "1"]]],
#     "onion": ["vegetable", 3, [["chopped", "1"]]],
#     "celery": ["vegetable", 4, [["stalks", "2"]]],
#     "tomato paste": ["canned vegetable", 5, [["ounces", "12"]]],
#     "tomato sauce": ["canned vegetable", 6, [["can", "1"], ["ounces", "15"]]],
#     "water": ["water", 7, [["cups", "3"]]]
#     }}
#     Input list of ingredients: {str(ingredients[2])}
#     Ouput: 
#     """

#     # -----------------------------------
#     # ----- SIMPLE PROMPT ----
#     # Get ONLY the food name and category from the list of ingredients
#     # -----------------------------------

    # category_only_prompt = f"""
    # You have to identify different types of foods in a list of ingredients.
    # The system should accurately detect and label various foods in a list of ingredients, providing the name
    # of the food. Additionally, the system should categorize the type of food (e.g., fruits, vegetables, grains, etc.) and remove any information about the units and/or quantities.
    # The output should be a JSON formatted response with the following structure:
    # {{
    # "ingredient1" : ["food_name1", "food_category1"],
    # "ingredient2" : ["food_name2", "food_category2"],
    # "ingredient3 or ingredient4" : [
    #     ["food_name3", "food_category3"],
    #     ["food_name4", "food_category4"]
    #     ],
    # "ingredient5 (or use ingredient6)" : [
    #     ["food_name5", "food_category5"],
    #     ["food_name6", "food_category6"]
    #     ]    
    # ...
    # }}
    
    # All values in the list should be strings, and if a value is not present or cannot be identified, use an empty string as a default value.
    # If an ingredient specifies that there is a substitute for the ingredient then you should add another element to the ingredient's key value list for the substitute(s). 
    # (Substitute ingredient(s) may be detected when language like "or" is used in the ingredient, if a delimiter such as a "/" separates the ingredient, if a set of parentheses is used describing possible substitutes, etc.)
    # The output JSON string has to be a valid JSON that is parsable and does not contain errors.

    # For example, given the input list of ingredients:
    # [
    # "4 pork chops",
    # "1 pinch garlic salt",
    # "1 tablespoon vegetable oil",
    # "1 onion, chopped",
    # "2 stalks chopped celery, with leaves",
    # "12 ounces tomato paste",
    # "1 (15 ounce) can tomato sauce",
    # "3 cups water",
    # "Butter or margarine (about 1/2 cup)"
    # "3 eggs"
    # ]

    # The output should be:
    # {{
    # "4 pork chops" : ["pork chops", "meat"],
    # "1 pinch garlic salt": ["garlic salt", "spice"],
    # "1 tablespoon vegetable oil": ["vegetable oil", "oil"],
    # "1 onion, chopped": ["onion", "vegetable"],
    # "2 stalks chopped celery, with leaves": ["celery", "vegetable"],
    # "12 ounces tomato paste": ["tomato paste", "canned vegetable"],
    # "1 (15 ounce) can tomato sauce": ["tomato sauce", "canned vegetable"],
    # "3 cups water": ["water", "water"],
    # "Butter or margarine (about 1/2 cup)": [
    #     ["Butter", "dairy"],
    #     ["margarine", "dairy"]
    #     ],
    # "3 eggs": ["eggs", "meat"]
    # }}
    # Input list of ingredients: {str(list(set(ingredients)))}
    # Ouput: 
    # """

#     # -----------------------------------
#     # ----- 2nd BEST PROMPT SO FAR ----
#     # Get the food name, category, and units from the list of ingredients
#     # -----------------------------------
#     detailed_prompt = f"""
#     You have to identify different types of foods in a list of ingredients.
#     The system should accurately detect and label various foods in a list of ingredients, providing the name
#     of the food. Additionally, the system should categorize the type of food (e.g., fruits, vegetables, grains, etc.) and extract any information about the units and/or quantities.
#     The output should be a JSON formatted response with the following structure:
#     {{
#     "ingredient1" : {{"food_name1": ["food_category1", [["quantity_units1", "quantity_value1"], ["quantity_units2", "quantity_value2"]]]}},
#     "ingredient2" :{{"food_name2": ["food_category2", [["quantity_units1", "quantity_value1"]]]}},
#     ...
#     }}
    
#     All values in the list should be strings, and if a value is not present or cannot be identified, use an empty string as a default value.
#     If there are multiple units, create a nested list with an inner list for each unit and quantity. The output JSON string has to be a valid JSON that is parsable and does not contain errors.

#     For example, given the input list of ingredients:
#     [
#     '4 pork chops',
#     '1 pinch garlic salt',
#     '1 tablespoon vegetable oil',
#     '1 onion, chopped',
#     '2 stalks chopped celery, with leaves',
#     '12 ounces tomato paste',
#     '1 (15 ounce) can tomato sauce',
#     '3 cups water'
#     ]

#     The output should be:
#     {{
#     "4 pork chops" : {{"pork chops": ["meat", [["chops", "4"]]]}},
#     "1 pinch garlic salt": {{"garlic salt": ["spice", [["pinch", "1"]]]}},
#     "1 tablespoon vegetable oil": {{"vegetable oil": ["oil", [["tablespoon", "1"]]]}},
#     "1 onion, chopped": {{"onion": ["vegetable", [["chopped", "1"]]]}},
#     "2 stalks chopped celery, with leaves": {{"celery": ["vegetable", [["stalks", "2"]]]}},
#     "12 ounces tomato paste": {{"tomato paste": ["canned vegetable", [["ounces", "12"]]]}},
#     "1 (15 ounce) can tomato sauce": {{"tomato sauce": ["canned vegetable", [["can", "1"], ["ounces", "15"]]]}},
#     "3 cups water": {{"water": ["water", [["cups", "3"]]}}
#     }}
#     Input list of ingredients: {str(list(set(ingredients)))}
#     Ouput: 
#     """

#     # -----------------------------------
#     # ----- 1st BEST PROMPT SO FAR ----
#     # Get the food name, category, and units from the list of ingredients
#     # If there are substitutes, add them as another entry to the ingredient's key value list
#     # -----------------------------------

#     combine_details_prompt1 = f"""
#     You have to identify different types of foods in a list of ingredients.
#     The system should accurately detect and label various foods in a list of ingredients, providing the name
#     of the food. Additionally, the system should categorize the type of food (e.g., fruits, vegetables, grains, etc.) and extract any information about the units and/or quantities.
#     The output should be a JSON formatted response with the following structure:
#     {{
#     "ingredient1" : [["food_name1", "food_category1", ["quantity_and_units1A", "quantity_and_units1B"]]],
#     "ingredient2" : [["food_name2", "food_category2", ["quantity_and_units1A"]]],
#     "ingredient3 or ingredient4" : [
#         ["food_name3", "food_category3", ["quantity_and_units3A"]],
#         ["food_name4", "food_category4", ["quantity_and_units4A"]]
#         ],
#     "ingredient5 (or use ingredient6)" : [
#         ["food_name5", "food_category5", ["quantity_and_units5A"]],
#         ["food_name6", "food_category6", ["quantity_and_units6A"]]
#         ]    
#     ...
#     }}
    
#     All values in the list should be strings, and if a value is not present or cannot be identified, use an empty string as a default value.
#     If an ingredient specifies that there is a substitute for the ingredient then you should add another element to the ingredient's key value list for the substitute(s). 
#     (Substitute ingredient(s) may be detected when language like "or" is used in the ingredient, if a delimiter such as a "/" separates the ingredient, if a set of parentheses is used describing possible substitutes, etc.)
#     The output JSON string has to be a valid JSON that is parsable and does not contain errors.

#     For example, given the input list of ingredients:
#     [
#     "4 pork chops",
#     "1 pinch garlic salt",
#     "1 tablespoon vegetable oil",
#     "1 onion, chopped",
#     "2 stalks chopped celery, with leaves",
#     "12 ounces tomato paste",
#     "1 (15 ounce) can tomato sauce",
#     "3 cups water",
#     "Butter or margarine (about 1/2 cup)"
#     "3 eggs"
#     ]

#     The output should be:
#     {{
#     "4 pork chops" : [["pork chops", "meat", ["chops", "4"]]],
#     "1 pinch garlic salt": [["garlic salt", "spice", ["pinch", "1"]]],
#     "1 tablespoon vegetable oil": [["vegetable oil", "oil", ["tablespoon", "1"]]],
#     "1 onion, chopped": [["onion", "vegetable", ["chopped", "1"]]],
#     "2 stalks chopped celery, with leaves": [["celery", "vegetable", ["stalks", "2"]]],
#     "12 ounces tomato paste": [["tomato paste", "canned vegetable", ["ounces", "12"]]],
#     "1 (15 ounce) can tomato sauce": [["tomato sauce", "canned vegetable", [["can", "1"], ["ounces", "15"]]],
#     "3 cups water": [["water", "water", ["cups", "3"]]],
#     "Butter or margarine (about 1/2 cup)": [
#         ["Butter", "dairy", ["cup", "1/2"]],
#         ["margarine", "dairy", ["cup", "1/2"]]
#         ],
#     "3 eggs": [["eggs", "meat", ["eggs", "3"]]]
#     }}
#     Input list of ingredients: {str(list(set(ingredients)))}
#     Ouput: 
#     """

#     combine_details_prompt2 = f"""
#     You have to identify different types of foods in a list of ingredients.
#     The system should accurately detect and label various foods in a list of ingredients, providing the name
#     of the food. Additionally, the system should categorize the type of food (e.g., fruits, vegetables, grains, etc.) and extract any information about the units and/or quantities.
#     The output should be a JSON formatted response with the following structure:
#     {{
#     "ingredient1": [
#         {{
#         "food_name": "food_name1",
#         "food_category": "food_category1",
#         "quantity": [
#             "quantity_and_units1A",
#             "quantity_and_units1B"
#         ]
#         }}
#     ],
#     "ingredient2": [
#         {{
#         "food_name": "food_name2",
#         "food_category": "food_category2",
#         "quantity": [
#             "quantity_and_units2A"
#         ]
#         }}
#     ],
#     "ingredient3 or ingredient4": [
#         {{
#         "food_name": "food_name3",
#         "food_category": "food_category3",
#         "quantity": [
#             "quantity_and_units3A"
#         ]
#         }},
#         {{
#         "food_name": "food_name4",
#         "food_category": "food_category4",
#         "quantity": [
#             "quantity_and_units4A"
#         ]
#         }}
#     ],
#     "ingredient5 (or use ingredient6)": [
#         {{
#         "food_name": "food_name5",
#         "food_category": "food_category5",
#         "quantity": [
#             "quantity_and_units5A"
#         ]
#         }},
#         {{
#         "food_name": "food_name6",
#         "food_category": "food_category6",
#         "quantity": [
#             "quantity_and_units6A"
#         ]
#         }}
#     ],
#     ...
#     }}
    
#     All values in the list should be strings, and if a value is not present or cannot be identified, use an empty string as a default value.
#     If an ingredient specifies that there is a substitute for the ingredient then you should add another element to the ingredient's key value list for the substitute(s). 
#     (Substitute ingredient(s) may be detected when language like "or" is used in the ingredient, if a delimiter such as a "/" separates the ingredient, if a set of parentheses is used describing possible substitutes, etc.)
#     The output JSON string has to be a valid JSON that is parsable and does not contain errors.

#     For example, given the input list of ingredients:
#     [
#     "4 pork chops",
#     "1 pinch garlic salt",
#     "1 tablespoon vegetable oil",
#     "1 onion, chopped",
#     "2 stalks chopped celery, with leaves",
#     "12 ounces tomato paste",
#     "1 (15 ounce) can tomato sauce",
#     "3 cups water",
#     "Butter or margarine (about 1/2 cup)",
#     "3 eggs"
#     ]

#     The output should be:
#     {{
#     "4 pork chops": [
#         {{
#         "food_name": "pork chops",
#         "food_category": "meat",
#         "quantity": ["chops", "4"]
#         }}
#     ],
#     "1 pinch garlic salt": [
#         {{
#         "food_name": "garlic salt",
#         "food_category": "spice",
#         "quantity": ["pinch", "1"]
#         }}],
#     "1 tablespoon vegetable oil": [
#         {{
#         "food_name": "vegetable oil",
#         "food_category": "oil",
#         "quantity": ["tablespoon", "1"]
#         }}
#     ],
#     "1 onion, chopped": [
#         {{
#         "food_name": "onion",
#         "food_category": "vegetable",
#         "quantity": ["chopped", "1"]
#         }}
#     ],
#     "2 stalks chopped celery, with leaves": [
#         {{
#         "food_name": "celery",
#         "food_category": "vegetable",
#         "quantity": ["stalks", "2"]
#         }}
#     ],
#     "12 ounces tomato paste": [
#         {{
#         "food_name": "tomato paste",
#         "food_category": "canned vegetable",
#         "quantity": ["ounces", "12"]
#         }}
#     ],
#     "1 (15 ounce) can tomato sauce": [
#         {{
#         "food_name": "tomato sauce",
#         "food_category": "canned vegetable",
#         "quantity": [
#             {{"can": "1"}},
#             {{"ounces": "15"}}
#         ]
#         }}
#     ],
#     "3 cups water": [
#         {{
#         "food_name": "water",
#         "food_category": "water",
#         "quantity": ["cups", "3"]
#         }}
#     ],
#     "Butter or margarine (about 1/2 cup)": [
#         {{
#         "food_name": "Butter",
#         "food_category": "dairy",
#         "quantity": ["cup", "1/2"]
#         }},
#         {{
#         "food_name": "margarine",
#         "food_category": "dairy",
#         "quantity": ["cup", "1/2"]
#         }}
#     ],
#     "3 eggs": [
#         {{
#         "food_name": "eggs",
#         "food_category": "meat",
#         "quantity": ["eggs", "3"]
#         }}
#     ]
#     }}
#     Input list of ingredients: {str(list(set(ingredients)))}
#     Ouput: 
#     """

#     str(ingredients[0])
#     str(ingredients[2])

#     # str(ingredients[1])
#     import inspect
#     import time
    
#     print(f"Following models support content generation:")
#     for m in genai.list_models():
#         # print(model)
#         if 'generateContent' in m.supported_generation_methods:
#             print(f"- {m.name}")

#     pro_model = genai.GenerativeModel('gemini-1.0-pro')

#     promptResultsPro = {"prompt1": [], "prompt2": []}

#     promptPro1_fails = 0
#     promptPro2_fails = 0

#     for i in range(10):
#         print(f"Trying prompts for the {i}th time...")
#         print(f"- Prompt 1 fails: {promptPro1_fails}")
#         print(f"- Prompt 2 fails: {promptPro2_fails}")

#         time.sleep(2)
#         print(f"Generating content for prompt1...")
#         resp1 = pro_model.generate_content(combine_details_prompt1)
#         print(f"Content returned for prompt1...")
#         time.sleep(2)
#         print(f"Generating content for prompt2...")
#         resp2 = pro_model.generate_content(combine_details_prompt1.replace("\n", ""))
#         print(f"Content returned for prompt2...")
#         try:
#             json_data1 = json.loads(resp1.text)
#             print(f"Succesfully parsed JSON for --> prompt1")
#             is_failed1 = False
#         except Exception as e:
#             print(f"Exception: {e}")
#             print(f"----> FAILED TO PARSE JSON for prompt1")
#             json_data1 = "failed to parse JSON"
#             promptPro1_fails += 1
#             is_failed1 = True
        
#         try:
#             json_data2 = json.loads(resp2.text)
#             print(f"Succesfully parsed JSON for --> prompt2")
#             is_failed2 = False
#         except Exception as e:
#             print(f"Exception: {e}")
#             print(f"----> FAILED TO PARSE JSON for prompt2")
#             # print(f"resp2.text: {resp2.text}")
#             json_data2 = "failed to parse JSON"
#             promptPro2_fails += 1
#             is_failed2 = True

#         print(f"Adding results to promptResults...")

#         promptResultsPro["prompt1"].append([resp1.text, json_data1, promptPro1_fails, is_failed1])
#         promptResultsPro["prompt2"].append([resp2.text, json_data2, promptPro2_fails, is_failed2])

#     bad_resultsPro1 = [i for i in promptResultsPro["prompt1"] if i[1] == "failed to parse JSON"]

#     model = genai.GenerativeModel('gemini-pro')

#     promptResults = {"prompt1": [], "prompt2": []}

#     prompt1_fails = 0
#     prompt2_fails = 0

#     for i in range(10):
#         print(f"Trying prompts for the {i}th time...")
#         print(f"- Prompt 1 fails: {prompt1_fails}")
#         print(f"- Prompt 2 fails: {prompt2_fails}")

#         time.sleep(2)
#         print(f"Generating content for prompt1...")
#         resp1 = model.generate_content(combine_details_prompt1)
#         print(f"Content returned for prompt1...")
#         time.sleep(2)
#         print(f"Generating content for prompt2...")
#         resp2 = model.generate_content(combine_details_prompt1.replace("\n", ""))
#         print(f"Content returned for prompt2...")
#         try:
#             json_data1 = json.loads(resp1.text)
#             print(f"Succesfully parsed JSON for --> prompt1")
#             is_failed1 = False
#         except Exception as e:
#             print(f"Exception: {e}")
#             print(f"----> FAILED TO PARSE JSON for prompt1")
#             json_data1 = "failed to parse JSON"
#             prompt1_fails += 1
#             is_failed1 = True
        
#         try:
#             json_data2 = json.loads(resp2.text)
#             print(f"Succesfully parsed JSON for --> prompt2")
#             is_failed2 = False
#         except Exception as e:
#             print(f"Exception: {e}")
#             print(f"----> FAILED TO PARSE JSON for prompt2")
#             # print(f"resp2.text: {resp2.text}")
#             json_data2 = "failed to parse JSON"
#             prompt2_fails += 1
#             is_failed2 = True

#         print(f"Adding results to promptResults...")

#         promptResults["prompt1"].append([resp1.text, json_data1, prompt1_fails, is_failed1])
#         promptResults["prompt2"].append([resp2.text, json_data2, prompt2_fails, is_failed2])

#         print(f"=====" * 6)
#         print(f"=====" * 6)

    
#     past_fails = 0
#     bad_results = []
#     promptResults["prompt1"][5][1]

#     bad_results1 = [i for i in promptResults["prompt1"] if i[1] == "failed to parse JSON"]

#     json.loads(bad_results1[0][0].replace("\n", ""))

#     for i in range(len(promptResults["prompt1"])):
#         # print(f"prompt1: {i[0]}")
#         # print(f"prompt1: {i[1]}")
#         results = promptResults["prompt1"][i]
#         if results[2] > past_fails:
#             print(f"current fails is greater than past fails...")
#             print(f"results[2]: {results[2]}")
#             bad_results.append(results)
#             past_fails = results[2]

#         print(f"prompt1: {results[2]}")
#         print(f"past_fails: {past_fails}")
#         print(f"=====" * 6)
#         print(f"=====" * 6)

#     bad_result
#     # model.emperature
#     # mtemp = genai.get_model("models/gemini-pro")
#     # mtemp.temperature
    
#     combo_resp = model.generate_content(combine_details_prompt,
#             generation_config=genai.types.GenerationConfig(
#             candidate_count=1,
#             temperature=0.9
#             ))
    
#     combo_med_temp_resp = model.generate_content(
#         combine_details_prompt, 
#         generation_config=genai.types.GenerationConfig(
#             candidate_count=1,
#             temperature=0.5
#             )
#             )
    
#     combo_low_temp_resp = model.generate_content(
#         combine_details_prompt, 
#         generation_config=genai.types.GenerationConfig(
#             candidate_count=1,
#             temperature=0.1
#             )
#             )
    
#     cat_resp = model.generate_content(category_only_prompt)
#     cat_med_temp_resp = model.generate_content(
#         category_only_prompt,
#         generation_config=genai.types.GenerationConfig(
#             candidate_count=1,
#             temperature=0.5
#             )
#             )
    
#     cat_low_temp_resp = model.generate_content(
#         category_only_prompt,
#         generation_config=genai.types.GenerationConfig(
#             candidate_count=1,
#             temperature=0.1
#             )
#             )
#     combo_output = combo_resp.text
#     combo_med_temp_output = combo_med_temp_resp.text
#     combo_low_temp_output = combo_low_temp_resp.text
    
#     print(f"combo_output: {combo_output}")
#     print(f"combo_med_temp_output: {combo_med_temp_output}")
#     print(f"combo_low_temp_output: {combo_low_temp_output}")

#     high_temp = json.loads(combo_output)
#     med_temp = json.loads(combo_med_temp_output)
#     low_temp = json.loads(combo_low_temp_output)

#     for key in high_temp:
#         print(f"key: {key}")
#         print(f"high_temp[key]: {high_temp[key]}")
#         print(f"med_temp[key]: {med_temp[key]}")
#         print(f"low_temp[key]: {low_temp[key]}")
#         print(f"=====================")

#     cat_output = cat_resp.text
#     cat_med_temp_output = cat_med_temp_resp.text
#     cat_low_temp_output = cat_low_temp_resp.text

#     high_cat = json.loads(cat_output)
#     med_cat = json.loads(cat_med_temp_output)
#     low_cat = json.loads(cat_low_temp_output)


#     print(f"combo_output: {combo_output}")
#     print(f"cat_output: {cat_output}")
#     dir(model.generate_content)
#     inspect.signature(model.generate_content)
#     raw_output
#     raw_output.encode('utf-8')
#     # try:
#     json_data = json.loads(raw_output)

#     # loop through the keys in the json_data dictionary and match the keys to the ingredients list and create a new dictionary with the matched keys and their values
#     for key in json_data:
#         print(f"key: {key}")
#         print(f"json_data[key]: {json_data[key]}")
#         print(f"=====================")


#     # except Exception as e:

#     ingredients[2]
#     json_data.keys() in ingredients[2]
    
#     len([key for key in json_data if key in ingredients[2]])
#     len(ingredients[2])

#     for key in json_data:
#         print(f"key: {key}")

#         category = json_data[key][0]
#         index = json_data[key][1]
#         # print(f"json_data[key]: {json_data[key]}")
#         print(f"category: {category}")
#         print(f"index: {index}")
        
#         ingredients[2]

#         print(f"quantity_units: {json_data[key][2][0][0]}")
#         print(f"quantity_value: {json_data[key][2][0][1]}")
#         print(f"=====================")
#     ingredients[2]

#     raw_list = list(raw_output.replace("`", "").replace("\n", ""))
#     raw_list.pop(277)
#     len(raw_list)
#     "".join(raw_list)
#     json.loads(raw_output.replace("`", ""))

#     ingredients[1]
#     response_tags = model.generate_content(tag_foods_prompt)
#     response.text

#     tag_dict = json.loads(response_tags.text)

#     for key in tag_dict:
#         print(f"key: {key}")
#         print(f"tag_dict[key]: {tag_dict[key]}")
#     print(f"=====================")
#     food_categories = ["vegan",  "dairy_free", "no_meat", 
#                     "contains_peanuts", "contains_nuts",
#                         "vegetarian", "sugar_free", "gluten-free"]

#     ### PROMPT BELOW: #####

#     food_list = ["cherry tomatoes", "oatmeal", "tofu", "peas", "peanuts", "rice", "beans"]

