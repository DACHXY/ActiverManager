import uuid

def replace_uuid(text):
    new_uuid = str(uuid.uuid4())
    return text.replace(r'%%UUID%%', new_uuid)
    
def generate_uuid():
    new_uuid = str(uuid.uuid4())
    return new_uuid