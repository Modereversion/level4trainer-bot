# Helper functions
def get_user_language(user):
    return user.language if user.language else "en"

def get_welcome_text(lang: str = "en"):
    if lang == "ru":
        return (
            "👋 Добро пожаловать в LEVEL 4 Trainer!\n\n"
            "Здесь вы сможете:\n"
            "— Пройти обучение\n"
            "— Тренироваться с реальными вопросами\n"
            "— Подготовиться к экзамену ICAO\n"
            "— Работать с аварийными ситуациями\n\n"
            "Начните с выбора языка 👇"
        )
    return (
        "👋 Welcome to LEVEL 4 Trainer!\n\n"
        "Here you can:\n"
        "— Learn English grammar\n"
        "— Train with real ICAO questions\n"
        "— Prepare for the ICAO exam\n"
        "— Practice emergency communication\n\n"
        "Start by choosing your language 👇"
    )
