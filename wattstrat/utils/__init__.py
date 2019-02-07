
def list_to_dict(list, key):
    """
    Transform a list of object into a dict of object, using one object key for the dict key and the object as a value
    
    var array = [{'name': 'py', 'label': 'Python'}, {'name': 'js', 'label': 'Javascript'}]
    array_to_dict(array, 'name', 'label')
    ==>
    { 'py': {'name': 'py', 'label': 'Python'}, 'js': {'name': 'js', 'label': 'Javascript'} }
    """
    return { object[key] : object for object in list }