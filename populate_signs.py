import os
import django

# 1. Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fslearn_main.settings') 
django.setup()

from learning.models import Theme, Section, Word

# 2. The Data Structure
# Subsections are flattened into their main sections. Tagalog translations included.
SIGNS_DATA = {
    "THEME 1: KNOWING WHO WE ARE AND OUR FAMILIES": {
        "Basic Identity": [
            ("Me/I", "Ako"), ("You", "Ikaw"), ("Name", "Pangalan"),
            ("Child", "Bata"), ("Boy", "Lalaki"), ("Girl", "Babae")
        ],
        "Emotions": [
            ("Happy", "Masaya"), ("Sad", "Malungkot"), ("Angry", "Galit"),
            ("Scared", "Takot"), ("Love", "Mahal"), ("Joy", "Tuwa")
        ],
        "Family Members": [
            ("Family", "Pamilya"), ("Mother", "Nanay"), ("Father", "Tatay"),
            ("Big Sister", "Ate"), ("Big Brother", "Kuya"), ("Youngest", "Bunso"),
            ("Grandmother", "Lola"), ("Grandfather", "Lolo"), ("Aunt", "Tita"), ("Uncle", "Tito")
        ],
        "Physical Health & Body Parts": [
            ("Head", "Ulo"), ("Eyes", "Mata"), ("Nose", "Ilong"), ("Mouth", "Bibig"),
            ("Hands", "Kamay"), ("Feet", "Paa"), ("Heart", "Puso"), ("Healthy", "Malusog"),
            ("Clean", "Malinis"), ("Eat", "Kain"), ("Drink", "Inom"), ("Sleep", "Tulog")
        ],
        "Safety & Movement": [
            ("Safe", "Ligtas"), ("Be Careful", "Mag-ingat"), ("Help", "Tulong"),
            ("No/Don't", "Hindi/Huwag"), ("Walk", "Lakad"), ("Run", "Takbo"),
            ("Dance", "Sayaw"), ("Play", "Laro")
        ],
        "Similarities & Differences": [
            ("Same", "Pareho"), ("Different", "Magkaiba"), ("Big", "Malaki"),
            ("Small", "Maliit"), ("Old", "Luma"), ("New", "Bago")
        ],
        "Daily Activities & Social Skills": [
            ("How are you", "Kamusta"), ("Thank you", "Salamat"), ("Sorry", "Pasensya"),
            ("Hello", "Kumusta"), ("Goodbye", "Paalam")
        ]
    },
    "THEME 2: EXPLORING OUR COMMUNITY": {
        "Values & Character": [
            ("Discipline", "Disiplina"), ("Honesty/Truth", "Katapatan"), ("Respect", "Respeto"),
            ("Friendship", "Pagkakaibigan"), ("Care/Concern", "Malasakit"), ("Good", "Mabuti"),
            ("Correct/Right", "Tama")
        ],
        "Community Places & People": [
            ("Community", "Komunidad"), ("House", "Bahay"), ("School", "Paaralan"),
            ("Church", "Simbahan"), ("Hospital", "Ospital"), ("Store", "Tindahan"),
            ("Park", "Parke"), ("Street", "Kalsada"), ("Teacher", "Guro"), ("Police", "Pulis"),
            ("Doctor", "Doktor"), ("Firefighter", "Bumbero"), ("Vendor", "Tindero")
        ],
        "Transportation": [
            ("Car", "Kotse"), ("Bus", "Bus"), ("Jeep", "Jeep"), ("Bicycle", "Bisikleta"),
            ("Train", "Tren"), ("Motorcycle", "Motorsiklo"), ("Boat", "Bangka"),
            ("Ship", "Barko"), ("Airplane", "Eroplano"), ("Helicopter", "Helikopter")
        ],
        "Time Concepts": [
            ("Sunday", "Linggo"), ("Monday", "Lunes"), ("Tuesday", "Martes"),
            ("Wednesday", "Miyerkules"), ("Thursday", "Huwebes"), ("Friday", "Biyernes"),
            ("Saturday", "Sabado"), ("January", "Enero"), ("February", "Pebrero"),
            ("December", "Disyembre")
        ],
        "Colors & Shapes": [
            ("Color", "Kulay"), ("Red", "Pula"), ("Blue", "Asul"), ("Yellow", "Dilaw"),
            ("Green", "Berde"), ("Black", "Itim"), ("White", "Puti"), ("Shape", "Hugis"),
            ("Circle", "Bilog"), ("Square", "Parisukat"), ("Triangle", "Tatsulok")
        ],
        "Positions & Directions": [
            ("Inside", "Loob"), ("Outside", "Labas"), ("On top", "Ibabaw"), ("Under", "Ilalim"),
            ("Top", "Tuktok"), ("Bottom", "Baba"), ("Left", "Kaliwa"), ("Right", "Kanan"),
            ("Front", "Harap"), ("Back", "Likod")
        ],
        "Rules & Behavior": [
            ("Rules", "Panuntunan"), ("Follow", "Sunod"), ("Don't", "Huwag"),
            ("Allowed", "Pwede"), ("Forbidden", "Bawal"), ("Polite", "Magalang"),
            ("Quiet", "Tahimik"), ("Proper", "Wasto"), ("Careful", "Maingat")
        ],
        "Environmental Sounds & Objects": [
            ("Sound", "Tunog"), ("Dog bark", "Tahol ng aso"), ("Whistle", "Pito"),
            ("Song", "Kanta"), ("Noise", "Ingay"), ("Things/Objects", "Bagay"),
            ("Pencil", "Lapis"), ("Book", "Libro"), ("Ball", "Bola"), ("Toy", "Laruan")
        ],
        "Sequencing & Patterns": [
            ("First", "Una"), ("Second", "Pangalawa"), ("Last", "Huli"),
            ("Next", "Susunod"), ("Pattern", "Padron")
        ]
    },
    "THEME 3: EXPLORING OUR COMMUNITY": {
        "Country & National Identity": [
            ("Philippines", "Pilipinas"), ("Country", "Bansa"), ("Flag", "Watawat"),
            ("National Anthem", "Pambansang Awit"), ("Filipino", "Pilipino"),
            ("Patriotic", "Makabayan"), ("Love of Country", "Pagmamahal sa Bayan"),
            ("Culture", "Kultura"), ("Tradition", "Tradisyon"), ("Rice", "Bigas")
        ],
        "Natural Environment": [
            ("Mountain", "Bundok"), ("Ocean", "Karagatan"), ("Island", "Isla"),
            ("River", "Ilog"), ("Forest", "Gubat"), ("Waterfall", "Talon"),
            ("Flowers", "Bulaklak"), ("Tree", "Puno"), ("Sun", "Araw"), ("Rain", "Ulan"),
            ("Wind", "Hangin"), ("Typhoon", "Bagyo"), ("Hot", "Init"), ("Cold", "Lamig")
        ],
        "Philippine Money": [
            ("Money", "Pera"), ("Coins", "Barya"), ("Paper Money", "Papel na pera"),
            ("Peso", "Piso"), ("Payment", "Bayad"), ("Change", "Sukli"), ("Buy", "Bili"),
            ("1 Peso", "Piso"), ("5 Pesos", "Limang Piso"), ("10 Pesos", "Sampung Piso")
        ],
        "Mathematical Concepts": [
            ("Count", "Bilang"), ("Add/Plus", "Dagdag"), ("Subtract/Minus", "Bawas"),
            ("All/Total", "Lahat"), ("None/Zero", "Wala"), ("Many", "Marami"),
            ("Few", "Kaunti"), ("Stones", "Bato"), ("Leaves", "Dahon"), ("Sticks", "Patpat"),
            ("Seeds", "Buto"), ("Shells", "Kabibe")
        ],
        "Problem-Solving & Communication": [
            ("Conversation", "Usapan"), ("Listen", "Makinig"), ("Tell/Say", "Sabi"),
            ("Question", "Tanong"), ("Answer", "Sagot"), ("Solution", "Solusyon"),
            ("Problem", "Problema"), ("Think", "Isip"), ("Idea", "Ideya"),
            ("Plan", "Plano"), ("Make/Do", "Gawa")
        ],
        "Respect & Care for Country": [
            ("Take Care", "Alaga"), ("Clean", "Linis"), ("Throw Away", "Tapon"),
            ("Plant", "Tanim"), ("Water", "Dilig"), ("Protect", "Protekta"),
            ("Responsibility", "Responsibilidad"), ("Citizen", "Mamamayan"),
            ("Rights", "Karapatan"), ("Unity", "Pagkakaisa"), ("Peace", "Kapayapaan")
        ],
        "Filipino Heroes & History": [
            ("Hero", "Bayani"), ("Jose Rizal", "Jose Rizal"), ("Andres Bonifacio", "Andres Bonifacio"),
            ("Freedom", "Kalayaan"), ("History", "Kasaysayan"), ("Past", "Nakaraan"),
            ("Present", "Kasalukuyan"), ("Future", "Hinaharap")
        ]
    },
    "THEME 4: CARING FOR OUR WORLD": {
        "Environmental Beauty & Appreciation": [
            ("Nature", "Kalikasan"), ("Beautiful", "Maganda"), ("Beauty", "Ganda"),
            ("World", "Mundo"), ("Environment", "Kapaligiran"), ("Natural", "Likas"),
            ("Perfect", "Perpekto"), ("Art", "Sining"), ("Draw", "Guhit"),
            ("Color", "Kulay"), ("Design", "Disenyo"), ("Create", "Lika"),
            ("Imagination", "Imahinasyon"), ("Expression", "Ekspresyon")
        ],
        "Environmental Care & Protection": [
            ("Take Care", "Alaga"), ("Protect", "Protekta"), ("Guard/Protect", "Bantay"),
            ("Plant", "Tanim"), ("Water Plants", "Dilig"), ("Clean", "Linis"),
            ("Garbage/Trash", "Basura"), ("Dirt/Pollution", "Dumi"), ("Smoke", "Usok"),
            ("Pollution", "Polusyon"), ("Broken/Damaged", "Sira"), ("Bad/Harmful", "Masama"),
            ("Recycle", "Recycle"), ("Save/Conserve", "Tipid"), ("Don't Waste", "Huwag Sayangin"),
            ("Reuse", "Gamitin Ulit"), ("Reduce", "Bawasan")
        ],
        "Weather & Daily Observations": [
            ("Weather", "Panahon"), ("Sunny", "Maaraw"), ("Rain", "Ulan"), ("Clouds", "Ulap"),
            ("Lightning", "Kidlat"), ("Thunder", "Kulog"), ("Storm", "Bagyo"),
            ("Windy", "Mahangin"), ("Drizzle", "Ambon"), ("Temperature", "Temperatura"),
            ("Hot", "Mainit"), ("Cold", "Malamig"), ("Humid", "Maalinsangan"),
            ("Cool/Fresh", "Presko"), ("Icy", "Yelo"), ("Morning", "Umaga"),
            ("Noon", "Tanghali"), ("Afternoon", "Hapon"), ("Night", "Gabi"),
            ("Time", "Oras"), ("Daily", "Araw-araw")
        ],
        "Prediction & Observation": [
            ("Look/Observe", "Tingin"), ("Watch", "Nood"), ("Monitor", "Bantay"),
            ("Examine", "Suri"), ("Record", "Tala"), ("Predict", "Hula"),
            ("Will Happen", "Mangyayari"), ("Might/Could", "Baka"), ("Maybe", "Siguro"),
            ("Next", "Susunod"), ("Because", "Dahil"), ("Therefore", "Kaya"),
            ("Cause", "Sanhi"), ("Effect/Result", "Bunga"), ("If", "Kung"),
            ("When", "Kailan"), ("Happen", "Nangyari")
        ],
        "Feelings & Attitudes About Environment": [
            ("Pleased", "Nasiyahan"), ("Delighted", "Galak"), ("Entertained", "Naliw"),
            ("Amazed", "Namangha"), ("Inspired", "Inspirado"), ("Worried", "Nag-aalala"),
            ("Sad", "Malungkot"), ("Afraid", "Takot"), ("Angry", "Galit"), ("Hope", "Pag-asa")
        ],
        "Creative Expression Mediums": [
            ("Pencil", "Lapis"), ("Brush", "Pinsil"), ("Clay", "Putik"), ("Paper", "Papel"),
            ("Paint", "Pintura"), ("Scissors", "Gunting"), ("Song", "Kanta"),
            ("Dance", "Sayaw"), ("Poem", "Tula"), ("Story", "Kwento"), ("Theater", "Teatro")
        ]
    }
}

def run():
    print("Starting database population...")
    
    theme_order = 1
    for theme_title, sections in SIGNS_DATA.items():
        # Get or create Theme
        theme, t_created = Theme.objects.get_or_create(
            title=theme_title,
            defaults={"order": theme_order}
        )
        if t_created:
            print(f"\n[+] Created Theme: {theme.title}")
        theme_order += 1

        section_order = 1
        for section_title, words in sections.items():
            # Get or create Section
            section, s_created = Section.objects.get_or_create(
                theme=theme,
                title=section_title,
                defaults={"order": section_order}
            )
            if s_created:
                print(f"  [+] Created Section: {section.title}")
            section_order += 1

            word_order = 1
            for english, tagalog in words:
                # Format the description exactly as you asked
                word_desc = f"Tagalog: {tagalog}. Sign language instructions for '{english}'."
                
                # Get or create Word
                word, w_created = Word.objects.get_or_create(
                    section=section,
                    name=english,
                    defaults={
                        "description": word_desc,
                        "order": word_order
                    }
                )
                if w_created:
                    print(f"    [-] Created Word: {word.name} ({tagalog})")
                word_order += 1

    print("\nDatabase population complete. Check your Django Admin.")

if __name__ == "__main__":
    run()