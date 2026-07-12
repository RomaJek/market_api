from django.core.paginator import Paginator


def paginate_queryset(queryset, request=None, page_number: int | None=None, page_size: int | None=None, default_page_size=10):
    page_number = request.query_params.get('page', 1) if request else page_number
    page_size = request.query_params.get('page_size', default_page_size) if request else page_size

    try:
        page_number = int(page_number)
    except (TypeError, ValueError):
        page_number = 1

    try:
        page_size = int(page_size)
    except (TypeError, ValueError):
        page_size = default_page_size

    if page_size < 1:
        page_size = default_page_size
    if page_size > 100:
        page_size = 100

    paginator = Paginator(queryset, page_size)

    if page_number < 1:
        page_number = 1
    if page_number > paginator.num_pages:
        page_number = paginator.num_pages

    page = paginator.page(page_number)

    return {
        'results': page.object_list,
        'pagination': {
            'page': page_number,
            'page_size': page_size,
            'total_count': paginator.count,
            'total_pages': paginator.num_pages,
        },
    }
