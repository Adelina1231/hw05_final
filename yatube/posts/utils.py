from django.core.paginator import Paginator
from django.conf import settings


def get_page_context(posts, request):
    paginator = Paginator(posts, settings.NUM_OF_POST)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
