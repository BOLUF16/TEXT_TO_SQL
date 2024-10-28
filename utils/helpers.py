def format_gandalf(response_dict):
    if isinstance(response_dict, dict):
        sql_query = response_dict.get('sql_query').splitlines()
        re = [res for res in response_dict.get("results")]
        result = []
        for i in re[0].items():
            result.append(f'{i} \n')
        result = ''.join(result).splitlines()

    return sql_query, result
