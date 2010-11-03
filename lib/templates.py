"""Class models for dataset scripts from various locations. Scripts should
inherit from the most specific class available."""

from dbtk.lib.models import Database, Cleanup, correct_invalid_value
from dbtk.lib.tools import get_opts, choose_engine


class DbTk:
    """This class represents a database toolkit script. Scripts should inherit
    from this class and execute their code in the download method."""
    def __init__(self, name="", shortname="", urls=dict(), ref="", public=True, 
                 addendum=None):
        self.name = name
        self.shortname = shortname
        self.urls = urls
        self.ref = ref
        self.public = public
        self.addendum = addendum
    def __str__(self):
        desc = self.name
        if self.reference_url():
            desc += "\n" + self.reference_url()
        return desc
    def download(self, engine=None):
        self.engine = self.checkengine(engine)
        db = Database()
        db.dbname = self.shortname
        self.engine.db = db
        self.engine.get_cursor()
        self.engine.create_db()
    def reference_url(self):
        if self.ref:
            return self.ref
        else:
            if len(self.urls) == 1:
                return self.urls[self.urls.keys()[0]]
            else:
                return None
    def checkengine(self, engine=None):
        if not engine:
            opts = get_opts()
            engine = choose_engine(opts)
        engine.script = self            
        return engine
    def exists(self, engine=None):
        return all([engine.table_exists(self.shortname, key) 
                    for key in self.urls.keys() if key])
    
    
class EcologicalArchives(DbTk):
    """DbTk script template based on data files from Ecological Archives."""
    def __init__(self, name="", shortname="", urls=dict(), ref="", public=True, 
                 addendum=None, nulls=['-999', '-999.9']):
        DbTk.__init__(self, name, shortname, urls, ref, public, addendum)
        self.nulls = nulls
    def download(self, engine=None):
        DbTk.download(self, engine)
        
        for key, value in self.urls.items():
                self.engine.auto_create_table(key, url=value,
                                              cleanup=Cleanup(correct_invalid_value, 
                                                  {"nulls":self.nulls})
                                              )
                self.engine.insert_data_from_url(value)
        return self.engine
        
    def reference_url(self):
        if self.ref:
            return self.ref
        else:
            if len(self.urls) == 1:
                return '/'.join(self.urls[self.urls.keys()[0]].split('/')[0:-1]) + '/'
        
        
TEMPLATES = [
             ("Ecological Archives", EcologicalArchives)
             ]