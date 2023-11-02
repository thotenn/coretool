from .controllers import b64_to_img, image_name_for_save

# import re
# from datetime import datetime
#
# from django.conf import settings
# from django.db import connection
#
# settings.DEBUG = True
#
#
# global_query_counter = 0
# old_execute = None
#
# def dbquery_log(flag):
#     Cursor = None
#     if settings.DATABASES["default"]['ENGINE'] == 'django.db.backends.sqlite3':
#         from django.db.backends.sqlite3.base import SQLiteCursorWrapper
#         Cursor = SQLiteCursorWrapper
#     elif settings.DATABASES["default"]['ENGINE'] == 'django.db.backends.oracle':
#         from django.db.backends.oracle.base import FormatStylePlaceholderCursor
#         Cursor = FormatStylePlaceholderCursor
#
#     setattr(Cursor, 'log_flag', flag)
#
#     global old_execute
#     if old_execute is None:
#         old_execute = Cursor.execute
#
#     def new_execute(self, query, params=None):
#         if self.log_flag:
#             global global_query_counter
#             global_query_counter += 1
#
#             if params:
#                 q = query % tuple(params)
#             else:
#                 q = query
#             m = re.search('^(SELECT )(.*)( FROM .*)$', q)
#
#             print('   -----EJECUTAR_DB_QUERY_%d-----' % global_query_counter)
#             print('   %s' % q)
#         old_execute(self, query, params)
#         print("")
#     Cursor.execute = new_execute
#
# dbquery_log(True)
