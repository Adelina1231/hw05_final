import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    request = datetime.date.today().year
    return {
        'year': request,
    }
