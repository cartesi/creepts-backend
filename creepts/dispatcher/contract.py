import json

class Contract:
    """Encapsulates the information of a Contract as returned by the dispatcher"""

    def __init__(self, json_obj):
        """Creates a class to encapsulate the contract state returned by dispatcher
        Parses json encoded data inside json_data field into an indexable property
        """
        self.json_obj = json_obj
        if "json_data" in json_obj:
            self.data = json.loads(json_obj["json_data"])
        else:
            self.data = {}

        if "sub_instances" in json_obj:
            self.children = [Contract(child) for child in json_obj["sub_instances"]]
        else:
            self.children = []

    @staticmethod
    def convert_type(value):
        """Converts hexadecimal strings to integers, unless its a ethereum address or blob"""
        if isinstance(value, str):
            # if starts with 0x and has more then 42 characters
            # consider it a address or binary blob and return string as is
            if value.startswith("0x") and len(value) >= 42:
                return value

            # if starts with 0x, convert to int
            if value.startswith("0x"):
                return int(value[2:], 16)

        return value
    
    def __getitem__(self, key):
        """Returns a property of the contract by name"""
        return self.convert_type(self.data[key])

    def get_name(self):
        """Returns the name of the contract"""
        return self.json_obj["name"]

    def get_contract_address(self):
        """Returns the address of the contract in the blockchain"""
        return self.json_obj["concern"]["contract_address"]

    def get_user_address(self):
        """Returns the account owner of the contract in the blockchain"""
        return self.json_obj["concern"]["user_address"]

    name = property(get_name)
    contract_address = property(get_contract_address)
    user_address = property(get_user_address)
