from operator import itemgetter


def reformat_data(data: list[list[str, str]]) -> dict[str, int]:
    """Creates useful datafomat.
    :param data: list of lists by column, returned by extract.get_values_from_sheet
    :return: a dict containing numeric data as ints
    """
    formatted_data = dict([[col[0], int(col[1])]
                            for col
                            in data])
    return formatted_data


def get_limited_cats_in_data(data: dict[str, int],
                             limit_info: dict[str, int] = {"categ_1": 0,
                                                           "categ_2": 0}
                             ) -> dict[str, int]:
    """Removes limit categories if they are not in data 
    :param data: dict containing actual spending data for categories, and month
    :param limit_info: dict either returned by extract.get_config()["limit_info"],
                       or a dict with categories and limits
    :return: filtered limit_info
    """
    cats_in_both_datasets = set(data.keys()).intersection(set(limit_info.keys()))
    if len(cats_in_both_datasets) == 0:
        raise RuntimeError("No limited category found among spending categories!\n" + \
                           f"\tSpending categories: {", ".join(data.keys())}\n" + \
                           f"\tLimited categories: {", ".join(limit_info.keys())}")
    filtered_limits = {cat: amount
                       for cat, amount
                       in limit_info.items()
                       if cat in cats_in_both_datasets}
    return filtered_limits
    

def get_overspent_categories(data: dict[str, int],
                             limit_info: dict[str, int] = {"categ_1": 0,
                                                           "categ_2": 0}
                             ) -> list[str]:
    """Checks if current spending is over the set limit
    :param data: dict containing actual spending data for categories, and month
    :param limit_info: dict either returned by extract.get_config()["limit_info"],
                       or a dict with categories and limits
    :return: list of category names
    """
    
    relevant_categoies = get_limited_cats_in_data(data, limit_info)
    
    remaining_budget = {cat: limit - int(data[cat])
                        for cat, limit
                        in relevant_categoies.items()}

    overspent_categories = {cat: abs(value)
                            for cat, value
                            in remaining_budget.items()
                            if value < 0}
    
    return overspent_categories


def generate_email(overspent_data: dict[str, int]) -> dict[str,str]:
    """Creates email subject and body
    :param data: dict of categories with ovespending amount
    :return: dict of email subject and text body
    """
    category_list = ', '.join(overspent_data.keys())
    category_string = f"categor{'ies' if len(overspent_data) > 1 else 'y'}"
    subject_text = f"Overspent in {category_list} {category_string}"
    body = f"You spent more than this month's budget in the following {category_string}:\n" + \
           "\n".join([f"\t{cat}:\t{amount}"
                      for cat, amount
                      in overspent_data.items()])
    return {"subject": subject_text,
            "body": body}


def generate_push():
    raise(NotImplementedError)

