from mockhass import MockHomeAssistant


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
                                                    {"RecipeName": "Hole Milk"},
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
            "Milk": "Hole Milk, Void Flavored Milk",
        }
    }

    response = await hass.services.async_call(
        "python_script",
        "parse_school_lunch",
        service_data=mock_lunch_response,
        blocking=True,
        return_response=True,
    )
    assert response == expected_lunch


async def test_no_data_returns_empty_dict(hass):
    mock_lunch_response = {
        "FamilyMenuSessions": [{"ServingSession": "Lunch", "MenuPlans": [{"Days": []}]}]
    }
    response = await hass.services.async_call(
        "python_script",
        "parse_school_lunch",
        service_data=mock_lunch_response,
        blocking=True,
        return_response=True,
    )
    assert response == {}


async def test_school_lunch_event_updates_sensors(hass: MockHomeAssistant):
    event_data = {
        "daily_lunches": {
            "1/1/2040": {
                "Main Entree": "Roasted Nothing, Fried Air",
                "Sides": "Faux Fries, Imaginary Salad",
                "Milk": "Hole Milk, Void Flavored Milk",
            }
        },
        "first_date": "1/1/2040",
    }

    async with hass:
        hass.bus.async_fire("school_lunch_updated", event_data)
        await hass.async_block_till_done()
        hass.assert_entity("sensor.next_school_lunch_date").equals("1/1/2040")
        hass.assert_entity("sensor.next_school_lunch_entrees").equals(
            "Roasted Nothing, Fried Air"
        )
        hass.assert_entity("sensor.next_school_lunch_sides").equals(
            "Faux Fries, Imaginary Salad"
        )
