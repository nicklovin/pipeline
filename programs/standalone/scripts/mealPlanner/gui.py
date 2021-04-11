from PySide2 import QtWidgets, QtCore, QtGui
# from functools import partial
from pprint import pprint, pformat

import mealPlanner
from pipeline.utils import data_formatting
from pipeline.utils import contexts
from pipeline.utils.widgets import baseWidgets as bsWidgets
from pipeline.utils.widgets import dynamicListWidgets as dyWidgets
from pipeline.utils.widgets import labeledWidgets as myWidgets
from pipeline.utils.widgets import dialogWidgets as dgWidgets

dialog = None
app = QtWidgets.QApplication([])

# TODO: Long term idea - make an icon/image window for selecting meals or foods
#   Involves a lot more setup, but excellent user experience

# TODO: May want to do food "variants" for future re-writes


def load_latest_items():
    return data_formatting.load_from_json(mealPlanner.ITEMS_PATH)


def load_latest_meals():
    return data_formatting.load_from_json(mealPlanner.MEALS_PATH)


def load_latest_calendar_meals():
    return data_formatting.load_from_json(mealPlanner.CALENDAR_PATH)


class MealPlanner(dgWidgets.WindowWidget):
    window_name = 'Meal Planner'

    food_categories = [
        'protein',
        'grain',
        'vegetable',
        'fruit',
        'dairy',
        'liquid',
        'oil',
        'condiment',
        'seasoning',
        'herbs',
        'dessert'
    ]

    meal_types = [
        'breakfast',
        'lunch',
        'dinner',
        'snack',
        'dessert'
    ]

    months = {
        1:  'January',
        2:  'February',
        3:  'March',
        4:  'April',
        5:  'May',
        6:  'June',
        7:  'July',
        8:  'August',
        9:  'September',
        10: 'October',
        11: 'November',
        12: 'December',
    }

    generated_items = {}
    generated_inventory = {}
    generated_meals = {}
    generated_calendar_meals = {}

    all_items = {}

    calendar_meals = {}

    # pop_up = DatePlanner()

    item_tab_width = 100
    inventory_tab_width = 100
    meal_tab_width = 150

    def __init__(self, parent=None, ss_path=r'C:\Users\Nick Love\Documents\coding\pipeline\programs\standalone\scripts\mealPlanner\test.qss'):
        super(MealPlanner, self).__init__(parent=parent)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle(self.window_name)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.setMinimumWidth(400)
        self.setMinimumHeight(400)

        # Optional Stylesheet for later work
        if ss_path:
            try:
                style_sheet_file = open(ss_path)
                self.setStyleSheet(style_sheet_file.read())
            except IOError:
                pass

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(1, 1, 1, 1)
        self.layout().setSpacing(5)

        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)

        self._set_defaults()

        self.main_widget_layout = QtWidgets.QHBoxLayout()
        main_widget.setLayout(self.main_widget_layout)

        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setTabPosition(self.tab_widget.North)
        self.main_widget_layout.addWidget(self.tab_widget)

        # Layouts per tab
        self.item_tab_layout = QtWidgets.QHBoxLayout()
        self.inventory_tab_layout = QtWidgets.QVBoxLayout()
        self.meal_tab_layout = QtWidgets.QVBoxLayout()
        self.calendar_tab_layout = QtWidgets.QVBoxLayout()

        self.build_item_tab()
        self.build_meal_tab()
        self.build_calendar_tab()

        self.setup_connections()

        # Inventory Tab -------------------------------------------------------------------------- #
        # inventory_tab = QtWidgets.QWidget()
        # self.tab_widget.addTab(inventory_tab, 'Inventory')
        # inventory_tab.setLayout(self.inventory_tab_layout)

        # \Inventory Tab ------------------------------------------------------------------------- #

        # self._update_display_label()

    def build_item_tab(self):
        # Item Tab ------------------------------------------------------------------------------- #
        self.item_tab = QtWidgets.QWidget()
        self.tab_widget.addTab(self.item_tab, 'Items')
        self.item_tab.setLayout(self.item_tab_layout)

        # Add Item
        self.add_item_widget = QtWidgets.QFrame()
        self.item_tab_layout.addWidget(self.add_item_widget)
        self.add_item_layout = QtWidgets.QVBoxLayout()
        self.add_item_layout.setContentsMargins(1, 1, 1, 1)
        self.add_item_widget.setLayout(self.add_item_layout)

        self.item_column_widget = bsWidgets.ColumnWidget(column_count=2, column_sizes=[0, 200])

        self.add_item_label = QtWidgets.QLabel('Add New Item')
        # self.add_item_label.setAttribute('editable', False)
        self.add_item_title = myWidgets.LabelLineEdit('Set Name', width=self.item_tab_width)
        self.add_item_category = myWidgets.LabelComboBox('Set Category', width=self.item_tab_width)
        self.add_item_category.addItems(self.food_categories)
        self.add_item_cost = myWidgets.LabelNumberEdit('Set Cost', regex='money',
                                                       width=self.item_tab_width)
        self.add_item_tags = myWidgets.LabelDynamicList('Set Tags', width=self.item_tab_width)
        self.create_item_button = QtWidgets.QPushButton('Create Item')

        self.item_column_widget.addWidget(self.add_item_label, 0)
        self.item_column_widget.addWidget(self.add_item_title, 0)
        self.item_column_widget.addWidget(self.add_item_category, 0)
        self.item_column_widget.addWidget(self.add_item_cost, 0)
        self.item_column_widget.addWidget(self.add_item_tags, 0)
        self.item_column_widget.addSpacerItem(
                QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Minimum,
                                      QtWidgets.QSizePolicy.Expanding),
                0
        )

        self.add_item_layout.addWidget(self.item_column_widget)
        self.add_item_layout.addWidget(self.create_item_button)

        # Temporary displays
        self.display_items = bsWidgets.FilteredList(filter_widget=self.add_item_title.line_edit)
        self.display_items.add_items(
                [title for title in load_latest_items().keys()]
        )
        self.item_column_widget.addWidget(self.display_items, 1)

        self.add_item_layout.addSpacerItem(
                QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Minimum,
                                      QtWidgets.QSizePolicy.Expanding)
        )

        self.horizontal_item_button_frame = QtWidgets.QFrame()
        self.horizontal_item_button_frame_layout = QtWidgets.QHBoxLayout()
        self.horizontal_item_button_frame.setLayout(self.horizontal_item_button_frame_layout)

        self.overwrite_item_checkbox = QtWidgets.QCheckBox('Overwrite')
        self.overwrite_item_checkbox.setChecked(False)
        self.write_items_button = QtWidgets.QPushButton('Write Items')

        self.horizontal_item_button_frame_layout.addWidget(self.overwrite_item_checkbox)
        self.horizontal_item_button_frame_layout.addWidget(self.write_items_button)
        self.add_item_layout.addWidget(self.horizontal_item_button_frame)


        # Edit Item
        # self.edit_item_widget = QtWidgets.QFrame()
        # self.item_tab_layout.addWidget(self.edit_item_widget)
        # self.edit_item_layout = QtWidgets.QVBoxLayout()
        # self.edit_item_widget.setLayout(self.edit_item_layout)
        #
        # sample_button2 = QtWidgets.QPushButton('Edit')
        # self.edit_item_layout.addWidget(sample_button2)

        # \Item Tab ------------------------------------------------------------------------------ #

    def build_meal_tab(self):
        # Meal Tab ------------------------------------------------------------------------------- #
        meal_tab = QtWidgets.QWidget()
        self.tab_widget.addTab(meal_tab, 'Meals')
        meal_tab.setLayout(self.meal_tab_layout)

        # Meal Item
        self.add_meal_widget = QtWidgets.QFrame()
        self.meal_tab_layout.addWidget(self.add_meal_widget)
        self.add_meal_layout = QtWidgets.QVBoxLayout()
        self.add_meal_layout.setContentsMargins(1, 1, 1, 1)
        self.add_meal_widget.setLayout(self.add_meal_layout)

        # self.add_meal_layout.addLayout(self.top_bar)
        # self.add_meal_layout.addLayout(self.column_layout)
        # self.add_meal_layout.addLayout(self.layout())

        self.meal_column_widget = bsWidgets.ColumnWidget(column_count=2)

        self.add_meal_label = QtWidgets.QLabel('New Meal')
        self.add_meal_title = myWidgets.LabelLineEdit('Set Name', width=65)
        self.add_meal_ingredients = myWidgets.LabelDynamicList(
                'Set Ingredients', input_type='options', input_options=mealPlanner.ITEMS,
                width=self.meal_tab_width)
        self.add_meal_substitutions = myWidgets.LabelDynamicList(
                'Set Substitutions (optional)', input_type='options',
                input_options=mealPlanner.ITEMS, width=self.meal_tab_width)
        self.add_meal_add_ons = myWidgets.LabelDynamicList(
                'Add-ons (optional)', input_type='options', input_options=mealPlanner.ITEMS,
                width=self.meal_tab_width)
        self.add_meal_type = myWidgets.LabelComboBox('Set Type', width=self.meal_tab_width)
        self.add_meal_type.addItems(self.meal_types)
        self.add_meal_author = myWidgets.LabelLineEdit('Author', width=65, default_text='Nick Love')
        self.add_meal_tags = myWidgets.LabelDynamicList('Set Tags', width=self.meal_tab_width)
        self.add_meal_recipe = myWidgets.LabelParagraphBox('Recipe', width=65)
        self.add_meal_prep_time = myWidgets.LabelNumberEdit('Prep Time', regex='int',
                                                            width=65)
        self.add_meal_cook_time = myWidgets.LabelNumberEdit('Cook Time', regex='int',
                                                            width=65)
        self.create_meal_button = QtWidgets.QPushButton('Create Meal')

        # Column setup
        self.meal_column_widget.addWidget(self.add_meal_title, 0)
        self.meal_column_widget.addWidget(self.add_meal_ingredients, 1)
        self.meal_column_widget.addWidget(self.add_meal_substitutions, 1)
        self.meal_column_widget.addWidget(self.add_meal_add_ons, 1)
        self.meal_column_widget.addWidget(self.add_meal_type, 1)
        self.meal_column_widget.addWidget(self.add_meal_author, 0)
        self.meal_column_widget.addWidget(self.add_meal_tags, 1)
        self.meal_column_widget.addWidget(self.add_meal_recipe, 0)
        self.meal_column_widget.addWidget(self.add_meal_prep_time, 0)
        self.meal_column_widget.addWidget(self.add_meal_cook_time, 0)

        self.add_meal_layout.addWidget(self.add_meal_label)
        self.add_meal_layout.addWidget(self.meal_column_widget)
        self.add_meal_layout.addWidget(self.create_meal_button)

        self.add_meal_layout.addSpacerItem(
                QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Minimum,
                                      QtWidgets.QSizePolicy.Expanding)
        )

        self.horizontal_meal_button_frame = QtWidgets.QFrame()
        self.horizontal_meal_button_frame_layout = QtWidgets.QHBoxLayout()
        self.horizontal_meal_button_frame.setLayout(self.horizontal_meal_button_frame_layout)

        self.overwrite_meal_checkbox = QtWidgets.QCheckBox('Overwrite')
        self.overwrite_meal_checkbox.setChecked(False)
        self.write_meals_button = QtWidgets.QPushButton('Write Meals')

        self.horizontal_meal_button_frame_layout.addWidget(self.overwrite_meal_checkbox)
        self.horizontal_meal_button_frame_layout.addWidget(self.write_meals_button)
        self.add_meal_layout.addWidget(self.horizontal_meal_button_frame)

        # \Meal Tab ------------------------------------------------------------------------------ #

    def build_calendar_tab(self):
        # Calendar Tab --------------------------------------------------------------------------- #

        calendar_tab = QtWidgets.QWidget()
        self.tab_widget.addTab(calendar_tab, 'Calendar')
        calendar_tab.setLayout(self.calendar_tab_layout)

        # Meal Item
        self.calendar_frame = QtWidgets.QFrame()
        self.calendar_tab_layout.addWidget(self.calendar_frame)
        self.calendar_layout = QtWidgets.QVBoxLayout()
        self.calendar_layout.setContentsMargins(1, 1, 1, 1)
        self.calendar_frame.setLayout(self.calendar_layout)

        self.calendar_radio_button = myWidgets.LabelRadioButtons(
                'Interaction Mode:', items=['view', 'add', 'edit'], default='view')

        self.calendar_label = QtWidgets.QLabel('A calendar')
        self.calendar_widget = QtWidgets.QCalendarWidget()
        self.fitted_calendar_widget = bsWidgets.AspectRatioWidget(self.calendar_widget)
        self.calendar_widget.setGridVisible(True)

        self.calendar_layout.addWidget(self.calendar_label)
        self.calendar_layout.addWidget(self.calendar_radio_button)
        self.calendar_layout.addWidget(self.fitted_calendar_widget)
        # self.calendar_layout.addSpacerItem(
        #     QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        # )

        # \Calendar Tab -------------------------------------------------------------------------- #

    def setup_connections(self):
        self.create_item_button.clicked.connect(self.create_item)
        self.write_items_button.clicked.connect(self.write_items_to_file)

        self.create_meal_button.clicked.connect(self.create_meal)
        self.write_meals_button.clicked.connect(self.write_meals_to_file)

        self.calendar_widget.clicked[QtCore.QDate].connect(self._click_calendar_date)

    def _clear_inputs(self, tab):
        if tab == 'items':
            self.add_item_title.clear()
            self.add_item_cost.clear()
            self.add_item_tags.clear()
            # self.add_item_category.set_value('protein')
        elif tab == 'meals':
            self.add_meal_title.clear()
            self.add_meal_ingredients.clear()
            self.add_meal_substitutions.clear()
            self.add_meal_add_ons.clear()
            # self.add_meal_type.set_value('breakfast')
            self.add_meal_tags.clear()
            self.add_meal_recipe.clear()
            self.add_meal_prep_time.clear()
            self.add_meal_cook_time.clear()
        else:
            raise NotImplementedError

    def _update_item_list(self):
        items = load_latest_items()
        self.all_items = items

    def create_item(self):
        title = self.add_item_title.get_value()
        category = self.add_item_category.get_value()
        cost = self.add_item_cost.get_value()
        if '.' in cost:
            cost = float(cost)
        else:
            cost = int(cost)
        tags = self.add_item_tags.get_values()
        item_info = {
            'category': category,
            'cost': cost,
            'tags': tags
        }

        new_item = mealPlanner.Item(title.title(), item_info)
        self.generated_items.update(new_item.get_info())

        self._clear_inputs(tab='items')
        self._update_item_list()

    def create_meal(self):
        title = self.add_meal_title.get_value()
        ingredients = self.add_meal_ingredients.get_values()
        substitutions = self.add_meal_substitutions.get_values()
        add_ons = self.add_meal_add_ons.get_values()
        meal_type = self.add_meal_type.get_value()
        author = self.add_meal_author.get_value()
        tags = self.add_meal_tags.get_values()
        recipe = self.add_meal_recipe.get_value()
        prep_time = self.add_meal_prep_time.get_value()
        cook_time = self.add_meal_cook_time.get_value()

        meal_info = {
            'ingredients': ingredients,
            'substitutions': substitutions,
            'add-ons': add_ons,
            'meal-type': meal_type,
            'author': author,
            'tags': tags,
            'recipe': recipe,
            'prep-time': prep_time,
            'cook-time': cook_time
        }

        new_meal = mealPlanner.Meal(title, meal_info)
        print(new_meal.get_info())
        self.generated_meals.update(new_meal.get_info())

        self._clear_inputs(tab='meals')

    def write_items_to_file(self):
        if not self.generated_items:
            return
        overwrite = self.overwrite_item_checkbox.isChecked()
        current_saved_items = load_latest_items()
        write_items = current_saved_items.copy()
        if not overwrite:
            if any([dup in self.generated_items.keys() for dup in current_saved_items.keys()]):
                if self.pop_up_question(
                        'Some of the items you are trying to commit conflict with pre-existing items.'
                        'Do you want to overwrite the current items?'):
                    current_saved_items.update(self.generated_items)
                else:
                    return
        write_items.update(self.generated_items)
        try:
            data_formatting.save_to_json(write_items, mealPlanner.ITEMS_PATH)
        except:
            data_formatting.save_backup_to_json(current_saved_items, mealPlanner.ITEMS_PATH)

        self.clear_generated_items()
        self._update_widget_settings()
        self._update_item_list()
        self._update_display_label()

        return self.pop_up_message('Your stored items have been updated!')

    def write_meals_to_file(self):
        if not self.generated_meals:
            raise
        overwrite = self.overwrite_meal_checkbox.isChecked()
        current_saved_meals = load_latest_meals()
        write_meals = current_saved_meals.copy()
        if not overwrite:
            if any([dup in self.generated_meals.keys() for dup in current_saved_meals.keys()]):
                if self.pop_up_question(
                        'Some of the items you are trying to commit conflict with pre-existing items.'
                        'Do you want to overwrite the current items?'):
                    current_saved_meals.update(self.generated_meals)
                else:
                    raise
        write_meals.update(self.generated_meals)
        try:
            data_formatting.save_to_json(write_meals, mealPlanner.MEALS_PATH)
        except:
            data_formatting.save_backup_to_json(current_saved_meals, mealPlanner.MEALS_PATH)

        self.clear_generated_items()
        self._update_widget_settings()

        return self.pop_up_message('Your stored meals have been updated!')

    def write_meal_to_calendar(self):
        if not self.generated_calendar_meals:
            raise
        current_saved_calendar = load_latest_calendar_meals()
        write_calendar = current_saved_calendar.copy()
        write_calendar.update(self.generated_calendar_meals)
        print(write_calendar)
        try:
            data_formatting.save_to_json(write_calendar, mealPlanner.CALENDAR_PATH)
        except:
            data_formatting.save_backup_to_json(current_saved_calendar, mealPlanner.CALENDAR_PATH)

        return self.pop_up_message('Meal Plan added to calendar date!')

    def _update_widget_settings(self):
        latest_items = load_latest_items().keys()
        self.add_meal_ingredients.dynamic_list.set_input_options(latest_items)
        self.add_meal_substitutions.dynamic_list.set_input_options(latest_items)
        self.add_meal_add_ons.dynamic_list.set_input_options(latest_items)

    def clear_generated_items(self):
        self.generated_items = {}

    def _click_calendar_date(self):
        date = self.calendar_widget.selectedDate()
        day = date.day()
        month = date.month()
        year = date.year()
        meal_key = '{}.{}.{}'.format(month, day, year)

        self.meal_plan_pop_up(meal_key)

        print(month, day)

    def _set_defaults(self):
        self.calendar_meals = load_latest_calendar_meals()
        self._update_item_list()

    def meal_plan_pop_up(self, date):
        print('popup')
        pop_up = DatePlanner.pop_up(self, date=date)

    def get_date_interaction_mode(self):
        return self.calendar_radio_button.get_value()


