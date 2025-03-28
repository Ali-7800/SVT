class Check:
    """ 
    This class is a collection of static methods used for checking 
    that input satisfy conditions
    """
    def __init__(self) -> None:
        pass

    @staticmethod
    def validity(variable,variable_name:str,valid_variables:list,error_msg=None):
        """ 
        This method is for checking a variable is a member of list of
        valid variables
        """
        if variable not in valid_variables:
            if error_msg is None:
                raise ValueError("{0} is not a valid {1}, must be one of {2}".format(variable,variable_name,valid_variables))
            else:
                raise ValueError(error_msg)
    
    @staticmethod
    def min_length(list,list_name:str,min_length:int,error_msg=None):
        """ 
        This method is for checking a list is of a certian length
        """
        if len(list)<min_length:
            if error_msg is None:
                raise ValueError("{0} must at least have {1} element/s".format(list_name,min_length))
            else:
                raise ValueError(error_msg)
    
    @staticmethod
    def max_length(list,list_name:str,max_length:int,error_msg=None):
        """ 
        This method is for checking a list is of a certian length
        """
        if len(list)>max_length:
            if error_msg is None:
                raise ValueError("{0} must at most have {1} element/s".format(list_name,max_length))
            else:
                raise ValueError(error_msg)
    
    @staticmethod
    def length(list,list_name:str,length:int,error_msg=None):
        """ 
        This method is for checking a list is of a certian length
        """
        if len(list)==length:
            if error_msg is None:
                raise ValueError("{0} must have exactly {1} element/s".format(list_name,length))
            else:
                raise ValueError(error_msg)
            
    @staticmethod
    def object_class(variable,desired_class,variable_name:str,error_msg=None):
        """ 
        This method is for checking a object is an instance of a certian class
        """
        if not isinstance(variable,desired_class):
            if error_msg is None:
                raise ValueError("{0} must be an instance of {1}, it is instead an instance of {2}".format(variable_name,desired_class.__name__,type(variable).__name__))
            else:
                raise ValueError(error_msg)
    
    @staticmethod
    def object_class_validity(variable,valid_classes,variable_name:str,error_msg=None):
        """ 
        This method is for checking a object is an instance of a certian class
        """
        valid = False
        for valid_class in valid_classes:
            valid = (valid or isinstance(variable,valid_class))
        if not valid:
            if error_msg is None:
                raise ValueError("{0} must be an instance of one of {1}, it is instead an instance of {2}".format(variable_name,valid_classes,type(variable).__name__))
            else:
                raise ValueError(error_msg)
    
    @staticmethod
    def list_class(list,desired_class,variable_name:str,list_name:str,error_msg=None):
        """ 
        This method is for checking every object in a list is an instance of a certian class
        """
        for element in list:
            if not isinstance(element,desired_class):
                if error_msg is None:
                    raise ValueError("Every {0} in {1} must be an instance of {2}".format(variable_name,list_name,desired_class.__name__))
                else:
                    raise ValueError(error_msg)
    
    @staticmethod
    def condition(condition,error_class,error_msg):
        """ 
        This method is for checking a condition is satisfied
        """
        if not condition:
            raise error_class(error_msg)