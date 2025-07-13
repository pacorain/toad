"""
Parse LINQ response
"""
def get_first(data, key, value):
    for item in data:
        if item[key] == value:
            return item
    raise ValueError(f'{key} not found in data')


lunch = get_first(data['FamilyMenuSessions'], 'ServingSession', 'Lunch')
days = lunch['MenuPlans'][0]['Days']

for day in days:
    menu = {}
    recipe_categories = day['MenuMeals'][0]['RecipeCategories']
    for category in recipe_categories:
        recipes = category['Recipes']
        menu[category['CategoryName']] = ', '.join([recipe['RecipeName'] for recipe in recipes])


    output[day['Date']] = menu