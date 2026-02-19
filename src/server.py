from flask import Flask, jsonify
import requests
import html
import re
from collections import OrderedDict
import copy

app = Flask(__name__)
pokemon_names = None

class PokemonDatabase():
    def __init__(self) -> None:
        self.pokemon_names_and_types = []
        self.pokemon_forms = []
        self.pokemon_array = []
        self.pokemon_lines = {}

        self.gen_bulba_url          = 'https://bulbapedia.bulbagarden.net/wiki/List_of_{}_Pok%C3%A9mon_names'
        self.fam_bulba_url          = 'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_evolutionary_line'

        self.images = [
            {"name": "home",        "url": "https://img.pokemondb.net/sprites/home/normal/{}.png"},
            # {"name": "home_shiny",  "url": "https://img.pokemondb.net/sprites/home/shiny/{}.png"},
            {"name": "go",          "url": "https://img.pokemondb.net/sprites/go/normal/{}.png"},
            # {"name": "go_shiny",    "url": "https://img.pokemondb.net/sprites/go/shiny/{}.png"},
        ]

        ## Test the REGEX on https://regex101.com/
        self.languages = [
            {'name': 'English',                 'searchregex': '\\(Pokémon\\)">(.{1,15})<\\/a><',   'code': 'EN'},
            # {'name': 'Japanese',                'searchregex': 'title="ja:(.{1,15})".*',            'code': 'JA'},
            # {'name': 'German',                  'searchregex': 'title="de:(.{1,15})".*',            'code': 'DE'},
            # {'name': 'French',                  'searchregex': 'title="fr:(.{1,15})".*',            'code': 'FR'},
            # {'name': 'Spanish',                 'searchregex': 'title="es:(.{1,15})".*',            'code': 'ES'},
            # {'name': 'Italian',                 'searchregex': 'title="it:(.{1,15})".*',            'code': 'IT'},
            # {'name': 'Korean',                  'searchregex': 'lang="ko">(.{1,15}).*',             'code': 'KO'},
            # {'name': 'Chinese',                 'searchregex': 'lang="zh-Hant">(.{1,15})',          'code': 'ZHT'},
            # {'name': 'Chinese',                 'searchregex': 'lang="zh-Hans">(.{1,15})<',         'code': 'ZHS'},
            # {'name': 'Brazilian_Portuguese',    'searchregex': 'lang="br">(.{1,15}).*',             'code': 'PT'},
            # {'name': 'Turkish',                 'searchregex': 'lang="tr">(.{1,15}).*',             'code': 'TR'},
            # {'name': 'Russian',                 'searchregex': 'lang="ru">(.{1,15}).*',             'code': 'RU'},
            # {'name': 'Thai',                    'searchregex': 'lang="th">(.{1,15}).*',             'code': 'TH'},
            # {'name': 'Hindi',                   'searchregex': 'lang="hi">(.{1,15}).*',             'code': 'HI'}
        ]

        for language in self.languages:
            self.initialize_pokemon_names_and_types(language)
        
        self.initialize_pokemon_lines()

        self.initialize_pokemon_forms()

        self.initalize_pokemon_array()

        self.inject_pokemon_images()

        self.inject_pokemon_regions()
        
        self.inject_go_keywords()

        self.inject_pokemon_lines()

    def inject_pokemon_lines(self) -> None:
        for pokemon in self.pokemon_array:
            for line_name in self.pokemon_lines:
                if pokemon["name_EN"] in self.pokemon_lines[line_name]:
                    pokemon["line"] = line_name
                    pokemon["family"] = copy.deepcopy(self.pokemon_lines[line_name])
    
    ## Tag Pokemon if they're one of the categories based on Pokemon GO's search phrase keywords
    ## https://leidwesen.github.io/SearchPhrases/
    def __get_pokemon_keywords(self, nat_dex_number: int) -> [str]:
        ## Specific catagories of Pokemon
        legendary_pokemon = [144, 145, 146, 150, 243, 244, 245, 249, 250, 377, 378, 379, 380, 381, 382, 383, 384, 480, 481, 482, 483, 484, 485, 486, 487, 488, \
            638, 639, 640, 641, 642, 643, 644, 645, 646, 716, 717, 718, 772, 773, 785, 786, 787, 788, 789, 790, 791, 792, 800, 888, 889, 890, 891, 892, 894, 895, \
                896, 897, 898, 905, 1001, 1002, 1003, 1004, 1007, 1008, 1014, 1015, 1016, 1017, 1024]
        mythical_pokemon = [151, 251, 385, 386, 489, 490, 491, 492, 493, 494, 647, 648, 649, 719, 720, 721, 801, 802, 807, 808, 809, 893, 1025]
        ultra_beasts = [793, 794, 795, 796, 797, 798, 799, 803, 804, 805, 806]
        paradox_pokemon = [984, 985, 986, 987, 988, 989, 1005, 1007, 1009, 1020, 1021, 990, 991, 992, 993, 994, 995, 1006, 1008, 1010, 1022, 1023]
        starter_pokemon = [1, 2, 3, 4, 5, 6, 7, 8 , 9, 25, 133, 152, 153, 154, 155, 156, 157, 158, 159, 160, 252, 253, 254, 255, 256, 257, 258, 259, 260, 387, 388, \
            389, 390, 391, 392, 393, 394, 395, 495, 496, 497, 498, 499, 500, 501, 502, 503, 650, 651, 652, 653, 654, 655, 656, 657, 658, 722, 723, 724, 725, 726, 727, \
                728,  729, 730, 810, 811, 812, 813, 814, 815, 816, 817, 818, 906, 907, 908, 909, 910, 911, 912, 913, 914]
        baby_pokemon = [172, 173, 174, 175, 236, 238, 239, 240, 298, 360, 406, 433, 438, 439, 440, 446, 447, 458, 848]
        fossil_pokemon = [138, 139, 140, 141, 142, 345, 346, 347, 348, 408, 409, 410, 564, 565, 566, 567, 696, 697, 698, 699, 880, 881, 882, 883]
        pseudo_legendary_pokemon = [147, 148, 149, 246, 247, 248, 371, 372, 373, 374, 375, 376, 443, 444, 445, 633, 634, 635, 704, 705, 706, 782, 783, 784, 885, 886, 887, 996, 997, 998]
        mega_evolution_pokemon = [3, 6, 9, 15, 18, 65, 80, 94, 115, 127, 130, 142, 150, 181, 208, 212, 214, 229, 248, 254, 257, 260, 282, 302, 303, 306, 308, 310, 319, 323, 334, 354, 359, 362, 373, 376, 380, 381, 384, 428, 445, 448, 460, 475, 531, 719]
        za_mega_evolution_pokemon = [26, 36, 71, 121, 149, 154, 160, 227, 358, 398, 478, 485, 491, 500, 530, 545, 560, 604, 609, 623, 652, 655, 658, 668, 670, 678, 687, 689, 691, 701, 718, 740, 768, 780, 801, 807, 870, 952, 970, 978, 998]
        gigantamax_pokemon = [3, 6, 9, 12, 25, 52, 68, 94, 99, 131, 133, 143, 569, 809, 812, 815, 818, 823, 826, 834, 839, 841, 842, 844, 849, 851, 858, 861, 869, 879, 884, 892]
        early_rodent_pokemon = [19, 20, 161, 162, 263, 264, 399, 400, 504, 505, 659, 660, 734, 735, 819, 820, 915, 916]
        early_bird_pokemon = [16, 17, 18, 21, 22, 163, 164, 276, 277, 278, 279, 396, 397, 398, 519, 520, 521, 661, 662, 663, 731, 732, 733, 821, 822, 823, 940, 941]
        early_bug_pokemon = [10, 11, 12, 13, 14, 15, 165, 166, 167, 168, 265, 266, 267, 268, 269, 401, 402, 540, 541, 542, 543, 544, 545, 664, 665, 666, 736, 737, 738, 824, 825, 826, 917, 918, 919, 920]
        pikaclone_pokemon = [25, 26, 172, 311, 312, 417, 587, 702, 777, 877, 921, 922, 923, 778, ]
        # https://www.serebii.net/pokemongo/exclusives.shtml
        regional_pokemon = [83, 115, 122, 128, 214, 222, 313,  314, 324, 335, 336, 337, 338, 357, 369, 417, 422, 423, 439, 441, 455, 480, 481, 482, 511, 512, 513, \
            514, 515, 516, 538 ,539, 550,  556, 561, 626, 631, 632, 669, 670, 671, 676, 701, 707, 741, 764, 797, 798, 805, 806, 978]

        resulting_keywords = []
        if (nat_dex_number in legendary_pokemon):
            resulting_keywords.extend(['legendary', 'legendaries'])
        if (nat_dex_number in mythical_pokemon):
            resulting_keywords.extend(['mythical', 'mythicals'])
        if (nat_dex_number in baby_pokemon):
            resulting_keywords.extend(['baby', 'babies', 'eggsonly', 'eggs only'])
        if (nat_dex_number in ultra_beasts):
            resulting_keywords.extend(['ultra beast', 'ultra beasts', 'ultrabeast'])
        if (nat_dex_number in paradox_pokemon):
            resulting_keywords.extend(['paradox', 'paradox pokemon', 'paradox pokémon'])
        if (nat_dex_number in starter_pokemon):
            resulting_keywords.extend(['starter', 'starters'])
        if (nat_dex_number in pseudo_legendary_pokemon):
            resulting_keywords.extend(['psuedo', 'psuedos', 'psuedo legendary'])
        if (nat_dex_number in fossil_pokemon):
            resulting_keywords.extend(['fossil', 'fossils'])
        if (nat_dex_number in mega_evolution_pokemon):
            resulting_keywords.extend(['mega', 'megas', 'mega evolution', 'mega evolve', 'can mega evolve'])
        if (nat_dex_number in za_mega_evolution_pokemon):
            resulting_keywords.extend(['mega', 'megas', 'mega evolution', 'mega evolve', 'can mega evolve'])
        if (nat_dex_number in gigantamax_pokemon):
            resulting_keywords.extend(['gigantamax', 'can gigantamax'])
        if (nat_dex_number in early_rodent_pokemon):
            resulting_keywords.extend(['early rodent', 'early game rodent', 'regional rodent', 'early rodents', 'early game rodents', 'regional rodents'])
        if (nat_dex_number in early_bird_pokemon):
            resulting_keywords.extend(['early bird', 'early game bird', 'regional bird', 'early birds', 'early game birds', 'regional birds'])
        if (nat_dex_number in early_bug_pokemon):
            resulting_keywords.extend(['early bug', 'early game bug', 'regional bug', 'early bugs', 'early game bugs', 'regional bugs'])
        if (nat_dex_number in pikaclone_pokemon):
            resulting_keywords.extend(['pikaclone', 'pika clone', 'pikaclones', 'pika clones'])
        if (nat_dex_number in regional_pokemon):
            resulting_keywords.extend(['regional', 'regionals', 'region exclusive'])
        
        return resulting_keywords

    def inject_go_keywords(self) -> None:
        for pokemon in self.pokemon_array:
            pokemon["keywords"] = self.__get_pokemon_keywords(pokemon["nat_dex_number"])

    def __get_pokemon_region(self, nat_dex_number: int) -> str:
        if (nat_dex_number >= 1 and nat_dex_number <= 151):
            return "kanto"
        elif (nat_dex_number >= 152 and nat_dex_number <= 251):
            return "johto"
        elif (nat_dex_number >= 252 and nat_dex_number <= 386):
            return "hoenn"
        elif (nat_dex_number >= 387 and nat_dex_number <= 493):
            return "sinnoh"
        elif (nat_dex_number >= 494 and nat_dex_number <= 649):
            return "unova"
        elif (nat_dex_number >= 650 and nat_dex_number <= 721):
            return "kalos"
        elif (nat_dex_number >= 722 and nat_dex_number <= 807):
            return "alola"
        elif (nat_dex_number >= 810 and nat_dex_number <= 898):
            return "galar"
        elif (nat_dex_number >= 899 and nat_dex_number <= 905):
            return "hisui"
        elif (nat_dex_number >= 906 and nat_dex_number <= 1025):
            return "paldea"
        else:
            return "unknown"

    def inject_pokemon_regions(self) -> None:
        region = None
        for pokemon in self.pokemon_array:
            if pokemon["is_orig_form"]:
                region = self.__get_pokemon_region(pokemon["nat_dex_number"])
            else:
                form_name = pokemon["form"]
                if "alolan" in form_name:
                    region = "alola"
                elif "galarian" in form_name:
                    region = "galar"
                elif "hisuian" in form_name:
                    region = "hisui"
                elif "paldea" in form_name:
                    region = "paldea"
                else: ## Hack to get around Megas that have regional forms (ex. Raichu)
                    region = self.__get_pokemon_region(pokemon["nat_dex_number"])
            pokemon["region_name"] = region

    def __has_new_types(self, form: dict) -> bool:
        return "typed_forms" in form

    def __is_dex_number_female_gigantamax_match(self, form: dict, nat_dex_number: int | None) -> bool:
        return nat_dex_number and (form["suffix"] == "f" or form["suffix"] == 'gigantamax') and nat_dex_number in form["members"] 

    def __is_dex_number_dex_match(self, form: dict, nat_dex_number: int) -> bool:
        return nat_dex_number in form["dex_number"]
    
    def __is_member_name_match(self, form: dict, EN_name_lower: bool) -> bool:
        return EN_name_lower in form["members"]

    def __is_regional_or_mega_form_search(self, form: str, nat_dex_number: int | None) -> bool:
        regions = ["alolan", "galarian", "hisuian", "paldean"]
        return nat_dex_number and "suffix" in form and (form["suffix"] in regions or "mega" in form["suffix"])

    def __find_forms(self, forms: list[dict], EN_name_lower: str, default_types: list[str] | None = None, nat_dex_number: int | None = None) -> list[dict]:
        additional_forms = []
        for form in forms:
            if self.__is_member_name_match(form, EN_name_lower) and self.__has_new_types(form):
                for typed_form in form["typed_forms"]:
                    additional_forms.append({
                        "name": "{0}-{1}".format(EN_name_lower, typed_form["suffix"]),
                        "types": typed_form["types"]
                    })
            elif self.__is_member_name_match(form, EN_name_lower) and not self.__has_new_types(form):
                for suffix in form["suffix"]:
                    additional_forms.append({
                        "name": "{0}-{1}".format(EN_name_lower, suffix),
                        "types": default_types
                    })
            elif self.__is_dex_number_female_gigantamax_match(form, nat_dex_number):
                additional_forms.append({
                    "name": "{0}-{1}".format(EN_name_lower, form["suffix"]),
                    "types": default_types
                })
            elif self.__is_regional_or_mega_form_search(form, nat_dex_number):
                for member in form["members"]:
                    if self.__is_dex_number_dex_match(member, nat_dex_number):
                        additional_forms.append({
                            "name": "{0}-{1}".format(EN_name_lower, form["suffix"]),
                            "types": member["types"]
                        })
            else:
                None
        return additional_forms 

    def inject_pokemon_images(self) -> None:
        for pokemon in self.pokemon_array:
            img_html = pokemon["form"]
            for img_type in self.images:
                pokemon["image_{0}".format(img_type["name"])] = img_type["url"].format(img_html)

    def initalize_pokemon_array(self) -> None:
        for i, pokemon in enumerate(self.pokemon_forms):
            pokemon_dict = copy.deepcopy(pokemon)
            pokemon_dict["form_id"] = i
            self.pokemon_array.append(pokemon_dict)

    def get_fully_named_forms(self, EN_name_lower: str, default_types: list[str]) -> list[dict]:
        ## TODO: Remember to think of 'search terms' vs 'forms'. None of the below can be searched.
        forms = [
            {"members": ["unown"], "suffix": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "qm", "em"]},
            {"members": ["deoxys"], "suffix": ["normal", "attack", "defense", "speed"]},
            {"members": ["burmy"], "suffix": ["plant", "sandy", "trash"]},
            {
                "members": ["wormadam"], "typed_forms": [
                    {"suffix": "plant", "types": ["bug", "grass"]}, 
                    {"suffix": "sandy", "types": ["bug", "ground"]},
                    {"suffix": "trash", "types": ["bug", "steel"]}
                ]
            },
            {"members": ["cherrim"], "suffix": ["overcast", "sunshine"]},
            {"members": ["shellos", "gastrodon"], "suffix": ["west-sea", "east-sea"]},
            {"members": ["giratina"], "suffix": ["altered"]},
            {"members": ["dialga", "palkia", "giritina"], "suffix": ["origin"]},
            {
                "members": ["shaymin"], "typed_forms": [
                    {"suffix": "land", "types": ["grass"]}, 
                    {"suffix": "sky", "types": ["grass", "flying"]}
                ]
            },
            {"members": ["basculin"], "suffix": ["red-striped", "blue-striped", "white-striped"]},
            {
                "members": ["darmanitan"], "typed_forms": [
                    {"suffix": "standard", "types": ["fire"]}, 
                    {"suffix": "zen", "types": ["fire", "psychic"]},
                    {"suffix": "galarian-standard", "types": ["ice"]},
                    {"suffix": "galarian-zen", "types": ["ice", "fire"]}
                ]
            },
            {"members": ["deerling", "sawsbuck"], "suffix": ["sprint", "summer", "autumn", "winter",]},
            {"members": ["thunderus", "tornadus", "landorus", "enamorus"], "suffix": ["incarnate", "therian"]},
            {"members": ["keldeo"], "suffix": ["ordinary", "resolute"]},
            {"members": ["vivillon"], "suffix": ["meadow", "icy-snow", "polar", "tundra", "continental", "garden", "elegant", "modern", "marine", "achipelago", "high-planes", "sandstorm", "river", "monsoon", "savanna", "sun", "ocean", "jungle", "fancy", "poke-ball"]},
            {"members": ["flabébé", "floette", "florges"], "suffix": ["red", "yellow", "orange", "blue", "white"]},
            {"members": ["floette"], "suffix": ["eternal"]}, ## TODO: double check this mega naming when it's out, is it floette-mega, or floette-eternal-mega?
            {"members": ["furfrou"], "suffix": ["natural", "heart", "star", "diamond", "debutante", "matron", "dandy", "la-reine", "kabuki", "pharoh"]},
            {"members": ["pumpkaboo", "gourgeist"], "suffix": ["medium", "small", "large", "jumbo"]},
            {"members": ["zygarde"], "suffix": ["50", "10", "complete"]},
            {
                "members": ["hoopa"], "typed_forms": [
                    {"suffix": "confined", "types": ["psychic", "ghost"]}, 
                    {"suffix": "unbound", "types": ["psychic", "dark"]}
                ]
            },
            {
                "members": ["oricorio"], "typed_forms": [
                    {"suffix": "baile", "types": ["fire", "flying"]}, 
                    {"suffix": "pom-pom", "types": ["electric", "flying"]},
                    {"suffix": "pau", "types": ["psychic", "flying"]},
                    {"suffix": "sensu", "types": ["ghost", "flying"]}
                ]
            },
            {"members": ["lycanroc"], "suffix": ["midday", "midnight", "dusk"]},
            {"members": ["minior"], "suffix": ["meteor", "red-core", "orange-core", "yellow-core", "green-core", "blue-core", "indigo-core", "violet-core"]},
            {"members": ["toxtricity"], "suffix": ["amped", "low-key"]},
            {
                "members": ["zacian"], "typed_forms": [
                    {"suffix": "hero", "types": ["fairy"]}, 
                    {"suffix": "crowned", "types": ["fairy", "steel"]}
                ]
            },
            {
                "members": ["zamazenta"], "typed_forms": [
                    {"suffix": "hero", "types": ["fighting"]}, 
                    {"suffix": "crowned", "types": ["fighting", "steel"]}
                ]
            },
            {
                "members": ["urshifu"], "typed_forms": [
                    {"suffix": "single-strike", "types": ["fighting", "dark"]}, 
                    {"suffix": "rapid-strike", "types": ["fighting", "water"]},
                    {"suffix": "single-strike-gigantamax", "types": ["fighting", "flying"]},
                    {"suffix": "rapid-strike-gigantamax", "types": ["fighting", "flying"]}
                ]
            },
            {"members": ["maushold"], "suffix": ["family4", "family3"]},
            {"members": ["squawkabilly"], "suffix": ["green-plumage", "blue-plumage", "yellow-plumage", "white-plumage"]},
            {"members": ["tatsugiri"], "suffix": ["curly", "droopy", "stretchy", "curly-mega", "droopy-mega", "stretchy-mega"]},
            {"members": ["dudunsparce"], "suffix": ["two-segment", "three-segment"]},
            {"members": ["gimmighoul"], "suffix": ["chest", "roaming"]},
            {"members": ["poltchageist", "sinistcha"], "suffix": ["artistan"]},
            {
                "members": ["ogerpon"], "typed_forms": [
                    {"suffix": "teal", "types": ["grass"]}, 
                    {"suffix": "cornerstone", "types": ["grass", "water"]},
                    {"suffix": "hearthflame", "types": ["grass", "fire"]},
                    {"suffix": "wellspring", "types": ["grass", "rock"]}
                ]
            },
            {"members": ["meowstic", "indeedee", "basculegion", "oinkologne"], "suffix": ["male", "female"]}, ## Hack since HOME considers these different forms
            ## GO exclusive
            {"members": ["spinda"], "suffix": ["01", "02", "03", "04", "05", "06", "07", "08", "09"]},
            ## Main line games/battle only forms
            {
                "members": ["meloetta"],  "typed_forms": [
                    {"suffix": "aria", "types": ["normal", "psychic"]}, 
                    {"suffix": "pirouette", "types": ["normal", "fighting"]},
                ]
            },
            # {"members": ["minior"], "suffix": ["meteor"]},
            ## Battle only forms Xerneas, Mimiyku, Porpeko, another Gmax Tox, Iceque, Eternamax, Stellar and Terastral, School, Gulping, Gorging, Hero, missing 7 forms...
        ]

        return self.__find_forms(forms, EN_name_lower, default_types)
    
    def get_post_base_named_forms(self, EN_name_lower: str, default_types: list[str]) -> list[dict]:
        ## All the Pokemon who don't have names for their 'default' forms
        forms = [
            {
                "members": ["tauros"], "typed_forms": [
                    {"suffix": "paldean-combat", "types": ["fighting"]},
                    {"suffix": "paldean-blaze", "types": ["fighting", "fire"]},
                    {"suffix": "paldean-aqua", "types": ["fighting", "water"]}
                ]
            },
            {
                "members": ["castform"], "typed_forms": [
                    {"suffix": "sunny", "types": ["fire"]},
                    {"suffix": "rainy", "types": ["water"]},
                    {"suffix": "snowy", "types": ["ice"]}
                ]
            },
            {
                "members": ["rotom"], "typed_forms": [
                    {"suffix": "heat", "types": ["electric", "fire"]},
                    {"suffix": "wash", "types": ["electric", "water"]},
                    {"suffix": "frost", "types": ["electric", "ice"]},
                    {"suffix": "fan", "types": ["electric", "flying"]},
                    {"suffix": "mow", "types": ["electric", "grass"]}
                ]
            },
            {"members": ["kyurem"], "suffix": ["white", "black"]},
            {"members": ["genesect"], "suffix": ["douse", "shock", "burn", "chill"]},
            {"members": ["greninja"], "suffix": ["ash"]},
            {"members": ["rockruff"], "suffix": ["own-tempo"]}, ## TODO: POGO is named 'Dusk'
            {
                "members": ["necrozma"], "typed_forms": [
                    {"suffix": "dusk-mane", "types": ["psychic", "steel"]},
                    {"suffix": "dawn-wings", "types":  ["psychic", "ghost"]},
                    {"suffix": "ultra", "types": ["psychic", "dragon"]}
                ]
            },
            {"members": ["magearna"], "suffix": ["original", "original-mega"]}, ## TODO: double check this mega naming when it's out
            {"members": ["sinistea", "polteageist"], "suffix": ["antique"]},
            {"members": ["zarude"], "suffix": ["dada"]},
            {
                "members": ["calyrex"], "typed_forms": [
                    {"suffix": "ice-rider", "types": ["psychic", "ice"]},
                    {"suffix": "shadow-rider", "types":  ["psychic", "ghost"]}
                ]
            },
            {"members": ["ursaluna"], "suffix": ["bloodmoon"]},
            ## Main line games exclusive
            # {"members": ["pikachu"], "suffix": ["original-cap", "hoenn-cap", "sinnoh-cap", "unova-cap", "kalos-cap", "alola-cap", "partner-cap", "world-cap"}
        ]

        return self.__find_forms(forms, EN_name_lower, default_types)

    def get_arceus_silvally_forms(self, EN_name_lower: str) -> list[dict]:
        types = ["normal", "fighting", "flying", "poison", "ground", "rock", "bug", "ghost", "steel", "fire", "water", "grass", "electric", "psychic", "ice", "dragon", "dark", "fairy"]

        arceus_silvally_forms = []
        for type in types:
            arceus_silvally_forms.append({
                "name": "{0}-{1}".format(EN_name_lower, type),
                "types": [type]
            })

        return arceus_silvally_forms

    def get_alcremie_forms(self) -> list[dict]:
        creams = ["vanilla-cream", "ruby-cream", "matcha-cream", "mint-cream", "lemon-cream", "salted-cream", "ruby-swirl", "caramel-swirl", "rainbow-swirl"]
        sweets = ["strawberry", "blueberry", "heart", "star", "clover", "flower", "ribbon"]

        alcremie_forms = []
        for cream in creams:
            for sweet in sweets:
                alcremie_forms.append({
                    "name": "alcremie-{0}-{1}".format(cream, sweet),
                    "types": ["fairy"]
                })

        return alcremie_forms

    def get_female_and_regional_forms(self, EN_name_lower: str, default_types: list[str], nat_dex_number: int) -> list[dict]:
        ## https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_with_gender_differences
        ## No Meowstic (678), Indeedee (876), Basculegion (902), Oinkologne (916) because HOME considers them different forms
        female_forms = {"suffix": "f", "members": [3, 12, 19, 20, 25, 26, 41, 42, 44, 45, 64, 65, 84, 85, 97, 111, 112, 118, 119, 123, 129, 130, 133, 154, \
            165, 166, 178, 185, 186, 190, 194, 195, 198, 202, 203, 207, 208, 212, 214, 215, 215, 217, 221, 224, 229, 232, 255, 256, 257, 267, 269, 272, 274, \
            275, 307, 308, 315, 316, 317, 322, 323, 332, 350, 369, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 407, 415, 417, 418, 419, 424, 443, 444, \
            445, 449, 450, 453, 454, 456, 457, 459, 460, 461, 464, 465, 473, 521, 592, 593, 668]}

        ## https://www.serebii.net/sunmoon/alolaforms.shtml
        alolan_forms = {
            "suffix": "alolan", 
            "members": [
                {"dex_number": [19, 20], "types": ["dark", "normal"]},
                {"dex_number": [26], "types": ["electric", "psychic"]},
                {"dex_number": [27, 28], "types": ["ice", "steel"]},
                {"dex_number": [37], "types": ["ice"]},
                {"dex_number": [38], "types": ["ice", "fairy"]},
                {"dex_number": [50, 51], "types": ["ground", "steel"]},
                {"dex_number": [52, 53], "types": ["dark"]},
                {"dex_number": [74, 75, 76], "types": ["rock", "electric"]},
                {"dex_number": [88, 89], "types": ["poison", "dark"]},
                {"dex_number": [103], "types": ["grass", "dragon"]},
                {"dex_number": [105], "types": ["fire", "ghost"]}
            ]
        }

        ## https://www.serebii.net/swordshield/galarianforms.shtml
        ## No Darmanitan (555) because it has forms
        galarian_forms = {
            "suffix": "galarian", 
            "members": [
                {"dex_number": [52], "types": ["steel"]},
                {"dex_number": [77], "types": ["psychic"]},
                {"dex_number": [78], "types": ["psychic", "fairy"]},
                {"dex_number": [79], "types": ["psychic"]},
                {"dex_number": [80], "types": ["poison", "psychic"]},
                {"dex_number": [83], "types": ["fighting"]},
                {"dex_number": [110], "types": ["poison", "fairy"]},
                {"dex_number": [122], "types": ["ice", "psychic"]},
                {"dex_number": [144], "types": ["psychic", "flying"]},
                {"dex_number": [145], "types": ["fighting", "flying"]},
                {"dex_number": [146], "types": ["dark", "flying"]},
                {"dex_number": [199], "types": ["poison", "psychic"]},
                {"dex_number": [222], "types": ["ghost"]},
                {"dex_number": [263, 264], "types": ["dark", "normal"]},
                {"dex_number": [554], "types": ["ice"]},
                {"dex_number": [562], "types": ["ground", "ghost"]},
                {"dex_number": [618], "types": ["ground", "steel"]}
            ]    
        }

        ## https://www.serebii.net/legendsarceus/hisuianforms.shtml
        hisuian_forms = {
            "suffix": "hisuian",
            "members": [
                {"dex_number": [58], "types": ["fire", "rock"]},
                {"dex_number": [100, 101], "types": ["electric", "grass"]},
                {"dex_number": [157], "types": ["fire", "ghost"]},
                {"dex_number": [211], "types": ["dark", "poison"]},
                {"dex_number": [215], "types": ["fighting", "poison"]},
                {"dex_number": [503], "types": ["water", "dark"]},
                {"dex_number": [549], "types": ["grass", "fighting"]},
                {"dex_number": [570, 571], "types": ["normal", "ghost"]},
                {"dex_number": [628], "types": ["psychic", "flying"]},
                {"dex_number": [705, 706], "types": ["steel", "dragon"]},
                {"dex_number": [713], "types": ["ice", "rock"]},
                {"dex_number": [724], "types": ["grass", "fighting"]},
            ]
        }

        ## https://www.serebii.net/scarletviolet/paldeanforms.shtml
        ## No Tauros (128) because it has forms
        paldean_forms = {
            "suffix": "paldean", 
            "members": [
                {"dex_number": [194], "types": ["poison", "ground"]},
            ]
        }

        forms = [
            female_forms,
            alolan_forms,
            galarian_forms,
            hisuian_forms,
            paldean_forms
        ]

        return self.__find_forms(forms, EN_name_lower, default_types, nat_dex_number)

    def get_gigantamax_forms(self, EN_name_lower: str, default_types: list[str], nat_dex_number: int) -> list[str]:
        ## https://www.serebii.net/swordshield/gigantamax.shtml
        ## No Urshifu (892) because it has forms
        gigantamax_forms_swsh = {"suffix": "gigantamax", "members": [3, 6, 9, 12, 25, 52, 68, 94, 99, 131, 133, 143, 569, 809, 812, 815, 818, 823, 826, \
                834, 839, 841, 842, 844, 849, 851, 858, 861, 869, 879, 884]}

        forms = [
            gigantamax_forms_swsh
        ]

        return self.__find_forms(forms, EN_name_lower, default_types, nat_dex_number)

    def get_mega_forms(self, EN_name_lower: str, nat_dex_number: int) -> list[str]:
        ## https://bulbapedia.bulbagarden.net/wiki/Mega_Evolution#Introduced_in_Pok%C3%A9mon_X_and_Y        
        mega_forms_xy = {
            "suffix": "mega",
            "members": [
                {"dex_number": [3], "types": ["grass", "poison"]},
                {"dex_number": [9], "types": ["water"]},
                {"dex_number": [65], "types": ["psychic"]},
                {"dex_number": [94], "types": ["ghost", "poison"]},
                {"dex_number": [115], "types": ["normal"]},
                {"dex_number": [127], "types": ["bug", "flying"]},
                {"dex_number": [130], "types": ["water", "dark"]},
                {"dex_number": [142], "types": ["rock", "flying"]},
                {"dex_number": [181], "types": ["electric", "dragon"]},
                {"dex_number": [212], "types": ["bug", "steel"]},
                {"dex_number": [214], "types": ["bug", "fighting"]},
                {"dex_number": [229], "types": ["dark", "fire"]},
                {"dex_number": [248], "types": ["rock", "dark"]},
                {"dex_number": [257], "types": ["fire", "fighting"]},
                {"dex_number": [282], "types": ["psychic", "fairy"]},
                {"dex_number": [303], "types": ["steel", "fairy"]},
                {"dex_number": [306], "types": ["steel"]},
                {"dex_number": [308], "types": ["fighting", "psychic"]},
                {"dex_number": [310], "types": ["electric"]},
                {"dex_number": [354], "types": ["ghost"]},
                {"dex_number": [359], "types": ["dark"]},
                {"dex_number": [380], "types": ["dragon", "psychic"]},
                {"dex_number": [381], "types": ["dragon", "psychic"]},
                {"dex_number": [445], "types": ["dragon", "ground"]},
                {"dex_number": [448], "types": ["fighting", "steel"]},
                {"dex_number": [460], "types": ["grass", "ice"]}
            ]
        }

        ## split off because img-search suffix is different
        mega_xy_x = {
            "suffix": "mega-x",
            "members": [
                {"dex_number": [6], "types": ["fire", "dragon"]},
                {"dex_number": [150], "types": ["psychic", "fighting"]}
            ]
        }

        mega_xy_y = {
            "suffix": "mega-y",
            "members": [
                {"dex_number": [6], "types": ["fire", "flying"]},
                {"dex_number": [150], "types": ["psychic"]}
            ]
        }

        ## https://bulbapedia.bulbagarden.net/wiki/Mega_Evolution#Introduced_in_Pok%C3%A9mon_Omega_Ruby_and_Alpha_Sapphire
        mega_forms_oras = {
            "suffix": "mega",
            "members": [
                {"dex_number": [15], "types": ["bug", "poison"]},
                {"dex_number": [18], "types": ["normal", "flying"]},
                {"dex_number": [80], "types": ["water", "psychic"]},
                {"dex_number": [208], "types": ["steel", "ground"]},
                {"dex_number": [254], "types": ["grass", "dragon"]},
                {"dex_number": [260], "types": ["water", "ground"]},
                {"dex_number": [302], "types": ["dark", "ghost"]},
                {"dex_number": [319], "types": ["water", "dark"]},
                {"dex_number": [323], "types": ["fire", "ground"]},
                {"dex_number": [334], "types": ["dragon", "fairy"]},
                {"dex_number": [362], "types": ["ice"]},
                {"dex_number": [373], "types": ["dragon", "flying"]},
                {"dex_number": [376], "types": ["steel", "psychic"]},
                {"dex_number": [384], "types": ["dragon", "flying"]},
                {"dex_number": [428], "types": ["normal", "fighting"]},
                {"dex_number": [475], "types": ["psychic", "fighting"]},
                {"dex_number": [531], "types": ["normal", "fairy"]},
                {"dex_number": [719], "types": ["rock", "fairy"]}
            ]
        }

        ## https://bulbapedia.bulbagarden.net/wiki/Primal_Reversion#Pok%C3%A9mon_capable_of_Primal_Reversion
        primal_reversion = {
            "suffix": "primal",
            "members": [
                {"dex_number": [382], "types": ["water"]},
                {"dex_number": [383], "types": ["ground", "fire"]}
            ]
        }

        ## https://bulbapedia.bulbagarden.net/wiki/Mega_Evolution#Introduced_in_Pok%C3%A9mon_Legends:_Z-A
        ## No Floeete (670) because it has a form
        mega_za = {
            "suffix": "mega",
            "members": [
                {"dex_number": [36], "types": ["fairy", "flying"]},
                {"dex_number": [71], "types": ["grass", "poison"]},
                {"dex_number": [121], "types": ["water", "psychic"]},
                {"dex_number": [149], "types": ["dragon", "flying"]},
                {"dex_number": [154], "types": ["grass", "fairy"]},
                {"dex_number": [160], "types": ["water", "dragon"]},
                {"dex_number": [227], "types": ["steel", "flying"]},
                {"dex_number": [478], "types": ["ice", "ghost"]},
                {"dex_number": [500], "types": ["fire", "fighting"]},
                {"dex_number": [530], "types": ["ground", "steel"]},
                {"dex_number": [545], "types": ["bug", "poison"]},
                {"dex_number": [560], "types": ["dark", "fighting"]},
                {"dex_number": [604], "types": ["electric"]},
                {"dex_number": [609], "types": ["ghost", "fire"]},
                {"dex_number": [652], "types": ["grass", "fighting"]},
                {"dex_number": [655], "types": ["fire", "psychic"]},
                {"dex_number": [658], "types": ["water", "dark"]},
                {"dex_number": [668], "types": ["fire", "normal"]},
                {"dex_number": [687], "types": ["dark", "psychic"]},
                {"dex_number": [689], "types": ["rock", "fighting"]},
                {"dex_number": [691], "types": ["poison", "dragon"]},
                {"dex_number": [701], "types": ["fighting", "flying"]},
                {"dex_number": [718], "types": ["dragon", "ground"]},
                {"dex_number": [780], "types": ["normal", "dragon"]},
                {"dex_number": [870], "types": ["fighting"]}
            ]
        }

        ## https://bulbapedia.bulbagarden.net/wiki/Mega_Evolution#Introduced_in_Mega_Dimension
        ## No Tatsugiri (978) because it has named forms
        mega_dim = {
            "suffix": "mega",
            "members": [
                {"dex_number": [358], "types": ["psychic", "steel"]},
                {"dex_number": [398], "types": ["fighting", "flying"]},
                {"dex_number": [485], "types": ["fire", "steel"]},
                {"dex_number": [491], "types": ["dark"]},
                {"dex_number": [623], "types": ["ground", "ghost"]},
                {"dex_number": [678], "types": ["psychic"]},
                {"dex_number": [740], "types": ["fighting", "ice"]},
                {"dex_number": [768], "types": ["bug", "steel"]},
                {"dex_number": [801], "types": ["steel", "fairy"]},
                {"dex_number": [807], "types": ["electric"]},
                {"dex_number": [952], "types": ["grass", "fire"]},
                {"dex_number": [970], "types": ["rock", "poison"]},
                {"dex_number": [998], "types": ["dragon", "ice"]}
            ]
        }

        ## split off because img-search suffix is different
        mega_dim_x = {
            "suffix": "mega-x",
            "members": [
                {"dex_number": [26], "types": ["electric"]}
            ]
        }

        mega_dim_y = {
            "suffix": "mega-y",
            "members": [
                {"dex_number": [26], "types": ["electric"]}
            ]
        }

        mega_dim_z = {
            "suffix": "mega-z",
            "members": [
                {"dex_number": [359], "types": ["dark", "ghost"]},
                {"dex_number": [445], "types": ["dragon"]},
                {"dex_number": [448], "types": ["fighting", "steel"]}
            ]
        }

        forms = [
            mega_forms_xy,
            mega_xy_x,
            mega_xy_y,
            mega_forms_oras,
            primal_reversion,
            mega_za,
            mega_dim,
            mega_dim_x,
            mega_dim_y,
            mega_dim_z
        ]

        return self.__find_forms(forms, EN_name_lower, None, nat_dex_number)
    
    def __add_forms(self, pokemon: object, addiontal_forms: list, flag_orig_form: bool = False) -> None:
        for i, form in enumerate(addiontal_forms):
            new_form = copy.deepcopy(pokemon)
            new_form["form"] = form["name"]
            new_form["types"] = form["types"]
            new_form["is_orig_form"] = False
            if flag_orig_form and i == 0:
                new_form["is_orig_form"] = True
            self.pokemon_forms.append(new_form)

    def initialize_pokemon_forms(self) -> None:
        for pokemon in self.pokemon_names_and_types:
            pokemon_name_EN_lower = pokemon['name_EN'].lower()
            pokemon_nat_dex_number = pokemon['nat_dex_number']
            pokemon_default_types = pokemon["types"]
        
            ## Fix Nidoran ♀
            if ("♀" in pokemon_name_EN_lower):
                pokemon_name_EN_lower = pokemon_name_EN_lower.replace("♀", "-f")
            ## Fix Nidoran ♂
            elif ("♂" in pokemon_name_EN_lower):
                pokemon_name_EN_lower = pokemon_name_EN_lower.replace("♂", "-m")
            ## Fix Farfetch'd
            elif ("\'" in pokemon_name_EN_lower):
                pokemon_name_EN_lower = pokemon_name_EN_lower.replace("\'", "")
            ## Fix Mr. Mime and Mr. Rime
            elif (". " in pokemon_name_EN_lower):
                pokemon_name_EN_lower = pokemon_name_EN_lower.replace(". ", "-")
            ## Fix Mime Jr.
            elif (" Jr." in pokemon_name_EN_lower):
                pokemon_name_EN_lower = pokemon_name_EN_lower.replace(" jr.", "-jr")
            ## Fix Flabébé
            elif ("é" in pokemon_name_EN_lower):
                pokemon_name_EN_lower = pokemon_name_EN_lower.replace("é", "e")
            ## Fix Type: Null
            elif (": " in pokemon_name_EN_lower):
                pokemon_name_EN_lower = pokemon_name_EN_lower.replace(": ", "-")   
            ## Fix Paradox Pokemon (ex: Roaring Moon)
            elif (" " in pokemon_name_EN_lower):
                pokemon_name_EN_lower = pokemon_name_EN_lower.replace(" ", "-")

            ## Initialize the 'form' structure w/ the default (useful in the IMG search)
            pokemon["form"] = pokemon_name_EN_lower
            pokemon["is_orig_form"] = True
            self.pokemon_forms.append(pokemon)

            ## Pokemon who have names for their 'default' forms
            named_specific_forms = self.get_fully_named_forms(pokemon_name_EN_lower, pokemon_default_types)
            ## Get rid of the last form on there, because it's going to be superceeded
            if len(named_specific_forms) > 0:
                self.pokemon_forms.pop()
            self.__add_forms(pokemon, named_specific_forms, flag_orig_form=True)

            ## Pokemon who DO NOT have names for their 'default' forms
            unnamed_specific_forms = self.get_post_base_named_forms(pokemon_name_EN_lower, pokemon_default_types)
            self.__add_forms(pokemon, unnamed_specific_forms)

            ## Special case for Arceus and Silvally since they have 18 forms
            if pokemon_name_EN_lower == 'arceus' or pokemon_name_EN_lower == 'silvally':
                arceus_silvally_forms = self.get_arceus_silvally_forms(pokemon_name_EN_lower)
                self.__add_forms(pokemon, arceus_silvally_forms, flag_orig_form=True)

            ## Special case for Alcremie since it has 63 forms
            if pokemon_name_EN_lower == "alcremie":
                alcremie_forms = self.get_alcremie_forms()
                self.__add_forms(pokemon, alcremie_forms, flag_orig_form=True)
    
            ## Grab all the non-specific forms
            female_and_regional_forms = self.get_female_and_regional_forms(pokemon_name_EN_lower, pokemon_default_types, pokemon_nat_dex_number)
            self.__add_forms(pokemon, female_and_regional_forms)

            gigantamax_forms = self.get_gigantamax_forms(pokemon_name_EN_lower, pokemon_default_types, pokemon_nat_dex_number)
            self.__add_forms(pokemon, gigantamax_forms)

            mega_forms = self.get_mega_forms(pokemon_name_EN_lower, pokemon_nat_dex_number)
            self.__add_forms(pokemon, mega_forms)

    def initialize_pokemon_lines(self) -> None:
        in_main_content = False

        line_html = requests.get(self.fam_bulba_url)
        line_html = html.unescape(line_html.text)
        line_html_lines = line_html.splitlines()

        current_pokemon_line = ''
        current_pokemon_line_set = set()

        for html_line in line_html_lines:
            ## If a match, you've found a new Pokemon line
            pokemon_line_re_match = re.findall(';\">(.{1,15}) line', html_line)
            ## If a match, you're scanning through the Pokemon's line
            pokemon_name_re_match = re.findall('title="(.{1,15}) \\(Pok', html_line)

            if pokemon_line_re_match:
                ## Add previous line to the dictionary
                if current_pokemon_line != '':
                    self.pokemon_lines[current_pokemon_line] = list(current_pokemon_line_set)
                    current_pokemon_line_set = set()
                current_pokemon_line = pokemon_line_re_match[0]
            if pokemon_name_re_match:
                pokemon_name = pokemon_name_re_match[0]
                if pokemon_name == "Bulbasaur":
                    in_main_content = True
                if in_main_content:
                    current_pokemon_line_set.add(pokemon_name)

    def initialize_pokemon_names_and_types(self, language: dict) -> None:
        ## Fetching the names for each Pokemon in each langauge
        pokemon_html = requests.get(self.gen_bulba_url.format(language['name']))
        pokemon_html = html.unescape(pokemon_html.text)
        ## Can potentially be truncated, like in Turkish where it's just Type: Null and Paradox Pokemon
        current_language_pokemon_list = []

        current_pokemon_number = -1
        current_pokemon_name = ''
        current_pokemon_types = []
        skip_types = False

        for line in pokemon_html.splitlines():
            pokemon_number = re.findall('monospace">#(\\d*).*', line)
            pokemon_name = re.findall(language['searchregex'], line)
            ## Only do the types regex finds in English. Save on computation
            pokemon_type = None
            if language['name'] == 'English':
                pokemon_type = re.findall('\\(type\\)" title="(.\\w{1,8}) \\(type\\)', line)

            ## While scanning you've found a Pokemon
            if pokemon_number:
                ## You found another Pokemon. Reset the variables. Extra check is in case the trivia (RU) has old names
                if current_pokemon_number != -1 and len(current_language_pokemon_list) < current_pokemon_number:
                    current_language_pokemon_list.append({"name": current_pokemon_name, "nat_dex_number": current_pokemon_number, 'types': current_pokemon_types})
                    current_pokemon_name = ''
                ## Set the number for the first Pokemon found and all subsequent ones AFTER a reset
                current_pokemon_number = int(pokemon_number[0])
            ## You found a name for that Pokemon a few lines down
            if pokemon_name:
                ## Keep this check, since some langauges have their regex match older names side by side in the table
                if current_pokemon_name == '':
                    current_pokemon_name = pokemon_name[0]
                    skip_types = False
                # You're on the same Pokemon but a different form (Regional, Legendary, etc.) Do not capture it's types
                else:
                    skip_types = True
            ## Capture the types only for the original form
            if pokemon_type and not skip_types:
                current_pokemon_types.append(pokemon_type[0].lower())

        ## Make sure the last Pokemon is added in too!
        current_language_pokemon_list.append({"name": current_pokemon_name, "nat_dex_number": current_pokemon_number, 'types': current_pokemon_types})

        for i in range(len(current_language_pokemon_list)):
            pokemon_name = current_language_pokemon_list[i]["name"]
            nat_dex_number = current_language_pokemon_list[i]["nat_dex_number"]
            ## Filter out duplicate types just in case
            english_types = list(set(current_language_pokemon_list[i]['types']))
            if language['name'] == 'English':
                pokemon_data = {
                    "nat_dex_number": nat_dex_number,
                    "name_EN": pokemon_name,
                    "types": ["type01", "type02"]
                }
                ## Set default to EN name since some langauges don't have proper translations
                for language_i in self.languages:
                    pokemon_data['name_{}'.format(language_i['code'])] = pokemon_name
                self.pokemon_names_and_types.append(pokemon_data)
            else:
                self.pokemon_names_and_types[nat_dex_number-1]['name_{}'.format(language['code'])] = pokemon_name

@app.route('/pokemon/', methods=['GET'])
def pokemon() -> list:
    resp = jsonify(pokemon_database.pokemon_array)
    resp.status_code = 200
    return resp

@app.route('/pokemon/names', methods=['GET'])
def pokemon_names() -> list:
    resp = jsonify(pokemon_database.pokemon_names)
    resp.status_code = 200
    return resp

@app.route('/pokemon/lines', methods=['GET'])
def pokemon_lines() -> list:
    resp = jsonify(pokemon_database.pokemon_lines)
    resp.status_code = 200
    return resp

@app.route('/pokemon/forms', methods=['GET'])
def pokemon_forms() -> list:
    resp = jsonify(pokemon_database.pokemon_forms)
    resp.status_code = 200
    return resp

if __name__ == "__main__":
    pokemon_database = PokemonDatabase()
    app.run()