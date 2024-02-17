import google.generativeai as genai
import os
import json
import re
import pandas as pd
import numpy as np 

from config import Config

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def remove_trailing_commas(json_like_string):
    # Define a regular expression pattern to match trailing commas
    pattern = r',(?=\s*[\]}])'

    # Replace any trailing commas with an empty string
    result = re.sub(pattern, '', json_like_string)

    return result

def make_prompt(ingredients_list):
    combine_details_prompt = f"""You have to identify different types of foods in a list of ingredients.
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

    return combine_details_prompt

# # function to extract food ingredients from a list of ingredients using the FoodModel
def ingredients_to_tags(ingredients_map, ingredient_list):
    # ingredients_map = json_response
    # ingredient_list = json.loads(df["ingredients"].values.tolist()[1])
    # ingredient_list = ingredient_list["ingredients"]

    food_tags = []

    tagged_foods = {i : ingredients_map[i][0][0] for i in ingredient_list}
    tagged_categories = {i : ingredients_map[i][0][1] for i in ingredient_list}
    tags_to_categories = {ingredients_map[i][0][0] : ingredients_map[i][0][1] for i in ingredient_list}
    tagged_quantities = {i : ingredients_map[i][0][2] for i in ingredient_list}

    # input = " ... ".join(ingredient_list)

    # model_output = model.extract_foods(input)

    # for food in model_output[0]["Ingredient"]:
    #     food_tags.append(food['text'].lower())
        
    # return food_tags
    # return json.dumps(food_tags)
    return tagged_foods, tagged_categories, tags_to_categories, tagged_quantities

def get_ingredient_predictions(df, gemini_api_key):

    genai.configure(api_key=gemini_api_key)

    # get all the ingredients from the dataframe
    ingredient_lists = [json.loads(df.ingredients.values.tolist()[i])["ingredients"] for i in range(1, len(df))]
    # ingredient_lists = [json.loads(df.ingredients.values.tolist()[i])["ingredients"] for i in range(len(df))]

    # Merge all lists into a single list
    ingredients = [item for sublist in ingredient_lists for item in sublist]

    # create a prompt for the model
    prompt = make_prompt(ingredients)

    model = genai.GenerativeModel('gemini-pro')
    
    # Get the model's response
    response = model.generate_content(prompt,
            generation_config=genai.types.GenerationConfig(
            candidate_count=1,
            temperature=1.0
            ))
    
    # Get the response as a string
    response_text = response.text
    # # tmp = 
    # response_text[-2]
    # resp_list = list(response_text)
    # resp_list.insert(-1, ', ')
    # resp_list = "".join(resp_list)
    # json.loads(resp_list)
    # remove_trailing_commas(resp_list)
    # json.loads(resp_list)
    # json.loads(response_text)

    # Remove trailing commas from the response
    json_response = json.loads(response_text)
    json.loads(df["ingredients"].values.tolist()[0])

    # df["ingredient_tags"] = df["ingredients"].apply(ast.literal_eval).apply(lambda x: generate_tags(model, x))

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

#     category_only_prompt = f"""
#     You have to identify different types of foods in a list of ingredients.
#     The system should accurately detect and label various foods in a list of ingredients, providing the name
#     of the food. Additionally, the system should categorize the type of food (e.g., fruits, vegetables, grains, etc.) and remove any information about the units and/or quantities.
#     The output should be a JSON formatted response with the following structure:
#     {{
#     "ingredient1" : ["food_name1", "food_category1"],
#     "ingredient2" : ["food_name2", "food_category2"],
#     "ingredient3 or ingredient4" : [
#         ["food_name3", "food_category3"],
#         ["food_name4", "food_category4"]
#         ],
#     "ingredient5 (or use ingredient6)" : [
#         ["food_name5", "food_category5"],
#         ["food_name6", "food_category6"]
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
#     "4 pork chops" : ["pork chops", "meat"],
#     "1 pinch garlic salt": ["garlic salt", "spice"],
#     "1 tablespoon vegetable oil": ["vegetable oil", "oil"],
#     "1 onion, chopped": ["onion", "vegetable"],
#     "2 stalks chopped celery, with leaves": ["celery", "vegetable"],
#     "12 ounces tomato paste": ["tomato paste", "canned vegetable"],
#     "1 (15 ounce) can tomato sauce": ["tomato sauce", "canned vegetable"],
#     "3 cups water": ["water", "water"],
#     "Butter or margarine (about 1/2 cup)": [
#         ["Butter", "dairy"],
#         ["margarine", "dairy"]
#         ],
#     "3 eggs": ["eggs", "meat"]
#     }}
#     Input list of ingredients: {str(list(set(ingredients)))}
#     Ouput: 
#     """

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

