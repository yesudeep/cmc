
from google.appengine.ext import db
from google.appengine.api import memcache

MAX_COUNT = 100
CACHE_DURATION = 120
LONG_CACHE_DURATION = 7200

def serialize_entities(models):
    if models is None:
        return None
    elif isinstance(models, db.Model):
        # Just one instance
        return db.model_to_protobuf(models).Encode()
    else:
        # A list
        return [db.model_to_protobuf(x).Encode() for x in models]

def deserialize_entities(data):
    from google.appengine.datastore import entity_pb
    if data is None:
        return None
    elif isinstance(data, str):
        # Just one instance
        return db.model_from_protobuf(entity_pb.EntityProto(data))
    else:
        return [db.model_from_protobuf(entity_pb.EntityProto(x)) for x in data]

class SerializableModel(db.Model):
    """
    A model parent that includes properties and functionality
    common to many model classes.

    """
    is_deleted = db.BooleanProperty(default=False)
    is_starred = db.BooleanProperty(default=False)
    is_active = db.BooleanProperty(default=False)
    when_created = db.DateTimeProperty(auto_now_add=True)
    when_modified = db.DateTimeProperty(auto_now=True)

    @classmethod
    def get_all(cls, count=MAX_COUNT):
        cache_key = '%s.get_all()' % (cls.__name__,)
        entities = deserialize_entities(memcache.get(cache_key))
        if not entities:
            entities = db.GqlQuery('SELECT * FROM %s' % cls.__name__).fetch(count)
            memcache.set(cache_key, serialize_entities(entities), CACHE_DURATION)
        return entities

    def to_json_dict(self, *props):
        properties = self.properties()
        if props:
            serializable_properties = props
        else:
            serializable_properties = getattr(self, '__serialize__', [])
            if not serializable_properties:
                serializable_properties = properties.keys()
            else:
                serializable_properties.extend([
                    'is_deleted',
                    'is_starred',
                    'is_active',
                    'when_created',
                    'when_modified',
                    ])
        output = {}
        output['key'] = str(self.key())
        for prop in set(serializable_properties):
            v = properties[prop]
            if isinstance(v, db.DateTimeProperty) or isinstance(v, db.DateProperty):
                convert_function = (lambda d: d.strftime('%Y-%m-%dT%H:%M:%S'))
                output[prop] = convert_function(getattr(self, prop))
            elif isinstance(v, db.ReferenceProperty):
                str_key = str(getattr(self, prop).key())
                output[prop] = str_key
                #output[prop + '_key'] = str_key
            #elif isinstance(v, db.StringProperty):
            #    output[prop] = str(getattr(self, prop))
            #elif isinstance(v, db.BooleanProperty):
            #    output[prop] = bool(getattr(self, prop))
            else:
                output[prop] = getattr(self, prop)
        return output

    def to_json(self, *props):
        from django.utils import simplejson as json
        from jsmin import jsmin
        
        json_dict = self.to_json_dict(*props)
        return jsmin(json.dumps(json_dict))
