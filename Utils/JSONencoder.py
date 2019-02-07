from datetime import date, datetime
from json import JSONEncoder
def jsonEncoder(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        serial = obj.isoformat()
        return serial
    # Let the base class default method raise the TypeError
    return JSONEncoder.default(self, o)
