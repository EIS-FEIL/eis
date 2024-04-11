from formencode import *
from formencode import validators 

class FilteringSchema(Schema):
    "Schema with extra fields filtered by default"
    filter_extra_fields = True

# Model-based validators

class Unique(validators.FancyValidator):
    
    """
    Checks if given value is unique to the model.Will check the state: if state object
    is the same as the instance, or the state contains a property with the same name
    as the context name. For example:
    
    validator = validators.Unique(model.NewsItem, "title", context_name="news_item")
    
    This will check if there is an existing instance with the same "title". If there
    is a matching instance, will check if the state passed into the validator is the
    same instance, or if the state contains a property "news_item" which is the same
    instance.
    """
    
    __unpackargs__ = ('model', 'attr', "model_name", "context_name", "attribute_name")
    messages = {
        'notUnique' : "%(modelName)s already exists with this %(attrName)s"
    }
    
    model_name = "Item"
    attribute_name = None
    context_name = None
    
    def _validate_python(self, value, state):
        instance = self.model.get_by(**{self.attr : value})
        if instance:
            context_name = self.context_name or self.model.__name__.lower()
            if state != instance and \
                getattr(state, context_name, None) != instance:
                attr_name = self.attribute_name or self.attr
                raise Invalid(self.message('notUnique', state, 
                                           modelName=self.model_name,
                                           attrName=attr_name), 
                              value, state)
 
validators.Unique = Unique
