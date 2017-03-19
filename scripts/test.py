class PackageManager(object):
    def __init__(self, name, version, info): ##constructor call
        self.name = name
        self.version = version
        self.__info = info ## Private

    def getInformation(self):
        print "name" , self.name
        print "version" , self.version

    def _getInformation1(self):
        self.__info = self.__info[::-1]  # This will be invisible to the user
        print "name", self.name
        print "version", self.version
        print "info", self.__info

    def wrapper(self): ###public method to invoke private method
        self._getInformation1()

pm = PackageManager("ABC" , "2.2.2", "cool") ## when you create object, the object calls constructor __init__
pm.getInformation()
print pm.name ## everything is public in python
print pm.version## everything is public in python
# print pm.info ## this will fail as info is private member. You can access this using pblic method called wrapper
print pm.wrapper() ## this will call _getinformation through wrapper

