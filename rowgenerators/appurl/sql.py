# Copyright (c) 2018 Civic Knowledge. This file is licensed under the terms of the
# MIT, included in this distribution as LICENSE

"""Appurls or sql databases"""

from rowgenerators.appurl import Url, parse_app_url
from rowgenerators.exceptions import SourceError, RowGeneratorError, AppUrlError

class Sql(Url):

    """"""

    match_priority = Url.match_priority - 1

    def __init__(self, url=None, downloader=None, **kwargs):
        # Save for auth_url()


        self.username

        self._orig_url = url
        self._orig_kwargs = dict(kwargs.items())


        super().__init__(url,downloader=downloader, **kwargs)

    def get_resource(self):
        return self

    def get_target(self):
        return self

    @property
    def dsn(self):
        """Return a database connection string. The string will have values interpolated from
        the environment"""

        import os

        u = self.clone()
        u.fragment = []
        try:
            u.password = u.password.format(**os.environ)
        except KeyError as e:
            raise RowGeneratorError(f"Failed to set password from environment variable in connection string '{str(u)}'. "
                                    f" exception = {str(e)}")

        return str(u)

    @property
    def sql(self):
        """Return the query, which is embedded in the fragment"""
        return self._fragment[0]

    @sql.setter
    def sql(self, value):
        """Return the query, which is embedded in the fragment"""
        self._fragment[0] = value


class SqlDsn(Sql):
    """
    SQL Urls of the Form:

        sql://dsn#<SQL Query>

    The dsn component must be resolved to another Sql URL, external to this system.

    """

    def __init__(self, url=None, downloader=None, dsns = None, **kwargs):
        super().__init__(url, downloader, **kwargs)

        self.dsns = dsns or {} # A dict of DSNs for DSN resolution

    def get_resource(self):

        if self.dsn_name not in self.dsns:
            raise AppUrlError(f"Resolving a SqlDsn URL requires a DSN dict with the name '{self.dsn_name}' in it. "
                              "Pass the dict to parse_app_url as parse_app_url('urlstr', dsns={<dsn_dict>}) ")

        u = parse_app_url(self.dsns[self.dsn_name])


        u._fragment[0] = self.sql

        return u

    @classmethod
    def _match(cls, url, **kwargs):
        return url.proto == 'sql'

    @property
    def dsn_name(self):
        """Return the name of the DSN that should be used"""

        return self.hostname

class OracleSql(Sql):

    generator_class = Sql

    @classmethod
    def _match(cls, url, **kwargs):
        return url.proto == 'oracle'
