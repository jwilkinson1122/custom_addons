def combine_result(map_1, map_2):
    result = map_1.copy()
    for key in map_2:
        if key not in result.keys():
            result[key] = []
        result[key] = result[key] + map_2[key]
    return result
