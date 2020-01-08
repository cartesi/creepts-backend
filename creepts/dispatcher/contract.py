import json

class Contract:
    """Encapsulates the information of a Contract as returned by the dispatcher"""

    def __init__(self, json_obj):
        """Creates a class to encapsulate the contract state returned by dispatcher
        Parses json encoded data inside json_data field into an indexable property
        """
        self.json_obj = json_obj
        if "json_data" in json_obj:
            #This conversion is not needed in the mocked data
            if type(json_obj["json_data"]) == str:
                self.data = json.loads(json_obj["json_data"])
            else:
                self.data = json_obj["json_data"]
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

            # if starts with 0x, assume its a numeric value in hexadecimal and convert to int
            if value.startswith("0x"):
                return int(value, 16)

        return value

    def __getitem__(self, key):
        """Returns a property of the contract by name"""
        if key not in self.data:
            raise KeyError("Attribute '%s' not found in contract" % (key))

        return self.convert_type(self.data[key])

    def __contains__(self, key):
        """Returns if a property exists in the contract"""
        return key in self.data

    def get_name(self):
        """Returns the name of the contract"""
        return self.json_obj["name"]

    def get_index(self):
        """Returns the index of the contract instance"""
        return self.convert_type(self.json_obj["index"])

    def get_contract_address(self):
        """Returns the address of the contract in the blockchain"""
        return self.json_obj["concern"]["contract_address"]

    def get_user_address(self):
        """Returns the account owner of the contract in the blockchain"""
        return self.json_obj["concern"]["user_address"]

    name = property(get_name)
    contract_address = property(get_contract_address)
    user_address = property(get_user_address)
    index = property(get_index)
