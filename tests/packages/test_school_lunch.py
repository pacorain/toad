async def test_parse_school_lunch(hass):
    mock_lunch_response = {
        "FamilyMenuSessions": [
            {
                "ServingSession": "Breakfast",
                "MenuPlans": [
                    {
                        "MenuPlanName": "BreakfastShouldNotBeIncluded",
                        "Days": [
                            {
                                "Date": "1/1/2040",
                                "MenuMeals": [
                                    {
                                        "MenuPlanName": "BreakfastShouldNotBeIncluded",
                                        "MenuMealName": "BreakfastShouldNotBeIncluded",
                                        "RecipeCategories": [
                                            {
                                                "CategoryName": "Main Entree",
                                                "Recipes": [
                                                    {
                                                        "RecipeName": "BreakfastShouldNotBeIncluded",
                                                    }
                                                ],
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    }
                ],
            },
            {
                "ServingSession": "Lunch",
                "MenuPlans": [
                    {
                        "MenuPlanName": "MenuPlanNameDoesntMatter",
                        "Days": [
                            {
                                "Date": "1/1/2040",
                                "MenuMeals": [
                                    {
                                        "MenuPlanName": "PlanNameDoesntMatter",
                                        "MenuMealName": "WeekNameDoesntMatter",
                                        "RecipeCategories": [
                                            {
                                                "CategoryName": "Main Entree",
                                                "Recipes": [
                                                    {"RecipeName": "Roasted Nothing"},
                                                    {"RecipeName": "Fried Air"},
                                                ],
                                            },
                                            {
                                                "CategoryName": "Sides",
                                                "Recipes": [
                                                    {"RecipeName": "Faux Fries"},
                                                    {"RecipeName": "Imaginary Salad"},
                                                ],
                                            },
                                            {
                                                "CategoryName": "Milk",
                                                "Recipes": [
                                                    {"RecipeName": "Unwhole Milk"},
                                                    {
                                                        "RecipeName": "Void Flavored Milk"
                                                    },
                                                ],
                                            },
                                        ],
                                    }
                                ],
                            }
                        ],
                    }
                ],
            },
        ]
    }

    expected_lunch = {
        "1/1/2040": {
            "Main Entree": "Roasted Nothing, Fried Air",
            "Sides": "Faux Fries, Imaginary Salad",
            "Milk": "Unwhole Milk, Void Flavored Milk",
        }
    }

    response = await hass.services.async_call("python_script", "parse_school_lunch", service_data=mock_lunch_response, blocking=True, return_response=True)
    assert response == expected_lunch
