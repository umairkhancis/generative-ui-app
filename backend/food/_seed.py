"""Seed script: produces restaurants.csv and menu_items.csv in `food/db/`.

Run once to (re)populate the mock catalogue used by `backend/food/`:

    .venv/bin/python backend/food/_seed.py

Deterministic — uses a seeded RNG. Re-running overwrites the files.
"""

from __future__ import annotations

import csv
import random
from pathlib import Path
from typing import Any

DB_DIR = Path(__file__).resolve().parent / "db"
RESTAURANTS_CSV = DB_DIR / "restaurants.csv"
MENU_ITEMS_CSV = DB_DIR / "menu_items.csv"

_SEED = 42

# 10 cuisines × 5 restaurants = 50 restaurants. Per cuisine, a base dish pool
# (~25 dishes) that is expanded with modifier rounds to reach 50 items each.

_CUISINES: list[dict[str, Any]] = [
    {
        "name": "Lebanese",
        "restaurants": [
            "Operation Falafel", "Beirut Express", "Cedars Kitchen",
            "Zaatar w Zeit", "Levant House",
        ],
        "dishes": [
            ("Shawarma Wrap", "Marinated chicken, garlic sauce, pickles in saj bread", False, False),
            ("Beef Shawarma", "Spiced beef, tahini, tomato, parsley", False, False),
            ("Falafel Plate", "Crispy chickpea fritters with tahini and salad", True, False),
            ("Hummus", "Smooth chickpea dip with olive oil and warm pita", True, False),
            ("Moutabal", "Smoky grilled eggplant blended with tahini and lemon", True, False),
            ("Tabbouleh", "Parsley salad with bulgur, tomato, mint and lemon", True, False),
            ("Fattoush", "Crunchy fresh salad with sumac and toasted bread", True, False),
            ("Mixed Grill", "Skewers of shish taouk, kafta and lamb kebab", False, False),
            ("Shish Taouk", "Grilled chicken cubes marinated in garlic and yogurt", False, False),
            ("Kafta Skewer", "Minced lamb with parsley and onion, charcoal grilled", False, True),
            ("Manakish Zaatar", "Stone-baked flatbread with zaatar and olive oil", True, False),
            ("Manakish Cheese", "Stone-baked flatbread with akkawi cheese", True, False),
            ("Kibbeh", "Bulgur shells stuffed with spiced minced meat", False, False),
            ("Sambousek", "Crispy pastries filled with cheese or meat", False, False),
            ("Warak Enab", "Vine leaves stuffed with rice, tomato and herbs", True, False),
            ("Mujadara", "Lentils and rice topped with caramelised onions", True, False),
            ("Lamb Mandi", "Slow-cooked lamb on saffron rice", False, False),
            ("Chicken Mandi", "Smoky roasted chicken on aromatic rice", False, False),
            ("Mixed Mezze", "Chef's selection of cold and hot mezze", True, False),
            ("Baba Ghanouj", "Charred eggplant dip with pomegranate molasses", True, False),
            ("Knafeh", "Sweet cheese pastry soaked in rose syrup", True, False),
            ("Baklava", "Layered filo pastry with pistachio and honey", True, False),
            ("Atayef", "Stuffed pancakes with walnuts and syrup", True, False),
            ("Arabic Coffee", "Cardamom-spiced coffee, finely brewed", True, False),
            ("Fresh Lemonade", "Mint, lemon and ice", True, False),
        ],
    },
    {
        "name": "Italian",
        "restaurants": [
            "Pasta della Nonna", "Trattoria Roma", "Forno Napoli",
            "Olivocarne", "La Piazza",
        ],
        "dishes": [
            ("Margherita Pizza", "San Marzano tomato, fior di latte, basil", True, False),
            ("Pepperoni Pizza", "Tomato, mozzarella and spicy pepperoni", False, True),
            ("Quattro Formaggi", "Mozzarella, gorgonzola, parmesan, taleggio", True, False),
            ("Diavola Pizza", "Tomato, mozzarella, spicy salami, chilli", False, True),
            ("Funghi Pizza", "Mushroom medley with truffle oil", True, False),
            ("Spaghetti Carbonara", "Egg yolk, pecorino, guanciale, black pepper", False, False),
            ("Spaghetti Bolognese", "Slow-cooked beef and tomato ragu", False, False),
            ("Penne Arrabbiata", "Tomato, garlic, chilli, parsley", True, True),
            ("Lasagna al Forno", "Layered pasta with beef ragu and bechamel", False, False),
            ("Fettuccine Alfredo", "Butter, cream, parmesan, parsley", True, False),
            ("Tagliatelle Tartufo", "Black truffle, butter, parmesan", True, False),
            ("Ravioli Ricotta", "Stuffed pasta with spinach and ricotta", True, False),
            ("Gnocchi Sorrentina", "Potato dumplings with tomato and mozzarella", True, False),
            ("Risotto Funghi", "Creamy arborio rice with porcini mushrooms", True, False),
            ("Risotto Frutti di Mare", "Saffron rice with mixed seafood", False, False),
            ("Caprese Salad", "Buffalo mozzarella, tomato, basil, EVOO", True, False),
            ("Bruschetta", "Toasted bread, tomato, basil, garlic", True, False),
            ("Arancini", "Fried rice balls stuffed with ragu and mozzarella", False, False),
            ("Burrata Salad", "Burrata, heirloom tomato, rocket", True, False),
            ("Antipasto Misto", "Cured meats, cheeses, olives and pickles", False, False),
            ("Tiramisu", "Mascarpone, espresso-soaked savoiardi, cocoa", True, False),
            ("Panna Cotta", "Vanilla cream, berry compote", True, False),
            ("Cannoli", "Crispy shells filled with sweet ricotta and pistachio", True, False),
            ("Affogato", "Vanilla gelato drowned in hot espresso", True, False),
            ("Limoncello Spritz", "Limoncello, prosecco, soda", True, False),
        ],
    },
    {
        "name": "Burgers",
        "restaurants": [
            "Charburger Co.", "Smash & Stack", "Patty Lab",
            "Brew Burger House", "The Grindhouse",
        ],
        "dishes": [
            ("Classic Cheeseburger", "Beef patty, cheddar, lettuce, pickles, house sauce", False, False),
            ("Double Smash Burger", "Two smashed beef patties, American cheese, onion", False, False),
            ("Bacon BBQ Burger", "Beef, smoked bacon, BBQ sauce, crispy onions", False, False),
            ("Mushroom Swiss Burger", "Beef, sauteed mushrooms, swiss cheese", False, False),
            ("Spicy Jalapeno Burger", "Beef, pepper jack, jalapenos, chipotle mayo", False, True),
            ("Truffle Burger", "Beef, truffle aioli, gruyere, arugula", False, False),
            ("Buttermilk Chicken Burger", "Crispy chicken, slaw, pickles, ranch", False, False),
            ("Nashville Hot Chicken", "Spiced fried chicken, pickles, hot honey", False, True),
            ("Veggie Smash", "Black bean patty, avocado, smoked paprika mayo", True, False),
            ("Beyond Burger", "Plant-based patty, cheddar, secret sauce", True, False),
            ("Chili Cheese Fries", "Fries, beef chili, melted cheese, jalapenos", False, True),
            ("Loaded Fries", "Fries, cheese sauce, bacon, scallion", False, False),
            ("Sweet Potato Fries", "With chipotle aioli", True, False),
            ("Onion Rings", "Beer-battered, ranch dip", True, False),
            ("Crispy Wings", "Choice of buffalo, BBQ or garlic parm", False, True),
            ("Boneless Tenders", "Buttermilk-fried, honey mustard", False, False),
            ("Caesar Salad", "Romaine, parmesan, croutons, anchovy dressing", False, False),
            ("Coleslaw", "Creamy cabbage and carrot slaw", True, False),
            ("Mac & Cheese", "Three-cheese baked mac", True, False),
            ("Chicken Caesar Wrap", "Grilled chicken, romaine, parmesan", False, False),
            ("Chocolate Milkshake", "Hand-spun with dark chocolate", True, False),
            ("Vanilla Milkshake", "Madagascar vanilla bean", True, False),
            ("Strawberry Milkshake", "Fresh strawberries", True, False),
            ("Salted Caramel Shake", "Burnt caramel, sea salt", True, False),
            ("Brownie Sundae", "Warm brownie, vanilla ice cream, fudge", True, False),
        ],
    },
    {
        "name": "Indian",
        "restaurants": [
            "Bombay Brasserie", "Tandoor Express", "Curry Leaf",
            "Spice Route", "Punjab Grill",
        ],
        "dishes": [
            ("Butter Chicken", "Tandoori chicken in creamy tomato gravy", False, False),
            ("Chicken Tikka Masala", "Grilled chicken in spiced tomato cream sauce", False, True),
            ("Lamb Rogan Josh", "Slow-cooked lamb in Kashmiri chilli gravy", False, True),
            ("Palak Paneer", "Indian cheese in spiced spinach gravy", True, False),
            ("Paneer Tikka", "Grilled cottage cheese with bell peppers", True, False),
            ("Chana Masala", "Spiced chickpea curry", True, True),
            ("Dal Makhani", "Slow-cooked black lentils with cream", True, False),
            ("Dal Tadka", "Yellow lentils tempered with cumin and garlic", True, False),
            ("Aloo Gobi", "Potato and cauliflower with turmeric", True, False),
            ("Biryani Chicken", "Fragrant basmati with marinated chicken", False, True),
            ("Biryani Lamb", "Layered basmati rice with spiced lamb", False, True),
            ("Biryani Vegetable", "Mixed vegetable biryani with raita", True, False),
            ("Garlic Naan", "Tandoor-baked bread brushed with garlic butter", True, False),
            ("Butter Naan", "Soft flatbread brushed with ghee", True, False),
            ("Tandoori Roti", "Whole wheat flatbread from the tandoor", True, False),
            ("Samosa", "Crispy pastry with spiced potato and peas", True, False),
            ("Onion Bhaji", "Crispy onion fritters with chutney", True, False),
            ("Vegetable Pakora", "Mixed vegetable fritters", True, False),
            ("Chicken 65", "Fiery South Indian fried chicken", False, True),
            ("Tandoori Chicken", "Charred yogurt-marinated chicken", False, True),
            ("Mango Lassi", "Sweet yogurt drink with Alphonso mango", True, False),
            ("Masala Chai", "Spiced milk tea", True, False),
            ("Gulab Jamun", "Milk dumplings in rose syrup", True, False),
            ("Kheer", "Cardamom rice pudding with pistachio", True, False),
            ("Kulfi", "Traditional Indian ice cream with saffron", True, False),
        ],
    },
    {
        "name": "Chinese",
        "restaurants": [
            "Wok This Way", "Golden Dragon", "Lotus Garden",
            "Dim Sum House", "Szechuan Spice",
        ],
        "dishes": [
            ("Kung Pao Chicken", "Chicken, peanuts, dried chilli, Sichuan pepper", False, True),
            ("Sweet & Sour Chicken", "Crispy chicken, pineapple, bell pepper", False, False),
            ("General Tso's Chicken", "Crispy chicken in tangy sweet glaze", False, True),
            ("Beef in Black Bean Sauce", "Stir-fried beef with fermented black beans", False, False),
            ("Mongolian Beef", "Tender beef, scallion, sweet soy", False, False),
            ("Mapo Tofu", "Silken tofu in spicy Sichuan sauce", True, True),
            ("Yang Chow Fried Rice", "Egg, shrimp, char siu, peas", False, False),
            ("Vegetable Fried Rice", "Mixed vegetables, soy, scallion", True, False),
            ("Singapore Noodles", "Curry-spiced rice noodles, shrimp, char siu", False, True),
            ("Chow Mein", "Stir-fried egg noodles with vegetables", True, False),
            ("Lo Mein", "Soft noodles tossed in soy and sesame", True, False),
            ("Hot & Sour Soup", "Tofu, bamboo shoots, vinegar, white pepper", True, True),
            ("Wonton Soup", "Pork-shrimp wontons in clear broth", False, False),
            ("Egg Drop Soup", "Silky egg ribbons in chicken broth", False, False),
            ("Pork Dumplings", "Steamed jiao zi with ginger-soy", False, False),
            ("Vegetable Dumplings", "Steamed dumplings with garlic chive", True, False),
            ("Char Siu Bao", "Steamed buns with sweet BBQ pork", False, False),
            ("Spring Rolls", "Crispy rolls with vegetable filling", True, False),
            ("Salt & Pepper Squid", "Crispy squid with chilli and scallion", False, True),
            ("Honey Glazed Prawns", "Crispy prawns with honey-walnut sauce", False, False),
            ("Peking Duck Pancakes", "Crispy duck, hoisin, cucumber, scallion", False, False),
            ("Sesame Balls", "Glutinous rice balls with red bean paste", True, False),
            ("Mango Pudding", "Smooth mango pudding with cream", True, False),
            ("Bubble Tea", "Milk tea with tapioca pearls", True, False),
            ("Jasmine Tea", "Fragrant loose-leaf jasmine", True, False),
        ],
    },
    {
        "name": "Japanese",
        "restaurants": [
            "Sushi Sora", "Tonkotsu Bar", "Izakaya 81",
            "Ramen House", "Tokyo Bites",
        ],
        "dishes": [
            ("Salmon Sashimi", "Six slices of Atlantic salmon", False, False),
            ("Tuna Sashimi", "Six slices of yellowfin tuna", False, False),
            ("Salmon Nigiri", "Two pieces of salmon over seasoned rice", False, False),
            ("Tuna Nigiri", "Two pieces of tuna over seasoned rice", False, False),
            ("Shrimp Tempura Roll", "Crispy shrimp, avocado, cucumber", False, False),
            ("Spicy Tuna Roll", "Tuna, sriracha mayo, cucumber", False, True),
            ("Rainbow Roll", "California roll topped with assorted fish", False, False),
            ("Dragon Roll", "Eel, cucumber, avocado, eel sauce", False, False),
            ("Vegetable Roll", "Cucumber, avocado, carrot, pickled radish", True, False),
            ("Chicken Katsu Curry", "Crispy chicken cutlet with Japanese curry", False, False),
            ("Pork Tonkatsu", "Breaded pork cutlet, cabbage, tonkatsu sauce", False, False),
            ("Teriyaki Chicken", "Grilled chicken with teriyaki glaze", False, False),
            ("Beef Teriyaki", "Sliced beef with teriyaki sauce and rice", False, False),
            ("Tonkotsu Ramen", "Rich pork bone broth, chashu, ajitama", False, False),
            ("Shoyu Ramen", "Soy-based broth, bamboo, scallion", False, False),
            ("Miso Ramen", "Hearty miso broth, ground pork, corn", False, False),
            ("Spicy Tantanmen", "Spicy sesame miso broth ramen", False, True),
            ("Vegetable Ramen", "Mushroom dashi, tofu, vegetables", True, False),
            ("Edamame", "Salted soybean pods", True, False),
            ("Gyoza", "Pan-fried pork dumplings", False, False),
            ("Chicken Karaage", "Crispy fried marinated chicken", False, False),
            ("Miso Soup", "Tofu, wakame, scallion", True, False),
            ("Mochi Ice Cream", "Three pieces, mixed flavours", True, False),
            ("Matcha Cheesecake", "Japanese matcha-infused cheesecake", True, False),
            ("Ramune Soda", "Classic Japanese lemonade", True, False),
        ],
    },
    {
        "name": "Mexican",
        "restaurants": [
            "Taqueria del Sol", "Casa Tequila", "El Mariachi",
            "Burrito Brothers", "Pueblo Mexicano",
        ],
        "dishes": [
            ("Chicken Tacos", "Three soft tacos, salsa verde, cilantro", False, False),
            ("Carne Asada Tacos", "Grilled beef, onion, cilantro", False, False),
            ("Al Pastor Tacos", "Marinated pork, pineapple, cilantro", False, False),
            ("Fish Tacos", "Beer-battered fish, slaw, lime crema", False, False),
            ("Veggie Tacos", "Grilled vegetables, salsa, cotija", True, False),
            ("Chicken Burrito", "Rice, beans, cheese, salsa wrapped in flour tortilla", False, False),
            ("Beef Burrito", "Carne asada, rice, beans, guacamole", False, False),
            ("Bean Burrito", "Refried beans, rice, salsa, cheese", True, False),
            ("Burrito Bowl", "Rice, beans, protein, salsa, guacamole", False, False),
            ("Chicken Quesadilla", "Flour tortilla, chicken, cheese, pico", False, False),
            ("Cheese Quesadilla", "Three-cheese blend, charred tortilla", True, False),
            ("Steak Fajitas", "Sizzling steak with peppers and onions", False, False),
            ("Chicken Fajitas", "Marinated chicken with peppers and onions", False, False),
            ("Beef Enchiladas", "Tortillas with beef, mole sauce, queso", False, True),
            ("Cheese Enchiladas", "Tortillas rolled in red sauce with cheese", True, False),
            ("Chicken Tostadas", "Crispy tortilla, chicken, beans, salsa", False, False),
            ("Nachos Supreme", "Tortilla chips, beef, beans, cheese, jalapeno", False, True),
            ("Guacamole & Chips", "Hand-mashed avocado with lime", True, False),
            ("Pico de Gallo", "Fresh tomato, onion, cilantro, lime", True, False),
            ("Mexican Street Corn", "Elote with crema, cotija, chilli", True, True),
            ("Churros", "Cinnamon sugar dusted, chocolate sauce", True, False),
            ("Tres Leches Cake", "Sponge cake soaked in three milks", True, False),
            ("Flan", "Caramel custard with vanilla", True, False),
            ("Horchata", "Sweet rice milk with cinnamon", True, False),
            ("Jamaica Agua Fresca", "Hibiscus iced tea", True, False),
        ],
    },
    {
        "name": "Thai",
        "restaurants": [
            "Bangkok Bowl", "Thai Orchid", "Soi 38",
            "Lemongrass", "Pad Thai Co.",
        ],
        "dishes": [
            ("Pad Thai Chicken", "Rice noodles, chicken, peanuts, tamarind", False, False),
            ("Pad Thai Shrimp", "Rice noodles, shrimp, peanuts, lime", False, False),
            ("Pad Thai Vegetable", "Rice noodles, tofu, bean sprout, egg", True, False),
            ("Pad See Ew", "Wide noodles, soy, broccoli, egg", False, False),
            ("Drunken Noodles", "Wide noodles, basil, chilli, holy basil", False, True),
            ("Green Curry Chicken", "Coconut milk, green curry paste, basil", False, True),
            ("Red Curry Beef", "Red curry, bamboo shoots, basil", False, True),
            ("Massaman Curry", "Slow-cooked beef, potato, peanut, tamarind", False, False),
            ("Panang Curry", "Rich peanut curry with chicken", False, True),
            ("Yellow Curry Tofu", "Mild turmeric curry with tofu and potato", True, False),
            ("Tom Yum Soup", "Hot and sour soup with shrimp", False, True),
            ("Tom Kha Gai", "Coconut chicken soup with galangal", False, False),
            ("Som Tum", "Spicy green papaya salad with peanut", True, True),
            ("Larb Gai", "Spicy minced chicken salad with mint", False, True),
            ("Thai Beef Salad", "Grilled beef, mint, lime, chilli", False, True),
            ("Crispy Spring Rolls", "Vegetable filled, sweet chilli sauce", True, False),
            ("Chicken Satay", "Grilled skewers with peanut sauce", False, False),
            ("Fish Cakes", "Curried fish patties with cucumber relish", False, True),
            ("Thai Fried Rice", "Jasmine rice, egg, scallion, soy", False, False),
            ("Pineapple Fried Rice", "Fragrant rice with pineapple and cashew", False, False),
            ("Mango Sticky Rice", "Coconut sticky rice with ripe mango", True, False),
            ("Coconut Ice Cream", "Served in young coconut shell", True, False),
            ("Thai Iced Tea", "Black tea with condensed milk", True, False),
            ("Lemongrass Cooler", "Iced lemongrass, ginger and honey", True, False),
            ("Coconut Water", "Fresh young coconut", True, False),
        ],
    },
    {
        "name": "American Diner",
        "restaurants": [
            "Route 66 Diner", "Stacks & Cakes", "Big Sky Diner",
            "Sunny Side Up", "Liberty Grill",
        ],
        "dishes": [
            ("Buttermilk Pancakes", "Three fluffy pancakes, maple syrup, butter", True, False),
            ("Blueberry Pancakes", "Pancakes with wild blueberries", True, False),
            ("Chocolate Chip Pancakes", "Pancakes with melted chocolate", True, False),
            ("French Toast", "Brioche soaked in vanilla cream, syrup", True, False),
            ("Eggs Benedict", "Poached eggs, hollandaise, ham, English muffin", False, False),
            ("Avocado Toast", "Sourdough, smashed avocado, chilli flakes", True, True),
            ("Breakfast Burrito", "Egg, bacon, hash, cheese, salsa", False, False),
            ("Western Omelette", "Egg, ham, bell pepper, cheddar", False, False),
            ("Veggie Omelette", "Egg, mushroom, spinach, feta", True, False),
            ("Steak & Eggs", "Sirloin, sunny eggs, hash browns", False, False),
            ("Country Fried Steak", "Crispy steak, peppered gravy, biscuits", False, False),
            ("Reuben Sandwich", "Corned beef, swiss, sauerkraut, rye", False, False),
            ("Club Sandwich", "Turkey, bacon, lettuce, tomato, mayo", False, False),
            ("Grilled Cheese", "Three-cheese toasted sandwich", True, False),
            ("BLT", "Smoked bacon, lettuce, tomato, sourdough", False, False),
            ("Tuna Melt", "Tuna salad, cheddar, sourdough", False, False),
            ("Patty Melt", "Beef patty, swiss, caramelised onion, rye", False, False),
            ("Chicken & Waffles", "Buttermilk fried chicken, waffle, hot honey", False, True),
            ("Buffalo Wings", "Tossed in classic buffalo sauce", False, True),
            ("Mozzarella Sticks", "Crispy fried mozzarella with marinara", True, False),
            ("Apple Pie", "Warm cinnamon apple pie with ice cream", True, False),
            ("Cheesecake", "New York style with berry compote", True, False),
            ("Banana Split", "Three scoops, banana, cherry, nuts", True, False),
            ("Root Beer Float", "Classic A&W with vanilla ice cream", True, False),
            ("Cold Brew Coffee", "Slow-steeped 18 hours", True, False),
        ],
    },
    {
        "name": "Healthy",
        "restaurants": [
            "Green Bowl", "Kale & Co.", "The Salad Project",
            "Wholesome", "Roots & Greens",
        ],
        "dishes": [
            ("Cobb Salad", "Romaine, chicken, egg, avocado, bacon, blue cheese", False, False),
            ("Caesar Salad", "Romaine, parmesan, croutons, caesar dressing", False, False),
            ("Greek Salad", "Tomato, cucumber, olives, feta, oregano", True, False),
            ("Quinoa Power Bowl", "Quinoa, kale, roasted veg, tahini", True, False),
            ("Buddha Bowl", "Brown rice, edamame, avocado, sesame", True, False),
            ("Chicken Poke Bowl", "Sushi rice, chicken, avocado, edamame", False, False),
            ("Salmon Poke Bowl", "Sushi rice, salmon, mango, sesame", False, False),
            ("Tofu Poke Bowl", "Sushi rice, tofu, edamame, ginger", True, False),
            ("Acai Bowl", "Acai, granola, banana, berries, honey", True, False),
            ("Green Smoothie Bowl", "Spinach, banana, almond milk, granola", True, False),
            ("Grilled Chicken Wrap", "Whole wheat wrap, chicken, hummus, greens", False, False),
            ("Falafel Wrap", "Whole wheat wrap, falafel, tahini, salad", True, False),
            ("Salmon Salad", "Pan-seared salmon, mixed greens, citrus", False, False),
            ("Chicken Caesar Wrap", "Grilled chicken, romaine, parmesan", False, False),
            ("Turkey Avocado Sandwich", "Turkey, avocado, sourdough, sprouts", False, False),
            ("Vegan Beet Burger", "Beet patty, tahini, pickled onion", True, False),
            ("Cauliflower Steak", "Roasted cauliflower, chimichurri", True, False),
            ("Zucchini Noodles", "Zucchini, pesto, cherry tomato, parmesan", True, False),
            ("Lentil Soup", "Red lentil, carrot, lemon, cumin", True, False),
            ("Pumpkin Soup", "Roasted pumpkin, ginger, coconut", True, False),
            ("Avocado Toast", "Sourdough, smashed avocado, chilli", True, True),
            ("Chia Pudding", "Coconut chia, mango, granola", True, False),
            ("Energy Balls", "Date, oat, cacao, almond", True, False),
            ("Cold Pressed Juice", "Beet, apple, ginger, lemon", True, False),
            ("Matcha Latte", "Ceremonial grade matcha, oat milk", True, False),
        ],
    },
]

