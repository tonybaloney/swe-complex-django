import datetime
from unittest import mock

from django.db import DEFAULT_DB_ALIAS, DatabaseError, connection, connections
from django.db.models.sql.compiler import cursor_iter
from django.db.models.sql.constants import NO_RESULTS
from django.test import TestCase

from .models import Article


class QuerySetIteratorTests(TestCase):
    def test_execute_sql_closes_cursor_without_masking_error(self):
        msg = "syntax error"
        compiler = Article.objects.all().query.get_compiler(DEFAULT_DB_ALIAS)
        cursor = mock.Mock(
            execute=mock.Mock(side_effect=DatabaseError(msg)),
            close=mock.Mock(side_effect=DatabaseError("cursor does not exist")),
        )
        with mock.patch.object(connection, "cursor", return_value=cursor):
            with self.assertRaisesMessage(DatabaseError, msg):
                compiler.execute_sql(NO_RESULTS)
        self.assertIs(cursor.close.called, True)

    itersize_index_in_mock_args = 3

    @classmethod
    def setUpTestData(cls):
        Article.objects.create(name="Article 1", created=datetime.datetime.now())
        Article.objects.create(name="Article 2", created=datetime.datetime.now())

    def test_iterator_invalid_chunk_size(self):
        for size in (0, -1):
            with self.subTest(size=size):
                with self.assertRaisesMessage(
                    ValueError, "Chunk size must be strictly positive."
                ):
                    Article.objects.iterator(chunk_size=size)

    def test_default_iterator_chunk_size(self):
        qs = Article.objects.iterator()
        with mock.patch(
            "django.db.models.sql.compiler.cursor_iter", side_effect=cursor_iter
        ) as cursor_iter_mock:
            next(qs)
        self.assertEqual(cursor_iter_mock.call_count, 1)
        mock_args, _mock_kwargs = cursor_iter_mock.call_args
        self.assertEqual(mock_args[self.itersize_index_in_mock_args], 2000)

    def test_iterator_chunk_size(self):
        batch_size = 3
        qs = Article.objects.iterator(chunk_size=batch_size)
        with mock.patch(
            "django.db.models.sql.compiler.cursor_iter", side_effect=cursor_iter
        ) as cursor_iter_mock:
            next(qs)
        self.assertEqual(cursor_iter_mock.call_count, 1)
        mock_args, _mock_kwargs = cursor_iter_mock.call_args
        self.assertEqual(mock_args[self.itersize_index_in_mock_args], batch_size)

    def test_no_chunked_reads(self):
        """
        If the database backend doesn't support chunked reads, then the
        result of SQLCompiler.execute_sql() is a list.
        """
        qs = Article.objects.all()
        compiler = qs.query.get_compiler(using=qs.db)
        features = connections[qs.db].features
        with mock.patch.object(features, "can_use_chunked_reads", False):
            result = compiler.execute_sql(chunked_fetch=True)
        self.assertIsInstance(result, list)