class OverwritePrompt(dgWidgets.CustomMessageBox):
    window_name = 'Overwrite {}'

    def build_ui(self):
        pass


class DatePlanner(dgWidgets.CustomMessageBox):
    window_name = 'Date Planner'

    def build_ui(self):
        calendar_info = load_latest_calendar_meals()

        self.date = self.options['date']
        self.daily_meal = calendar_info.get(self.date, {})

        month_number, day, year = self.date.split('.')
        month = self.parent_instance.months[int(month_number)]
        date_string = '{month} {day}, {year}'.format(
                month=month,
                day=day,
                year=year
        )

        header_widget = QtWidgets.QLabel(date_string)
        # header_widget.setReadOnly(True)
        header_font = QtGui.QFont()
        header_font.setPixelSize(24)
        header_font.setBold(True)
        header_widget.setFont(header_font)
        self.base_layout.addWidget(header_widget)

        ui_type = self.parent_instance.get_date_interaction_mode()

        # If no entry exists, user should add/create a plan
        if not self.daily_meal:
            ui_type = 'add'
        if ui_type == 'view':
            self.build_view_ui()
        elif ui_type == 'add':
            self.build_add_ui()
        elif ui_type == 'edit':
            self.build_edit_ui()
        else:
            raise NotImplementedError

    def build_view_ui(self):
        formatted_string = '''     
        Breakfast:
        \t{breakfast}

        Lunch:
        \t{lunch}

        Snack:
        \t{snack}

        Dinner:
        \t{dinner}

        Dessert:
        \t{dessert}
        '''.format(
            breakfast=self.daily_meal.get('breakfast', 'Nothing'),
            lunch=self.daily_meal.get('lunch', 'Nothing'),
            snack=self.daily_meal.get('snack', 'Nothing'),
            dinner=self.daily_meal.get('dinner', 'Nothing'),
            dessert=self.daily_meal.get('dessert', 'Nothing')
        )
        # Layouts per info
        display_text = QtWidgets.QPlainTextEdit(formatted_string)
        display_text.setReadOnly(True)
        buttons = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Close
        button_box = QtWidgets.QDialogButtonBox(buttons)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        self.base_layout.addWidget(display_text)
        self.base_layout.addWidget(button_box)

    def build_add_ui(self):
        self.breakfasts = ['Nothing']
        self.lunches = ['Nothing']
        self.snacks = ['Nothing']
        self.dinners = ['Nothing']
        self.desserts = ['Nothing']

        self.sort_meal_types()

        self.breakfast_combo = myWidgets.LabelComboBox('Breakfast')
        self.breakfast_combo.addItems(self.breakfasts)
        self.lunch_combo = myWidgets.LabelComboBox('Lunch')
        self.lunch_combo.addItems(self.lunches)
        self.snack_combo = myWidgets.LabelComboBox('Snack')
        self.snack_combo.addItems(self.snacks)
        self.dinner_combo = myWidgets.LabelComboBox('Dinner')
        self.dinner_combo.addItems(self.dinners)
        self.dessert_combo = myWidgets.LabelComboBox('Dessert')
        self.dessert_combo.addItems(self.desserts)

        # Set defaults
        if self.daily_meal:
            self.breakfast_combo.set_value(self.daily_meal.get('breakfast', 'Nothing'))
            self.lunch_combo.set_value(self.daily_meal.get('lunch', 'Nothing'))
            self.snack_combo.set_value(self.daily_meal.get('snack', 'Nothing'))
            self.dinner_combo.set_value(self.daily_meal.get('dinner', 'Nothing'))
            self.dessert_combo.set_value(self.daily_meal.get('dessert', 'Nothing'))

        self.base_layout.addWidget(self.breakfast_combo)
        self.base_layout.addWidget(self.lunch_combo)
        self.base_layout.addWidget(self.snack_combo)
        self.base_layout.addWidget(self.dinner_combo)
        self.base_layout.addWidget(self.dessert_combo)

        button_row = QtWidgets.QWidget()
        button_row_layout = QtWidgets.QHBoxLayout()
        button_row.setLayout(button_row_layout)

        apply_button = QtWidgets.QPushButton('Apply')
        save_button = QtWidgets.QPushButton('Apply & Save')
        close_button = QtWidgets.QPushButton('Close')

        button_row_layout.addWidget(apply_button)
        button_row_layout.addWidget(save_button)
        button_row_layout.addWidget(close_button)

        apply_button.clicked.connect(self.generate_meal)
        save_button.clicked.connect(self._generate_and_save_meal)
        close_button.clicked.connect(self.close)

        self.base_layout.addWidget(button_row)

    def generate_meal(self):
        self.parent_instance.generated_calendar_meals[self.date] = {}

        breakfast = self.breakfast_combo.get_value()
        lunch = self.lunch_combo.get_value()
        snack = self.snack_combo.get_value()
        dinner = self.dinner_combo.get_value()
        dessert = self.dessert_combo.get_value()

        self.parent_instance.generated_calendar_meals[self.date]['breakfast'] = breakfast
        self.parent_instance.generated_calendar_meals[self.date]['lunch'] = lunch
        self.parent_instance.generated_calendar_meals[self.date]['snack'] = snack
        self.parent_instance.generated_calendar_meals[self.date]['dinner'] = dinner
        self.parent_instance.generated_calendar_meals[self.date]['dessert'] = dessert

        for k, v in self.parent_instance.generated_calendar_meals.items():
            if v == 'Nothing':
                self.parent_instance.generated_calendar_meals.remove(k)

    def save_meal(self):
        self.parent_instance.write_meal_to_calendar()
        self.close()

    def _generate_and_save_meal(self):
        self.generate_meal()
        self.save_meal()

    def build_edit_ui(self):
        self.build_add_ui()

    def sort_meal_types(self):
        meals_info = load_latest_meals()
        for meal, contents in meals_info.items():
            meal_types = contents['meal-type']
            if isinstance(meal_types, str):
                # `Sample` meal is the only string
                continue
            if 'breakfast' in meal_types:
                self.breakfasts.append(meal)
            if 'lunch' in meal_types:
                self.lunches.append(meal)
            if 'snack' in meal_types:
                self.snacks.append(meal)
            if 'dinner' in meal_types:
                self.dinners.append(meal)
            if 'dessert' in meal_types:
                self.desserts.append(meal)


def main():
    global dialog
    if dialog is None:
        dialog = MealPlanner()
    dialog.show()
    app.exec_()


if __name__ == '__main__':
    main()
