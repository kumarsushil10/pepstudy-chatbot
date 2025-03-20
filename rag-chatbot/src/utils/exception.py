import sys

def error_message_detail(error,error_detail:sys):
    _,_,exc_tb = error_detail.exc_info()
    error_message = "Error occured in python script name [{0}] at line number [{1}] error message [{2}]".format(
        exc_tb.tb_frame.f_code.co_filename, #file name
        exc_tb.tb_lineno, #line number
        str(error) #error message
        )
    return error_message


class CustomException(Exception):
    def __init__(self, error_message,error_detail:sys):
        self.error_message = error_message_detail(error_message,error_detail)
        super().__init__(error_message)

    def __str__(self):
        return self.error_message