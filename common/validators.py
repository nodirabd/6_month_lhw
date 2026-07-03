from datetime import date

from rest_framework.exceptions import ValidationError


def validate_product_creation_age(request):
    token = getattr(request, "auth", None)
    birthdate = None

    if token is None:
        raise ValidationError("Укажите дату рождения, чтобы создать продукт.")

    try:
        birthdate = token.get("birthdate")
    except Exception:
        try:
            birthdate = token["birthdate"]
        except Exception:
            birthdate = None

    if not birthdate:
        raise ValidationError("Укажите дату рождения, чтобы создать продукт.")

    if isinstance(birthdate, str):
        try:
            birthdate = date.fromisoformat(birthdate)
        except ValueError:
            raise ValidationError("Неверный формат даты рождения.")

    if not isinstance(birthdate, date):
        raise ValidationError("Укажите дату рождения, чтобы создать продукт.")

    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

    if age < 18:
        raise ValidationError("Вам должно быть 18 лет, чтобы создать продукт.")

    return True
