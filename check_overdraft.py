import spending_alert.extract as ex
import spending_alert.analyze as an
import spending_alert.send_alert as sa
from pprint import pprint



def main():
    """Gets values from GSheet.
    """

    app_config = ex.get_config("conf/app_config.json")
    credential = ex.authenticate(app_config)
    category_spendings_raw = ex.get_values_from_sheet(
                                  credential,
                                  spreadsheet_id=app_config["sheet_info"]["spreadsheet_id"],
                                  range=app_config["sheet_info"]["range"])
    if not category_spendings_raw:
        raise ValueError("No data found.")
    else:
        category_spendings = an.reformat_data(category_spendings_raw)

    actual_month = category_spendings["Hónap"]
    overspent_categories = an.get_overspent_categories(category_spendings,
                                                       app_config["limit_info"])
    if len(overspent_categories):
        email_content = an.generate_email(overspent_categories)
        pprint(email_content)
        #sa.send_email(get_user_email,
        #              email_content)
        

if __name__ == "__main__":
    main()
