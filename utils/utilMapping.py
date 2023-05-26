def type_to_factor(in_type):
    if(in_type == 'BUY') :
        return 1
    elif(in_type == 'SELL') :
        return -1
    else :
        raise Exception
def from_entry_to_category(in_entries) :
    in_entries = in_entries['Reason']
    if in_entries == 'DEAL_REASON_TP' :
        return 1
    elif (in_entries == 'DEAL_REASON_EXPERT' or 'DEAL_REASON_CLIENT'):
        return 0
    elif   in_entries == 'DEAL_REASON_SL' :
        return 2
    else :
        raise Exception('from_entry_to_category function')
