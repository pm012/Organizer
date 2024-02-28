from abc import ABC, abstractmethod
import pickle
import os.path

class FileConnector(ABC):
    @abstractmethod
    def save_data(self, connection_string):
        pass

    @abstractmethod
    def retreive_data(self, connection_string):
        pass


class BinaryFileDBConnector(FileConnector):
    FILENAME = "./BotAssistant/BotAssistant/res/phone_book.dat"

    def save_data(self, filename=FILENAME):
        with open (filename, "wb") as file:
            pickle.dump(self, file)
    
    def retreive_data(self, filename=FILENAME):
        if os.path.isfile(filename):
            with open(filename, 'rb') as file:            
                content = pickle.load(file)
            return content
        else:
            return None
        
# Can be extended in case other file storage types usage
class FileConnectorFactory:
    
    def get_connector(self, file_storage_type):
        if file_storage_type == 'binary':
            return BinaryFileDBConnector()
        else:
            raise ValueError(f"Unsupported connector type")
        



