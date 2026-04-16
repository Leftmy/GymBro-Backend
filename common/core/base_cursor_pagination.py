from rest_framework.pagination import CursorPagination


class BaseCursorPagination(CursorPagination):
    page_size = 10
    ordering = "-created_at"