'''
Obsoleted

@author: ljiang
'''
def searchKeyInDic(search_dict, field):
    """
    Takes a dict with nested lists and dicts,
    and searches all dicts for a key of the field
    provided.
    """
    fields_found = []

    for key, value in search_dict.iteritems():

        if key == field:
            fields_found.append(value)

        elif isinstance(value, dict):
            results = searchKeyInDic(value, field)
            for result in results:
                fields_found.append(result)

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    more_results = searchKeyInDic(item, field)
                    for another_result in more_results:
                        fields_found.append(another_result)

    return fields_found


dict1={"a":1,"b":{"n":2},"c":{"d":3,"j":8},"g":[{"h":6,"i":{"l":[10,12,14],"m":11}},{'l':[10,12,14]},{'l':100000}],'l':100000}
dict2={"a":1,"m":{"d":3},"g":{"i":{"l":10}}}
key="l"
print searchKeyInDic(dict1,key)