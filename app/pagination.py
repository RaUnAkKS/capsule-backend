from rest_framework.pagination import PageNumberPagination
from rest_framework.pagination import CursorPagination

class CapsulePagination(PageNumberPagination):
    page_size = 5
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 50

class MemoryCursorPagination(CursorPagination):
    cursor_query_param = 'cursor'
    page_size = 5
    ordering = '-created_at'

