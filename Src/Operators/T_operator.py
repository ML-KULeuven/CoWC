def T_operator(frequent):
    """
   Truncation operator
   1 2 3
   1 2 4
   1 2 5 6
   ------->
   1 2

   :param frequent: a list of the frequent items
   :return: the resulting frequent items
   :note: This implementation is pretty useless
   """
    return [frequent]