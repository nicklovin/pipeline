import os
import sys

from pipeline.utils import data_formatting

# trash

ROOT = os.path.dirname(__file__)
ITEMS_PATH = os.path.join(ROOT, 'items.json')
MEALS_PATH = os.path.join(ROOT, 'meals.json')
CALENDAR_PATH = os.path.join(ROOT, 'currentCalendar.json')
ITEMS = data_formatting.load_from_json(ITEMS_PATH)
MEALS = data_formatting.load_from_json(MEALS_PATH)


class Item(object):
    """ It's a docstring n shit

    """
    category = None
    cost = None
    tags = []

    def __init__(self, name, info={}):
        self.name = name
        self.set_info(info)

    def __eq__(self, other):
        return self.name == other.name

    def set_info(self, info):
        self.category = info.get('category', None)
        self.cost = info.get('cost', None)
        self.tags = info.get('tags', [])

    def get_info(self):
        return {
            self.name: {
                'category': self.category,
                'cost': self.cost,
                'tags': self.tags
            }
        }


class Meal(object):
    title = ""

    ingredients = []
    substitutions = []
    add_ons = []
    category = ""
    author = ""
    tags = []
    recipe = ""

    def __init__(self, title, info={}):
        self.title = title
        self.set_info(info)

    def __repr__(self):
        return """
        Ingredients: {}
        Substitutions: {}
        Add-Ons: {}
        Meal Type: {}
        Author: {}
        Tags: {}
        Recipe: {}
        Prep Time: {}
        Cook Time: {}        
        """.format(
                self.ingredients,
                self.substitutions,
                self.add_ons,
                self.meal_type,
                self.author,
                self.tags,
                self.recipe,
                self.prep_time,
                self.cook_time,
        )

    def set_info(self, info):
        self.ingredients = info.get('ingredients')
        self.substitutions = info.get('substitutions')
        self.add_ons = info.get('add-ons')
        self.meal_type = info.get('meal-type')
        self.author = info.get('author')
        self.tags = info.get('tags')
        self.recipe = info.get('recipe')
        self.prep_time = info.get('prep-time')
        self.cook_time = info.get('cook-time')

        print(self.info)

    def get_info(self):
        return {
            self.title: {
                'ingredients': self.ingredients,
                'substitutions': self.substitutions,
                'add-ons': self.add_ons,
                'meal-type': self.meal_type,
                'author': self.author,
                'tags': self.tags,
                'recipe': self.recipe,
                'prep-time': self.prep_time,
                'cook-time': self.cook_time
            }
        }


class Inventory(object):
    inventory = {}
    default_filepath = os.path.join(ROOT, 'inventory.json')
    filepath = ''

    def __init__(self, filepath=''):
        inventory = json.load_from_json(filepath)
        self.filepath = filepath or self.default_filepath

    def get(self, item):
        return self.inventory[item]

    def add_item(self, item, update=True):
        if isinstance(item, dict):
            pass
        elif isinstance(item, Item):
            pass
        else:
            raise TypeError('Invalid input type for Inventory item.')

        if update:
            self.update_json_file()

    def update_json_file(self):
        json.save_to_json(self.inventory, self.default_filepath)

    def write_inventory_to_file(self, filepath):
        json.save_to_json(self.inventory, filepath)