_MODIFIERS = [
    ("Classic ", ""),
    ("Signature ", " — house special"),
    ("Family ", " (sharing portion)"),
    ("Mini ", " (small)"),
    ("Chef's ", " (chef's pick)"),
]

_TAGS_POOL = [
    ["Top Eats"],
    ["Free delivery"],
    ["New on Talabat"],
    ["Top Eats", "Free delivery"],
    ["Halal"],
    [],
]


def _build_dataset() -> tuple[list[list[Any]], list[list[Any]]]:
    rng = random.Random(_SEED)
    rest_rows: list[list[Any]] = []
    item_rows: list[list[Any]] = []
    counter = 0

    for cuisine in _CUISINES:
        cuisine_name = cuisine["name"]
        for r_name in cuisine["restaurants"]:
            counter += 1
            rid = f"r-{counter:03d}"
            rating = round(rng.uniform(4.0, 4.9), 1)
            low = rng.choice([15, 20, 25, 30])
            delivery_time = f"{low}-{low + 10} min"
            fee_choice = rng.choice([0, 3, 5, 7, 10])
            delivery_fee = "Free" if fee_choice == 0 else f"AED {fee_choice}"
            tags = rng.choice(_TAGS_POOL)
            rest_rows.append([
                rid, r_name, cuisine_name, rating,
                delivery_time, delivery_fee, "|".join(tags),
            ])

            base_dishes = cuisine["dishes"]
            item_idx = 0
            for base in base_dishes:
                name, desc, is_veg, is_spicy = base
                item_rows.append([
                    f"{rid}-i-{item_idx:03d}", rid, r_name,
                    name, desc, f"AED {rng.randint(12, 95)}",
                    "true" if is_spicy else "false",
                    "true" if is_veg else "false",
                    "true" if rng.random() < 0.25 else "false",
                ])
                item_idx += 1

            mod_round = 0
            while item_idx < 50:
                base = base_dishes[mod_round % len(base_dishes)]
                prefix, suffix = _MODIFIERS[(mod_round // len(base_dishes)) % len(_MODIFIERS)]
                name, desc, is_veg, is_spicy = base
                if prefix == "" and suffix == "":
                    mod_round += 1
                    continue
                item_rows.append([
                    f"{rid}-i-{item_idx:03d}", rid, r_name,
                    f"{prefix}{name}".strip(), f"{desc}{suffix}",
                    f"AED {rng.randint(12, 95)}",
                    "true" if is_spicy else "false",
                    "true" if is_veg else "false",
                    "true" if rng.random() < 0.15 else "false",
                ])
                item_idx += 1
                mod_round += 1

    return rest_rows, item_rows


def main() -> None:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    rest_rows, item_rows = _build_dataset()

    with RESTAURANTS_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "cuisine", "rating",
                    "delivery_time", "delivery_fee", "tags"])
        w.writerows(rest_rows)

    with MENU_ITEMS_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "restaurant_id", "restaurant", "name",
                    "description", "price", "spicy", "vegetarian", "popular"])
        w.writerows(item_rows)

    print(f"Wrote {len(rest_rows)} restaurants → {RESTAURANTS_CSV}")
    print(f"Wrote {len(item_rows)} menu items → {MENU_ITEMS_CSV}")


if __name__ == "__main__":
    main()
